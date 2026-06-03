import json
from typing import Protocol
from core.metrics.summary import TranslationAuditSummary

class MetricsExporter(Protocol):
    """SOTA: Interfaz limpia para desacoplar el destino de los reportes del dominio de traducción."""
    def export(self, summary: TranslationAuditSummary) -> None:
        ...

class ConsoleMetricsExporter:
    """Implementación limpia para entornos CLI e interactivos."""
    def export(self, summary: TranslationAuditSummary) -> None:
        print("\n" + "="*33 + "\n REPORTES DE EJECUCIÓN (FinOps) \n" + "="*33)
        print(f"Chunks Totales: {summary.total_chunks}")
        print(f"  - Red:        {summary.translated_chunks_network}")
        print(f"  - Caché:      {summary.translated_chunks_cache}")
        print(f"  - Passthrough:{summary.passthrough_chunks}")
        print(f"Eficiencia Caché: {summary.cache_hit_ratio * 100:.2f}%")
        print(f"Costo Real:       ${summary.total_cost_usd:.6f} USD")
        print(f"Ahorro por Caché: ${summary.cost_saved_by_cache_usd:.6f} USD")
        print(f"Latencia Total:   {summary.total_latency_ms / 1000:.2f} seg")
        print("="*33)

class JsonMetricsExporter:
    """Implementación para auditorías estructuradas o ingesta de logs secundarios."""
    def __init__(self, output_path: str):
        self.output_path = output_path

    def export(self, summary: TranslationAuditSummary) -> None:
        import dataclasses
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(summary), f, indent=2)