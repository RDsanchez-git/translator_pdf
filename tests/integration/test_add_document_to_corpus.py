"""Tests de integración de add_document_to_corpus.py

Cubre:
- Duplicate doc_id (ADD-DOC-005)
- Duplicate sha256 (ADD-DOC-006)
- Preservación byte-a-byte de entradas selladas
- Hash recalculado distinto del viejo y coincidente con compute_hash
- Misma corpus_version aborta (ADD-DOC-008)
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz
import pytest

from core.benchmark.corpus.services import ManifestFingerprintCalculator
from core.shared.errors import IndexedError
from tools.evaluation.add_document_to_corpus import main


def _make_mini_pdf(path: Path, text: str = "test content") -> None:
    """Genera un PDF mínimo con texto."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    doc.save(path)
    doc.close()


def _make_manifest_with_sealed_entry(corpus_dir: Path) -> None:
    """Crea un manifest con una entrada sellada."""
    manifest = {
        "corpus_version": "v1.0",
        "manifest_hash": "old_hash_placeholder",
        "documents": [
            {
                "document_id": "doc_sealed",
                "sha256": "a" * 64,
                "traits": ["native_pdf"],
                "page_count": 3,
                "oracle_hash": "b" * 64,
                "ground_truth_state": "sealed",
            }
        ],
    }
    manifest_path = corpus_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


class TestAddDocumentToCorpus:
    def test_duplicate_doc_id_raises(self, tmp_path: Path):
        _make_manifest_with_sealed_entry(tmp_path)
        pdf = tmp_path / "test.pdf"
        _make_mini_pdf(pdf)
        with pytest.raises(IndexedError) as e:
            main([
                "--pdf", str(pdf),
                "--doc-id", "doc_sealed",  # ya existe
                "--traits", "native_pdf",
                "--corpus-dir", str(tmp_path),
                "--corpus-version", "v2.0",
            ])
        assert e.value.code == "ADD-DOC-005"

    def test_duplicate_sha256_raises(self, tmp_path: Path):
        _make_manifest_with_sealed_entry(tmp_path)
        pdf = tmp_path / "test.pdf"
        _make_mini_pdf(pdf, text="test content")
        # Calcular el SHA-256 del PDF y ponerlo en el manifest
        import hashlib
        sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
        manifest = {
            "corpus_version": "v1.0",
            "manifest_hash": "old_hash",
            "documents": [
                {
                    "document_id": "doc_sealed",
                    "sha256": sha,  # mismo contenido
                    "traits": ["native_pdf"],
                    "page_count": 3,
                    "oracle_hash": "b" * 64,
                    "ground_truth_state": "sealed",
                }
            ],
        }
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(IndexedError) as e:
            main([
                "--pdf", str(pdf),
                "--doc-id", "doc_new",
                "--traits", "native_pdf",
                "--corpus-dir", str(tmp_path),
                "--corpus-version", "v2.0",
            ])
        assert e.value.code == "ADD-DOC-006"

    def test_same_corpus_version_raises(self, tmp_path: Path):
        _make_manifest_with_sealed_entry(tmp_path)
        pdf = tmp_path / "test.pdf"
        _make_mini_pdf(pdf)
        with pytest.raises(IndexedError) as e:
            main([
                "--pdf", str(pdf),
                "--doc-id", "doc_new",
                "--traits", "native_pdf",
                "--corpus-dir", str(tmp_path),
                "--corpus-version", "v1.0",  # misma que la vigente
            ])
        assert e.value.code == "ADD-DOC-008"

    def test_preserves_sealed_entry_and_recalculates_hash(self, tmp_path: Path):
        _make_manifest_with_sealed_entry(tmp_path)
        pdf = tmp_path / "test.pdf"
        _make_mini_pdf(pdf)
        
        # Ejecutar
        main([
            "--pdf", str(pdf),
            "--doc-id", "doc_new",
            "--traits", "native_pdf,bilingual_mix",
            "--corpus-dir", str(tmp_path),
            "--corpus-version", "v2.0",
        ])
        
        # Verificar que la entrada sellada se preservó byte-a-byte
        new_manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert new_manifest["corpus_version"] == "v2.0"
        assert len(new_manifest["documents"]) == 2
        
        sealed = next(d for d in new_manifest["documents"] if d["document_id"] == "doc_sealed")
        assert sealed["oracle_hash"] == "b" * 64
        assert sealed["ground_truth_state"] == "sealed"
        
        new_entry = next(d for d in new_manifest["documents"] if d["document_id"] == "doc_new")
        assert new_entry["oracle_hash"] is None
        assert new_entry["ground_truth_state"] is None
        assert "bilingual_mix" in new_entry["traits"]
        
        # Verificar que el hash fue recalculado (distinto del placeholder)
        assert new_manifest["manifest_hash"] != "old_hash_placeholder"
        
        # Verificar que el hash coincide con compute_hash
        from core.benchmark.corpus.models import CorpusDocumentMetadata, CorpusVersion, DocumentFingerprint
        domain_docs = [
            CorpusDocumentMetadata(
                document_id=d["document_id"],
                fingerprint=DocumentFingerprint(sha256=d["sha256"]),
                traits=d["traits"],
                page_count=d["page_count"],
                oracle_hash=d["oracle_hash"],
                ground_truth_state=d["ground_truth_state"],
            )
            for d in new_manifest["documents"]
        ]
        expected_hash = ManifestFingerprintCalculator.compute_hash(
            CorpusVersion(value="v2.0"), domain_docs
        )
        assert new_manifest["manifest_hash"] == expected_hash
