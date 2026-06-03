from typing import List
from core.ast.models import TranslatedUnit, ReconstructedDocument
from core.execution.exceptions import IncompleteDocumentError

class DocumentAssembler:
    """SOTA: Compilador determinista aislado de I/O con validación estricta de topología y tokens."""
    
    def __init__(self, separator: str = ""):
        self.separator = separator

    def _validate_sequence(self, units: List[TranslatedUnit]) -> None:
        """Auditoría O(N) lineal. Aísla duplicados antes de evaluar continuidad estructural."""
        if not units:
            return

        # Ajuste 2: Validación explícita de duplicados para no enmascarar telemetría
        indexes = [u.chunk_index for u in units]
        if len(set(indexes)) != len(indexes):
            raise ValueError("Duplicate chunk_index detected")

        expected_index = 1
        for unit in units:
            if unit.chunk_index != expected_index:
                raise IncompleteDocumentError(
                    document_id=unit.chunk_id, 
                    expected=expected_index, 
                    actual=unit.chunk_index
                )
            expected_index += 1

    def assemble(self, units: List[TranslatedUnit]) -> ReconstructedDocument:
        if not units:
            return ReconstructedDocument(
                content="", total_chunks=0, translated_chunks=0, 
                passthrough_chunks=0, total_input_tokens=0, total_output_tokens=0
            )

        # Garantía absoluta de ordenamiento previo a la validación
        sorted_units = sorted(units, key=lambda x: x.chunk_index)
        self._validate_sequence(sorted_units)

        total = len(sorted_units)
        translated = sum(1 for u in sorted_units if u.chunk_type == "translate")
        passthrough = total - translated
        
        # Ajuste 4: Agregación atómica de volumen de tokens consumidos
        total_input = sum(u.input_tokens for u in sorted_units)
        total_output = sum(u.output_tokens for u in sorted_units)

        content = self.separator.join([u.translated_payload for u in sorted_units])

        return ReconstructedDocument(
            content=content,
            total_chunks=total,
            translated_chunks=translated,
            passthrough_chunks=passthrough,
            total_input_tokens=total_input,
            total_output_tokens=total_output
        )