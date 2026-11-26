"""B02.3: store PyMuPDF raster images as immutable content-addressed PNG assets.

This imperative edge does not change G3/G5 or attest to mathematical fidelity.
Do not expose partially written files to the compiler. No implicit overwrite.
"""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import tempfile

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def persist_png_asset(png: bytes, *, source_root: Path) -> str:
    """Publish an immutable PNG via atomic hard-link, or verify existing bytes.

    The canonical reference is relative to APP_ROOT and stays stable for replay.
    If atomic publication is unsupported by the filesystem, fail closed.
    """
    if not isinstance(png, bytes) or not png.startswith(_PNG_SIGNATURE):
        raise ValueError("B023_IMAGE_NOT_PNG")
    return _persist_asset(png, extension="png", source_root=source_root)


def persist_pdf_asset(pdf: bytes, *, source_root: Path) -> str:
    """Publish bytes already validated by the protected-region producer."""
    if not isinstance(pdf, bytes) or not pdf.startswith(b"%PDF-") or not pdf.rstrip().endswith(b"%%EOF"):
        raise ValueError("DF01_ASSET_NOT_PDF")
    return _persist_asset(pdf, extension="pdf", source_root=source_root)


def _persist_asset(data: bytes, *, extension: str, source_root: Path) -> str:
    digest = sha256(data).hexdigest()
    root = source_root.resolve(strict=True)
    data_dir, folder = root / "data", root / "data" / "assets"
    for directory in (data_dir, folder):
        if directory.is_symlink():
            raise ValueError("B023_IMAGE_ASSET_DIRECTORY_SYMLINK")
        directory.mkdir(exist_ok=True)
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("B023_IMAGE_ASSET_DIRECTORY_INVALID")

    destination = folder / (digest + "." + extension)
    if destination.is_symlink():
        raise ValueError("B023_IMAGE_ASSET_SYMLINK")
    if destination.exists():
        if not destination.is_file() or destination.read_bytes() != data:
            raise ValueError("B023_IMAGE_EXISTING_ASSET_CONFLICT")
        return f"data/assets/{digest}.{extension}"

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".b023_", suffix=".tmp", dir=folder, delete=False) as file:
            temp_path = Path(file.name)
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        try:
            # No replace: another writer can publish the same digest concurrently.
            os.link(temp_path, destination)
        except FileExistsError:
            if destination.is_symlink() or not destination.is_file() or destination.read_bytes() != data:
                raise ValueError("B023_IMAGE_EXISTING_ASSET_CONFLICT")
        except OSError as exc:
            raise OSError("B023_IMAGE_ATOMIC_PUBLICATION_UNAVAILABLE") from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return f"data/assets/{digest}.{extension}"
