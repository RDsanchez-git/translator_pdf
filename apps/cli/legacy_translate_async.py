"""Legacy R1 translation executor retained for historical compatibility only.

NOT a supported PDF->PDF product entrypoint. The canonical CLI admission
and opt-in foreground route live in apps.cli.main and apps.cli.pdf_product.
Do not dispatch this module from Compose or production launchers.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

from rich.console import Console
from rich.status import Status
from rich.panel import Panel
from rich.table import Table

sys.path.append(str(Path(__file__).resolve().parents[2]))

from apps.bootstrap.pipeline_factory import build_pipeline
from core.pipeline.job import TranslationJob, PipelineStep
from core.chunking.semantic_chunking import build_semantic_chunks_as_units
from core.validation.estimators import ExactBPEEstimator
from infra.db.connection import get_connection

from apps.llm_workers.prompt_builder import PromptBuilder
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy
from core.finops.measurement import InferenceMeasurementService
from core.validation.protocols import TokenEstimatorProtocol
from apps.bootstrap.provider_stack_factory import build_provider_stack
from infra.resilience.sqlite_rate_limit_store import SQLiteRateLimitStore


class ChunkerProtocolAdapter:
    """SOTA Adapter Pattern: Cierra la brecha estructural para la Fase 13.00."""
    def __init__(self, estimator: TokenEstimatorProtocol):
        self._estimator = estimator
        self.last_report = None

    def chunk(self, nodes: list) -> list:
        units, report = build_semantic_chunks_as_units(nodes, self._estimator)
        self.last_report = report
        return units

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

    estimator = ExactBPEEstimator()
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
    
    # DF-27: Persistencia de cuotas con SQLite WAL
    rl_conn = get_connection("infra/db/rate_limits.db", timeout=30)
    rl_conn.execute("PRAGMA busy_timeout=30000")
    rl_store = SQLiteRateLimitStore(rl_conn)
    
    provider_stack = await build_provider_stack(
        api_key=api_key,
        rpm_limit=rpm_limit,
        tpm_limit=tpm_limit,
        rate_limit_store=rl_store,
    )

    optimal_concurrency = max(1, min(int((rpm_limit / 60.0) * 1.5) * 2, 50))

    try:
        chunker_adapter = ChunkerProtocolAdapter(estimator=estimator)
        pipeline = build_pipeline(
            chunker=chunker_adapter,
            prompt_builder=prompt_builder,
            provider_stack=provider_stack,
            concurrency=optimal_concurrency,
        )
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
                elif job.current_step == PipelineStep.FINISHED:
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
        table.add_row("Total Chunks Procesados", str(result.summary.total_chunks))
        table.add_row("Tasa de Éxito (Dispatch)", f"{result.summary.dispatch_success_rate * 100:.2f}%")
        table.add_row("Fallos de Ejecución", str(result.summary.total_failed_chunks))
        table.add_row("Degradación Aplicada (Fallback)", "N/A (ensamblado asíncrono)")
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

    except Exception as err:
        console.print(f"\n[bold red]✖ COLAPSO DEL RUNTIME:[/] {str(err)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # DF-27: Cerrar conexión de rate limits
        try:
            rl_conn.close()
        except Exception:
            pass

