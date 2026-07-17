class GroundTruthError(Exception):
    """Base exception for the ground_truth bounded context."""
    pass


class EmptyGroundTruthDraftError(GroundTruthError):
    """Raised when the extracted AST sequence is empty during the drafting campaign."""
    pass