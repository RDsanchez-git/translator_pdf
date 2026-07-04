from pydantic import BaseModel, Field
from enum import Enum
from typing import List
from core.benchmark.aggregation import calculate_decoupled_overall_score

class DefectCategory(str, Enum):
    OMISSION = "OMISSION"
    MATH_CORRUPTION = "MATH_CORRUPTION"
    UNTRANSLATED_TERM = "UNTRANSLATED_TERM"
    ANGLICISM = "ANGLICISM"
    GRAMMAR_FLUENCY = "GRAMMAR_FLUENCY"
    FORMAT_BREAK = "FORMAT_BREAK"

class ChunkEvaluationScore(BaseModel):
    judge_reasoning: str
    defects: List[DefectCategory] = Field(default_factory=list)
    terminology: float = Field(..., ge=0.0, le=5.0)
    fluency: float = Field(..., ge=0.0, le=5.0)
    structure: float = Field(..., ge=0.0, le=5.0)
    fidelity: float = Field(..., ge=0.0, le=5.0)

    @property
    def overall_score(self) -> float:
        return calculate_decoupled_overall_score(
            self.terminology, 
            self.fluency, 
            self.structure, 
            self.fidelity
        )