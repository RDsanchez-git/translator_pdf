import time
import uuid
import random
import logging
import threading
from contextvars import copy_context
from core.utils.telemetry import ctx_worker_id
from core.execution.state import RecoverZombieTaskCommand, RematerializeTaskCommand
from core.execution.state import MarkAssemblyReadyCommand
# (Importa los comandos definidos arriba)


logger = logging.getLogger(__name__)

class ReconcilerDaemon:
    def __init__(self, system_repo, task_repo, event_repo, recon_cmd_handler, doc_cmd_handler, ttl_sec: int = 120):
        self.system = system_repo
        self.task_repo = task_repo   
        self.event_repo = event_repo 
        self.recon_cmd_handler = recon_cmd_handler
        self.doc_cmd_handler = doc_cmd_handler
        
        self.node_id = f"reconciler_{uuid.uuid4().hex[:8]}"
        self.lease_name = "global_reconciler"
        self.ttl_sec = ttl_sec
        self.interval = ttl_sec * 0.3 
        
        self.INERTIA_WINDOW_SEC = 180.0 
        
        self.stop_event = threading.Event()
        self.is_leader = False
        self.current_epoch = 0

    def _sweep_fsm_stalls(self, now_safe: float):
        """SOTA: Reconciliación semántica del documento completo."""
        if not self.is_leader: 
            return

        # JOIN inter-tablas. El FSM y las tareas viven en control.db.
        # Condición: Procesamiento detenido en el tiempo, 100% de chunks en COMPLETED.
        cursor = self.task_repo.conn.execute("""
            SELECT d.document_id, d.ast_hash, d.state_version
            FROM document_fsm d
            JOIN chunk_tasks c ON d.document_id = c.document_id AND d.ast_hash = c.ast_hash
            WHERE d.current_state = 'PROCESSING'
              AND d.updated_at < ?
            GROUP BY d.document_id, d.ast_hash, d.state_version
            HAVING COUNT(c.task_id) > 0
               AND COUNT(c.task_id) = SUM(CASE WHEN c.task_state = 'COMPLETED' THEN 1 ELSE 0 END)
            LIMIT 50
        """, (now_safe,))
        
        stalled_docs = cursor.fetchall()
        
        for row in stalled_docs:
            if not self.is_leader: 
                return
            
            doc_id, ast_hash, state_version = row
            logger.info("FSM stall detectado. Despachando forward progress.", extra={"extra_data": {"doc_id": doc_id[:8]}})
            
            # SOTA: Forward Progress a través de la vía oficial (CQRS Command)
            # Nota: FSMValidator e Invariante de Optimistic Locking protegen contra Idempotencia aquí.
            cmd = MarkAssemblyReadyCommand(
                document_id=doc_id,
                ast_hash=ast_hash,
                owner_id=self.node_id, 
                expected_version=state_version
            )
            try:
                self.doc_cmd_handler.handle(cmd)
            except Exception as e:
                # Falla silenciosamente si otro orquestador revivió y ganó el lock
                logger.warning(f"FSM Stall bypass abortado (Posible race superado validamente): {e}")

    def _leadership_heartbeat(self):
        """SOTA: El hilo no muere al perder liderazgo, solo silencia la renovación."""
        while not self.stop_event.wait(self.interval):
            if self.is_leader:
                success = self.system.renew_leadership(self.lease_name, self.node_id, self.ttl_sec)
                if not success:
                    logger.critical("LEADERSHIP_LOST", extra={"extra_data": {"epoch": self.current_epoch}})
                    # SOTA: Degradación a follower. No usamos stop_event.set()
                    self.is_leader = False
                    self.current_epoch = 0

    def run(self):
        logger.info("Iniciando nodo Reconciliador", extra={"extra_data": {"node_id": self.node_id}})
        
        ctx = copy_context()
        ctx_worker_id.set(self.node_id)
        
        heartbeat_thread = threading.Thread(target=lambda: ctx.run(self._leadership_heartbeat), daemon=True)
        heartbeat_thread.start()

        try:
            while not self.stop_event.is_set():
                if not self.is_leader:
                    epoch = self.system.acquire_leadership(self.lease_name, self.node_id, self.ttl_sec)
                    if epoch == 0:
                        # SOTA: Jitter para evitar election storms
                        if self.stop_event.wait(timeout=random.uniform(25.0, 35.0)):
                            break
                        continue
                        
                    self.is_leader = True
                    self.current_epoch = epoch
                    logger.info("LEADERSHIP_ACQUIRED", extra={"extra_data": {"epoch": self.current_epoch}})

                now_safe = time.time() - self.INERTIA_WINDOW_SEC

                # BARRIDOS PAGINADOS
                try:
                    self._sweep_tasks(now_safe)
                    self._sweep_fsm_stalls(now_safe) # Llamada al Vector 3
                except Exception as e:
                    logger.exception(f"Error crítico durante barrido paginado: {e}")
                
                # SOTA: Jitter en el ciclo principal
                if self.stop_event.wait(timeout=random.uniform(25.0, 35.0)):
                    break
                
        finally:
            self.stop_event.set()
            heartbeat_thread.join(timeout=2.0)
            if self.is_leader:
                self.system.release_leadership(self.lease_name, self.node_id)

    def _sweep_tasks(self, now_safe: float):
        """SOTA: Unifica la búsqueda de tareas estancadas (Vector 1 y 2) en una sola pasada paginada."""
        if not self.is_leader:
            return

        # PAGINACIÓN SOTA: Limit 100 para no ahogar SQLite
        cursor = self.task_repo.conn.execute("""
            SELECT task_id, document_id, node_id, updated_at
            FROM chunk_tasks
            WHERE task_state = 'PROCESSING'
              AND lease_expires_at < ?
              AND updated_at < ?
            LIMIT 100
        """, (now_safe, now_safe))
        
        zombies = cursor.fetchall()
        
        for row in zombies:
            # Fencing Epoch: Si perdimos liderazgo a mitad del lote, abortamos instantáneamente
            if not self.is_leader:
                return 
            
            task_id, doc_id, node_id, updated_at = row
            
            # SOTA: Clave de Idempotencia Determinística
            # Si el Handler ya la procesó, la ignorará
            idem_key = f"recon:{task_id}:{updated_at}"
            
            # CRUCE VECTOR 2 (CQRS Anti-Entropy) vs VECTOR 1 (Zombie puro)
            # Consultamos si existe el evento de generación en el WAL
            latest_event = self.event_repo.get_latest_event(node_id)
            
            if latest_event and latest_event.lifecycle == "GENERATED":
                # VECTOR 2: El costo de API ya se pagó. Re-materializamos.
                logger.info("Desincronización CQRS detectada.", extra={"extra_data": {"task": task_id[:8]}})
                cmd = RematerializeTaskCommand(
                    reconciliation_id=idem_key,
                    reconciler_epoch=self.current_epoch,
                    task_id=task_id,
                    document_id=doc_id,
                    node_id=node_id,
                    content_hash=latest_event.content_hash
                )
                self.recon_cmd_handler.handle(cmd)
            else:
                # VECTOR 1: Zombie puro. Devolver a PENDING.
                logger.info("Zombie detectado.", extra={"extra_data": {"task": task_id[:8]}})
                cmd = RecoverZombieTaskCommand(
                    reconciliation_id=idem_key,
                    reconciler_epoch=self.current_epoch,
                    task_id=task_id,
                    document_id=doc_id
                )
                self.recon_cmd_handler.handle(cmd)

