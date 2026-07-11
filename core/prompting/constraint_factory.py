from core.ast.models import TranslationTaskType
from core.prompting.models import (
    PromptConstraints, StructuralConstraints, TranslationConstraints, PresentationConstraints
)

class ConstraintFactory:
    """SOTA: Composición dinámica de invariantes de dominio."""
    
    @staticmethod
    def create_for_task(task_type: TranslationTaskType) -> PromptConstraints:
        structural = StructuralConstraints()
        translation = TranslationConstraints()
        presentation = PresentationConstraints()

        if task_type == TranslationTaskType.TRANSLATE:
            presentation = PresentationConstraints(escape_latex_in_text=True, enforce_line_breaks=True)
        elif task_type == TranslationTaskType.PARTIAL:
            structural = StructuralConstraints(preserve_tables=True, preserve_math_environments=True)
            presentation = PresentationConstraints(escape_latex_in_text=False)
        elif task_type == TranslationTaskType.PRESERVE:
            translation = TranslationConstraints(
                forbid_omission=True, forbid_hallucination=True, forbid_summarization=True
            )

        return PromptConstraints(
            structural=structural, 
            translation=translation, 
            presentation=presentation
        )