import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple
from core.ast.models import TranslationUnit, FailureReason

# =====================================================================
# SOTA: METADATOS Y DESCRIPTORES (Trazabilidad)
# =====================================================================

@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    """SOTA: Identificación robusta a prueba de typos."""
    provider: str
    model: str
    version: str

@dataclass(frozen=True, slots=True)
class HardwareTelemetry:
    cpu_peak_percent: float
    rss_peak_mb: float
    rss_avg_mb: float
    sampling_interval_ms: int  # SOTA FIX: Reproducibilidad del muestreo del OS

@dataclass(frozen=True, slots=True)
class BenchmarkMetadata:
    """SOTA: Huella digital de la ejecución para auditoría CI/CD."""
    benchmark_version: str
    run_timestamp: float
    git_commit_sha: str
    chunking_strategy: str  # SOTA FIX: Documentación de asimetría
    percentile_method: str = "nearest_rank"

class DocumentComplexity(str, Enum):
    STANDARD_PROSE = "standard_prose"
    DENSE_MATH = "dense_math"         
    HEAVY_TABLES = "heavy_tables"     
    MIXED_HYBRID = "mixed_hybrid"     

class BenchmarkMode(str, Enum):
    """SOTA: Metodología experimental explícita."""
    CAPABILITY = "capability"  # Cada proveedor usa sus límites físicos reales
    EQUALIZED = "equalized"    # Se fuerza el mismo cuello de botella

@dataclass(frozen=True, slots=True)
class QuotaSnapshot:
    """SOTA: Fotografía inmutable del entorno de red."""
    rpm_limit: int
    tpm_limit: int
    concurrency: int

@dataclass(frozen=True, slots=True)
class QualityPolicy:
    """SOTA: Política de umbrales requeridos (Mantenida por compatibilidad de orquestación)."""
    structural_weight: float
    semantic_weight: float

@dataclass(frozen=True, slots=True)
class StructuralQualityMetrics:
    """SOTA FIX: Mide estructura y sintaxis, no semántica."""
    operational_reliability: float   
    token_structure_proxy: float     
    latex_syntax_score: float        # Calculado vía AST parser formal (pylatexenc)
    markdown_syntax_score: float     # Calculado vía GFM-compliant parser (markdown-it)

# =====================================================================
# SOTA: REGISTROS CRUDOS Y FORENSES
# =====================================================================

@dataclass(frozen=True, slots=True)
class TranslatedArtifact:
    """SOTA FIX: Encapsulamiento forense del resultado físico del LLM."""
    chunk_id: str
    translated_text: str
    text_sha256: str
    is_latex_valid: bool
    is_markdown_valid: bool

@dataclass(frozen=True, slots=True)
class ChunkBenchmarkRecord:
    chunk_id: str
    chunk_index: int
    complexity: DocumentComplexity
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    success: bool

    failure_reason: FailureReason | None  
    is_local_rejection: bool              
    
    quota_wait_seconds: float
    quota_attempts: int
    did_overflow: bool
    did_fallback: bool
    compression_ratio_used: float

    execution_stage: str       
    billing_model_used: str    
    tps_instantaneous: float   
    
    # SOTA FIX: Acoplamiento corregido y trazabilidad atómica
    artifact_metadata: TranslatedArtifact | None

    @property
    def tps_formula(self) -> str:
        return "(input_tokens + output_tokens) / (latency_ms / 1000.0)"
    
@dataclass(frozen=True, slots=True)
class BenchmarkDocument:
    id: str
    file_path: str
    file_sha256: str
    complexity: DocumentComplexity
    expected_pages: int
    input_tokens_actual: int  
    expected_chunks: int      

@dataclass(frozen=True, slots=True)
class BenchmarkDataset:
    dataset_id: str
    dataset_sha256: str
    documents: List[BenchmarkDocument]

# =====================================================================
# SOTA: MÉTRICAS AGREGADAS
# =====================================================================