if __name__ == "__main__":
    from core.utils.telemetry import setup_distributed_logger
    from core.metrics.metrics import Metrics
    from infra.db.control_repo import ControlPlaneRepository
    from infra.db.system_repo import SystemPlaneRepository
    from infra.db.event_repo import EventPlaneRepository
    from infra.db.materialized_repo import MaterializedPlaneRepository
    from infra.db.fsm_repository import FSMRepository
    from core.execution.handlers import DocumentCommandHandler, ReconciliationCommandHandler
    from infra.db.connection import get_connection
    
    setup_distributed_logger()
    metrics = Metrics()

    CONTROL_DB_PATH = "infra/db/control.db"
    EVENT_DB_PATH = "infra/db/event.db"
    MAT_DB_PATH = "infra/db/materialized.db"

    ctrl_conn = get_connection(CONTROL_DB_PATH,timeout=30)
    evt_conn = get_connection(EVENT_DB_PATH,timeout=30)
    mat_conn = get_connection(MAT_DB_PATH,timeout=30)


    # 2. Inyección de Repositorios
    system_repo = SystemPlaneRepository(ctrl_conn) 
    task_repo = ControlPlaneRepository(ctrl_conn)
    event_repo = EventPlaneRepository(evt_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    fsm_repo = FSMRepository(ctrl_conn)

    # 3. Inyección de Handlers
    doc_cmd_handler = DocumentCommandHandler(fsm_repo)
    recon_cmd_handler = ReconciliationCommandHandler(
        system_repo=system_repo,
        task_repo=task_repo,
        event_repo=event_repo,
        mat_repo=mat_repo,
        metrics=metrics
    )

    # 4. Arranque del Demonio
    daemon = ReconcilerDaemon(
        system_repo=system_repo,
        task_repo=task_repo,
        event_repo=event_repo,
        recon_cmd_handler=recon_cmd_handler,
        doc_cmd_handler=doc_cmd_handler,
        ttl_sec=120
    )
    
    daemon.run()
