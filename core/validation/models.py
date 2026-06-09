# core/validation/models.py

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class Severity(Enum):
    HARD_FAIL = 1
    WARNING = 2
    INFO = 3


class Scope(Enum):
    CHUNK = 1
    DOCUMENT = 2


@dataclass(frozen=True)
class ValidationContext:
    source_text: str
    target_text: str
    scope: Scope

    chunk_index: Optional[int] = None
    chunk_type: Optional[str] = None
    payload_sha256: Optional[str] = None

    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    invariant_id: str
    passed: bool
    severity: Severity
    message: str
    context: ValidationContext
    invariant_family: Optional[str] = None