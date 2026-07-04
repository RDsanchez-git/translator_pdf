import os

def calculate_decoupled_overall_score(terminology: float, fluency: float, structure: float, fidelity: float) -> float:
    """
    Calcula el score global aplicando la estrategia de dominancia semántica 
    configurada en las variables de entorno del sistema.
    """
    base = (0.35 * terminology) + (0.15 * fluency) + (0.25 * structure) + (0.25 * fidelity)
    strategy = os.getenv("EVAL_AGGREGATION_STRATEGY", "LINEAL").upper()

    if strategy == "LINEAL":
        return round(base, 2)

    if fidelity < 3.0:
        if strategy == "HARD_CEILING":
            return round(min(base, 2.99), 2)
            
        elif strategy == "FIDELITY_CEILING":
            return round(min(base, fidelity), 2)
            
        elif strategy == "PENALIZACION_EXPONENTIAL":
            factor_penalizacion = 0.60 * (fidelity / 3.0) ** 2
            return round(min(base * factor_penalizacion, 2.99), 2)

    return round(base, 2)