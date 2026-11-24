"""Pinned local compiler witness for the synthetic PPPR foreground only.

No acquisition, historical mutation, inference, or product policy is performed.
The exact cache and OTFs were exercised in the owner compiler-only witness.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from math import isfinite
from pathlib import Path

from apps.compiler.tectonic_runner import CachedTectonicResources, HostTectonicRunner

CACHE_TREE_SHA256 = "400fb7d1814d241e33d219dc25e0598e9e11b7e9560b5bdfe0b858567c07aa28"
CACHE_FONT = "1aa18cfefa58132c52ce5de70db1fd1154201c19cd2b2cdaffba4906a33e6852"
EXTRA_FONTS = (
    ("lmroman12-regular.otf", 110400, "e6be218ae83e61aa8a29990d3cdc401c678c1962188cb9a4a8b6359e4f5e5870"),
    ("lmroman10-bold.otf", 111240, "102fe06c430a8b681b2bf6876b7cd967ae4d47b4b6b41d915eb7913b726d9fb1"),
    ("lmroman12-bold.otf", 110496, "28c8782ac2b6486958b5dc7610ada7800c53546ff7f36bc65909a876e1cd338e"),
)
SECTIONS = (
    ("1 Methods", "The sample contains measured values."),
    ("1.1 Data", "The dataset contains independent observations."),
    ("1.1.1 Samples", "The experiment measures the response."),
)


def _read_font(path: Path, size: int, digest: str) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size != size:
        raise ValueError("PPPR_G5_FONT_MISSING_OR_SIZE_DRIFT: " + path.name)
    data = path.read_bytes()
    if len(data) != size or not data.startswith(b"OTTO") or sha256(data).hexdigest() != digest:
        raise ValueError("PPPR_G5_FONT_IDENTITY_DRIFT: " + path.name)
    return data


def read_extra_fonts(directory: Path) -> tuple[tuple[str, bytes], ...]:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("PPPR_G5_FONT_DIRECTORY_REQUIRED")
    return tuple((name, _read_font(directory / name, size, digest))
                 for name, size, digest in EXTRA_FONTS)


def verify_cache(cache: Path) -> None:
    if cache.is_symlink() or not cache.is_dir():
        raise ValueError("PPPR_G5_CACHE_DIRECTORY_REQUIRED")
    rows: list[tuple[str, int, str]] = []
    total = 0
    for path in cache.rglob("*"):
        if path.is_symlink():
            raise ValueError("PPPR_G5_CACHE_LINK_REJECTED")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("PPPR_G5_CACHE_NONREGULAR_FILE")
        size = path.stat().st_size
        total += size
        if len(rows) >= 294 or total > 43350180:
            raise ValueError("PPPR_G5_CACHE_COVERAGE_DRIFT")
        data = path.read_bytes()
        if len(data) != size:
            raise ValueError("PPPR_G5_CACHE_SIZE_DRIFT")
        rows.append((path.relative_to(cache).as_posix(), size, sha256(data).hexdigest()))
    digest = sha256(json.dumps(sorted(rows), separators=(",", ":")).encode()).hexdigest()
    if len(rows) != 294 or total != 43350180 or digest != CACHE_TREE_SHA256:
        raise ValueError("PPPR_G5_CACHE_IDENTITY_DRIFT")
    print("PPPR_G5_CACHE_IDENTITY_PASS:", digest, flush=True)


def load_resources(cache: Path, fonts: Path) -> CachedTectonicResources:
    verify_cache(cache)
    regular = _read_font(cache / "files" / CACHE_FONT[:2] / CACHE_FONT[2:],
                         111536, CACHE_FONT)
    resources = CachedTectonicResources(
        cache_dir=cache, fonts=(("lmroman10-regular.otf", regular), *read_extra_fonts(fonts)),
    )
    for name, data in resources.fonts:
        print("PPPR_G5_FONT_VERIFIED:", name, len(data), sha256(data).hexdigest(), flush=True)
    return resources


def fixture_png() -> bytes:
    from PIL import Image

    image = Image.new("RGB", (80, 40), "white")
    image.paste((20, 100, 180), (0, 0, 40, 40))
    image.paste((180, 50, 20), (40, 0, 80, 40))
    stream = BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def verify_fixture_pdf(pdf: Path) -> None:
    """Physical oracle for the synthetic echo fixture, never scientific validation."""
    import fitz

    with fitz.open(pdf) as document:
        text = " ".join(" ".join(page.get_text().split()) for page in document)
        lines = [line for page in document for block in page.get_text("dict")["blocks"]
                 if block["type"] == 0 for line in block["lines"]]
        sizes: list[float] = []
        for (heading, body), expected_font in zip(
            SECTIONS, ("LMRoman12-Bold", "LMRoman12-Bold", "LMRoman10-Bold"), strict=True
        ):
            matches = [line for line in lines if
                       "".join(span["text"] for span in line["spans"]).strip() == heading]
            if len(matches) != 1 or text.count(body) != 1:
                raise ValueError("PPPR_G5_FIXTURE_TEXT_COVERAGE: " + heading)
            spans = [span for span in matches[0]["spans"] if span["text"].strip()]
            points = [float(span["size"]) for span in spans]
            if (not points or not all(isfinite(p) and p > 0 for p in points)
                    or max(points) - min(points) > .05
                    or any(span["font"] != expected_font for span in spans)):
                raise ValueError("PPPR_G5_FIXTURE_HEADING_FONT_OR_SIZE: " + heading)
            sizes.append(min(points))
            print("PPPR_G5_PHYSICAL_HEADING:", heading, min(points), expected_font, flush=True)
        if not sizes[0] > sizes[1] > sizes[2]:
            raise ValueError("PPPR_G5_FIXTURE_HIERARCHY")
        images = [image for page in document for image in page.get_image_info()]
        if len(images) != 1 or (images[0]["width"], images[0]["height"]) != (80, 40):
            raise ValueError("PPPR_G5_FIXTURE_IMAGE_COVERAGE")
        x0, y0, x1, y1 = images[0]["bbox"]
        if (not all(isfinite(value) for value in (x0, y0, x1, y1)) or y1 <= y0
                or abs((x1 - x0) / (y1 - y0) - 2) >= .04):
            raise ValueError("PPPR_G5_FIXTURE_IMAGE_ASPECT")
    print("PPPR_G5_FIXTURE_PHYSICAL_PASS:", sha256(pdf.read_bytes()).hexdigest(), flush=True)


def compile_preflight(resources: CachedTectonicResources, root: Path) -> None:
    """Compile the actual fixture's typed content before DB bootstrap or HTTP."""
    from apps.compiler.tex_builder import TexBuilder
    from core.ast.enums import ContentNodeType, HeadingLevel
    from core.compiler.rendering.context import RenderContextFactory
    from core.compiler.rendering.models import AssetReference, RenderGeometry, RenderUnit
    from core.document_profile.models import InferredDocumentProfile, PageLayout
    from infra.extraction.providers.pymupdf_image_assets import persist_png_asset

    evidence = root / "data" / "compiler-preflight"
    evidence.mkdir(exist_ok=False)
    units: list[RenderUnit] = []
    for i, ((heading, body), level) in enumerate(zip(
        SECTIONS, (HeadingLevel.H1, HeadingLevel.H2, HeadingLevel.H3), strict=True
    )):
        units.extend((
            RenderUnit(f"h{i}", ContentNodeType.HEADING, heading, heading_level=level),
            RenderUnit(f"p{i}", ContentNodeType.PARAGRAPH, body),
        ))
    asset = AssetReference(persist_png_asset(fixture_png(), source_root=root))
    units.append(RenderUnit("img", ContentNodeType.IMAGE, asset.path,
                            geometry=RenderGeometry(.07, .6, .32, .1, 1), asset=asset))
    profile = InferredDocumentProfile(layout=PageLayout.SINGLE_COLUMN, document_type=None)
    tex = TexBuilder(RenderContextFactory.create(profile)).build(units)
    (evidence / "doc.tex").write_text(tex, encoding="utf-8")
    pdf = HostTectonicRunner(cached_resources=resources).compile(
        tex, str(evidence), "doc.pdf", image_assets=(asset,),
    )
    verify_fixture_pdf(Path(pdf))
    print("PPPR_G5_COMPILER_PREFLIGHT_PASS", flush=True)
