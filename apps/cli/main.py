"""Canonical PDF->PDF CLI entrypoint: admission and foreground OCR -> G3 -> G5.

R1's old async executor is deliberately NOT imported or callable here.
Its implementation is retained in apps.cli.legacy_translate_async only for
historical compatibility / controlled non-production usage.
"""
import os
import sys
import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.append(str(Path(__file__).resolve().parents[2]))
from infra.db.connection import get_connection

console = Console()

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
    """Compatibility symbol: never start legacy R1 from this product entrypoint."""
    raise RuntimeError("C4_T06_R1_LEGACY_ENTRYPOINT_DISABLED")


def handle_translate(args):
    # D-1: la CLI admite una solicitud. No ejecuta R1 ni llama al LLM.
    from apps.cli.pdf_inbox import PDFInboxSubmissionError, submit_pdf_to_inbox

    if args.job_id is not None:
        console.print(
            "[bold red]PDF_INBOX_JOB_ID_UNSUPPORTED:[/] "
            "El contrato canónico identifica el PDF por SHA-256 de sus bytes; "
            "--job-id no puede cambiar document_id."
        )
        raise SystemExit(2)

    repo_root = Path(__file__).resolve().parents[2]
    if getattr(args, "run", False) and os.getenv("APP_ROOT"):
        # Foreground uses the runtime workspace (/app in the offline lab),
        # while Python sources may live in a read-only checkout (/workspace).
        # Admission-only CLI preserves its original repository-root behavior.
        repo_root = Path(os.environ["APP_ROOT"]).expanduser().resolve()
    inbox = (Path(args.inbox_dir).expanduser() if args.inbox_dir
             else repo_root / "data" / "inbox")
    if getattr(args, "run", False):
        # Foreground is opt-in: default translate remains admission-only.
        from apps.cli.pdf_product import PDFProductError, preflight_product_run
        try:
            preflight_product_run(repo_root, inbox)
        except PDFProductError as exc:
            console.print(f"[bold red]PDF_RUN_PREFLIGHT_FAILED:[/] {exc}")
            raise SystemExit(2) from exc
    try:
        receipt = submit_pdf_to_inbox(Path(args.file_path), inbox)
    except (PDFInboxSubmissionError, OSError) as exc:
        console.print(f"[bold red]PDF_INBOX_ADMISSION_FAILED:[/] {exc}")
        raise SystemExit(2) from exc

    state = "YA PRESENTE EN INBOX" if receipt.already_present else "ENVIADO AL INBOX"
    console.print(Panel(
        f"[bold green]{state}[/]\n"
        f"[bold white]document_id (SHA-256):[/] {receipt.document_id}\n"
        f"[bold white]Archivo de ingesta:[/] {receipt.inbox_path}\n\n"
        "[yellow]Esto NO confirma OCR, inferencia, ensamblado ni PDF final. "
        "La progresión corresponde a OCR→G3→G5.[/]",
        title="Admisión PDF→PDF — contrato único",
    ))
    if getattr(args, "run", False):
        from apps.cli.pdf_product import PDFProductError, run_admitted_pdf
        try:
            result = run_admitted_pdf(receipt, repo_root)
        except PDFProductError as exc:
            console.print(f"[bold red]PDF_RUN_FAILED:[/] {exc}")
            raise SystemExit(1) from exc
        console.print(Panel(
            f"[bold green]PDF PUBLICADO (FSM COMPLETED)[/]\n"
            f"[bold white]Ruta:[/] {result.output_pdf}\n"
            "[yellow]Calidad científica: NO CERTIFICADA. "
            "Las ecuaciones visuales requieren investigación adicional.[/]",
            title="PDF→PDF — resultado operacional",
        ))

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
    
    t_parser = subparsers.add_parser(
        "translate", help="Admite un PDF en el recorrido OCR→G3→G5 (no espera salida)."
    )
    t_parser.add_argument("file_path", type=str, help="Ruta física al archivo PDF de entrada.")
    t_parser.add_argument(
        "--job-id", type=str, default=None,
        help="Obsoleto: se rechaza; document_id es SHA-256 de los bytes del PDF.",
    )
    t_parser.add_argument(
        "--inbox-dir", type=str, default=None,
        help="Directorio de inbox compartido con OCR Router (por defecto data/inbox).",
    )
    t_parser.add_argument(
        "--run", action="store_true", default=False,
        help="Ejecuta OCR→G3→G5 en primer plano; usa LLM si los chunks lo requieren.",
    )
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