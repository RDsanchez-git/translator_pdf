from typing import Protocol
from core.document_profile.models import (
    ProfileInput, 
    LayoutDetection, 
    TypeDetection, 
    ProfilingResult
)

class LayoutDetector(Protocol):
    def detect(self, input_data: ProfileInput) -> LayoutDetection:
        ...

class DocumentTypeDetector(Protocol):
    def detect(self, input_data: ProfileInput, layout: LayoutDetection) -> TypeDetection:
        ...

class DocumentProfiler(Protocol):
    def profile(self, input_data: ProfileInput) -> ProfilingResult:
        ...