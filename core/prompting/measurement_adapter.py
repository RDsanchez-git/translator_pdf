from core.prompting.models import PromptSchema
from core.prompting.canonicalizer import PromptCanonicalizer
from core.finops.measurement import MeasurableInference

class PromptMeasurementAdapter(MeasurableInference):
    """SOTA: Puente estructural entre Prompting y FinOps."""
    def __init__(self, schema: PromptSchema):
        self._schema = schema

    @property
    def logical_payload(self) -> str:
        return self._schema.payload.content

    @property
    def logical_context(self) -> str:
        return " > ".join(self._schema.context.breadcrumbs)

    @property
    def logical_instructions(self) -> str:
        # Se abstraen las intenciones e invariantes como bloque de reglas
        return f"{self._schema.intent.value} {self._schema.constraints.model_dump_json(exclude_none=True)}"

    @property
    def physical_network_payload(self) -> str:
        # Aquí se inyecta la representación que realmente viajará por la red
        return PromptCanonicalizer.to_canonical_json(self._schema)