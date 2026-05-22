from pathlib import Path


def ensure_parent_dir(path: str) -> None:
    """
    Garantiza que exista el directorio padre de un archivo.
    Ejemplo:
        /app/data/control/control.db
    crea:
        /app/data/control/
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)