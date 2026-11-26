"""Durable profile store; physical uncertainty is part of the persisted evidence."""
from core.document_profile.ports import ProfileStore
from core.document_profile.models import (
    InferredDocumentProfile, PageLayout, ProfileDiagnostics, SamplingCoverage,
)
from core.domain.document import DocumentType
from hashlib import sha256
from math import isfinite
import json
from typing import cast
import sqlite3


class InMemoryProfileStore:
    __slots__ = ("_store",)

    def __init__(self):
        self._store: dict[str, InferredDocumentProfile] = {}

    def save(self, document_id: str, profile: InferredDocumentProfile) -> None:
        self._store[document_id] = profile

    def get(self, document_id: str) -> InferredDocumentProfile | None:
        return self._store.get(document_id)


_: ProfileStore = InMemoryProfileStore()


class SQLiteProfileStore:
    """Compatible additive migration; legacy rows have UNKNOWN physical evidence."""

    _DDL = """CREATE TABLE IF NOT EXISTS inferred_document_profiles (
        document_id TEXT PRIMARY KEY NOT NULL,
        layout TEXT NOT NULL,
        document_type TEXT,
        profile_sha256 TEXT NOT NULL CHECK(length(profile_sha256)=64),
        diagnostics_json TEXT,
        diagnostics_sha256 TEXT
    )"""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        with self.conn:
            self.conn.execute(self._DDL)
            columns = {
                row[1] for row in self.conn.execute(
                    "PRAGMA table_info(inferred_document_profiles)"
                ).fetchall()
            }
            for column in ("diagnostics_json", "diagnostics_sha256"):
                if column not in columns:
                    self.conn.execute(
                        f"ALTER TABLE inferred_document_profiles ADD COLUMN {column} TEXT"
                    )

    @staticmethod
    def _digest(document_id: str, layout: str, kind: str | None) -> str:
        serialized = json.dumps(
            {"document_id": document_id, "layout": layout, "document_type": kind},
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        )
        return sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _fields(profile: InferredDocumentProfile) -> tuple[str, str | None]:
        if not isinstance(cast(object, profile), InferredDocumentProfile):
            raise TypeError("G3_B4_4_INVALID_PROFILE")
        if not isinstance(cast(object, profile.layout), PageLayout) or (
            profile.document_type is not None
            and not isinstance(cast(object, profile.document_type), DocumentType)
        ):
            raise ValueError("G3_B4_4_INVALID_PROFILE_ENUM")
        return (profile.layout.value,
                profile.document_type.value if profile.document_type is not None else None)

    @staticmethod
    def _encode(diagnostics: ProfileDiagnostics | None) -> str | None:
        if diagnostics is None:
            return None
        if not isinstance(cast(object, diagnostics), ProfileDiagnostics):
            raise TypeError("PPPR_G2_INVALID_PROFILE_DIAGNOSTICS")
        if not isinstance(diagnostics.sampling_coverage, SamplingCoverage):
            raise ValueError("PPPR_G2_INVALID_SAMPLING_COVERAGE")
        if not all(isinstance(reason, str) for reason in (
            *diagnostics.sampling_reasons, *diagnostics.geometry_reasons
        )):
            raise ValueError("PPPR_G2_INVALID_DIAGNOSTIC_REASON")
        if not (isfinite(diagnostics.layout_confidence)
                and isfinite(diagnostics.type_confidence)):
            raise ValueError("PPPR_G2_INVALID_PROFILE_CONFIDENCE")
        return json.dumps(
            {
                "layout_confidence": diagnostics.layout_confidence,
                "type_confidence": diagnostics.type_confidence,
                "sampling_coverage": diagnostics.sampling_coverage.value,
                "sampling_reasons": list(diagnostics.sampling_reasons),
                "geometry_reasons": list(diagnostics.geometry_reasons),
            },
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        )

    @staticmethod
    def _diagnostic_hash(document_id: str, profile_hash: str, data: str) -> str:
        return sha256(
            json.dumps(
                {"document_id": document_id, "profile_hash": profile_hash, "evidence": data},
                sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _decode(data: str) -> ProfileDiagnostics:
        try:
            parsed = json.loads(data)
            reasons = parsed["sampling_reasons"]
            geometry = parsed["geometry_reasons"]
            if not isinstance(reasons, list) or not isinstance(geometry, list):
                raise ValueError("invalid reason arrays")
            if not all(isinstance(item, str) for item in (*reasons, *geometry)):
                raise ValueError("invalid reasons")
            lc = parsed["layout_confidence"]
            tc = parsed["type_confidence"]
            if not isinstance(lc, (int, float)) or isinstance(lc, bool):
                raise ValueError("invalid layout confidence")
            if not isinstance(tc, (int, float)) or isinstance(tc, bool):
                raise ValueError("invalid type confidence")
            if not (isfinite(lc) and isfinite(tc)):
                raise ValueError("nonfinite confidence")
            return ProfileDiagnostics(
                layout_confidence=float(lc), type_confidence=float(tc),
                sampling_coverage=SamplingCoverage(parsed["sampling_coverage"]),
                sampling_reasons=tuple(reasons), geometry_reasons=tuple(geometry),
            )
        except (TypeError, ValueError, KeyError) as exc:
            raise ValueError("PPPR_G2_CORRUPT_PROFILE_DIAGNOSTICS") from exc

    def save(self, document_id: str, profile: InferredDocumentProfile) -> None:
        if not isinstance(cast(object, document_id), str) or not document_id:
            raise ValueError("G3_B4_4_INVALID_DOCUMENT_ID")
        layout, kind = self._fields(profile)
        digest = self._digest(document_id, layout, kind)
        evidence = self._encode(profile.physical_diagnostics)
        evidence_hash = (
            self._diagnostic_hash(document_id, digest, evidence)
            if evidence is not None else None
        )
        expected = (layout, kind, digest, evidence, evidence_hash)
        with self.conn:
            self.conn.execute(
                "INSERT INTO inferred_document_profiles "
                "(document_id, layout, document_type, profile_sha256, "
                "diagnostics_json, diagnostics_sha256) "
                "VALUES (?,?,?,?,?,?) ON CONFLICT(document_id) DO NOTHING",
                (document_id, *expected),
            )
            query = (
                "SELECT layout, document_type, profile_sha256, "
                "diagnostics_json, diagnostics_sha256 "
                "FROM inferred_document_profiles WHERE document_id=?"
            )
            row = self.conn.execute(query, (document_id,)).fetchone()
            # Permite añadir evidencia a un registro legado sin alterar el perfil
            # anterior. Nunca reemplaza evidencia ya registrada.
            if (
                row is not None and row[:3] == expected[:3]
                and row[3:] == (None, None) and evidence is not None
            ):
                self.conn.execute(
                    "UPDATE inferred_document_profiles SET diagnostics_json=?, "
                    "diagnostics_sha256=? WHERE document_id=? "
                    "AND diagnostics_json IS NULL AND diagnostics_sha256 IS NULL",
                    (evidence, evidence_hash, document_id),
                )
                row = self.conn.execute(query, (document_id,)).fetchone()
            if row != expected:
                raise ValueError("G3_B4_4_PROFILE_REPLAY_CONFLICT")

    def get(self, document_id: str) -> InferredDocumentProfile | None:
        row = self.conn.execute(
            "SELECT layout, document_type, profile_sha256, "
            "diagnostics_json, diagnostics_sha256 "
            "FROM inferred_document_profiles WHERE document_id=?",
            (document_id,),
        ).fetchone()
        if row is None:
            return None
        layout, kind, digest, evidence, evidence_hash = row
        if not isinstance(layout, str) or (kind is not None and not isinstance(kind, str)):
            raise ValueError("G3_B4_4_CORRUPT_PROFILE")
        if digest != self._digest(document_id, layout, kind):
            raise ValueError("G3_B4_4_PROFILE_HASH_DRIFT")
        diagnostics: ProfileDiagnostics | None = None
        if evidence is None:
            if evidence_hash is not None:
                raise ValueError("PPPR_G2_CORRUPT_PROFILE_DIAGNOSTICS")
        else:
            if not isinstance(evidence, str) or evidence_hash != (
                self._diagnostic_hash(document_id, digest, evidence)
            ):
                raise ValueError("PPPR_G2_PROFILE_DIAGNOSTICS_HASH_DRIFT")
            diagnostics = self._decode(evidence)
        try:
            return InferredDocumentProfile(
                layout=PageLayout(layout),
                document_type=DocumentType(kind) if kind is not None else None,
                physical_diagnostics=diagnostics,
            )
        except ValueError as exc:
            raise ValueError("G3_B4_4_CORRUPT_PROFILE_ENUM") from exc
