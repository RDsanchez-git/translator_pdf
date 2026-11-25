"""
Composition Root del provider stack.

Stack order: CircuitBreaker → Cache → RateLimiter → Provider

NADR-11 §5.1 R1: Único punto de construcción del grafo de objetos.
NADR-08 §5.1 R4: RateLimitStore inyectado desde Composition Root.
NADR-08 §5.2 R7: CircuitBreaker MANDATORY en todas las rutas.
NADR-08 §5.5: CB antes de RL previene consumo de cuota con circuito abierto.
"""
import os
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.compiler.tectonic_runner import CachedTectonicResources

import httpx
from groq import AsyncGroq

from infra.db.connection import resolve_sqlite_path

from apps.llm_workers.adapters import GroqProvider
from apps.llm_workers.g3_admission import GPT_OSS_120B, G3PreEffectAdmission
from apps.llm_workers.groq_free_transport import GroqFreeWitnessTransport
from apps.llm_workers.prompt_builder import PromptEnvelope
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.circuit_breaker_provider import CircuitBreakerProvider
from apps.llm_workers.routing import LLMProvider
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.resilience.circuit_breaker import GlobalCircuitBreaker
from core.resilience.rate_limit_store import RateLimitStore
from core.execution.effect_guard import g3_free_dispatch_permit, g3_pre_effect_guard
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.prompting.inference_result import InferenceResult
from core.validation.protocols import TokenEstimatorProtocol


@dataclass(frozen=True, slots=True)
class ProductGroqScope:
    """Explicit caller-supplied composition; never obtained from environment.

    The caller must independently establish the host, data/egress permissions,
    exclusive account quota, free entitlement and conservative wire bound.
    Ordinary prompt measurement is not a substitute for the admission bound.
    """

    admission: G3PreEffectAdmission
    prompt_estimator: TokenEstimatorProtocol
    transport_factory: Callable[[], httpx.AsyncBaseTransport]
    compiler_resources: "CachedTectonicResources | None" = None

    def require_compiler_resources(self) -> "CachedTectonicResources":
        if self.compiler_resources is None or not self.compiler_resources.cache_dir.is_dir():
            raise G3ExternalEffectNotStartedError(
                "PPPR_G6_PRODUCT_COMPILER_RESOURCES_REQUIRED", permanent=True,
            )
        return self.compiler_resources

    def validate(self, document_id: str, root_config_sha256: str) -> None:
        policy = self.admission
        witness = policy.free_tier_witness
        if (witness is None or witness.document_id is None
                or witness.document_id != document_id
                or policy.provider_id != "groq" or policy.model_name != GPT_OSS_120B
                or policy.root_config_sha256 != root_config_sha256
                or not isinstance(policy.authorized_max_cost, Decimal)
                or not policy.authorized_max_cost.is_finite()
                or policy.authorized_max_cost != Decimal("0")
                or type(policy.input_limit) is not int or not 1 <= policy.input_limit <= 8000
                or type(policy.output_limit) is not int or not 1 <= policy.output_limit <= 4096
                or type(policy.context_window) is not int or not 1 <= policy.context_window <= 131072
                or not all(isinstance(ref, str) and ref.strip() for ref in (
                    policy.estimator_evidence_ref, policy.egress_authorization_ref,
                    policy.data_scope_ref, policy.purpose_ref, policy.retention_ref,
                    policy.training_use_ref, policy.budget_authorization_ref,
                    policy.price_evidence_ref,
                ))):
            raise G3ExternalEffectNotStartedError(
                "PPPR_G6_PRODUCT_SCOPE_REJECTED", permanent=True,
            )
        witness.verify(model_name=GPT_OSS_120B, target_provider="primary", combined_tokens=1)


