import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Iterable, Dict

from rich.console import Console
from rich.status import Status
from rich.panel import Panel
from rich.table import Table

sys.path.append(str(Path(__file__).resolve().parents[2]))

from apps.bootstrap.pipeline_factory import build_pipeline
from core.pipeline.job import TranslationJob, PipelineStep
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from core.ast.models import FastWordEstimator
from infra.db.connection import get_connection

from apps.llm_workers.adapters import GroqProvider
from apps.llm_workers.rate_limiter import RateLimitedProvider, QuotaManager
from apps.llm_workers.cache_provider import CachedLLMProvider
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.dispatcher import AsyncDispatcher
from core.context.context_resolver import ResolvedContext
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
from core.finops.measurement import InferenceMeasurementService
from core.prompting.dialects.openai_compatible import OpenAICompatibleDialect

console = Console()

class ChunkerProtocolAdapter:
    """SOTA Adapter Pattern: Cierra la brecha estructural para la Fase 13.00."""
    def __init__(self, estimator: FastWordEstimator):
        self._estimator = estimator
        self.last_report = None

    def chunk(self, nodes: list) -> list:
        units, report = build_semantic_chunks_as_units(nodes, self._estimator)
        self.last_report = report
        return units


class DummyContextResolver:
    """
    TEMPORAL: Satisface ContextResolverProtocol emitiendo nulos estructurados rígidos.
    """
    def resolve(self, context_id: str) -> ResolvedContext:
        return ResolvedContext(
            context_id=context_id,
            breadcrumbs=()
        )

    def resolve_many(self, context_ids: Iterable[str]) -> Dict[str, ResolvedContext]:
        return {}

# =====================================================================
# MANEJADORES OPERACIONALES (HANDLERS)
# =====================================================================

def handle_sweep(args):
    from runtime.recovery import AbandonedProcessWatchdog
    watchdog = AbandonedProcessWatchdog()
    console.print("[bold yellow]Iniciando barrido de aislamiento manual en FSM...[/]")
    watchdog.execute_sweep(threshold_sec=3600)
    console.print("[bold green]Barrido culminado con éxito.[/]")