@dataclass(frozen=True, slots=True)
class LatencyMetrics:
    p50_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float

@dataclass(frozen=True, slots=True)
class StatisticalMoments:
    """SOTA FIX: Métricas de dispersión avanzadas para análisis de colas."""
    median_ci_95: Tuple[float, float]
    p95_ci_95: Tuple[float, float]

@dataclass(frozen=True, slots=True)
class ProviderBenchmarkMetrics:
    descriptor: ProviderDescriptor
    benchmark_mode: BenchmarkMode 
    quota_snapshot: QuotaSnapshot 
    
    total_chunks: int
    successful_chunks: int
    
    total_input_tokens: int
    total_output_tokens: int
    cumulative_chunk_latency_seconds: float 
    document_completion_seconds: float      
    
    latency: LatencyMetrics
    latency_moments: StatisticalMoments  # SOTA FIX: Bootstrap robusto inyectado
    
    total_cost_usd: float
    total_documents: int
    p95_cost_per_chunk_usd: float
    p99_cost_per_chunk_usd: float
    
    quality: StructuralQualityMetrics  # SOTA FIX: Referencia a la nueva taxonomía

    context_overflow_ratio: float
    provider_switch_ratio: float
    
    average_compression_ratio: float
    p95_compression_ratio: float
    p99_compression_ratio: float
    max_compression_ratio: float
    
    total_quota_wait_seconds: float
    average_quota_attempts: float

    hardware_telemetry: HardwareTelemetry
    p50_tps: float
    p95_tps: float
    p99_tps: float

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def reliability_score(self) -> float:
        return round(self.successful_chunks / self.total_chunks, 4) if self.total_chunks > 0 else 0.0

    @property
    def input_tps(self) -> float:
        return round(self.total_input_tokens / self.document_completion_seconds, 2) if self.document_completion_seconds > 0 else 0.0

    @property
    def output_tps(self) -> float:
        return round(self.total_output_tokens / self.document_completion_seconds, 2) if self.document_completion_seconds > 0 else 0.0

    @property
    def total_tps(self) -> float:
        return round(self.total_tokens / self.document_completion_seconds, 2) if self.document_completion_seconds > 0 else 0.0

    @property
    def cost_per_1m_tokens_usd(self) -> float:
        return round((self.total_cost_usd / self.total_tokens) * 1_000_000, 6) if self.total_tokens > 0 else 0.0
        
    @property
    def cost_per_1k_tokens_usd(self) -> float:
        return round((self.total_cost_usd / self.total_tokens) * 1_000, 6) if self.total_tokens > 0 else 0.0

# =====================================================================
# SOTA: FACTORY DE AGREGACIÓN
# =====================================================================

