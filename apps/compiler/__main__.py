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
from infra.db.fsm_repository import FSMRepository
from core.ast.registry import ASTRegistry

from apps.compiler.tex_builder import TexBuilder
from apps.compiler.docker_runner import DockerRunner

from core.execution.handlers import DocumentCommandHandler
from core.execution.state import (
    DocumentState,
    StartAssemblyCommand,
    MarkCompilationReadyCommand,
    StartCompilationCommand,
    CompleteDocumentCommand,
    FailDocumentCommand
) 

setup_distributed_logger()
logger = logging.getLogger("worker_assembler")

class AssemblerWorkerDaemon:
    """
    SOTA: Orquestador físico del Worker Assembler (CPU/IO Bound).
    Espera la tarea trigger, recolecta las proyecciones y compila Tectonic.
    """
    def __init__(self, control_repo, fsm_repo, cmd_handler, mat_repo, ast_registry, tex_builder, runner):
        self.control = control_repo
        self.fsm = fsm_repo
        self.cmd_handler = cmd_handler
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
        logger.info(f"Iniciando Assembler Worker Daemon [{self.node_id}] - FSM Driven (CPU/IO Bound)")
        consecutive_idle = 0
        
        while True:
            try:
                # 1. Polling limpio a través de la API del repositorio encapsulado
                next_doc = self.fsm.find_next_ready_for_assembly()
                
                if not next_doc:
                    consecutive_idle += 1
                    sleep_time = min(self.base_sleep * (1.2 ** consecutive_idle), self.max_sleep)
                    time.sleep(sleep_time + random.uniform(0.0, 1.0))
                    continue
                
                consecutive_idle = 0
                doc_id, ast_hash = next_doc
                
                try:
                    self._process_assembly_task(doc_id, ast_hash)
                except OptimisticLockError:
                    # Mitigación nativa TOCTOU: Otro assembler ganó el lease de forma concurrente
                    logger.warning(f"TOCTOU Evitado: El documento {doc_id[:8]} ya fue tomado por otro nodo.")
                    continue
                
                time.sleep(random.uniform(0.5, 1.0))
                
            except Exception as e:
                logger.exception(f"Error crítico en Assembler Worker loop: {e}")
                time.sleep(self.max_sleep)

    def _fail_document_safely(self, doc_id: str, ast_hash: str, current_version: int | None, reason: str):
        """Intenta marcar el documento como fallido en FSM para evitar estados colgados."""
        if current_version is None:
            try:
                status = self.fsm.get_status(doc_id, ast_hash)
                if status:
                    current_version = status["version"]
            except Exception as read_err:
                logger.error(f"No se pudo recuperar la versión del FSM durante mitigación de desastre: {read_err}")
        
        if current_version is not None:
            try:
                cmd_fail = FailDocumentCommand(doc_id, ast_hash, self.node_id, current_version, reason=reason)
                self.cmd_handler.handle(cmd_fail)
                logger.info(f"Documento {doc_id[:8]} marcado como FAILED en FSM de forma segura.")
            except Exception as fsm_err:
                logger.critical(f"DOOMSDAY: No se pudo abortar el documento en la FSM: {fsm_err}")

    def _process_assembly_task(self, doc_id: str, ast_hash: str):
        """
        SOTA: Procesamiento directo FSM-driven sin diccionarios intermedios de colas.
        """
        start_assembly = time.perf_counter()
        
        logger.info("Iniciando compilación del documento...", extra={"extra_data": {"doc": doc_id}})
        
        current_version = None
        try:
            # 1. Obtener estado actual de la FSM
            status = self.fsm.get_status(doc_id, ast_hash)
            if not status:
                raise ValueError("No se encontró el estado del documento en la FSM.")

            current_version = status["version"]
            
            # Adquisición formal del lease del documento (Exclusión mutua distribuida)
            current_version = self.fsm.acquire_lease(doc_id, ast_hash, self.node_id, ttl_sec=300)
            
            # Transición Start Assembly si el documento está listo
            if status["state"] == DocumentState.READY_FOR_ASSEMBLY.value:
                cmd_start = StartAssemblyCommand(doc_id, ast_hash, self.node_id, current_version)
                current_version = self.cmd_handler.handle(cmd_start)
            
            # 2. Recuperar la estructura original del AST
            cache_key = (doc_id, ast_hash)
            if cache_key not in self.ast_registry._cache:
                self.ast_registry._load_document(doc_id, ast_hash)
                
            doc_nodes = self.ast_registry._cache.get(cache_key, {})
            if not doc_nodes:
                raise ValueError("Los datos estructurales del AST no se encuentran disponibles (Cache Miss).")

            ordered_node_ids = list(doc_nodes.keys())

            # 3. Recolección segura desde la proyección materializada
            projection_records = self.materialized.get_assemblable_chunks(
                document_id=doc_id,
                ast_hash=ast_hash,
                expected_node_ids=ordered_node_ids,
                required_projection_v=1
            )
            
            text_map = {record.node_id: record.normalized_response for record in projection_records}

            valid_chunks: List[Tuple[str, str]] = []
            for n_id in ordered_node_ids:
                if n_id in text_map:
                    valid_chunks.append((n_id, text_map[n_id]))
                else:
                    original_node = doc_nodes.get(n_id)
                    if original_node and original_node.content:
                        valid_chunks.append((n_id, original_node.content))

            if not valid_chunks:
                raise ValueError("No se encontraron fragmentos válidos para proceder con el ensamblado.")

            # 4. Compilación (Gobernada y protegida por el lease de la FSM documental)
            output_filename = f"translated_{doc_id}.pdf"
            tex_content = self.tex_builder.build(valid_chunks)
            
            cmd_ready = MarkCompilationReadyCommand(doc_id, ast_hash, self.node_id, current_version)
            current_version = self.cmd_handler.handle(cmd_ready)
            
            cmd_compile = StartCompilationCommand(doc_id, ast_hash, self.node_id, current_version)
            current_version = self.cmd_handler.handle(cmd_compile)
            
            final_pdf_path = self.runner.compile(tex_content, output_filename)

            logger.info(f"Compilación exitosa: {final_pdf_path}", extra={"extra_data": {"latency": time.perf_counter() - start_assembly}})
            
            # 5. Transicionar FSM a COMPLETED (CQRS Command puro)
            cmd_complete = CompleteDocumentCommand(doc_id, ast_hash, self.node_id, current_version)
            self.cmd_handler.handle(cmd_complete)
            
        except Exception as err:
            logger.error(f"Fallo crítico durante el ensamblado/compilación para {doc_id}: {err}")
            # Evitar estados colgados abortando de forma legal a nivel de Kernel FSM
            self._fail_document_safely(doc_id, ast_hash, current_version, str(err)[:250])
            raise err
            
        finally:
            # Liberación del lease garantizado a nivel de Kernel FSM
            try:
                self.fsm.release_lease(doc_id, ast_hash, self.node_id)
            except Exception as lease_err:
                logger.debug(f"Error silencioso liberando lease: {lease_err}")

if __name__ == "__main__":
    CONTROL_DB_PATH = os.getenv("CONTROL_DB_PATH", "infra/db/control.db")
    MAT_DB_PATH = os.getenv("MAT_DB_PATH", "infra/db/materialized.db")
    
    ctrl_conn = get_connection(CONTROL_DB_PATH)
    mat_conn = get_connection(MAT_DB_PATH)
    
    control_repo = ControlPlaneRepository(ctrl_conn)
    mat_repo = MaterializedPlaneRepository(mat_conn)
    fsm_repo = FSMRepository(ctrl_conn)
    cmd_handler = DocumentCommandHandler(fsm_repo, task_repo=control_repo)
    ast_registry = ASTRegistry() 
    
    tex_builder = TexBuilder()
    runner = DockerRunner()
    
    daemon = AssemblerWorkerDaemon(
        control_repo=control_repo,
        fsm_repo=fsm_repo,
        cmd_handler=cmd_handler,
        mat_repo=mat_repo,
        ast_registry=ast_registry,
        tex_builder=tex_builder,
        runner=runner
    )
    daemon.run()