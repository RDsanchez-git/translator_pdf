"""
Composition Root del provider stack.

Stack order: CircuitBreaker → Cache → RateLimiter → Provider

NADR-11 §5.1 R1: Único punto de construcción del grafo de objetos.
NADR-08 §5.1 R4: RateLimitStore inyectado desde Composition Root.
NADR-08 §5.2 R7: CircuitBreaker MANDATORY en todas las rutas.
NADR-08 §5.5: CB antes de RL previene consumo de cuota con circuito abierto.
"""
from typing import Literal

from apps.llm_workers.adapters import GroqProvider
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.circuit_breaker_provider import CircuitBreakerProvider
from apps.llm_workers.routing import LLMProvider
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect
from core.resilience.circuit_breaker import GlobalCircuitBreaker
from core.resilience.rate_limit_store import RateLimitStore


async def build_provider_stack(
    api_key: str,
    provider_type: Literal["groq", "gemini"] = "groq",
    rpm_limit: int = 30,
    tpm_limit: int = 6000,
    cache_db_path: str | None = "infra/db/materialized.db",
    rate_limit_store: RateLimitStore | None = None,
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
    if provider_type == "groq":
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
            db_path=cache_db_path,
        )
        await cached_provider.initialize()
        provider: LLMProvider = cached_provider
    else:
        provider = rate_provider

    breaker = GlobalCircuitBreaker()
    return CircuitBreakerProvider(underlying=provider, breaker=breaker)