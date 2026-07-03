import time
import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, Tuple, Type
from pydantic import BaseModel, ConfigDict, Field
from core.telemetry.ports import TelemetryPort
from core.execution.exceptions import DomainException
from core.telemetry.ports import StageExecutionRecord

logger = logging.getLogger(__name__)

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class ProviderDescriptor(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    version: str
    engine: str
    capabilities: Dict[str, bool] = Field(default_factory=dict)

class MergePolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    strategy: str = "BALANCED"  # STRICT | BALANCED | AGGRESSIVE
    vertical_threshold: float = 0.02
    horizontal_overlap: float = 0.5
    
    # Pesos configurables de la Función de Costo Inversa
    v_weight: float = 0.5
    h_weight: float = 0.4
    a_weight: float = 0.1
    
    # Umbrales verticales máximos específicos por tipo lógico
    type_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "CODE": 0.005,
        "DISPLAY_EQUATION": 0.012,
        "PARAGRAPH": 0.025,
        "TITLE": 0.004
    })

class ReadingOrderPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    spanning_width_threshold: float = 0.65
    spanning_footer_y_anchor: float = 0.70
    vertical_overlap_tolerance: float = 0.005
    inter_column_y_slack: float = 0.05

class PipelineConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    merge_policy: MergePolicy = Field(default_factory=MergePolicy)
    reading_policy: ReadingOrderPolicy = Field(default_factory=ReadingOrderPolicy)
    spatial_pivots: Tuple[float, ...] = (0.45,)
    coordinate_precision: int = 3
    custom_policies: Dict[str, Any] = Field(default_factory=dict)

class PipelineContext(BaseModel):
    model_config = ConfigDict(frozen=True)
    execution_id: str
    provider: ProviderDescriptor
    config: PipelineConfig
    page_number: int
    page_width: float
    page_height: float

class LayoutStage(ABC, Generic[TInput, TOutput]):
    # Contratos estáticos de tipo gobernados a nivel de clase
    INPUT_TYPE: Type[Any]
    OUTPUT_TYPE: Type[Any]

    def __init__(self, telemetry: TelemetryPort):
        self._telemetry = telemetry

    @property
    @abstractmethod
    def stage_name(self) -> str:
        pass

    @property
    @abstractmethod
    def supports_parallel_execution(self) -> bool:
        pass

    def process(self, data: TInput, context: PipelineContext, stage_index: int) -> TOutput:
        start_time = time.perf_counter()
        error_msg = None
        status = "SUCCESS"
        result = None
        
        try:
            result = self._execute(data, context)
            return result
        except DomainException as e:
            status = "FAILED"
            error_msg = str(e)
            raise
        finally:
            latency = time.perf_counter() - start_time
            out_type_name = type(result).__name__ if result is not None else "None"
            
            # Red de seguridad absoluta: Errores en infraestructura de telemetría no rompen el pipeline
            try:
                record = StageExecutionRecord(
                    execution_id=context.execution_id,
                    stage_name=self.stage_name,
                    stage_index=stage_index,
                    latency_sec=latency,
                    input_type=type(data).__name__,
                    output_type=out_type_name,
                    status=status,
                    error_message=error_msg,
                    metadata={"page_number": context.page_number}
                )
                self._telemetry.record_execution(record)
            except Exception as telemetry_error:
                logger.error(
                    f"[FALTA_CRITICA_TELEMETRIA] Fallo no controlado en {self.stage_name}: "
                    f"{str(telemetry_error)} | Excepción original preservada.",
                    exc_info=True
                )

    @abstractmethod
    def _execute(self, data: TInput, context: PipelineContext) -> TOutput:
        pass
