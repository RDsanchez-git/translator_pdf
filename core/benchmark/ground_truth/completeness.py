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