async def build_provider_stack(
    api_key: str,
    provider_type: Literal["groq", "gemini"] = "groq",
    rpm_limit: int = 30,
    tpm_limit: int = 6000,
    cache_db_path: str | None = "infra/db/materialized.db",
    rate_limit_store: RateLimitStore | None = None,
    *, provider_override: LLMProvider | None = None,
) -> LLMProvider:
    """
    Composition Root del provider stack.

    Stack order: CircuitBreaker → Cache → RateLimiter → Provider

    Args:
        api_key: Credencial del provider.
        provider_type: "groq" (default, producción) o "gemini" (benchmark).
        rpm_limit: Requests per minute.
        tpm_limit: Tokens per minute.
        cache_db_path: Path al SQLite de cache. None = deshabilitado (benchmark).
        rate_limit_store: Backend de persistencia de cuotas. None = memoria local.

    Returns:
        LLMProvider con stack: CB → Cache → RL → Provider.
    """
    # Explicit caller-owned transport; never selected from environment.
    if provider_override is not None:
        base_provider = provider_override
    elif provider_type == "groq":
        dialect = OpenAICompatibleDialect()
        base_provider = GroqProvider(api_key=api_key, dialect=dialect)
    elif provider_type == "gemini":
        # Lazy import: google.generativeai genera warning de deprecación
        # al importarse. Se evita cargar la dependencia cuando solo se usa Groq.
        from apps.llm_workers.adapters import GeminiProvider
        base_provider = GeminiProvider(api_key=api_key)
    else:
        raise ValueError(f"Provider type no soportado: {provider_type}")

    quota_manager = QuotaManager(
        rpm_limit=rpm_limit,
        tpm_limit=tpm_limit,
        store=rate_limit_store,
    )
    rate_provider = RateLimitedProvider(
        underlying=base_provider,
        quota_manager=quota_manager,
    )

    if cache_db_path is not None:
        cached_provider = CachedLLMProvider(
            underlying=rate_provider,
            db_path=(resolve_sqlite_path(cache_db_path) if os.getenv("SQLITE_STATE_DIR") else cache_db_path),
        )
        await cached_provider.initialize()
        provider: LLMProvider = cached_provider
    else:
        provider = rate_provider

    breaker = GlobalCircuitBreaker()
    return CircuitBreakerProvider(underlying=provider, breaker=breaker)

class _GroqFreeWitnessProvider:
    """Own a per-attempt SDK client inside the bridge's event loop.

    The explicitly supplied transport factory is the host boundary. No
    default live transport, credential discovery or environment activation.
    Admission, a committed reservation and an accredited measurement remain
    the caller's responsibility. Each attempt requires its own committed permit.
    """

    def __init__(self, api_key: str, transport_factory: Callable[[], httpx.AsyncBaseTransport]):
        if not api_key.strip():
            raise ValueError("PPPR_G5_FREE_KEY_REQUIRED")
        self._api_key = api_key
        self._transport_factory = transport_factory

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        if (envelope.model_name != GPT_OSS_120B or envelope.target_provider != "primary"
                or g3_free_dispatch_permit.get() is None or g3_pre_effect_guard.get() is None):
            raise G3ExternalEffectNotStartedError("PPPR_G5_FREE_COMPOSITION_SCOPE_REQUIRED", permanent=True)
        # No socket or SDK client is created until this explicit route is
        # invoked after the canonical stack has checked quota and authority.
        async with AsyncGroq(
            api_key=self._api_key, base_url="https://api.groq.com", max_retries=0, timeout=30.0,
            http_client=httpx.AsyncClient(
                transport=GroqFreeWitnessTransport(self._transport_factory()),
                trust_env=False, follow_redirects=False, timeout=30.0,
            ),
        ) as client:
            return await GroqProvider(
                self._api_key, OpenAICompatibleDialect(), client=client,
                require_attributed_response=True,
            ).translate(envelope)


async def build_groq_free_witness_stack(
    *,
    api_key: str,
    transport_factory: Callable[[], httpx.AsyncBaseTransport],
    rate_limit_store: RateLimitStore,
) -> LLMProvider:
    """Compose guarded free attempts via the canonical provider stack.

    Requires caller-owned durable local quota store and explicit transport.
    No fallback, legacy cache or paid service selection. The per-minute
    configured maxima are not current remaining account balances; the
    existing request admission separately checks the four witness quotas.
    This factory grants no egress or measurement accreditation.
    """
    return await build_provider_stack(
        api_key=api_key, provider_type="groq",
        rpm_limit=30, tpm_limit=8000,
        cache_db_path=None, rate_limit_store=rate_limit_store,
        provider_override=_GroqFreeWitnessProvider(api_key, transport_factory),
    )
