import time
import uuid
import random
import logging
import threading
from contextvars import copy_context
from core.utils.telemetry import ctx_worker_id
from core.execution.state import RecoverZombieTaskCommand, RematerializeTaskCommand

# (Importa los comandos definidos arriba)

logger = logging.getLogger(__name__)

class ReconcilerDaemon:
    def __init__(self, system_repo, task_repo, event_repo, command_handler, ttl_sec: int = 120):
        self.system = system_repo
        self.task_repo = task_repo   # Para leer estados de chunks
        self.event_repo = event_repo # Para verificar el WAL
        self.cmd_handler = command_handler
        
        self.node_id = f"reconciler_{uuid.uuid4().hex[:8]}"
        self.lease_name = "global_reconciler"
        self.ttl_sec = ttl_sec
        self.interval = ttl_sec * 0.3 
        
        self.INERTIA_WINDOW_SEC = 180.0 
        
        self.stop_event = threading.Event()
        self.is_leader = False
        self.current_epoch = 0

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
                        time.sleep(random.uniform(10.0, 20.0))
                        continue
                        
                    self.is_leader = True
                    self.current_epoch = epoch
                    logger.info("LEADERSHIP_ACQUIRED", extra={"extra_data": {"epoch": self.current_epoch}})

                now_safe = time.time() - self.INERTIA_WINDOW_SEC

                # BARRIDOS PAGINADOS
                try:
                    self._sweep_tasks(now_safe)
                except Exception as e:
                    # SOTA: logger.exception incluye el stacktrace y referenciar 'e' limpia a Ruff
                    logger.exception(f"Error crítico durante barrido paginado: {e}")
                
                # SOTA: Jitter en el ciclo principal
                time.sleep(random.uniform(25.0, 35.0))
                
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
                self.cmd_handler.handle(cmd)
            else:
                # VECTOR 1: Zombie puro. Devolver a PENDING.
                logger.info("Zombie detectado.", extra={"extra_data": {"task": task_id[:8]}})
                cmd = RecoverZombieTaskCommand(
                    reconciliation_id=idem_key,
                    reconciler_epoch=self.current_epoch,
                    task_id=task_id,
                    document_id=doc_id
                )
                self.cmd_handler.handle(cmd)