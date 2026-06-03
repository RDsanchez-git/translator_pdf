class PricingEngine:
    """SOTA: Motor estático para cálculo determinista de costos. Aislado de proveedores I/O."""
    
    RATES_USD_PER_1M = {
        "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-mock": {"input": 0.075, "output": 0.30}
    }

    @classmethod
    def calculate_cost(cls, model_name: str, input_tokens: int, output_tokens: int) -> float:
        if model_name.startswith("cache_hit:") or model_name == "bypass_passthrough":
            return 0.0

        rates = cls.RATES_USD_PER_1M.get(model_name)
        if not rates:
            raise ValueError(f"Tarifario no encontrado para el modelo: {model_name}")
            
        cost_input = (input_tokens / 1_000_000) * rates["input"]
        cost_output = (output_tokens / 1_000_000) * rates["output"]
        
        return cost_input + cost_output