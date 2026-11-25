"""B02.2/G5 and DF-01: stage explicitly typed content-addressed visual assets.

A RenderUnit carries a reference, never TeX code. Asset bytes are checked and
copied into the compiler's execution-private directory. The producer must
validate the actual content, provenance and isolation before creating a node.
PDF support is the G5 consumer boundary, not a region detector or permission to
embed arbitrary source pages. Signature/digest checks do not validate PDF
semantics, hidden content or scientific fidelity.
"""

from __future__ import annotations

from hashlib import sha256
import re
from pathlib import Path
from typing import Sequence

from core.compiler.rendering.models import AssetReference

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_IMAGE_PATH = re.compile(r"data/assets/([0-9a-f]{64})\.(png|pdf)\Z")
_ASSET_EXTENSIONS = {"image/png": "png", "application/pdf": "pdf"}


def canonical_image_name(asset: AssetReference) -> str:
    """Only an explicitly typed, canonical digest reference may become TeX."""
    extension = _ASSET_EXTENSIONS.get(asset.mime_type)
    if extension is None:
        raise ValueError("B02_G5_IMAGE_UNSUPPORTED_MIME")
    # No normalization: backslashes, slash variants, traversal or whitespace
    # are not acceptable in persisted canonical AST references.
    match = _IMAGE_PATH.fullmatch(asset.path)
    if match is None or match.group(2) != extension:
        raise ValueError("B02_G5_IMAGE_NONCANONICAL_REFERENCE")
    return match.group(1) + "." + extension


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
        if asset.mime_type == "image/png" and not data.startswith(_PNG_SIGNATURE):
            raise ValueError("B02_G5_IMAGE_NOT_PNG: " + name)
        if asset.mime_type == "application/pdf" and (
            not data.startswith(b"%PDF-") or not data.rstrip().endswith(b"%%EOF")
        ):
            raise ValueError("DF01_G5_IMAGE_NOT_PDF: " + name)
        if sha256(data).hexdigest() + "." + _ASSET_EXTENSIONS[asset.mime_type] != name:
            raise ValueError("B02_G5_IMAGE_HASH_MISMATCH: " + name)
        (target / name).write_bytes(data)
        copied.add(name)
