# core/prompting/models.py
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import List

class PromptIntent(str, Enum):
    TRANSLATE = "translate"
    PRESERVE = "preserve"
    EVALUATE = "evaluate"

class StructuralConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)
    preserve_paragraphs: bool = True
    preserve_math_environments: bool = True
    preserve_latex_macros: bool = True
    preserve_tables: bool = True

class TranslationConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)
    forbid_omission: bool = True
    forbid_hallucination: bool = True
    forbid_summarization: bool = True
    preserve_technical_terminology: bool = True

class PresentationConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)
    escape_latex_in_text: bool = False
    enforce_line_breaks: bool = True

class PromptConstraints(BaseModel):
    model_config = ConfigDict(frozen=True)
    structural: StructuralConstraints = Field(default_factory=StructuralConstraints)
    translation: TranslationConstraints = Field(default_factory=TranslationConstraints)
    presentation: PresentationConstraints = Field(default_factory=PresentationConstraints)

class PromptContext(BaseModel):
    model_config = ConfigDict(frozen=True)
    chunk_index: int
    depth: int
    breadcrumbs: List[str] = Field(default_factory=list)
    is_pruned: bool = False

class PromptPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: str

class PromptSchema(BaseModel):
    model_config = ConfigDict(frozen=True)
    intent: PromptIntent
    context: PromptContext
    constraints: PromptConstraints
    payload: PromptPayload


