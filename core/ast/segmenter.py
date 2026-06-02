import re
import logging
from enum import Enum
from typing import List

logger = logging.getLogger(__name__)

class SegmentState(str, Enum):
    NORMAL = "NORMAL"
    IN_EQUATION = "IN_EQUATION"
    IN_TABLE = "IN_TABLE"
    IN_CODE = "IN_CODE"
    IN_FIGURE = "IN_FIGURE"
    IN_ALGORITHM = "IN_ALGORITHM"

class MarkdownSegmenter:
    """
    SOTA: FSM de Segmentación Estructural.
    Aísla entidades jerárquicas con TTL de protección contra corrupción de OCR.
    """
    def __init__(self):
        # SOTA: Barreras de Pánico (Anti-Lock)
        self.TTL = {
            SegmentState.IN_EQUATION: 150,
            SegmentState.IN_TABLE: 300,
            SegmentState.IN_CODE: 500,
            SegmentState.IN_FIGURE: 100,
            SegmentState.IN_ALGORITHM: 200
        }

        # Separación estricta de fronteras
        self.EQ_START = re.compile(r'^\s*(\$\$|\\begin\{(equation|align|aligned|gather|math)\*?\})', re.IGNORECASE)
        self.EQ_END = re.compile(r'(\$\$|\\end\{(equation|align|aligned|gather|math)\*?\})\s*$', re.IGNORECASE)

        self.TAB_START = re.compile(r'^\s*\\begin\{(tabular|table|array|longtable)\*?\}', re.IGNORECASE)
        self.TAB_END = re.compile(r'\\end\{(tabular|table|array|longtable)\*?\}\s*$', re.IGNORECASE)

        self.FIG_START = re.compile(r'^\s*\\begin\{(figure|tikzpicture|wrapfigure)\*?\}', re.IGNORECASE)
        self.FIG_END = re.compile(r'\\end\{(figure|tikzpicture|wrapfigure)\*?\}\s*$', re.IGNORECASE)

        self.ALG_START = re.compile(r'^\s*\\begin\{(algorithm|algorithmic)\*?\}', re.IGNORECASE)
        self.ALG_END = re.compile(r'\\end\{(algorithm|algorithmic)\*?\}\s*$', re.IGNORECASE)

        self.CODE_FENCE = re.compile(r'^\s*```')
        self.TABLE_PIPE = re.compile(r'^\s*\|')

    def segment(self, full_text: str) -> List[str]:
        if not full_text:
            return []

        lines = full_text.splitlines()
        blocks: List[str] = []
        current_block: List[str] = []
        state = SegmentState.NORMAL
        lines_in_state = 0

        def flush_block():
            nonlocal current_block, lines_in_state, state
            if current_block:
                blocks.append("\n".join(current_block))
            current_block = []
            lines_in_state = 0
            state = SegmentState.NORMAL

        for line_idx, line in enumerate(lines):
            stripped = line.strip()

            if state == SegmentState.NORMAL:
                if not stripped:
                    flush_block()
                    continue

                # Transiciones de estado duro (LaTeX nativo)
                if self.EQ_START.match(stripped):
                    flush_block()
                    state = SegmentState.IN_EQUATION
                    current_block.append(line)
                    continue
                if self.TAB_START.match(stripped):
                    flush_block()
                    state = SegmentState.IN_TABLE
                    current_block.append(line)
                    continue
                if self.FIG_START.match(stripped):
                    flush_block()
                    state = SegmentState.IN_FIGURE
                    current_block.append(line)
                    continue
                if self.ALG_START.match(stripped):
                    flush_block()
                    state = SegmentState.IN_ALGORITHM
                    current_block.append(line)
                    continue
                if self.CODE_FENCE.match(stripped):
                    flush_block()
                    state = SegmentState.IN_CODE
                    current_block.append(line)
                    continue

                # Markdown Tabular Fallback (se acumulan bajo NORMAL y se rompen con línea vacía)
                if self.TABLE_PIPE.match(stripped) and not current_block:
                    current_block.append(line)
                    continue

                current_block.append(line)

            else:
                # Modos anidados
                current_block.append(line)
                lines_in_state += 1

                # 1. Intercepción de Corrupción (TTL Anti-Lock)
                if lines_in_state >= self.TTL[state]:
                    logger.error(
                        f"[TELEMETRIA_CORRUPCION] Anti-Lock disparado en {state.value} "
                        f"(Línea límite {line_idx}). Entorno sin cierre. Forzando purga a COMPOSITE_BLOCK."
                    )
                    flush_block()
                    continue

                # 2. Cierres Nativos
                if state == SegmentState.IN_EQUATION and self.EQ_END.search(stripped):
                    flush_block()
                elif state == SegmentState.IN_TABLE and self.TAB_END.search(stripped):
                    flush_block()
                elif state == SegmentState.IN_FIGURE and self.FIG_END.search(stripped):
                    flush_block()
                elif state == SegmentState.IN_ALGORITHM and self.ALG_END.search(stripped):
                    flush_block()
                elif state == SegmentState.IN_CODE and self.CODE_FENCE.match(stripped) and lines_in_state > 1:
                    flush_block()

        # Flush final del buffer remanente
        flush_block()
        
        # Limpieza de bloques vacíos generados por múltiples saltos de línea continuos
        return [b for b in blocks if b.strip()]