import asyncio
import threading
import logging
from core.ast.models import ASTNode, TranslationTaskType, TranslationUnit
from apps.llm_workers.routing import LLMProvider
from apps.llm_workers.prompt_builder import PromptBuilder
from core.execution.constants import CURRENT_PROJECTION_VERSION  # SOTA: Fuente única de verdad
from core.context.context_resolver import ResolvedContext

logger = logging.getLogger(__name__)

class SyncProviderBridge:
    """SOTA: Adaptador de impedancia Thread-Safe con ciclo de vida asíncrono controlado."""
    
    def __init__(self, async_provider: LLMProvider, prompt_builder: PromptBuilder, timeout_sec: float = 180.0):
        self._provider = async_provider
        self._builder = prompt_builder
        self._timeout = timeout_sec
        
        self.prompt_v = prompt_builder.prompt_version
        self.model_v = prompt_builder.model_name
        self.projection_v = CURRENT_PROJECTION_VERSION  # SOTA: Eliminación de hardcode
        
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_loop, daemon=True, name="LLM-SyncBridgeLoop")
        self._ready_event = threading.Event()
        self._thread.start()
        
        if not self._ready_event.wait(timeout=5.0):
            raise RuntimeError("CRÍTICO: El Event Loop del SyncProviderBridge falló en la inicialización.")

    def _start_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._ready_event.set()
        try:
            self._loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    def shutdown(self) -> None:
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=2.0)

    def execute(self, node: ASTNode) -> str:
        """Contrato de ejecución sincrónico para hilos de ThreadPoolExecutor."""
        import hashlib
        
        # SOTA FIX: Extracción polimórfica segura desde Pydantic Union.
        # 6 de los 7 payloads usan 'content'. ImagePayload usa 'alt_text'.
        if not node.payload:
            target_payload = ""
        else:
            raw_text = getattr(node.payload, "content", getattr(node.payload, "alt_text", ""))
            target_payload = str(raw_text or "")
            
        payload_sha256 = hashlib.sha256(target_payload.encode('utf-8')).hexdigest()
        
        # SOTA: Reconstrucción completa del DTO satisfaciendo la firma inmutable
        unit = TranslationUnit(
            chunk_index=node.control_plane.get("chunk_index", -1),
            chunk_id=node.node_id,
            chunk_fingerprint=node.control_plane.get("chunk_fingerprint", f"fp_{node.node_id[:12]}"),
            chunk_type=TranslationTaskType.TRANSLATE,
            source_sequence_range=(0, 0),
            node_count=1,
            context_id=node.control_plane.get("context_id", ""),
            context_depth=node.control_plane.get("context_depth", 0),
            target_payload=target_payload,
            estimated_tokens=0,
            payload_sha256=payload_sha256
        )
        
        # SOTA: Null-Object válido con tupla vacía.
        fallback_context = ResolvedContext(
            context_id=unit.context_id,
            breadcrumbs=()
        )
        
        build_result = self._builder.build(unit, resolved_context=fallback_context)
        
        if build_result.status == "failed":
            raise RuntimeError(f"SyncBridge abortado: {build_result.message} (Razón: {build_result.error_reason.value})")
            
        envelope = build_result.envelope

        future = asyncio.run_coroutine_threadsafe(self._provider.translate(envelope), self._loop)
        
        try:
            result = future.result(timeout=self._timeout)
            return result.content
        except TimeoutError as e:
            logger.error(f"SyncBridge Timeout de {self._timeout}s excedido para nodo {node.node_id[:8]}")
            future.cancel()
            raise TimeoutError(f"Operación de red estancada: {e}") from e
        except Exception:
            # SOTA: Prevención estricta de fuga de memoria cancelando el future
            future.cancel()
            raise