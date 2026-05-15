import time
import hashlib
import logging

# Imports del Document FSM
from core.execution.state import (
    DocumentCommand, StartParsingCommand, StartProcessingCommand,
    MarkAssemblyReadyCommand, StartAssemblyCommand, MarkCompilationReadyCommand,
    StartCompilationCommand, CompleteDocumentCommand, FailDocumentCommand,
    CancelDocumentCommand, DocumentState, FSMValidator,
    StallDocumentCommand, ResumeDocumentCommand, TERMINAL_STATES,
    # SOTA: Nuevos comandos del Reconciliador
    RematerializeTaskCommand
)
from infra.db.fsm_repository import FSMRepository

# Imports del Reconciliador
from core.normalization.normalizer import TextNormalizer
from core.metrics.metrics import Metrics
from core.execution.state import RecoverZombieTaskCommand

logger = logging.getLogger(__name__)

# =====================================================================
# HANDLER 1: ORQUESTACIÓN DE DOCUMENTOS (FSM)
# =====================================================================

class DocumentCommandHandler:
    """SOTA: Capa de coordinación pura. Transiciona estados sin ejecutar side-effects."""
    
    def __init__(self, repository: FSMRepository):
        self.repo = repository

    def _get_target_state(self, command: DocumentCommand, doc_status: dict) -> DocumentState:
        if isinstance(command, ResumeDocumentCommand):
            suspended = doc_status.get("suspended_state")
            if not suspended:
                raise ValueError(f"No existe suspended_state para reanudar el doc {command.document_id}")
            return DocumentState(suspended)

        mapping = {
            StartParsingCommand: DocumentState.PARSING,
            StartProcessingCommand: DocumentState.PROCESSING,
            MarkAssemblyReadyCommand: DocumentState.READY_FOR_ASSEMBLY,
            StartAssemblyCommand: DocumentState.ASSEMBLING,
            MarkCompilationReadyCommand: DocumentState.READY_FOR_COMPILATION,
            StartCompilationCommand: DocumentState.COMPILING,
            CompleteDocumentCommand: DocumentState.COMPLETED,
            FailDocumentCommand: DocumentState.FAILED,
            CancelDocumentCommand: DocumentState.CANCELLED,
            StallDocumentCommand: DocumentState.STALLED 
        }
        target = mapping.get(type(command))
        if not target:
            raise TypeError(f"Comando desconocido: {type(command)}")
        return target

    def handle(self, command: DocumentCommand) -> int:
        doc_status = self.repo.get_status(command.document_id, command.ast_hash)
        if not doc_status:
            raise ValueError(f"Documento {command.document_id} no inicializado en FSM.")
        
        current_state = DocumentState(doc_status["state"])
        db_ast_hash = doc_status["ast_hash"]

        if db_ast_hash != command.ast_hash:
            raise ValueError(f"Fuga generacional: Comando esperaba {command.ast_hash}, FSM tiene {db_ast_hash}")

        target_state = self._get_target_state(command, doc_status)
        FSMValidator.validate(current_state, target_state)

        is_terminal = target_state in TERMINAL_STATES
        failure_reason = getattr(command, "reason", None) if is_terminal or target_state == DocumentState.STALLED else None
        suspended_state = current_state.value if target_state == DocumentState.STALLED else None

        self.repo.transition_to(
            document_id=command.document_id,
            ast_hash=command.ast_hash,
            old_state=current_state.value,
            new_state=target_state.value,
            current_version=command.expected_version,
            owner_id=command.owner_id,
            is_terminal=is_terminal,
            failure_reason=failure_reason,
            suspended_state=suspended_state
        )

        logger.info("FSM_TRANSITION_SUCCESS", extra={
            "extra_data": {
                "doc_id": command.document_id[:8],
                "transition": f"{current_state.value} -> {target_state.value}",
                "new_version": command.expected_version + 1
            }
        })

        return command.expected_version + 1


# =====================================================================
# HANDLER 2: REPARACIÓN DE CHUNKS (RECONCILIADOR)
# =====================================================================

class ReconciliationCommandHandler:
    """SOTA: Mutaciones idempotentes para recuperación de entropía."""
    
    def __init__(self, system_repo, task_repo, event_repo, mat_repo, metrics: Metrics):
        self.system = system_repo
        self.task = task_repo
        self.event = event_repo
        self.mat = mat_repo
        self.metrics = metrics

    def handle_rematerialize(self, cmd: RematerializeTaskCommand):
        t_start = time.perf_counter()
        
        current_epoch = self.system.get_current_epoch("global_reconciler")
        if cmd.reconciler_epoch != current_epoch:
            logger.warning("STALE_RECONCILER_COMMAND_DROPPED", extra={"extra_data": {"cmd_epoch": cmd.reconciler_epoch, "sys_epoch": current_epoch}})
            self.metrics.inc("reconciliation_stale_epoch_total")
            return

        try:
            latest_event = self.event.get_latest_event(cmd.node_id)
            if not latest_event or latest_event.lifecycle != "GENERATED":
                logger.error("CQRS_DESYNC_UNRECOVERABLE", extra={"extra_data": {"node_id": cmd.node_id}})
                self.metrics.inc("reconciliation_failed_total")
                return

            raw_response = latest_event.raw_response
            normalized = TextNormalizer.normalize(raw_response)
            normalized_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()

            # SOTA: Mantenemos "unknown_ast_hash" hasta que se inyecte por esquema o lectura
            self.mat.upsert_projection(
                cmd.document_id, "unknown_ast_hash", cmd.node_id, latest_event.content_hash, 
                normalized, normalized_hash, latest_event.projection_version
            )

            reconciled = self.task.mark_cqrs_reconciled(cmd.task_id, cmd.reconciliation_id)
            
            if not reconciled:
                logger.info("RECONCILIATION_DUPLICATE_IGNORED", extra={"extra_data": {"recon_id": cmd.reconciliation_id}})
                self.metrics.inc("reconciliation_duplicate_total")
                return

            duration_ms = (time.perf_counter() - t_start) * 1000
            logger.info("cqrs_rematerialization_complete", extra={"extra_data": {
                "operation": "cqrs_rematerialization",
                "reconciliation_id": cmd.reconciliation_id,
                "duration_ms": round(duration_ms, 2),
                "replay_source": "wal",
                "epoch": cmd.reconciler_epoch
            }})
            self.metrics.inc("reconciliation_success_total")

        except Exception as e:
            logger.exception("Fallo catastrófico en rematerialización.")
            self.metrics.inc("reconciliation_failed_total")
            raise e
        
    def handle_recover_zombie(self, cmd: RecoverZombieTaskCommand):
        # 1. Epoch Fencing Activo
        current_epoch = self.system.get_current_epoch("global_reconciler")
        if cmd.reconciler_epoch != current_epoch:
            logger.warning("STALE_RECONCILER_COMMAND_DROPPED")
            self.metrics.inc("reconciliation_stale_epoch_total")
            return

        # 2. Mutación Atómica (Idempotencia + Rollback lógico)
        reconciled = self.task.mark_zombie_recovered(cmd.task_id, cmd.reconciliation_id)
        if not reconciled:
            self.metrics.inc("reconciliation_duplicate_total")
            return

        # 3. SRE Telemetry
        logger.info("zombie_recovered", extra={"extra_data": {
            "operation": "recover_zombie",
            "task_id": cmd.task_id[:8],
            "recon_id": cmd.reconciliation_id,
            "epoch": cmd.reconciler_epoch
        }})
        self.metrics.inc("reconciliation_success_total")