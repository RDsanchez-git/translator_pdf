from __future__ import annotations

from typing import FrozenSet, List


class BaselineCompletenessVerifier:
    """Verificador de completitud biyectiva (NADR-13 §5.2 R4-R8)."""

    @staticmethod
    def verify(
        manifest_doc_ids: FrozenSet[str],
        artifact_doc_ids: FrozenSet[str],
    ) -> List[str]:
        errors: List[str] = []

        missing = sorted(manifest_doc_ids - artifact_doc_ids)
        for doc_id in missing:
            errors.append(f"Missing oracle for manifest document: {doc_id}")

        orphaned = sorted(artifact_doc_ids - manifest_doc_ids)
        for doc_id in orphaned:
            errors.append(f"Orphan oracle (not in manifest): {doc_id}")

        return errors

    @staticmethod
    def verify_pdf_ids(
        manifest_doc_ids: FrozenSet[str],
        pdf_doc_ids: FrozenSet[str],
    ) -> List[str]:
        """Verifica completitud biyectiva entre manifest y PDFs materializados.

        NADR-F17BIS-26 §5.3 R11-R12: La baseline debe ser completa y
        corresponder biyectivamente con los artefactos declarados.

        Función pura: compara conjuntos de IDs, sin I/O.
        El Imperative Shell (run_regression.py) lista los PDFs del filesystem
        y pasa los IDs.

        Args:
            manifest_doc_ids: IDs de documentos declarados en el manifest.
            pdf_doc_ids: IDs de PDFs presentes en pdf_dir.

        Returns:
            Lista ordenada de errores. Lista vacía si la biyección es completa.
        """
        errors: List[str] = []

        missing = sorted(manifest_doc_ids - pdf_doc_ids)
        for doc_id in missing:
            errors.append(f"Missing PDF for manifest document: {doc_id}")

        orphaned = sorted(pdf_doc_ids - manifest_doc_ids)
        for doc_id in orphaned:
            errors.append(f"Orphan PDF (not in manifest): {doc_id}")

        return errors