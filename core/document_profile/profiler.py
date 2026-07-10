from core.document_profile.models import ProfileInput, ProfilingResult, InferredDocumentProfile, ProfileDiagnostics, LayoutDetection, TypeDetection
from core.document_profile.protocols import LayoutDetector, DocumentTypeDetector
from core.document_profile.ports import ProfileSamplingPolicy

class HeuristicDocumentProfiler:
    __slots__ = ("_layout_detector", "_type_detector", "_sampler")

    def __init__(
        self, 
        layout_detector: LayoutDetector, 
        type_detector: DocumentTypeDetector,
        sampler: ProfileSamplingPolicy  # <--- CORRECCIÓN SOTA: Parámetro exigido por Hito 3B
    ):
        self._layout_detector = layout_detector
        self._type_detector = type_detector
        self._sampler = sampler

    def _build_result(self, layout: LayoutDetection, doc_type: TypeDetection) -> ProfilingResult:
        profile = InferredDocumentProfile(
            layout=layout.layout,
            document_type=doc_type.document_type
        )
        diagnostics = ProfileDiagnostics(
            layout_confidence=layout.confidence,
            type_confidence=doc_type.confidence
        )
        return ProfilingResult(profile=profile, diagnostics=diagnostics)

    def profile(self, input_data: ProfileInput) -> ProfilingResult:
        # Bounded Workload
        sampled_nodes = self._sampler.sample(input_data.nodes)
        sampled_input = ProfileInput(nodes=sampled_nodes)

        layout_detection = self._layout_detector.detect(sampled_input)
        type_detection = self._type_detector.detect(sampled_input, layout_detection)

        return self._build_result(layout_detection, type_detection)