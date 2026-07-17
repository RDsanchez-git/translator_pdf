from enum import Enum

class ExtractionChallengeTrait(str, Enum):
    NATIVE_PDF = "native_pdf"
    SCANNED_NOISE = "scanned_noise"
    MULTI_COLUMN = "multi_column"
    HEAVY_MATH = "heavy_math"
    NESTED_TABLES = "nested_tables"
    FLOATING_FIGURES = "floating_figures"
    BILINGUAL_MIX = "bilingual_mix"