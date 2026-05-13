from typing import Protocol, List
from core.execution.models import ValidationError

class BaseValidator(Protocol):
    @classmethod
    def validate(cls, text: str) -> List[ValidationError]:
        ...