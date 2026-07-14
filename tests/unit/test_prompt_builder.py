import unittest
from typing import Any
from core.ast.models import TranslationUnit, TranslationTaskType, FastWordEstimator
from core.context.context_resolver import ResolvedContext
from apps.llm_workers.prompt_builder import PromptBuilder
from core.finops.measurement import InferenceMeasurementService
from core.validation.budget import PromptBudgetCalculator, StandardCompressionPolicy

class TestPromptBuilder(unittest.TestCase):
    """Certificación rigurosa de la Fase 16.10."""
    
    def setUp(self):
        self.estimator = FastWordEstimator()
        
        # SOTA FIX: Inyección reglamentaria del ecosistema FinOps y políticas de compresión de la Fase 16
        measurement_service = InferenceMeasurementService(estimator=self.estimator)
        budget_calculator = PromptBudgetCalculator()
        compression_policy = StandardCompressionPolicy()
        
        self.builder = PromptBuilder(
            model_name="llama-3-70b", 
            prompt_version="v2.0", 
            measurement_service=measurement_service,
            budget_calculator=budget_calculator,
            compression_policy=compression_policy
        )
        
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
        res = self.builder.build(self.unit, self.context)
        
        # SOTA FIX: Extracción tolerante y Type Narrowing para saltar las restricciones de la Unión del PromptBuildResult
        envelope: Any = getattr(res, "envelope", res)
        
        self.assertEqual(envelope.chunk_id, "chk_001")
        self.assertEqual(envelope.model_name, "llama-3-70b")
        
        self.assertTrue(envelope.prompt_id.startswith("prm_"))
        self.assertEqual(envelope.prompt_id[4:], envelope.prompt_hash[:16])
        
        self.assertGreater(envelope.estimated_tokens, self.unit.estimated_tokens)

    def test_deterministic_prompt_hash(self):
        res_1 = self.builder.build(self.unit, self.context)
        res_2 = self.builder.build(self.unit, self.context)
        
        env_1: Any = getattr(res_1, "envelope", res_1)
        env_2: Any = getattr(res_2, "envelope", res_2)
        
        self.assertEqual(env_1.prompt_hash, env_2.prompt_hash)
        
    def test_hash_collision_avoidance(self):
        context_alt = ResolvedContext(context_id="CTX_2", breadcrumbs=("Chapter 2", "Conclusion"))
        
        res_1 = self.builder.build(self.unit, self.context)
        res_2 = self.builder.build(self.unit, context_alt)
        
        env_1: Any = getattr(res_1, "envelope", res_1)
        env_2: Any = getattr(res_2, "envelope", res_2)
        
        self.assertNotEqual(env_1.prompt_hash, env_2.prompt_hash)

    def test_prompt_hash_stability(self):
        """Certifica la inmunidad del hash contra inyecciones de entropía residual en 100 ciclos."""
        res_base = self.builder.build(self.unit, self.context)
        baseline_hash = getattr(getattr(res_base, "envelope", res_base), "prompt_hash", "")
        
        for _ in range(100):
            res_current = self.builder.build(self.unit, self.context)
            current_hash = getattr(getattr(res_current, "envelope", res_current), "prompt_hash", "")
            self.assertEqual(
                current_hash, 
                baseline_hash, 
                "Fallo crítico de determinismo: Mutación del hash en ciclo cerrado detectada."
            )

    def test_hash_mutation_on_model_or_version_change(self):
        """Certifica que un cambio de modelo o versión invalida el hash del prompt."""
        m_service = InferenceMeasurementService(estimator=self.estimator)
        b_calc = PromptBudgetCalculator()
        c_policy = StandardCompressionPolicy()
        
        builder_alt_model = PromptBuilder(model_name="gemini-2.5-pro", prompt_version="v2.0", measurement_service=m_service, budget_calculator=b_calc, compression_policy=c_policy)
        builder_alt_version = PromptBuilder(model_name="llama-3-70b", prompt_version="v2.1", measurement_service=m_service, budget_calculator=b_calc, compression_policy=c_policy)
        
        res_base = self.builder.build(self.unit, self.context)
        res_alt_model = builder_alt_model.build(self.unit, self.context)
        res_alt_version = builder_alt_version.build(self.unit, self.context)
        
        env_base: Any = getattr(res_base, "envelope", res_base)
        env_alt_model: Any = getattr(res_alt_model, "envelope", res_alt_model)
        env_alt_version: Any = getattr(res_alt_version, "envelope", res_alt_version)
        
        self.assertNotEqual(env_base.prompt_hash, env_alt_model.prompt_hash)
        self.assertNotEqual(env_base.prompt_hash, env_alt_version.prompt_hash)