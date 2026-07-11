from core.ast.models import TranslationTaskType
from core.prompting.models import PromptIntent

class PromptIntentMapper:
    """SOTA: Traduce estados del pipeline a intenciones de inferencia ortogonales."""
    
    @staticmethod
    def map_from_task(task_type: TranslationTaskType) -> PromptIntent:
        if task_type == TranslationTaskType.PRESERVE:
            return PromptIntent.PRESERVE
        # PARTIAL y TRANSLATE comparten la intención semántica subyacente.
        return PromptIntent.TRANSLATE