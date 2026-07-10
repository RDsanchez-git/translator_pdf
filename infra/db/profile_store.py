from core.document_profile.ports import ProfileStore
from core.document_profile.models import InferredDocumentProfile

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