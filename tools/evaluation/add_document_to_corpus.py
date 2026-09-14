"""tools/evaluation/add_document_to_corpus.py — Imperative Shell delgado.

La lógica de negocio vive en AddDocumentToCorpusUseCase (dominio).
Este Shell solo: parsea args, valida traits, copia el PDF, invoca el use case.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from core.benchmark.corpus.enums import ExtractionChallengeTrait
from core.benchmark.corpus.use_cases import AddDocumentToCorpusUseCase
from core.shared.errors import IndexedError
from core.shared.exit_codes import EXIT_OK
from infra.adapters.document_metadata import PyMuPdfDocumentMetadataExtractor
from infra.fs.corpus_repository import LocalFileSystemCorpusLoader
from tools.evaluation.entry_guard import run_entry


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Añadir un documento nuevo al corpus canónico sellado, "
                    "preservando las entradas selladas existentes."
    )
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--doc-id", type=str, required=True)
    parser.add_argument("--traits", type=str, required=True)
    parser.add_argument("--corpus-dir", type=Path, required=True)
    parser.add_argument("--corpus-version", type=str, required=True)
    return parser.parse_args(argv)


def _validate_traits(traits_str: str) -> list[str]:
    valid_traits = {t.value for t in ExtractionChallengeTrait}
    provided = [t.strip() for t in traits_str.split(",") if t.strip()]
    if not provided:
        raise IndexedError("ADD-DOC-001", "No se proporcionaron traits.")
    invalid = [t for t in provided if t not in valid_traits]
    if invalid:
        raise IndexedError(
            "ADD-DOC-002",
            f"Traits inválidos: {invalid}. Válidos: {sorted(valid_traits)}"
        )
    return provided


def main(argv=None) -> int:
    args = parse_args(argv)

    traits = _validate_traits(args.traits)

    if not args.pdf.exists():
        raise IndexedError("ADD-DOC-003", f"PDF no encontrado: {args.pdf}")

    # Copiar PDF a corpus_dir/pdf/ y calcular hash sobre el destino (identidad sobre destino)
    pdf_dir = args.corpus_dir / "pdf"
    pdf_dir.mkdir(exist_ok=True)
    dest_pdf = pdf_dir / f"{args.doc_id}.pdf"
    if dest_pdf.exists():
        raise IndexedError("ADD-DOC-009", f"PDF destino ya existe: {dest_pdf}")
    shutil.copy2(args.pdf, dest_pdf)

    # Inyección de puertos (reutilización estricta, ADR §5)
    loader = LocalFileSystemCorpusLoader(args.corpus_dir)
    extractor = PyMuPdfDocumentMetadataExtractor()
    use_case = AddDocumentToCorpusUseCase(reader=loader, writer=loader, extractor=extractor)

    new_hash, sha256, page_count = use_case.execute(
        pdf_path=dest_pdf,
        doc_id=args.doc_id,
        traits=traits,
        new_version=args.corpus_version,
    )

    print(f"[ADD-DOC-OK] Añadido '{args.doc_id}' al corpus.")
    print(f"  Corpus version: -> {args.corpus_version}")
    print(f"  SHA-256: {sha256[:16]}..., páginas: {page_count}, traits: {traits}")
    print(f"  Manifest hash: {new_hash[:16]}...")
    print("  WARNING: biyección rota hasta curar GT y sellar (pasos 6-8 del flujo).")
    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)