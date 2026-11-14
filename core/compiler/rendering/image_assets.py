"""B02.2/G5: reference and stage content-addressed PNG assets for Tectonic.

A RenderUnit carries a reference, never TeX code. Asset bytes are verified and
copied into the compiler's execution-private directory. The OCR producer must
write validated PNG bytes at data/assets/<sha256>.png before creating IMAGE AST.
This module alone does not approve the producer or certify a scientific PDF.
"""

from __future__ import annotations

from hashlib import sha256
import re
from pathlib import Path
from typing import Sequence

from core.compiler.rendering.models import AssetReference

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_IMAGE_PATH = re.compile(r"data/assets/([0-9a-f]{64})\.png\Z")


def canonical_image_name(asset: AssetReference) -> str:
    """Only a content-addressed, relative, PNG reference may become TeX."""
    if asset.mime_type != "image/png":
        raise ValueError("B02_G5_IMAGE_UNSUPPORTED_MIME")
    # No normalization: backslashes, slash variants, traversal or whitespace
    # are not acceptable in persisted canonical AST references.
    match = _IMAGE_PATH.fullmatch(asset.path)
    if match is None:
        raise ValueError("B02_G5_IMAGE_NONCANONICAL_REFERENCE")
    return match.group(1) + ".png"


def stage_image_assets(
    assets: Sequence[AssetReference], *, source_root: Path, execution_dir: Path
) -> None:
    """Fail-closed, idempotent staging; never link untrusted source paths.

    No persistent filesystem mutation: execution_dir belongs to the isolated
    compilation attempt and is discarded on both success and failure.
    """
    if not assets:
        return
    root = source_root.resolve(strict=True)
    data_dir = root / "data"
    asset_dir = data_dir / "assets"
    # Reject symlinked directories, including link redirection out of APP_ROOT.
    if data_dir.is_symlink() or asset_dir.is_symlink():
        raise ValueError("B02_G5_IMAGE_ASSET_ROOT_SYMLINK")
    if not asset_dir.is_dir():
        raise FileNotFoundError("B02_G5_IMAGE_ASSET_DIRECTORY_MISSING")

    target = execution_dir / "assets"
    target.mkdir(exist_ok=False)
    copied: set[str] = set()
    for asset in assets:
        name = canonical_image_name(asset)
        if name in copied:
            continue
        source = asset_dir / name
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError("B02_G5_IMAGE_ASSET_MISSING_OR_LINK: " + name)
        data = source.read_bytes()
        if not data.startswith(_PNG_SIGNATURE):
            raise ValueError("B02_G5_IMAGE_NOT_PNG: " + name)
        if sha256(data).hexdigest() + ".png" != name:
            raise ValueError("B02_G5_IMAGE_HASH_MISMATCH: " + name)
        (target / name).write_bytes(data)
        copied.add(name)
