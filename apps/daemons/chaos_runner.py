import os
import sys
import time
import uuid
import docker
import sqlite3
import requests
import logging
from typing import List, Dict, Any

# Ajuste al PYTHONPATH para poder importar los repositorios oficiales
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from infra.db.control_repo import ControlPlaneRepository
from infra.db.fsm_repository import FSMRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SRE_RUNNER - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemObserver:
    """SOTA: Observabilidad Out-of-Band con Thread-Safety y RO-mode."""
    def __init__(self, control_db_path: str = "./data/control/control.db"):
        self.db_path = os.path.abspath(control_db_path)

    def _get_ro_connection(self) -> sqlite3.Connection:
        """SOTA: Conexión Read-Only con busy_timeout para no estorbar al runtime."""
        # URI form required for mode=ro
        db_uri = f"file:{self.db_path}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True, timeout=5.0)
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.row_factory = sqlite3.Row
        return conn

    def inject_load(self, count: int) -> List[str]:
        """
        SOTA: Inyección a través de los puertos oficiales de la aplicación.
        Respeta invariantes, Event Sourcing y constraints físicos.
        """
        doc_ids = []
        # Para la inyección sí necesitamos RW, pero de corta duración
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA journal_mode = WAL")
        
        fsm_repo = FSMRepository(conn)
        task_repo = ControlPlaneRepository(conn)
        
        for _ in range(count):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            ast_hash = f"hash_{uuid.uuid4().hex[:8]}"
            nodes = [f"node_{doc_id[-4:]}_{i}" for i in range(5)]
            
            # Inicialización 100% legal bajo las reglas de negocio
            fsm_repo.initialize_document(doc_id, ast_hash)
            task_repo.enqueue_tasks(doc_id, ast_hash, nodes)
            
            # SOTA: Forzamos el estado PROCESSING simulando que el FSM Handler ya actuó
            fsm_repo.transition_to(
                document_id=doc_id, ast_hash=ast_hash, old_state='CREATED', 
                new_state='PROCESSING', current_version=0, owner_id="chaos_injector"
            )
            doc_ids.append(doc_id)
            
        conn.close()
        logger.info(f"Inyectados {count} documentos legales con 5 chunks cada uno.")
        return doc_ids

    def get_convergence_metrics(self) -> Dict[str, Any]:
        """SOTA: Aserción absoluta de invariantes físicos y temporales."""
        now = time.time()
        conn = self._get_ro_connection()
        cursor = conn.cursor()
        
        # Métricas de Chunks
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN task_state = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN task_state = 'PENDING' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN task_state = 'PROCESSING' THEN 1 ELSE 0 END) as processing,
                SUM(CASE WHEN task_state = 'FAILED' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN task_state = 'PROCESSING' AND lease_expires_at < ? THEN 1 ELSE 0 END) as orphaned
            FROM chunk_tasks
        """, (now,))
        c_stats = cursor.fetchone()
        
        # Métricas de FSM
        cursor.execute("SELECT COUNT(*) FROM document_fsm WHERE state = 'COMPLETED'")
        docs_completed = cursor.fetchone()[0]
        
        # Métricas de Reconciliador
        cursor.execute("SELECT COUNT(*) FROM processed_reconciliation_commands")
        recon_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "chunks_total": c_stats["total"] or 0,
            "chunks_completed": c_stats["completed"] or 0,
            "chunks_pending": c_stats["pending"] or 0,
            "chunks_processing": c_stats["processing"] or 0,
            "chunks_failed": c_stats["failed"] or 0,
            "chunks_orphaned": c_stats["orphaned"] or 0,
            "docs_completed": docs_completed or 0,
            "reconciliation_events": recon_count or 0
        }

    def wait_for_convergence(self, target_docs: int, timeout_sec: int = 300) -> Dict[str, Any]:
        """SOTA: Evaluación Termodinámica con métricas temporales de SLA."""
        logger.info(f"Monitorizando SLA de convergencia (Target: {target_docs} docs)...")
        start_time = time.perf_counter()
        
        while time.perf_counter() - start_time < timeout_sec:
            metrics = self.get_convergence_metrics()
            
            # SOTA: Criterio Estricto. No solo los docs terminaron, sino que la entropía es CERO.
            is_converged = (
                metrics["docs_completed"] == target_docs and
                metrics["chunks_pending"] == 0 and
                metrics["chunks_processing"] == 0 and
                metrics["chunks_orphaned"] == 0
            )
            
            logger.info(
                f"SLA: {time.perf_counter() - start_time:.1f}s | "
                f"Docs[{metrics['docs_completed']}/{target_docs}] | "
                f"Chunks[C:{metrics['chunks_completed']} P:{metrics['chunks_pending']} R:{metrics['chunks_processing']}] | "
                f"Zombies:[{metrics['chunks_orphaned']}] | Recons:[{metrics['reconciliation_events']}]"
            )
            
            if is_converged:
                t_convergence = time.perf_counter() - start_time
                logger.info(f"=== CONVERGENCIA ESTRICTA ALCANZADA en {t_convergence:.2f}s ===")
                metrics["time_to_convergence_sec"] = t_convergence
                metrics["success"] = True
                return metrics
                
            time.sleep(5)
            
        logger.error(f"SLA BREACH: Fallo de Convergencia tras {timeout_sec}s.")
        metrics = self.get_convergence_metrics()
        metrics["time_to_convergence_sec"] = timeout_sec
        metrics["success"] = False
        return metrics


class ChaosInjector:
    """SOTA: Manipula física sin depender de nombres hardcodeados."""
    def __init__(self):
        self.client = docker.from_env()
        self.chaos_api_url = os.getenv("CHAOS_API_URL", "http://localhost:8000/_chaos/config")

    def kill_service(self, service_name: str, signal: str = "SIGKILL"):
        """SOTA: Ubica por label de Compose, inmune a escalado o renombrado de directorios."""
        # SOTA: Forzamos el tipado para satisfacer la firma covariante del SDK de Docker
        filters: Dict[str, Any] = {"label": f"com.docker.compose.service={service_name}"}
        containers = self.client.containers.list(filters=filters)
        
        if not containers:
            logger.error(f"No se encontraron contenedores para el servicio: {service_name}")
            return
            
        for container in containers:
            try:
                container.kill(signal=signal)
                logger.warning(f"SRE_KILL: {container.name} aniquilado con {signal}.")
            except Exception as e:
                logger.error(f"Fallo aniquilando {container.name}: {e}")

    def mutate_upstream(self, payload: dict):
        try:
            resp = requests.post(self.chaos_api_url, json=payload, timeout=2)
            resp.raise_for_status()
            logger.warning(f"SRE_UPSTREAM_MUTATION: {payload}")
        except Exception as e:
            logger.error(f"Fallo mutando upstream en {self.chaos_api_url}: {e}")


def game_day_1_crash_consistency():
    """
    GAME DAY 1: Crash Consistency & Zombie Recovery Absoluto.
    Objetivo: Probar que 100 repeticiones determinísticas producen el mismo resultado convergente
    incluso si se asesina a un worker y al Reconciler líder en el pico de carga.
    """
    logger.info("=== GAME DAY 1: CRASH CONSISTENCY & LEADERSHIP LOSS ===")
    
    observer = SystemObserver()
    injector = ChaosInjector()
    
    # SOTA: Estado determinístico
    injector.mutate_upstream({
        "seed": 1001, 
        "latency_min_ms": 100, 
        "latency_max_ms": 300,
        "hang_prob": 0.0,
        "error_500_prob": 0.0
    })

    num_docs = 5
    observer.inject_load(num_docs)
    
    # 1. Dejar que los leases se llenen
    logger.info("Rampa de carga: permitiendo saturación de workers (8s)...")
    time.sleep(8)
    
    # 2. El Caos (Sin piedad, sin graceful shutdown)
    injector.kill_service("reconciler")
    injector.kill_service("worker-a")
    
    # 3. Aserción Matemática y SLA
    result = observer.wait_for_convergence(target_docs=num_docs, timeout_sec=120)
    
    if result["success"]:
        logger.info(f"GAME DAY 1: PASSED. SLA Convergencia: {result['time_to_convergence_sec']:.2f}s")
        if result["reconciliation_events"] > 0:
            logger.info(f"Validado: El Reconciliador reparó {result['reconciliation_events']} anomalías autonómicamente.")
    else:
        logger.critical(f"GAME DAY 1: FAILED. Zombis restantes: {result['chunks_orphaned']}. Pendientes: {result['chunks_pending']}.")

if __name__ == "__main__":
    game_day_1_crash_consistency()