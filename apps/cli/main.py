import os
import sys
import asyncio
import argparse
from pathlib import Path

from rich.console import Console
from rich.status import Status
from rich.panel import Panel
from rich.table import Table

# Inyección de dependencias de la raíz de composición
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apps.bootstrap.pipeline_factory import build_pipeline
from core.pipeline.job import TranslationJob, PipelineStep
from apps.llm_workers.dispatcher import AsyncDispatcher
from apps.llm_workers.workers import GeminiWorker
from apps.llm_workers.prompt_builder import PromptBuilder
from apps.llm_workers.cache import SQLiteTranslationCache
from apps.llm_workers.gemini_client import GeminiClient
from core.ast.hashing import SemanticChunker, ChunkPolicy
from core.ast.models import FastWordEstimator

console = Console()

class ChunkerProtocolAdapter:
    """SOTA Adapter Pattern: Cierra la brecha estructural entre ChunkerProtocol y SemanticChunker."""
    def __init__(self, semantic_chunker: SemanticChunker):
        self._chunker = semantic_chunker

    def chunk(self, nodes: list) -> list:
        return self._chunker.chunk_document(nodes)

def parse_arguments() -> argparse.Namespace:
    """Configuración estricta de argumentos sin dependencias pesadas."""
    parser = argparse.ArgumentParser(
        description="SOTA PDF Translator CLI - Hexagonal Runtime Layer"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos operacionales.")
    
    translate_parser = subparsers.add_parser("translate", help="Ejecuta el pipeline completo.")
    translate_parser.add_argument("file_path", type=str, help="Ruta física del archivo PDF.")
    translate_parser.add_argument("--job-id", type=str, default=None, help="ID único opcional.")
    
    subparsers.add_parser("sweep", help="Barrido manual de procesos zombies.")
    
    return parser.parse_args()

async def main_async():
    args = parse_arguments()
    
    if args.command == "sweep":
        from runtime.recovery import AbandonedProcessWatchdog
        watchdog = AbandonedProcessWatchdog()
        console.print("[bold yellow]Iniciando barrido de aislamiento manual en FSM...[/]")
        watchdog.execute_sweep(threshold_sec=3600)
        console.print("[bold green]Barrido culminado con éxito.[/]")
        return

    if not args.command or args.command == "translate":
        source_path = args.file_path if hasattr(args, "file_path") else sys.argv[1]
    else:
        return

    if not os.path.exists(source_path):
        console.print(f"[bold red]Error:[/] Archivo ausente en ruta: {source_path}")
        sys.exit(1)

    job_id = args.job_id or f"job_{Path(source_path).stem}"

    # Instanciación de dependencias operativas para inyección de LLM Workers
    client = GeminiClient()
    prompt_builder = PromptBuilder()
    estimator = FastWordEstimator()
    
    # SOTA Fix: Cumplimiento de firma exacta de GeminiWorker
    worker = GeminiWorker(client=client, prompt_builder=prompt_builder, estimator=estimator)
    
    # SOTA Fix: Pasar str (path) directo a la caché evitando variables desvinculadas u objetos Connection
    cache = SQLiteTranslationCache(db_path="infra/db/materialized.db")
    
    dispatcher = AsyncDispatcher(
        worker=worker,
        cache=cache,
        model_name="gemini-1.5-pro",
        prompt_version="v1.0"
    )
    
    base_chunker = SemanticChunker(estimator=estimator, policy=ChunkPolicy())
    chunker_adapter = ChunkerProtocolAdapter(base_chunker)
    
    pipeline = build_pipeline(chunker=chunker_adapter, dispatcher=dispatcher)
    job = TranslationJob(job_id=job_id, source_path=source_path)

    console.print(Panel(
        f"[bold green]SOTA Pipeline Runtime Inicializado[/]\n"
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

    try:
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
        
        table = Table(title="Reporte FinOps de Cierre Operacional")
        table.add_column("Métrica de Control", justify="left", style="cyan")
        table.add_column("Valor Registrado", justify="right", style="magenta")
        
        table.add_row("Total Chunks Procesados", str(result.document.total_chunks))
        table.add_row("Chunks Atajados por Caché", str(result.summary.translated_chunks_cache))
        table.add_row("Chunks Despachados a Red", str(result.summary.translated_chunks_network))
        table.add_row("Tokens de Entrada Consumidos", str(result.summary.total_input_tokens))
        table.add_row("Tokens de Salida Generados", str(result.summary.total_output_tokens))
        table.add_row("Costo de Operación (USD)", f"${result.summary.total_cost_usd:.6f}")
        table.add_row("Ahorro por Uso de Caché (USD)", f"${result.summary.cost_saved_by_cache_usd:.6f}")
        table.add_row("Eficiencia de Caché (Hit Ratio)", f"{result.summary.cache_hit_ratio * 100:.2f}%")
        
        console.print(table)

    except Exception as err:
        console.print(f"\n[bold red]✖ COLAPSO DEL RUNTIME:[/] {str(err)}")
        sys.exit(1)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()