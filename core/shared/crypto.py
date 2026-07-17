import hashlib

def compute_sha256(data: bytes) -> str:
    """Calcula de forma pura y determinista la firma SHA-256 de un bloque binario."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()