import os
import time
import uuid
import random
import logging
from typing import List, Tuple

from core.utils.telemetry import setup_distributed_logger
from core.execution.exceptions import OptimisticLockError

from infra.db.connection import get_connection
from infra.db.control_repo import ControlPlaneRepository
from infra.db.materialized_repo import MaterializedPlaneRepository
from core.ast.registry import ASTRegistry

from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner

# Reutilizamos el Heartbeat SOTA blindado de la Fase 7A
from apps.llm_workers.__main__ import TaskLeaseHeartbeat 

setup_distributed_logger()
logger = logging.getLogger("worker_assembler")

class AssemblerWorkerDaemon:
    """
    SOTA: Orquestador físico del Worker Assembler (CPU/IO Bound).
    Espera la tarea trigger, recolecta las proyecciones y compila Tectonic.
    """
    def __init__(self, control_repo, mat_repo, ast_registry, tex_builder, runner):
        self.control = control_repo
        self.materialized = mat_repo
        self.ast_registry = ast_registry
        self.tex_builder = tex_builder
        self.runner = runner
        
        self.node_id = f"assembler_{uuid.uuid4().hex[:8]}"
        self.worker_type = "ASSEMBLER"
        
        # Adaptive Sleep SOTA (El compilador hace menos polling, podemos relajar el sleep)
        self.base_sleep = 2.0
        self.max_sleep = 8.0

    def run(self):
        logger.info(f"Iniciando Assembler Worker Daemon [{self.node_id}] - CPU/IO Bound")
        consecutive_idle = 0
        task = None 
        
        while True:
            try:
                task = self.control.claim_next_pending_task(self.node_id, self.worker_type)
                
                if not task:
                    consecutive_idle += 1
                    sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)
                    time.sleep(sleep_time + random.uniform(0.0, 1.0))
                    continue
                
                consecutive_idle = 0
                self._process_assembly_task(task)
                task = None 
                
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                logger.exception(f"Error crítico en Assembler Worker loop: {e}")
                task = None
                time.sleep(self.max_sleep)

    def _process_assembly_task(self, task: dict):
        start_assembly = time.perf_counter()
        
        doc_id = task["document_id"]
        ast_hash = task["ast_hash"]
        task_id = task["task_id"]
        
        logger.info("Iniciando compilación del documento...", extra={"extra_data": {"doc": doc_id}})
        
        # 1. Recuperar la estructura original (El orden correcto de los nodos)
        cache_key = (doc_id, ast_hash)
        if cache_key not in self.ast_registry._cache:
            self.ast_registry._load_document(doc_id, ast_hash)
            
        doc_nodes = self.ast_registry._cache.get(cache_key, {})
        if not doc_nodes:
            logger.error("AST_NOT_FOUND", extra={"extra_data": {"doc": doc_id}})
            self.control.mark_task_failed(task_id, "AST Data missing", self.node_id, task["state_version"])
            return

        # El orden en el que leímos el JSON dicta el orden estructural del PDF
        ordered_node_ids = list(doc_nodes.keys())

        # 2. Recolección Segura usando tu get_assemblable_chunks existente (SOTA DTOs)
        projection_records = self.materialized.get_assemblable_chunks(
            document_id=doc_id,
            ast_hash=ast_hash,
            expected_node_ids=ordered_node_ids,
            required_projection_v=1
        )
        
        # Mapeo O(1) leyendo desde el DTO: .node_id y .normalized_response (según tu clase ProjectionRecord)
        text_map = {record.node_id: record.normalized_response for record in projection_records}

        valid_chunks: List[Tuple[str, str]] = []
        for n_id in ordered_node_ids:
            if n_id in text_map:
                valid_chunks.append((n_id, text_map[n_id]))
            else:
                # Bypass: Si no fue traducido (por ejemplo, ecuaciones passthrough o imágenes), inyecta original
                original_node = doc_nodes.get(n_id)
                if original_node and original_node.content:
                    valid_chunks.append((n_id, original_node.content))

        if not valid_chunks:
            self.control.mark_task_failed(task_id, "No valid chunks found", self.node_id, task["state_version"])
            return

        # 3. Compilación protegida por Heartbeat
        output_filename = f"translated_{doc_id}.pdf"
        CONTROL_DB_PATH = os.getenv("CONTROL_DB_PATH", "infra/db/control.db")
        
        with TaskLeaseHeartbeat(CONTROL_DB_PATH, task_id, self.node_id, ttl_sec=60) as heartbeat:
            # Ensamblaje en memoria
            tex_content = self.tex_builder.build(valid_chunks)
            
            # Ejecución de Tectonic (Subproceso Docker-less)
            final_pdf_path = self.runner.compile(tex_content, output_filename)
            
            if heartbeat.lease_lost.is_set():
                raise OptimisticLockError(f"Split-Brain evitado: lease de compilación {task_id} revocado.")

        logger.info(f"Compilación exitosa: {final_pdf_path}", extra={"extra_data": {"latency": time.perf_counter() - start_assembly}})
        
        # 4. Cerrar la Tarea
        self.control.mark_task_completed(task_id, self.node_id, task["state_version"])
        
        # NOTA: En un pipeline completo, aquí el Daemon podría disparar una señal al FSM 
        # (ej. fsm_repo.transition_to_completed(doc_id)) para marcar el documento como 100% terminado.

if __name__ == "__main__":
    CONTROL_DB_PATH = os.getenv("CONTROL_DB_PATH", "infra/db/control.db")
    MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")
    
    ctrl_conn = get_connection(CONTROL_DB_PATH)
    mat_conn = get_connection(MAT_DB_PATH)
    
    control_repo = ControlPlaneRepository(ctrl_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    ast_registry = ASTRegistry() 
    
    tex_builder = TexBuilder()
    runner = DockerRunner()
    
    daemon = AssemblerWorkerDaemon(
        control_repo=control_repo,
        mat_repo=mat_repo,
        ast_registry=ast_registry,
        tex_builder=tex_builder,
        runner=runner
    )
    daemon.run()