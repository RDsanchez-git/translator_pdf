import unittest
from core.metrics.pricing import PricingEngine

class TestPricingEngine(unittest.TestCase):
    """Certificación exclusiva del motor de tarificación y FinOps."""

    def test_flash_calculation(self):
        cost = PricingEngine.calculate_cost("gemini-2.5-flash", 100_000, 100_000)
        self.assertAlmostEqual(cost, 0.0375, places=6)

    def test_zero_usd_conditions(self):
        self.assertEqual(PricingEngine.calculate_cost("cache_hit:gemini-2.5-flash", 500, 500), 0.0)
        self.assertEqual(PricingEngine.calculate_cost("bypass_passthrough", 1000, 1000), 0.0)

    def test_invalid_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            PricingEngine.calculate_cost("invalid-model-v5", 10, 10)