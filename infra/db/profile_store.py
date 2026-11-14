from core.document_profile.ports import ProfileStore
from core.document_profile.models import InferredDocumentProfile, PageLayout
from core.domain.document import DocumentType
from hashlib import sha256
import json
from typing import cast
import sqlite3

class InMemoryProfileStore:
    """Implementación efímera del almacén de perfiles para despliegues single-node/PoC."""
    __slots__ = ("_store",)

    def __init__(self):
        self._store: dict[str, InferredDocumentProfile] = {}
        
    def save(self, document_id: str, profile: InferredDocumentProfile) -> None:
        self._store[document_id] = profile
        
    def get(self, document_id: str) -> InferredDocumentProfile | None:
        return self._store.get(document_id)

# Conformidad estructural implícita
_ : ProfileStore = InMemoryProfileStore()


class SQLiteProfileStore:
    """Durable ProfileStore on the already-shared documents.db connection.

    Identical OCR retries are idempotent. Differing profiles for the same
    content-addressed document fail closed instead of silently overwriting.
    Connections remain owned by the caller and are never shared across threads.
    """

    _DDL = """CREATE TABLE IF NOT EXISTS inferred_document_profiles (
        document_id TEXT PRIMARY KEY NOT NULL,
        layout TEXT NOT NULL,
        document_type TEXT,
        profile_sha256 TEXT NOT NULL CHECK(length(profile_sha256)=64)
    )"""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        with self.conn:
            self.conn.execute(self._DDL)

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

    def save(self, document_id: str, profile: InferredDocumentProfile) -> None:
        if not isinstance(cast(object, document_id), str) or not document_id:
            raise ValueError("G3_B4_4_INVALID_DOCUMENT_ID")
        layout, kind = self._fields(profile)
        digest = self._digest(document_id, layout, kind)
        with self.conn:
            self.conn.execute(
                "INSERT INTO inferred_document_profiles "
                "(document_id, layout, document_type, profile_sha256) "
                "VALUES (?,?,?,?) ON CONFLICT(document_id) DO NOTHING",
                (document_id, layout, kind, digest),
            )
            row = self.conn.execute(
                "SELECT layout, document_type, profile_sha256 FROM inferred_document_profiles "
                "WHERE document_id=?", (document_id,),
            ).fetchone()
            if row != (layout, kind, digest):
                raise ValueError("G3_B4_4_PROFILE_REPLAY_CONFLICT")

    def get(self, document_id: str) -> InferredDocumentProfile | None:
        row = self.conn.execute(
            "SELECT layout, document_type, profile_sha256 FROM inferred_document_profiles "
            "WHERE document_id=?", (document_id,),
        ).fetchone()
        if row is None:
            return None
        layout, kind, stored_hash = row
        if not isinstance(layout, str) or (kind is not None and not isinstance(kind, str)):
            raise ValueError("G3_B4_4_CORRUPT_PROFILE")
        if stored_hash != self._digest(document_id, layout, kind):
            raise ValueError("G3_B4_4_PROFILE_HASH_DRIFT")
        try:
            return InferredDocumentProfile(
                layout=PageLayout(layout),
                document_type=DocumentType(kind) if kind is not None else None,
            )
        except ValueError as exc:
            raise ValueError("G3_B4_4_CORRUPT_PROFILE_ENUM") from exc
