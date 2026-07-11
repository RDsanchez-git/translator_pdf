import hashlib

class PromptHasher:
    """
    SOTA: Generador de identidad criptográfica.
    Desacoplado de la serialización estructural.
    """
    
    @staticmethod
    def compute_hash(canonical_bytes: bytes) -> str:
        # Aislado para futura evolución (ej. BLAKE3, SHA-512) sin tocar el Canonicalizer
        return hashlib.sha256(canonical_bytes).hexdigest()