import os
import sys
import time
import asyncio
import logging
from pathlib import Path

# SOTA FIX: Asegurar que el script reconozca la raíz del proyecto al ejecutarse aislado
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from core.benchmark.models import ProviderDescriptor, BenchmarkMode
from core.benchmark.persistence import BenchmarkPersistenceGateway
from core.benchmark.orchestrator import SequentialBenchmarkOrchestrator
from core.benchmark.runners.groq_runner import GroqBenchmarkRunner

from core.telemetry.gateway import SQLiteTelemetryGateway
from core.telemetry.analyzer import TelemetryAnalyzer
from core.telemetry.gates import HealthGateEvaluator
from core.telemetry.models import ProductionTelemetryEvent, TelemetryEventType, ProviderSelectionReason


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BenchmarkDriver")

async def main() -> None:
    logger.info("Iniciando Laboratorio de Evaluación SOTA (Fase 16.10)...")
    
    # 1. Inicializar Telemetría de Producción (Fase 15.5)
    gateway = SQLiteTelemetryGateway()
    await gateway.start()
    
    try:
        # 2. Configurar Descriptores (Colisión Intrafamilia Groq LPU)
        baseline_desc = ProviderDescriptor(provider="groq", model="llama-3.3-70b-versatile", version="v1")
        challenger_desc = ProviderDescriptor(provider="groq", model="llama-3.1-8b-instant", version="v1")
        
        # SOTA FIX: Concurrencia estricta a 1 para no desbordar el techo de 6K TPM del Free Tier
        baseline_runner = GroqBenchmarkRunner(descriptor=baseline_desc, mode=BenchmarkMode.EQUALIZED, concurrency=1)
        challenger_runner = GroqBenchmarkRunner(descriptor=challenger_desc, mode=BenchmarkMode.EQUALIZED, concurrency=1)
        
        # 3. Configurar Orquestador y Persistencia
        persistence = BenchmarkPersistenceGateway()
        orchestrator = SequentialBenchmarkOrchestrator(
            baseline_runner=baseline_runner,
            challenger_runner=challenger_runner,
            persistence=persistence,
            cooldown_seconds=5.0  # La red LPU purga los rate limits más rápido
        )
        
        # 4. Inyectar el Dataset Real (Restauración de código faltante)
        logger.info("Ingestando documento físico para estrés volumétrico y semántico...")
        
        from core.benchmark.models import BenchmarkDataset, BenchmarkDocument, DocumentComplexity, PreparedBenchmarkDataset, QualityPolicy
        from core.ast.models import TranslationUnit, TranslationTaskType
        from apps.bootstrap.pipeline_factory import build_extraction_pipeline
        import hashlib

        pdf_target_path = Path.cwd() / "[Amoretal_2023]_3hojas.pdf"
        
        if not pdf_target_path.exists():
            raise FileNotFoundError(f"Documento físico no encontrado: {pdf_target_path}")

        logger.info(f"Ejecutando parser sobre {pdf_target_path.name}...")
        # NADR-10 §5.3 R9, R10: El benchmark es un consumidor del Composition Root.
        # No es otro pipeline. No reconstruye la extracción.
        production_parser = build_extraction_pipeline()
        ast_nodes = production_parser.parse(str(pdf_target_path))
        
        if not ast_nodes:
            raise RuntimeError("El parser devolvió un AST vacío.")

        prepared_units = []
        unit_complexity_map = {}
        total_estimated_tokens = 0
        
        for idx, node in enumerate(ast_nodes):
            # SOTA FIX: Reemplazar node.content por node.text_content
            safe_content = node.text_content or ""
            
            if not safe_content.strip():
                continue
                
            node_sha = hashlib.sha256(safe_content.encode('utf-8')).hexdigest()
            est_tokens = max(1, len(safe_content) // 4) 
            total_estimated_tokens += est_tokens
            
            task_type = TranslationTaskType.TRANSLATE
            complexity = DocumentComplexity.STANDARD_PROSE
            
            node_type_val = node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type)
            if "EQUATION" in node_type_val or "TABLE" in node_type_val:
                task_type = TranslationTaskType.PARTIAL
                complexity = DocumentComplexity.MIXED_HYBRID
            elif "IMAGE" in node_type_val:
                task_type = TranslationTaskType.PRESERVE
            
            unit = TranslationUnit(
                chunk_index=idx,
                chunk_id=node.node_id,
                chunk_fingerprint=node_sha,
                chunk_type=task_type,
                source_sequence_range=(0, len(safe_content)),
                node_count=1,
                context_id=f"ctx_{node.node_id}",
                context_depth=0,
                target_payload=safe_content,
                estimated_tokens=est_tokens,
                payload_sha256=node_sha
            )
            prepared_units.append(unit)
            unit_complexity_map[unit.chunk_id] = complexity

        doc_sha = hashlib.sha256(pdf_target_path.read_bytes()).hexdigest()
        doc = BenchmarkDocument(
            id=pdf_target_path.stem,
            file_path=str(pdf_target_path),
            file_sha256=doc_sha,
            complexity=DocumentComplexity.MIXED_HYBRID,
            expected_pages=3,
            input_tokens_actual=total_estimated_tokens,
            expected_chunks=len(prepared_units)
        )
        
        manifest = BenchmarkDataset(
            dataset_id=f"ds_{pdf_target_path.stem}", 
            dataset_sha256=doc_sha, 
            documents=[doc]
        )

        dataset = PreparedBenchmarkDataset(
            manifest=manifest,
            prepared_units=prepared_units,
            unit_complexity_map=unit_complexity_map
        )
            
        policy = QualityPolicy(structural_weight=0.7, semantic_weight=0.3)
        logger.info(f"Dataset materializado: {len(prepared_units)} chunks generados.")

        # 5. Fuego Real: Ejecutar Experimento
        logger.info("Iniciando colisión intrafamilia (Groq 70B vs Groq 8B)...")
        start_time = time.monotonic()
        report = await orchestrator.run_experiment(
            dataset=dataset,
            baseline_desc=baseline_desc,      
            challenger_desc=challenger_desc,  
            quality_policy=policy
        )
        makespan = time.monotonic() - start_time
        
        exec_id = f"run_{int(report.metadata.run_timestamp)}"
        
        # Puente de Ingesta Sincronizado
        for record in report.raw_baseline_records:
            evt_type = TelemetryEventType.CONTEXT_OVERFLOW if record.did_overflow else (
                TelemetryEventType.TRANSLATION_SUCCESS if record.success else TelemetryEventType.TRANSLATION_FAILURE)
            
            gateway.emit(ProductionTelemetryEvent(
                execution_id=exec_id,
                chunk_id=record.chunk_id,
                provider=report.baseline_metrics.descriptor.provider,
                event_type=evt_type,
                selection_reason=ProviderSelectionReason.PRIMARY_ROUTE,
                latency_ms=record.latency_ms,
                quota_wait_ms=record.quota_wait_seconds * 1000.0,
                input_tokens=record.input_tokens,
                output_tokens=record.output_tokens
            ))
            
        for record in report.raw_challenger_records:
            evt_type = TelemetryEventType.CONTEXT_OVERFLOW if record.did_overflow else (
                TelemetryEventType.TRANSLATION_SUCCESS if record.success else TelemetryEventType.TRANSLATION_FAILURE)
            
            # SOTA FIX: Saneamiento del bug de asignación de chunk_id
            gateway.emit(ProductionTelemetryEvent(
                execution_id=exec_id,
                chunk_id=record.chunk_id,
                provider=report.challenger_metrics.descriptor.provider,
                event_type=evt_type,
                selection_reason=ProviderSelectionReason.PRIMARY_ROUTE,
                latency_ms=record.latency_ms,
                quota_wait_ms=record.quota_wait_seconds * 1000.0,
                input_tokens=record.input_tokens,
                output_tokens=record.output_tokens
            ))
            
        logger.info("Drenando buffer asíncrono hacia disco (SQLite WAL)...")
        await asyncio.sleep(2.5) 
        await gateway.stop()
        
        # 6. Evaluar Gobernanza Operacional y Health Gates
        logger.info("Analizando salud de la migración y violaciones SLO...")
        analyzer = TelemetryAnalyzer()
        health_report = analyzer.generate_report(execution_id=exec_id, wall_clock_seconds=makespan)
        
        logger.info("=== RESUMEN SOTA DE OPERACIÓN ===")
        logger.info(f"Baseline (70B) TPS: {report.baseline_metrics.total_tps} | Challenger (8B) TPS: {report.challenger_metrics.total_tps}")
        logger.info(f"P95 Quota Wait: {health_report.p95_quota_wait_ms}ms")
        logger.info(f"Degradación de Throughput (Health): {health_report.throughput_degradation_ratio * 100:.2f}%")
        logger.info(f"Violaciones SLO Críticas: {len(health_report.slo_violations)}")
        
        try:
            HealthGateEvaluator.enforce(health_report)
            logger.info("Laboratorio finalizado exitosamente. Health Gate: PASSED.")
        except Exception as gate_error:
            logger.warning(f"Health Gate disparado (SLO Estricto): {gate_error}")
            logger.info("Laboratorio finalizado con DEGRADACIÓN ACEPTADA. Métrica retenida.")
            
    except Exception as e:
        logger.error(f"Ejecución abortada críticamente: {e}")
    finally:
        logger.info("Pipeline de telemetría desconectado.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GROQ_API_KEY"):
        logger.error("Abortado: Falta variable de entorno GROQ_API_KEY.")
        sys.exit(1)
        
    asyncio.run(main())