import unittest
from core.ast.models import TranslationUnit, TranslationTaskType, FastWordEstimator
from core.context.context_resolver import ResolvedContext
from apps.llm_workers.prompt_builder import PromptBuilder, PromptEnvelope

class TestPromptBuilder(unittest.TestCase):
    """Certificación rigurosa de la Fase 14.00.2."""
    
    def setUp(self):
        self.estimator = FastWordEstimator()
        self.builder = PromptBuilder(model_name="llama-3-70b", prompt_version="v2.0", estimator=self.estimator)
        self.unit = TranslationUnit(
            chunk_index=1,
            chunk_id="chk_001",
            chunk_fingerprint="fp_001",
            chunk_type=TranslationTaskType.TRANSLATE,
            source_sequence_range=(1, 1),
            node_count=1,
            context_id="CTX_1",
            context_depth=2,
            target_payload="Machine learning models.",
            estimated_tokens=4,
            payload_sha256="hash123"
        )
        self.context = ResolvedContext(context_id="CTX_1", breadcrumbs=("Chapter 1", "Introduction"))

    def test_envelope_structure_and_types(self):
        envelope = self.builder.build(self.unit, self.context)
        self.assertIsInstance(envelope, PromptEnvelope)
        self.assertEqual(envelope.chunk_id, "chk_001")
        self.assertEqual(envelope.model_name, "llama-3-70b")
        
        # Validación de la nueva estrategia de prompt_id vinculada al hash
        self.assertTrue(envelope.prompt_id.startswith("prm_"))
        self.assertEqual(envelope.prompt_id[4:], envelope.prompt_hash[:16])
        
        # Validación de sobrecarga de tokens calculada (debe ser > 4)
        self.assertGreater(envelope.estimated_tokens, self.unit.estimated_tokens)

    def test_deterministic_prompt_hash(self):
        env_1 = self.builder.build(self.unit, self.context)
        env_2 = self.builder.build(self.unit, self.context)
        self.assertEqual(env_1.prompt_hash, env_2.prompt_hash)
        
    def test_hash_collision_avoidance(self):
        context_alt = ResolvedContext(context_id="CTX_2", breadcrumbs=("Chapter 2", "Conclusion"))
        env_1 = self.builder.build(self.unit, self.context)
        env_2 = self.builder.build(self.unit, context_alt)
        self.assertNotEqual(env_1.prompt_hash, env_2.prompt_hash)

    def test_prompt_hash_stability(self):
        """Certifica la inmunidad del hash contra inyecciones de entropía residual en 100 ciclos."""
        baseline_hash = self.builder.build(self.unit, self.context).prompt_hash
        for _ in range(100):
            current_envelope = self.builder.build(self.unit, self.context)
            self.assertEqual(
                current_envelope.prompt_hash, 
                baseline_hash, 
                "Fallo crítico de determinismo: Mutación del hash en ciclo cerrado detectada."
            )

    def test_hash_mutation_on_model_or_version_change(self):
        """Certifica que un cambio de modelo o versión invalida el hash del prompt."""
        builder_alt_model = PromptBuilder(model_name="gemini-2.5-pro", prompt_version="v2.0", estimator=self.estimator)
        builder_alt_version = PromptBuilder(model_name="llama-3-70b", prompt_version="v2.1", estimator=self.estimator)
        
        env_base = self.builder.build(self.unit, self.context)
        env_alt_model = builder_alt_model.build(self.unit, self.context)
        env_alt_version = builder_alt_version.build(self.unit, self.context)
        
        self.assertNotEqual(env_base.prompt_hash, env_alt_model.prompt_hash)
        self.assertNotEqual(env_base.prompt_hash, env_alt_version.prompt_hash)