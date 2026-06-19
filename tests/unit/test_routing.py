import unittest
from core.ast.models import TranslationTaskType
from apps.llm_workers.routing import TranslationStrategyRouter, ProviderStrategy

class TestTranslationStrategyRouter(unittest.TestCase):
    """Certificación rigurosa de la Fase 14.00.3."""
    
    def setUp(self):
        self.router = TranslationStrategyRouter()

    def test_default_routing_translate(self):
        self.assertEqual(self.router.route(TranslationTaskType.TRANSLATE), ProviderStrategy.GROQ_HEAVY)

    def test_default_routing_partial(self):
        self.assertEqual(self.router.route(TranslationTaskType.PARTIAL), ProviderStrategy.GROQ_LIGHT)

    def test_default_routing_preserve(self):
        self.assertEqual(self.router.route(TranslationTaskType.PRESERVE), ProviderStrategy.BYPASS)

    def test_fail_fast_on_unknown_task_type(self):
        """Certifica la inmunidad del router ante inyección de tipos anómalos o expansiones no soportadas."""
        class FakeTaskType:
            pass
            
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_TASK_TYPE"):
            self.router.route(FakeTaskType()) #type: ignore

    def test_custom_routing_table_injection(self):
        """Certifica el soporte OCP (Open/Closed Principle) mediante inyección de dependencias."""
        custom_table = {TranslationTaskType.TRANSLATE: ProviderStrategy.GROQ_LIGHT}
        custom_router = TranslationStrategyRouter(routing_table=custom_table)
        
        self.assertEqual(custom_router.route(TranslationTaskType.TRANSLATE), ProviderStrategy.GROQ_LIGHT)
        
        # Debe fallar si la tabla custom está incompleta
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_TASK_TYPE"):
            custom_router.route(TranslationTaskType.PRESERVE)