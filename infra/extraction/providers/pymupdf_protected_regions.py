"""DF-01: conservative producer for complete, positively identified PDF regions.

Non-rotated pages with proven direct or bounded composed vector content are admitted.
Rectangular merged-cell tables, three-rule multiline-header tables and framed,
captioned figures have distinct
evidence. A drawing cluster alone never confers semantic authority.
No clipping-only asset, rasterization, or implicit omission.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import ceil, floor, isfinite
import re
from statistics import median
from typing import Any, Mapping, Sequence, cast

import fitz

from core.domain.document import LayoutBlockType
from infra.extraction.providers.pymupdf_integrity import UnrepresentedPdfContentError

_Box = tuple[float, float, float, float]


@dataclass(frozen=True, slots=True)
class ProtectedRegion:
    logical_type: LayoutBlockType
    bbox: _Box
    covered_blocks: tuple[int, ...]
    covered_drawings: tuple[int, ...]
    # Insert at a witnessed native block position, not a fabricated native ID.
    insert_before: int
    caption_block: int | None
    pdf: bytes


def _contains(outer: fitz.Rect, inner: fitz.Rect) -> bool:
    return (outer.x0 <= inner.x0 <= inner.x1 <= outer.x1
            and outer.y0 <= inner.y0 <= inner.y1 <= outer.y1)


def _intersects(a: fitz.Rect, b: fitz.Rect) -> bool:
    return a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1


def _rect(value: Any) -> fitz.Rect:
    r = fitz.Rect(value)
    if not all(isfinite(v) for v in (r.x0, r.y0, r.x1, r.y1)) or r.x0 > r.x1 or r.y0 > r.y1:
        raise UnrepresentedPdfContentError("DF01_INVALID_PHYSICAL_REGION")
    return r


def _box(r: fitz.Rect) -> _Box:
    return (r.x0, r.y0, r.x1, r.y1)


def _text(block: Mapping[str, Any]) -> str:
    return "\n".join(
        "".join(span.get("text", "") for span in line.get("spans", []))
        for line in block.get("lines", [])
    )


def _merged_grid(table: Any) -> bool:
    """Require a complete, non-overlapping cell tiling and a witnessed span."""
    bounds = _rect(table.bbox)
    cells = [_rect(value) for value in table.cells if value is not None]
    if len(cells) < 2 or any(c.is_empty or not _contains(bounds, c) for c in cells):
        return False
    if any(_intersects(a, b) for i, a in enumerate(cells) for b in cells[i + 1:]):
        return False
    # Coordinates are producer cell edges, not fabricated row/column counts.
    xs = sorted({v for c in cells for v in (c.x0, c.x1)})
    ys = sorted({v for c in cells for v in (c.y0, c.y1)})
    if len(xs) < 3 or len(ys) < 3:
        return False
    if abs(sum(c.get_area() for c in cells) - bounds.get_area()) > 1e-6:
        return False
    return any(xs.index(c.x1) - xs.index(c.x0) > 1
               or ys.index(c.y1) - ys.index(c.y0) > 1 for c in cells)


def _merged_row_grids(drawings: Sequence[Mapping[str, Any]]) -> list[fitz.Rect]:
    """Independent witness for exact rectilinear ruled grids with horizontal spans.

    Native table detectors differ across PyMuPDF versions. For this restricted
    profile use the original line geometry: connected straight rules, complete
    horizontal separators and outer borders, with column dividers either
    absent or complete in each row. A partial divider is not a merged cell.
    No snapping, invented edges, inferred missing boundaries or row-count
    heuristic. Other grid shapes still need the native table witness.
    """
    lines: list[fitz.Rect] = []
    for d in drawings:
        items = d.get("items", [])
        if d.get("type") != "s" or len(items) != 1 or items[0][0] != "l":
            continue
        r = _rect(d["rect"])
        if (r.width == 0) != (r.height == 0):
            lines.append(r)
    # Connected components of touching rules, including zero-width rectangles.
    remaining = set(range(len(lines)))
    grids: list[fitz.Rect] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = [seed]
        for i in component:
            a = lines[i]
            neighbors = [j for j in remaining if
                         a.x0 <= lines[j].x1 and lines[j].x0 <= a.x1
                         and a.y0 <= lines[j].y1 and lines[j].y0 <= a.y1]
            remaining.difference_update(neighbors)
            component.extend(sorted(neighbors))
        rules = [lines[i] for i in component]
        horizontal = [r for r in rules if r.height == 0]
        vertical = [r for r in rules if r.width == 0]
        ys = sorted({r.y0 for r in horizontal})
        xs = sorted({r.x0 for r in vertical})
        if len(xs) < 3 or len(ys) < 3:
            continue
        left, right, top, bottom = xs[0], xs[-1], ys[0], ys[-1]
        if (any(r.x0 not in xs or r.x1 not in xs for r in horizontal)
                or any(r.y0 not in ys or r.y1 not in ys for r in vertical)):
            continue

        def covers(intervals: Sequence[tuple[float, float]], lo: float, hi: float) -> bool:
            edge = lo
            for start, end in sorted(intervals):
                if end <= edge:
                    continue
                if start > edge:
                    return False
                edge = end
                if edge >= hi:
                    return True
            return False

        if not all(covers([(r.x0, r.x1) for r in horizontal if r.y0 == y], left, right) for y in ys):
            continue
        merged = False
        valid = True
        for x in xs:
            intervals = [(r.y0, r.y1) for r in vertical if r.x0 == x]
            for lo, hi in zip(ys, ys[1:]):
                present = any(start < hi and lo < end for start, end in intervals)
                if present and not covers(intervals, lo, hi):
                    valid = False
                if not present:
                    if x in (left, right):
                        valid = False
                    else:
                        merged = True
        if valid and merged:
            grids.append(fitz.Rect(left, top, right, bottom))
    return grids


def _row_cells(spans: Sequence[fitz.Rect]) -> list[list[tuple[float, float]]]:
    """Witness aligned columns without reconstructing their text or content.

    Use vertical centers to group overlapping glyph bands, then join nearby
    spans on the same row. Gaps relative to the observed glyph height are
    evidence of distinct column positions, not inferred cell boundaries.
    """
    rows: list[tuple[float, list[fitz.Rect]]] = []
    for span in sorted(spans, key=lambda r: ((r.y0 + r.y1) / 2, r.x0)):
        center = (span.y0 + span.y1) / 2
        if rows and abs(center - rows[-1][0]) <= span.height / 2:
            rows[-1][1].append(span)
        else:
            rows.append((center, [span]))
    result: list[list[tuple[float, float]]] = []
    for _, row in rows:
        gap = median(r.height for r in row) / 2
        cells: list[tuple[float, float]] = []
        for span in sorted(row, key=lambda r: r.x0):
            if cells and span.x0 - cells[-1][1] < gap:
                cells[-1] = (cells[-1][0], max(cells[-1][1], span.x1))
            else:
                cells.append((span.x0, span.x1))
        result.append(cells)
    return result


def _three_rule_tables(
    drawings: Sequence[Mapping[str, Any]], raw_blocks: Sequence[Mapping[str, Any]],
) -> list[fitz.Rect]:
    """Restricted evidence for scientific tables without vertical borders.

    Three coextensive horizontal rules delimit a multiline header and body.
    Require repeated aligned column positions and a separate adjacent Table
    caption. Never use whole-page text table detection or a bounding hull of
    unrelated rules. The common coverage and isolation checks still apply.
    """
    groups: dict[tuple[float, float], list[tuple[fitz.Rect, float]]] = {}
    for drawing in drawings:
        items = drawing.get("items", [])
        if drawing.get("type") != "s" or len(items) != 1 or items[0][0] != "l":
            continue
        r = _rect(drawing["rect"])
        width = drawing.get("width")
        if r.height != 0 or r.width <= 0 or not isinstance(width, (int, float)):
            continue
        if not isfinite(width) or width <= 0:
            continue
        groups.setdefault((r.x0, r.x1), []).append((r, float(width)))
    blocks = [_rect(b["bbox"]) for b in raw_blocks]
    candidates: list[fitz.Rect] = []
    for (left, right), rules in groups.items():
        if len(rules) != 3:
            continue
        top, middle, bottom = sorted(r.y0 for r, _ in rules)
        if not top < middle < bottom:
            continue
        # Use the actual stroke's horizontal extent, not an arbitrary margin.
        half_stroke = max(width for _, width in rules) / 2
        bounds = fitz.Rect(left - half_stroke, top, right + half_stroke, bottom)
        inside = [i for i, r in enumerate(blocks) if _contains(bounds, r)]
        if not inside or inside != list(range(inside[0], inside[-1] + 1)):
            continue
        if any(_intersects(bounds, r) and i not in inside for i, r in enumerate(blocks)):
            continue
        if any(raw_blocks[i].get("type") != 0 for i in inside):
            continue
        neighbors = [i for i in (inside[0] - 1, inside[-1] + 1) if 0 <= i < len(blocks)]
        captions = [i for i in neighbors
                    if re.match(r"^\s*Table\s+\d", _text(raw_blocks[i]), re.I)
                    and left < blocks[i].x1 and blocks[i].x0 < right
                    and (blocks[i].y1 <= top or blocks[i].y0 >= bottom)]
        if len(captions) != 1:
            continue
        spans = [_rect(span["bbox"]) for i in inside
                 for line in raw_blocks[i].get("lines", [])
                 for span in line.get("spans", []) if span.get("text", "").strip()]
        if not spans or any(r.is_empty or not _contains(bounds, r)
                            or r.y0 < middle < r.y1 for r in spans):
            continue
        header = _row_cells([r for r in spans if r.y1 <= middle])
        body = _row_cells([r for r in spans if r.y0 >= middle])
        # Two physical header rows and repeated independent column anchors.
        if len(header) < 2 or len(body) < 2:
            continue
        anchors = [(a + b) / 2 for a, b in max(header, key=len)]
        if len(anchors) < 3 or sum(len(row) >= 2 for row in header) < 2:
            continue
        matched_rows = sum(
            sum(any(a <= x <= b for x in anchors) for a, b in row) >= 3
            for row in body
        )
        if matched_rows < 2 or matched_rows * 2 <= len(body):
            continue
        candidates.append(bounds)
    return candidates


def _marks(page: fitz.Page) -> list[tuple[str, fitz.Rect]]:
    return [(str(kind), _rect(bounds)) for kind, bounds in page.get_bboxlog()]


def _clip_bounds(entry: Mapping[str, Any]) -> fitz.Rect:
    """Bound the actual clip path, not its already-intersected scissor."""
    coords: list[tuple[float, float]] = []
    for item in entry.get("items", []):
        if item[0] == "re" and len(item) == 3:
            box = _rect(item[1])
            coords.extend(((box.x0, box.y0), (box.x1, box.y1)))
        elif item[0] in ("l", "c"):
            for point in item[1:]:
                coords.append((float(point.x), float(point.y)))
        elif item[0] == "qu" and len(item) == 2:
            box = _rect(item[1].rect)
            coords.extend(((box.x0, box.y0), (box.x1, box.y1)))
        else:
            raise UnrepresentedPdfContentError("DF01_UNSUPPORTED_CLIP_PATH")
    if not coords:
        raise UnrepresentedPdfContentError("DF01_EMPTY_CLIP_PATH")
    return _rect((min(p[0] for p in coords), min(p[1] for p in coords),
                  max(p[0] for p in coords), max(p[1] for p in coords)))


def _composition(
    page: fitz.Page,
) -> tuple[list[fitz.Rect], list[dict[str, Any]]]:
    """Observe actual graphic scopes and ordered operators in page coordinates.

    Ignore only MuPDF's neutral page-sized transparency wrapper, which may
    appear when a page is copied. Never use effective clip intersection as
    evidence that an underlying, larger Form is itself fully represented.
    """
    entries = cast(list[dict[str, Any]], page.get_drawings(extended=True))
    offset = 0
    if entries:
        root = entries[0]
        if (root.get("type") == "group" and root.get("level") == 0
                and not root.get("layer") and root.get("rect") == page.rect
                and root.get("isolated") is True and root.get("knockout") is False
                and root.get("blendmode") == "Normal" and root.get("opacity") == 1.0):
            entries = entries[1:]
            offset = 1
    scopes: list[fitz.Rect] = []
    signature: list[dict[str, Any]] = []
    for entry in entries:
        kind = entry.get("type")
        level = entry.get("level", 0)
        if (kind not in ("clip", "group", "s", "f", "fs")
                or not isinstance(level, int) or level < offset or entry.get("layer")):
            raise UnrepresentedPdfContentError("DF01_UNSUPPORTED_GRAPHIC_COMPOSITION")
        if kind == "clip":
            bounds = _clip_bounds(entry)
            scissor = _rect(entry["scissor"])
            if bounds.is_empty or not _contains(bounds, scissor):
                raise UnrepresentedPdfContentError("DF01_CLIP_GEOMETRY_UNPROVEN")
            scopes.append(bounds)
        elif kind == "group":
            bounds = _rect(entry["rect"])
            if bounds.is_empty:
                raise UnrepresentedPdfContentError("DF01_GROUP_GEOMETRY_UNPROVEN")
            scopes.append(bounds)
        # seqno is page-local and shifts when exterior text is removed.
        signature.append({**{k: v for k, v in entry.items() if k != "seqno"},
                          "level": level - offset})
    return scopes, signature


def _form_inventory(page: fitz.Page) -> Counter[tuple[bool, _Box]]:
    """Restrict reusable resources to local Form XObjects.

    This is supplementary inventory evidence, not an invocation geometry
    proof: actual scopes and observed paint operations supply that proof.
    """
    source = page.parent
    if source is None:
        raise UnrepresentedPdfContentError("DF01_SOURCE_PAGE_DETACHED")
    result: Counter[tuple[bool, _Box]] = Counter()
    for xref, _, parent, bounds in page.get_xobjects():
        if source.xref_get_key(xref, "Subtype") != ("name", "/Form"):
            raise UnrepresentedPdfContentError("DF01_UNSUPPORTED_XOBJECT")
        for key in ("Ref", "F", "OPI", "OC", "Metadata", "PieceInfo"):
            if source.xref_get_key(xref, key)[0] != "null":
                raise UnrepresentedPdfContentError("DF01_UNSUPPORTED_FORM_RESOURCE")
        result[(parent == 0, _box(_rect(bounds)))] += 1
    return result


def _isolated_pdf(
    page: fitz.Page, region: fitz.Rect, expected_text: str, expected_drawings: int,
    *, composed: bool = False,
) -> bytes:
    """Remove exterior marks on a disposable copy and inspect it *before* crop.

    Bounded compositions must survive as complete operator scopes and local
    Forms. The direct profile remains unchanged. Neither profile constitutes
    a general PDF sanitizer or authorization for external disclosure.
    """
    source = page.parent
    page_index = page.number
    if source is None or not isinstance(page_index, int):
        raise UnrepresentedPdfContentError("DF01_SOURCE_PAGE_DETACHED")
    source_signature = _composition(page)[1] if composed else []
    forms = _form_inventory(page) if composed else Counter()
    expected_marks = [(kind, _box(r)) for kind, r in _marks(page)
                      if _contains(region, r)] if composed else []
    with fitz.open() as isolated:
        isolated.insert_pdf(source, from_page=page_index, to_page=page_index,
                            links=False, annots=False, widgets=False)
        copied = isolated[0]
        outer = copied.rect
        for band in (
            fitz.Rect(outer.x0, outer.y0, outer.x1, region.y0),
            fitz.Rect(outer.x0, region.y1, outer.x1, outer.y1),
            fitz.Rect(outer.x0, region.y0, region.x0, region.y1),
            fitz.Rect(region.x1, region.y0, outer.x1, region.y1),
        ):
            if not band.is_empty:
                # PyMuPDF documents False as the no-fill sentinel; None
                # uses the default fill. Its type stub only accepts OptSeq.
                copied.add_redact_annot(band, fill=cast(Any, False), cross_out=False)
        if not copied.apply_redactions(images=1, graphics=2, text=0):
            raise UnrepresentedPdfContentError("DF01_EXTERIOR_REMOVAL_FAILED")
        copied.clean_contents(sanitize=True)
        if any(not _contains(region, r) for _, r in _marks(copied)):
            raise UnrepresentedPdfContentError("DF01_EXTERIOR_MARK_RETAINED")
        if copied.get_images(full=True) or (not composed and copied.get_xobjects()):
            raise UnrepresentedPdfContentError("DF01_UNSUPPORTED_ISOLATED_RESOURCES")
        if composed:
            if _form_inventory(copied) != forms:
                raise UnrepresentedPdfContentError("DF01_FORM_INVENTORY_DRIFT")
            if _composition(copied)[1] != source_signature:
                raise UnrepresentedPdfContentError("DF01_COMPOSITION_OPERATOR_DRIFT")
            if [(kind, _box(r)) for kind, r in _marks(copied)] != expected_marks:
                raise UnrepresentedPdfContentError("DF01_COMPOSITION_PAINT_DRIFT")
        copied_dict = cast(dict[str, Any], copied.get_text("dict"))
        actual = "\n".join(
            _text(b) for b in copied_dict["blocks"] if b.get("type") == 0
        )
        if actual != expected_text:
            raise UnrepresentedPdfContentError("DF01_PROTECTED_TEXT_DRIFT")
        before_crop_drawings = len(copied.get_drawings())
        if before_crop_drawings != expected_drawings:
            raise UnrepresentedPdfContentError("DF01_PROTECTED_VECTOR_COUNT_DRIFT")
        copied.set_cropbox(region)
        data = isolated.tobytes(garbage=4, clean=True, deflate=True, no_new_id=True)

    with fitz.open(stream=data, filetype="pdf") as verified:
        if len(verified) != 1 or verified.embfile_count():
            raise UnrepresentedPdfContentError("DF01_ASSET_STRUCTURE_DRIFT")
        result = verified[0]
        if composed and len(result.get_xobjects()) != sum(forms.values()):
            raise UnrepresentedPdfContentError("DF01_SERIALIZED_FORM_INVENTORY_DRIFT")
        if len(result.get_drawings()) != before_crop_drawings or result.get_image_info():
            raise UnrepresentedPdfContentError("DF01_ASSET_VECTOR_DRIFT")
        if result.rect.width != region.width or result.rect.height != region.height:
            raise UnrepresentedPdfContentError("DF01_ASSET_GEOMETRY_DRIFT")
        for scale in (1, 2):
            matrix = fitz.Matrix(scale, scale)
            expected = page.get_pixmap(clip=region, matrix=matrix, alpha=False)
            observed = result.get_pixmap(matrix=matrix, alpha=False)
            if (expected.width, expected.height, expected.samples) != (
                observed.width, observed.height, observed.samples
            ):
                raise UnrepresentedPdfContentError("DF01_ASSET_VISUAL_DRIFT")
    return data


def prepare_protected_regions(
    page: fitz.Page, raw_blocks: Sequence[Mapping[str, Any]], *, page_number: int,
) -> tuple[ProtectedRegion, ...]:
    """Complete coverage of observed vector marks or fail before publication."""
    drawings = cast(list[dict[str, Any]], page.get_drawings())
    if not drawings:
        return ()
    def reject(reason: str = "REGION_UNPROVEN") -> UnrepresentedPdfContentError:
        return UnrepresentedPdfContentError(
            f"B02_UNREPRESENTED_VECTOR_DRAWING: page={page_number}; DF01_{reason}"
        )

    source = page.parent
    if (source is None or page.rotation or page.cropbox != page.mediabox
            or source.get_ocgs() or source.embfile_count()
            or page.first_annot is not None or page.first_widget is not None):
        raise reject("UNSUPPORTED_PAGE_RESOURCES")
    scopes, signature = _composition(page)
    forms = _form_inventory(page)
    composed = bool(scopes or forms)
    if forms and not scopes:
        raise reject("FORM_SCOPE_UNPROVEN")
    if not composed and any(d["level"] != 0 for d in signature):
        raise reject("UNSUPPORTED_GRAPHIC_COMPOSITION")
    marks = _marks(page)
    if any(kind not in ("fill-text", "stroke-text", "fill-path", "stroke-path", "fill-image")
           or not _contains(page.rect, extent) for kind, extent in marks):
        raise reject()

    rects = [_rect(d["rect"]) for d in drawings]
    block_rects = [_rect(b["bbox"]) for b in raw_blocks]
    finder = page.find_tables(strategy="lines_strict")
    tables = finder.tables if finder is not None else []
    table_bounds = [_rect(t.bbox) for t in tables]
    candidates: list[tuple[LayoutBlockType, fitz.Rect]] = [
        (LayoutBlockType.TABLE_COMPLEX, _rect(t.bbox)) for t in tables if _merged_grid(t)
    ]
    # Require an explicit table caption for the independent geometry witness.
    # Otherwise a rectilinear diagram could be mistaken for a table.
    native_table_count = len(candidates)
    for grid in _merged_row_grids(drawings):
        if not any(_intersects(grid, b) for _, b in candidates):
            candidates.append((LayoutBlockType.TABLE_COMPLEX, grid))
    for bounds in _three_rule_tables(drawings, raw_blocks):
        if not any(_intersects(bounds, b) for _, b in candidates):
            candidates.append((LayoutBlockType.TABLE_COMPLEX, bounds))
    table_bounds.extend(b for _, b in candidates)
    # A frame and an exterior caption are required; never infer a figure from
    # a line, decorative rule, or text-containing cluster in isolation.
    for drawing, bounds in zip(drawings, rects, strict=True):
        items = drawing.get("items", [])
        if (len(items) != 1 or items[0][0] != "re" or bounds.is_empty
                or any(_contains(t, bounds) or _intersects(t, bounds) for t in table_bounds)
                or sum(_contains(bounds, r) for r in rects) < 2):
            continue
        candidates.append((LayoutBlockType.IMAGE, bounds))

    if composed:
        # A complete outer graphic scope may delimit a figure without a
        # drawn frame. It still requires a distinct caption and all other
        # semantic checks. Never collapse overlapping unrelated scopes.
        outer_scopes = [r for r in scopes if r != page.rect
                        and not any(s != r and _contains(s, r) for s in scopes)]
        for bounds in outer_scopes:
            if any(_intersects(bounds, b) for b in table_bounds):
                continue
            if sum(_contains(bounds, r) for r in rects) < 2:
                continue
            # Prefer the whole scope over an internal figure frame.
            candidates = [(kind, b) for kind, b in candidates
                          if kind != LayoutBlockType.IMAGE or not _contains(bounds, b)]
            candidates.append((LayoutBlockType.IMAGE, bounds))

    pending: list[tuple[LayoutBlockType, fitz.Rect, tuple[int, ...], tuple[int, ...], int, int | None]] = []
    covered: set[int] = set()
    covered_blocks: set[int] = set()
    for candidate_index, (kind, bounds) in enumerate(candidates):
        indices = tuple(i for i, r in enumerate(rects) if _contains(bounds, r))
        if not indices:
            continue
        # Include the actual paint extent, not just the path centerline.
        paint = fitz.Rect(bounds)
        for i in indices:
            seq = drawings[i].get("seqno")
            if not isinstance(seq, int) or not 0 <= seq < len(marks):
                raise reject()
            mark_kind, extent = marks[seq]
            if mark_kind not in ("stroke-path", "fill-path"):
                raise reject()
            paint |= extent
        region = fitz.Rect(floor(paint.x0), floor(paint.y0), ceil(paint.x1), ceil(paint.y1))
        if region.is_empty or not _contains(page.rect, region) or region == page.rect:
            raise reject()
        # A mark may not straddle the boundary. Raster marks in a protected
        # region are not yet supported by this direct-vector producer.
        for mark_kind, extent in marks:
            if _intersects(region, extent) and (
                not _contains(region, extent) or mark_kind == "fill-image"
            ):
                raise reject()
        inside = tuple(i for i, r in enumerate(block_rects) if _contains(region, r))
        if any(_intersects(region, r) and i not in inside for i, r in enumerate(block_rects)):
            raise reject()
        if any(raw_blocks[i].get("type") != 0 for i in inside):
            raise reject()
        if not inside or tuple(range(inside[0], inside[-1] + 1)) != inside:
            raise reject()
        if any(re.match(r"^\s*(?:Fig(?:ure)?\.?|Table)\s+\d", _text(raw_blocks[i]), re.I) for i in inside):
            raise reject()
        # Do not absorb text merely because it sits inside the padded stroke
        # envelope. The semantic boundary is the witnessed frame or grid.
        if any(not _contains(bounds, block_rects[i]) for i in inside):
            raise reject()
        # An adjacent native caption remains a distinct translatable block.
        # The figure requires one; the merged grid is independent evidence.
        pattern = r"^\s*Fig(?:ure)?\.?\s+\d" if kind == LayoutBlockType.IMAGE else r"^\s*Table\s+\d"
        neighbors = [i for i in (inside[0] - 1, inside[-1] + 1) if 0 <= i < len(raw_blocks)]
        captions = [
            i for i in neighbors
            if re.match(pattern, _text(raw_blocks[i]), re.I)
            and region.x0 < block_rects[i].x1 and block_rects[i].x0 < region.x1
            and (block_rects[i].y1 <= region.y0 or block_rects[i].y0 >= region.y1)
        ]
        needs_caption = kind == LayoutBlockType.IMAGE or candidate_index >= native_table_count
        if len(captions) > 1 or (needs_caption and not captions):
            raise reject()
        caption = captions[0] if captions else None
        if caption is not None and any(p[5] == caption for p in pending):
            raise reject()
        if covered.intersection(indices) or covered_blocks.intersection(inside) or any(
            _intersects(region, p[1]) for p in pending
        ):
            raise reject()
        covered.update(indices)
        covered_blocks.update(inside)
        pending.append((kind, region, inside, indices, inside[0], caption))

    if covered != set(range(len(drawings))):
        raise reject("UNCOVERED_VECTOR_DRAWINGS")
    # Also verify each independently observed paint operation, not only the
    # get_drawings count (which may aggregate fill and stroke).
    if any(
        sum(_contains(p[1], extent) for p in pending) != 1
        for kind, extent in marks if kind in ("fill-path", "stroke-path")
    ):
        raise reject()
    if composed:
        # Initial admission is one complete composition, never partition a
        # shared graphics state or a reusable Form across separate assets.
        if len(pending) != 1 or any(not _contains(pending[0][1], r) for r in scopes):
            raise reject("COMPOSITION_SCOPE_UNPROVEN")
    output: list[ProtectedRegion] = []
    for kind, region, inside, indices, insertion, caption in sorted(pending, key=lambda p: p[4]):
        expected_text = "\n".join(_text(raw_blocks[i]) for i in inside)
        pdf = _isolated_pdf(page, region, expected_text, len(indices), composed=composed)
        output.append(ProtectedRegion(kind, _box(region), inside, indices, insertion, caption, pdf))
    return tuple(output)
