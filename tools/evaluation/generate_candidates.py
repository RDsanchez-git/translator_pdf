import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Dict, Type

from core.extraction.ocr_providers.pymupdf_provider import PyMuPDFProvider
from core.extraction.provider import ExtractionProvider
from core.shared.crypto import compute_sha256
from core.utils.fs import ensure_parent_dir
from infra.serialization.ast_json import serialize_ast_json
from tools.evaluation.services.candidate_generator import CandidateGenerationService
from core.extraction.ocr_providers.docling_provider import DoclingProvider

_AVAILABLE_PROVIDERS: Dict[str, Type[ExtractionProvider]] = {
    "pymupdf": PyMuPDFProvider,
    "docling": DoclingProvider,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generador Canónico de Candidatos AST para Benchmarking Topológico (Fase 17.3)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        choices=list(_AVAILABLE_PROVIDERS.keys()),
        help="Identificador del proveedor de extracción registrado.",
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=Path("tests/corpus/calibration_v1"),
        help="Directorio del corpus fuente con documentos PDF.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("candidates"),
        help="Directorio raíz para depositar los candidatos JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    provider_key = args.provider.lower()
    provider_cls = _AVAILABLE_PROVIDERS[provider_key]
    provider_instance = provider_cls()

    service = CandidateGenerationService()
    target_dir = args.output_dir / provider_key
    pdf_files = sorted(list(args.corpus_dir.glob("*.pdf")))

    if not pdf_files:
        print(f"[ERROR] No se encontraron archivos PDF en '{args.corpus_dir}'.", file=sys.stderr)
        sys.exit(1)

    print(f"=== Generando candidatos AST para Proveedor: '{provider_key}' ===")

    processed = 0
    accepted = 0
    rejected = 0

    for pdf_path in pdf_files:
        processed += 1
        with open(pdf_path, "rb") as f:
            pdf_sha256 = compute_sha256(f.read())

        result = service.generate_candidate(
            provider=provider_instance,
            provider_name=provider_key,
            pdf_path=pdf_path,
            pdf_sha256=pdf_sha256,
        )

        if not result.validation_report.is_valid:
            rejected += 1
            formatted_errors = "\n - ".join(result.validation_report.errors)
            print(
                f" [REJECTED] '{result.doc_id}' violó invariantes de DocumentLayout:\n - {formatted_errors}",
                file=sys.stderr,
            )
            continue

        accepted += 1
        output_json_path = target_dir / f"{result.doc_id}.json"
        output_meta_path = target_dir / f"{result.doc_id}.meta.json"

        # Serialización de infraestructura en la capa externa (CLI)
        ast_payload = serialize_ast_json(list(result.ast_nodes))
        nodes_data = ast_payload if isinstance(ast_payload, list) else json.loads(ast_payload)

        ensure_parent_dir(output_json_path)

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(nodes_data, f, indent=2, ensure_ascii=False)

        if result.metadata:
            meta_dict = dataclasses.asdict(result.metadata)
            meta_dict["execution_timestamp"] = result.metadata.execution_timestamp.isoformat()
            clean_meta = {k: v for k, v in meta_dict.items() if v is not None}
            
            with open(output_meta_path, "w", encoding="utf-8") as f:
                json.dump(clean_meta, f, indent=2)

        print(f" [OK] '{result.doc_id}' -> '{output_json_path}' ({len(result.ast_nodes)} nodos)")

    print("-" * 50)
    print(f"Resumen: Procesados={processed} | Aceptados={accepted} | Rechazados={rejected}")
    print("-" * 50)

    if rejected > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()