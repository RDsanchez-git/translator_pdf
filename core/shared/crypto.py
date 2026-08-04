import hashlib


def compute_sha256(data: bytes) -> str:
    """Calcula de forma pura y determinista la firma SHA-256 de un bloque binario."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def compute_md5(data: bytes) -> str:
    """
    Calcula de forma pura y determinista la firma MD5 de un bloque binario.

    ADVERTENCIA DE USO: MD5 NO debe emplearse para seguridad criptográfica.
    Su uso en este proyecto está restringido exclusivamente a la generación
    de identificadores cortos de fingerprint (chunk_fingerprint), donde la
    propiedad requerida es determinismo, no resistencia a colisiones.
    """
    hasher = hashlib.md5()
    hasher.update(data)
    return hasher.hexdigest()