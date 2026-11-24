"""Explicit synthetic-only foreground composition, never a product approval."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import socket
import sys

from apps.lab.g3_fake import DUMMY_KEY, FAKE_MODEL
from apps.llm_workers.g3_admission import G3PreEffectAdmission
from apps.llm_workers.prompt_builder import PromptEnvelope
from core.execution.exceptions import G3ExternalEffectNotStartedError
from core.prompting.inference_result import InferenceResult
from core.validation.protocols import TokenEstimatorProtocol

ENDPOINT = "http://127.0.0.1:8080"
OPT_IN = "EXPLICIT_OFFLINE_TEST_ONLY"
PROVIDER_ID = "offline-test"
PROMPT_VERSION = "pppr-g5-offline-v1"
# Never turn inherited credentials or proxy settings into an approval.
_FORBIDDEN_ENV = (
    "GEMINI_API_KEY", "GEMINI_API_URL", "GOOGLE_API_KEY", "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY", "HF_TOKEN", "HUGGING_FACE_HUB_TOKEN",
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
    "TPDF_FAKE_PRIVATE_DOCKER", "TPDF_C0_VOLUME_INIT", "TPDF_LOCAL_VOLUME_INIT",
)


def require_isolated_environment() -> None:
    """Fail closed before bootstrap or provider construction; no network I/O."""
    if (os.getenv("TPDF_OFFLINE_LAB") != OPT_IN
            or os.getenv("GROQ_API_KEY") != DUMMY_KEY
            or os.getenv("GROQ_BASE_URL") != ENDPOINT
            or os.getenv("IS_BENCHMARK") != "0"
            or os.getenv("APP_ROOT") != "/app"
            or os.getenv("SQLITE_STATE_DIR") != "/app/state"
            or os.getenv("COMPILER_OUTPUT_DIR") != "/app/output"
            or os.getenv("TIKTOKEN_CACHE_DIR") != "/app/data/tiktoken-cache"
            or any(os.getenv(key) for key in _FORBIDDEN_ENV)):
        raise G3ExternalEffectNotStartedError("PPPR_G5_LAB_ENVIRONMENT_REJECTED", permanent=True)
    if sys.platform != "linux":
        raise G3ExternalEffectNotStartedError("PPPR_G5_LAB_ISOLATION_REQUIRED", permanent=True)
    try:
        status = dict(line.split(":", 1) for line in
                      Path("/proc/self/status").read_text().splitlines() if ":" in line)
        mounts = {fields[4]: set(fields[5].split(",")) for line in
                  Path("/proc/self/mountinfo").read_text().splitlines()
                  if len(fields := line.split(" - ", 1)[0].split()) >= 6}
        isolated = (
            {name for _, name in socket.if_nameindex()} == {"lo"}
            and os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 10001
            and all(int(status[key].strip(), 16) == 0
                    for key in ("CapEff", "CapPrm", "CapBnd"))
            and status["NoNewPrivs"].strip() == "1"
            and "ro" in mounts.get("/workspace", set())
            and all("rw" in mounts.get(path, set()) for path in (
                "/app/state", "/app/data", "/app/output", "/app/.cache/tectonic",
            ))
        )
    except (OSError, ValueError, KeyError) as exc:
        raise G3ExternalEffectNotStartedError(
            "PPPR_G5_LAB_ISOLATION_REQUIRED", permanent=True,
        ) from exc
    if not isolated:
        raise G3ExternalEffectNotStartedError("PPPR_G5_LAB_ISOLATION_REQUIRED", permanent=True)


@dataclass(frozen=True, slots=True)
class OfflineLabScope:
    """Only the launcher passes this explicitly, for one generated PDF."""
    document_id: str

    def validate(self, document_id: str) -> None:
        require_isolated_environment()
        if not re.fullmatch(r"[0-9a-f]{64}", self.document_id) or document_id != self.document_id:
            raise G3ExternalEffectNotStartedError("PPPR_G5_LAB_DOCUMENT_SCOPE_REJECTED", permanent=True)

    def validate_source(self, path: Path) -> None:
        if (path != Path("/app/data/offline_smoke.pdf") or path.is_symlink()
                or not path.is_file()):
            raise G3ExternalEffectNotStartedError("PPPR_G5_LAB_SOURCE_REJECTED", permanent=True)
        self.validate(sha256(path.read_bytes()).hexdigest())

    @property
    def root_config_sha256(self) -> str:
        options = {
            "scope": "PPPR_G5_SYNTHETIC_LOOPBACK_ECHO_V1",
            "provider_id": PROVIDER_ID, "model_name": FAKE_MODEL,
            "endpoint": ENDPOINT, "dialect": "openai_compatible_json_v1",
            "source_language": "en", "target_language": "es",
            "prompt_version": PROMPT_VERSION, "response_contract": "G3_CHUNK_RESPONSE_V1",
            "temperature": 0.00001, "stream": False, "target_lang_expansion": 2.0,
            "primary_window_limit": 8192, "fallback_window_limit": 1048576,
            "min_output_reserve": 256, "max_output_reserve": 4096,
        }
        return sha256(json.dumps(options, sort_keys=True, ensure_ascii=False,
                                 separators=(",", ":")).encode("utf-8")).hexdigest()

    def admission(self, estimator: TokenEstimatorProtocol) -> G3PreEffectAdmission:
        return G3PreEffectAdmission(
            provider_id=PROVIDER_ID, model_name=FAKE_MODEL,
            root_config_sha256=self.root_config_sha256,
            input_limit=32768, output_limit=4096, context_window=65536,
            input_estimator=estimator, estimator_evidence_ref="SYNTHETIC_CL100K_NOT_COMMERCIAL",
            egress_authorization_ref="SYNTHETIC_LOOPBACK_ONLY",
            data_scope_ref="SYNTHETIC_GENERATED_PDF_ONLY",
            purpose_ref="SYNTHETIC_PPPR_5_2_1_EN_ES_ECHO",
            retention_ref="SYNTHETIC_LOCAL_EVIDENCE_ONLY",
            training_use_ref="SYNTHETIC_NO_MODEL_NO_TRAINING",
            budget_authorization_ref="SYNTHETIC_ZERO_COMMERCIAL_SPEND",
            price_evidence_ref="SYNTHETIC_NO_COMMERCIAL_PRICES",
            input_price_per_token=Decimal("0"), output_price_per_token=Decimal("0"),
            authorized_max_cost=Decimal("0"),
        )


class OfflineLoopbackProvider:
    """Reuse the physical SDK adapter; own and close a bounded local client per call."""

    def __init__(self, scope: OfflineLabScope) -> None:
        scope.validate(scope.document_id)
        self._scope = scope

    async def translate(self, envelope: PromptEnvelope) -> InferenceResult:
        from groq import AsyncGroq
        import httpx
        from apps.llm_workers.adapters import GroqProvider
        from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect

        try:
            document_id = json.loads(envelope.schema.payload.content)["response_binding"]["document_id"]
        except (TypeError, ValueError, KeyError) as exc:
            raise G3ExternalEffectNotStartedError(
                "PPPR_G5_LAB_DOCUMENT_SCOPE_REJECTED", permanent=True,
            ) from exc
        self._scope.validate(document_id)
        if envelope.model_name != FAKE_MODEL or envelope.target_provider != "primary":
            raise G3ExternalEffectNotStartedError("PPPR_G5_LAB_SELECTION_REJECTED", permanent=True)
        # No DNS, env-derived proxy, redirects or SDK retries. One client per
        # bounded synthetic call; the context closes it even on exceptions.
        async with AsyncGroq(
            api_key=DUMMY_KEY, base_url=ENDPOINT, max_retries=0, timeout=15.0,
            http_client=httpx.AsyncClient(trust_env=False, follow_redirects=False, timeout=15.0),
        ) as client:
            return await GroqProvider(
                DUMMY_KEY, OpenAICompatibleDialect(), client=client,
            ).translate(envelope)
