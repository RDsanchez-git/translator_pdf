"""tools/evaluation/check_candidate.py

Pre-admision de un PDF candidato al corpus canonico.
Verifica: paginas esperadas, Type 3 sin ToUnicode, text layer, markers del trait.

Semantica de salida uniforme (DF-18): main() -> int + run_entry.
Exit 0 = candidato valido. Exit 2 = defecto que impediria un GT util.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import fitz

from core.shared.errors import IndexedError
from core.shared.exit_codes import EXIT_OK
from tools.evaluation.entry_guard import run_entry


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Pre-admision de un PDF candidato al corpus canonico."
    )
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--expected-pages", type=int, default=None)
    parser.add_argument("--markers", type=str, default=None,
                        help="Markers separados por coma. Si se pasan y NINGUNO aparece, falla (CHECK-CAND-004).")
    return parser.parse_args(argv)


def check_candidate(pdf_path: Path, expected_pages: int | None, markers: list[str]) -> None:
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise IndexedError("CHECK-CAND-000", f"PDF corrupto o ilegible: {e}") from e
    try:
        page_count = doc.page_count
        if expected_pages is not None and page_count != expected_pages:
            raise IndexedError(
                "CHECK-CAND-001",
                f"paginas {page_count} != esperadas {expected_pages}",
            )

        type3_no_tounicode: list[tuple[int, str]] = []
        pages_text: list[tuple[int, str]] = []
        for idx in range(page_count):
            page = doc.load_page(idx)
            pno = idx + 1
            for font in page.get_fonts():
                xref = int(font[0])
                ftype = str(font[2])
                basefont = str(font[3])
                if ftype == "Type3":
                    has_tounicode = doc.xref_get_key(xref, "ToUnicode")[0] != "null"
                    if not has_tounicode:
                        type3_no_tounicode.append((pno, basefont))
            raw_text = page.get_text()
            page_text = raw_text if isinstance(raw_text, str) else ""
            pages_text.append((pno, page_text))

        if type3_no_tounicode:
            raise IndexedError(
                "CHECK-CAND-002",
                f"{len(type3_no_tounicode)} fuente(s) Type 3 sin ToUnicode: {type3_no_tounicode}",
            )

        total_chars = sum(len(t) for _, t in pages_text)
        if total_chars == 0:
            raise IndexedError("CHECK-CAND-003", "sin text layer extraible (scanned PDF)")

        if markers:
            any_found = False
            for pno, text in pages_text:
                found = [m for m in markers if m in text]
                if found:
                    any_found = True
                    print(f"[CHECK-CAND-OK] pagina {pno}: markers presentes: {found}")
            if not any_found:
                raise IndexedError(
                    "CHECK-CAND-004",
                    f"ningun marker encontrado {markers}: recorte o candidato incorrecto",
                )

        print(f"[CHECK-CAND-OK] {pdf_path.name}: {page_count} paginas, {total_chars} chars")
    finally:
        doc.close()


def main(argv=None) -> int:
    args = parse_args(argv)
    markers = [m.strip() for m in args.markers.split(",") if m.strip()] if args.markers else []
    check_candidate(args.pdf, args.expected_pages, markers)
    return EXIT_OK


if __name__ == "__main__":
    run_entry(main)