class MetricAggregator:
    @staticmethod
    def _percentile(data: List[float], p: float) -> float:
        if not data:
            return 0.0
        s_data = sorted(data)
        idx = math.ceil(p * len(s_data)) - 1
        return s_data[max(0, idx)]

    @staticmethod
    def aggregate(
        descriptor: ProviderDescriptor,
        records: List[ChunkBenchmarkRecord],
        document_completion_seconds: float,
        total_documents: int,
        quality_assessment: StructuralQualityMetrics,
        benchmark_mode: BenchmarkMode,          
        quota_snapshot: QuotaSnapshot,          
        hardware_telemetry: HardwareTelemetry,
        latency_moments: StatisticalMoments     # SOTA FIX: Se inyectan los momentos pre-calculados
    ) -> ProviderBenchmarkMetrics:
        
        total_chunks = len(records)
        successful_chunks = sum(1 for r in records if r.success)
        
        total_in_tokens = sum(r.input_tokens for r in records)
        total_out_tokens = sum(r.output_tokens for r in records)
        total_cost = sum(r.cost_usd for r in records)
        
        latencies = [r.latency_ms for r in records]
        costs = [r.cost_usd for r in records]
        comp_ratios = [r.compression_ratio_used for r in records]
        tps_values = [r.tps_instantaneous for r in records] 
        
        latency_dto = LatencyMetrics(
            p50_ms=MetricAggregator._percentile(latencies, 0.50),
            p95_ms=MetricAggregator._percentile(latencies, 0.95),
            p99_ms=MetricAggregator._percentile(latencies, 0.99),
            max_ms=max(latencies) if latencies else 0.0
        )
        
        overflows = sum(1 for r in records if r.did_overflow)
        fallbacks = sum(1 for r in records if r.did_fallback)
        quota_waits = sum(r.quota_wait_seconds for r in records)
        quota_attempts = sum(r.quota_attempts for r in records)
        
        return ProviderBenchmarkMetrics(
            descriptor=descriptor,
            benchmark_mode=benchmark_mode,
            quota_snapshot=quota_snapshot,
            total_chunks=total_chunks,
            successful_chunks=successful_chunks,
            total_input_tokens=total_in_tokens,
            total_output_tokens=total_out_tokens,
            cumulative_chunk_latency_seconds=sum(latencies) / 1000.0,
            document_completion_seconds=document_completion_seconds,
            latency=latency_dto,
            latency_moments=latency_moments,
            total_cost_usd=total_cost,
            total_documents=total_documents,
            p95_cost_per_chunk_usd=MetricAggregator._percentile(costs, 0.95),
            p99_cost_per_chunk_usd=MetricAggregator._percentile(costs, 0.99),
            quality=quality_assessment,
            context_overflow_ratio=round(overflows / total_chunks, 4) if total_chunks > 0 else 0.0,
            provider_switch_ratio=round(fallbacks / total_chunks, 4) if total_chunks > 0 else 0.0,
            average_compression_ratio=round(sum(comp_ratios) / len(comp_ratios), 4) if comp_ratios else 1.0,
            p95_compression_ratio=MetricAggregator._percentile(comp_ratios, 0.95),
            p99_compression_ratio=MetricAggregator._percentile(comp_ratios, 0.99),
            max_compression_ratio=max(comp_ratios) if comp_ratios else 1.0,
            total_quota_wait_seconds=round(quota_waits, 3),
            average_quota_attempts=round(quota_attempts / total_chunks, 2) if total_chunks > 0 else 1.0,
            hardware_telemetry=hardware_telemetry,
            p50_tps=MetricAggregator._percentile(tps_values, 0.50),
            p95_tps=MetricAggregator._percentile(tps_values, 0.95),
            p99_tps=MetricAggregator._percentile(tps_values, 0.99)
        )

# =====================================================================
# SOTA: REPORTING
# =====================================================================

@dataclass(frozen=True, slots=True)
class BenchmarkRunReport:
    metadata: BenchmarkMetadata
    dataset: BenchmarkDataset
    quality_policy: QualityPolicy 
    
    baseline_metrics: ProviderBenchmarkMetrics
    challenger_metrics: ProviderBenchmarkMetrics
    raw_baseline_records: List[ChunkBenchmarkRecord]     
    raw_challenger_records: List[ChunkBenchmarkRecord]   
    
    @property
    def total_tps_delta_percentage(self) -> float:
        base = self.baseline_metrics.total_tps
        chall = self.challenger_metrics.total_tps
        return round(((chall - base) / base) * 100, 2) if base > 0 else 0.0

    @property
    def cost_delta_percentage(self) -> float:
        base = self.baseline_metrics.cost_per_1m_tokens_usd
        chall = self.challenger_metrics.cost_per_1m_tokens_usd
        return round(((chall - base) / base) * 100, 2) if base > 0 else 0.0

@dataclass(frozen=True, slots=True)
class PreparedBenchmarkDataset:
    """SOTA: Fixture inmutable pre-computado. Aísla el benchmark de la latencia I/O."""
    manifest: BenchmarkDataset
    prepared_units: List[TranslationUnit]
    unit_complexity_map: Dict[str, DocumentComplexity] # O(1) lookup para el ChunkBenchmarkRecord