async def handle_translate_async(args):
    """Orquesta el flujo principal asíncrono del pipeline utilizando Rich UX."""
    source_path = args.file_path
    if not os.path.exists(source_path):
        console.print(f"[bold red]Error:[/] Archivo ausente en ruta: {source_path}")
        sys.exit(1)

    job_id = args.job_id or f"job_{Path(source_path).stem}"

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY no configurada. Abortando inicialización de pipeline.")

    estimator = FastWordEstimator()
    measurement_service = InferenceMeasurementService(estimator=estimator)
    
    budget_calculator = PromptBudgetCalculator(
        primary_window_limit=8192,
        fallback_window_limit=1048576,
        min_output_reserve=256,
        max_output_reserve=4096
    )
    
    compression_policy = StandardCompressionPolicy()
    
    prompt_builder = PromptBuilder(
        model_name="llama3-70b-8192", 
        prompt_version="v1.0", 
        measurement_service=measurement_service,
        budget_calculator=budget_calculator,
        compression_policy=compression_policy
    )
    
    rpm_limit = int(os.getenv("GROQ_RPM_LIMIT", "30"))
    tpm_limit = int(os.getenv("GROQ_TPM_LIMIT", "6000"))
    
    dialect = OpenAICompatibleDialect()
    groq_provider = GroqProvider(api_key=api_key, dialect=dialect)
    quota_manager = QuotaManager(rpm_limit=rpm_limit, tpm_limit=tpm_limit)
    rate_provider = RateLimitedProvider(underlying=groq_provider, quota_manager=quota_manager)
    cached_provider = CachedLLMProvider(underlying=rate_provider, db_path="infra/db/materialized.db")
    
    await cached_provider.initialize()

    optimal_concurrency = max(1, min(int((rpm_limit / 60.0) * 1.5) * 2, 50))

    try:
        dispatcher = AsyncDispatcher(
            context_resolver=DummyContextResolver(),
            prompt_builder=prompt_builder,
            provider_stack=cached_provider,
            concurrency=optimal_concurrency
        )
        
        chunker_adapter = ChunkerProtocolAdapter(estimator=estimator)
        pipeline = build_pipeline(chunker=chunker_adapter, dispatcher=dispatcher)
        job = TranslationJob(job_id=job_id, source_path=source_path)

        console.print(Panel(
            f"[bold green]SOTA Pipeline Runtime Inicializado (Fase 16.10)[/]\n"
            f"[bold white]Job ID:[/] {job_id}\n"
            f"[bold white]Archivo:[/] {source_path}",
            title="[bold blue]TPS Control Plane[/]"
        ))

        with Status("[bold yellow]Validando identidad genética en FSM...", console=console) as status:
            snapshot = pipeline.state_store.load(job.job_id)
            if snapshot:
                status.update(f"[bold cyan]Snapshot de FSM detectado ({snapshot.state_value}). Aplicando Resume Macro...[/]")
            else:
                status.update("[bold green]Línea de tiempo limpia. Inicializando contexto documental...[/]")
            await asyncio.sleep(0.5)

        with Status("[bold magenta]Ejecutando Fase de Parseo Estructural...[/]", console=console) as macro_status:
            def update_ux_boundary():
                if job.current_step == PipelineStep.CHUNKING:
                    macro_status.update("[bold orange3]Segmentando AST y aplicando consistencia semántica...[/]")
                elif job.current_step == PipelineStep.ASSEMBLING:
                    macro_status.update("[bold blue]Límites cruzados. Reconstruyendo estructura documental...[/]")
                elif job.current_step == PipelineStep.AUDITING:
                    macro_status.update("[bold green]Procesando métricas FinOps de telemetría final...[/]")

            original_enter_step = job.enter_step
            def proxy_enter_step(step: PipelineStep):
                original_enter_step(step)
                update_ux_boundary()
            job.enter_step = proxy_enter_step

            result = await pipeline.execute(job)

        console.print("\n[bold green]✓ Ejecución de Pipeline Completada Exitosamente.[/]\n")
        
        table = Table(title="Reporte FinOps y Telemetría Operacional")
        table.add_column("Métrica de Control", justify="left", style="cyan")
        table.add_column("Valor Registrado", justify="right", style="magenta")
        table.add_row("Total Chunks Procesados", str(result.document.total_chunks))
        table.add_row("Tasa de Éxito (Dispatch)", f"{result.summary.dispatch_success_rate * 100:.2f}%")
        table.add_row("Fallos de Ejecución", str(result.summary.total_failed_chunks))
        table.add_row("Degradación Aplicada (Fallback)", "Sí" if result.assembly_report.degradation_applied else "No")
        table.add_row("Chunks Atajados por Caché", str(result.summary.translated_chunks_cache))
        table.add_row("Chunks Despachados a Red", str(result.summary.translated_chunks_network))
        table.add_row("Tokens de Entrada Consumidos", str(result.summary.total_input_tokens))
        table.add_row("Tokens de Salida Generados", str(result.summary.total_output_tokens))
        table.add_row("Costo de Operación (USD)", f"${result.summary.total_cost_usd:.6f}")
        table.add_row("Ahorro por Uso de Caché (USD)", f"${result.summary.cost_saved_by_cache_usd:.6f}")
        table.add_row("Eficiencia de Caché (Hit Ratio)", f"{result.summary.cache_hit_ratio * 100:.2f}%")
        
        if chunker_adapter.last_report:
            table.add_row("Grupos Semánticos Lógicos", str(chunker_adapter.last_report.total_groups))
            table.add_row("Eventos de Desbordamiento (Split)", str(chunker_adapter.last_report.overflow_events))
            
        console.print(table)

        if result.assembly_report.failure_reasons:
            fail_table = Table(title="Taxonomía Analítica de Fallos")
            fail_table.add_column("Razón de Fallo", style="red")
            fail_table.add_column("Frecuencia", justify="right", style="white")
            for reason, count in result.assembly_report.failure_reasons.items():
                fail_table.add_row(reason, str(count))
            console.print(fail_table)

    except Exception as err:
        console.print(f"\n[bold red]✖ COLAPSO DEL RUNTIME:[/] {str(err)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def handle_translate(args):
    asyncio.run(handle_translate_async(args))

def handle_resume(args):
    from runtime.resumer import OnDemandResumeManager
    resumer = OnDemandResumeManager()
    console.print(f"[bold yellow]Emitiendo orden de rescate para documento {args.document_id}...[/]")
    success = resumer.rescue_stalled_document(args.document_id, args.ast_hash)
    if success:
        console.print("[bold green]Cuarentena levantada. El documento puede ser relanzado via 'translate'.[/]")
    else:
        console.print("[bold red]No se pudo reanudar el documento. Verifique locks relacionales.[/]")

def handle_status(args):
    from infra.db.fsm_repository import FSMRepository
    with get_connection("infra/db/fsm.db") as conn:
        repo = FSMRepository(conn)
        status = repo.get_status(args.document_id, args.ast_hash)
        if not status:
            console.print(f"[bold red]Error:[/] No existen registros en la FSM para ID: {args.document_id}")
            return
        
        table = Table(title=f"Auditoría Forense FSM: {args.document_id[:8]}")
        table.add_column("Propiedad Inmutable", style="cyan")
        table.add_column("Valor Actual", style="magenta")
        table.add_row("Estado en Control Plane", status.current_state)
        table.add_row("Versión de Transición (CAS)", str(status.state_version))
        table.add_row("Estado de Suspensión Interno", str(status.suspended_state or "Ninguno"))
        console.print(table)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SOTA PDF Translator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Comandos operacionales:")
    
    t_parser = subparsers.add_parser("translate", help="Ejecuta el pipeline completo de traducción.")
    t_parser.add_argument("file_path", type=str, help="Ruta física al archivo PDF de entrada.")
    t_parser.add_argument("--job-id", type=str, default=None, help="Fuerza un ID único de ejecución.")
    t_parser.set_defaults(func=handle_translate)
    
    sw_parser = subparsers.add_parser("sweep", help="Ejecuta un barrido manual de procesos zombies en la FSM.")
    sw_parser.set_defaults(func=handle_sweep)
    
    r_parser = subparsers.add_parser("resume", help="Levanta la cuarentena de un documento congelado en STALLED.")
    r_parser.add_argument("document_id", type=str, help="ID del documento.")
    r_parser.add_argument("ast_hash", type=str, help="Firma SHA256 genética del árbol AST.")
    r_parser.set_defaults(func=handle_resume)
    
    st_parser = subparsers.add_parser("status", help="Inspecciona el estado físico del documento en la FSM.")
    st_parser.add_argument("document_id", type=str, help="ID del documento.")
    st_parser.add_argument("ast_hash", type=str, help="Firma SHA256 genética del árbol AST.")
    st_parser.set_defaults(func=handle_status)
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    args.func(args)

if __name__ == "__main__":
    main()