from dataclasses import dataclass, field
from typing import List, Set
from core.domain.document import DocumentLayout


@dataclass(frozen=True)
class LayoutValidationReport:
    """Reporte inmutable de auditoría de invariantes de maquetación."""
    is_valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


class DocumentLayoutValidator:
    """
    Auditor puro de dominio para verificar las invariantes físicas y de unicidad
    de un DocumentLayout antes de la construcción del AST V2.
    """

    def validate(self, layout: DocumentLayout) -> LayoutValidationReport:
        errors: List[str] = []
        seen_block_ids: Set[str] = set()
        seen_page_numbers: Set[int] = set()
        last_page_number: int = 0

        # 1. Invariante: El documento debe poseer al menos una página
        if not layout.pages:
            errors.append("El DocumentLayout no contiene páginas.")
            return LayoutValidationReport(is_valid=False, errors=tuple(errors))

        for page in layout.pages:
            # 2. Invariante: Índices de página válidos (>= 1)
            if page.page_number < 1:
                errors.append(
                    f"Página con índice inválido page_number={page.page_number}. Debe ser >= 1."
                )

            # 3. Invariante: Unicidad de números de página
            if page.page_number in seen_page_numbers:
                errors.append(f"Número de página duplicado detectado: {page.page_number}.")
            seen_page_numbers.add(page.page_number)

            # 4. Invariante: Monotonicidad en la secuencia de páginas
            # Se asume que DocumentLayout preserva el orden físico de las páginas.
            if page.page_number <= last_page_number and last_page_number > 0:
                errors.append(
                    f"Secuencia de páginas no monótona: la página {page.page_number} "
                    f"aparece después de la página {last_page_number}."
                )
            last_page_number = page.page_number

            # Auditoría de bloques
            for block in page.blocks:
                # 5. Invariante: Unicidad global de block_id
                raw_id = str(block.block_id.value)
                if raw_id in seen_block_ids:
                    errors.append(f"Colisión de BlockId duplicado detectada: '{raw_id}'.")
                seen_block_ids.add(raw_id)

                # 6. Invariante: Validez geométrica delegada al modelo del dominio
                if block.bbox is not None:
                    if block.bbox.x0 >= block.bbox.x1 or block.bbox.y0 >= block.bbox.y1:
                        errors.append(
                            f"Bloque '{raw_id}' posee BoundingBox geométricamente inválido o con dimensiones negativas."
                        )

        return LayoutValidationReport(
            is_valid=len(errors) == 0,
            errors=tuple(errors)
        )