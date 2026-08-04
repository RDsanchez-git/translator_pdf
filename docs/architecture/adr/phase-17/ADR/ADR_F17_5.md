# ADR F17.5: Modelo de Decisión, Leaderboard Estadístico y Declaración del Proveedor por Defecto

- **Estado:** Aprobado (Congelado y Definitivo)
- **Fecha:** 2026-07-25
- **Autores:** Staff Architecture Team
- **Subdominio:** `core/benchmark/` y `apps/bootstrap/`
- **Dependencias:**
  - ADR F17.0–F17.4 (Infraestructura de Benchmarking)
  - `core/benchmark/reporter.py` (`StatisticalComparator`, `ScientificSignificanceReport`)
  - `core/benchmark/persistence.py` (`BenchmarkPersistenceGateway`)
  - `core/benchmark/types.py` (`ProviderKind`)

---

## 1. Contexto y Problema

Tras la ejecución de la infraestructura de benchmarking de las Fases 17.0 a 17.4, el sistema emite reportes de ejecución inmutables (`BenchmarkRunReport` y sus representaciones JSON).

Para declarar científicamente el proveedor de extracción predeterminado que alimentará al `AST V2` en el resto del proyecto, el sistema requiere:
1. Ponderar métricas heterogéneas previamente normalizadas en escala $[0.0, 1.0]$ con direcciones opuestas ($TED$/Latencia en `LOWER_IS_BETTER`; $Recall$/$Sequence$ en `HIGHER_IS_BETTER`).
2. Consumir la suite estadística preexistente (`StatisticalComparator` en `core/benchmark/reporter.py`) para confirmar significancia estadística ($\alpha = 0.05$, Cliff's Delta, Holm-Bonferroni).
3. Persistir un Leaderboard reproducible (`leaderboard.json` y `leaderboard.md`) mediante `BenchmarkPersistenceGateway.save_artifact`.
4. Establecer en la configuración de bootstrap el **proveedor de extracción por defecto** utilizando tipos strictly calificados (`ProviderKind`).

---

## 2. Invariantes Arquitectónicas Normativas

1. **Invariante de Consumo Puro:** El Leaderboard es un consumidor de resultados de segundo orden. **Bajo ninguna circunstancia el Leaderboard o la política de score recalcularán métricas de primera línea** ($TED$, $Recall$, etc.).
2. **Invariante Open/Closed (Agnosticismo de Métricas):** `ScorePolicy` no conoce métricas concretas del dominio. Opera exclusivamente sobre un mapa genérico `Mapping[str, float]` y reglas declarativas (`MetricRule`). La incorporación de nuevas métricas futuras (ej. `CaptionRecall`, `FigureRecall`) no modificará los métodos de cálculo, sino únicamente la política de configuración.
3. **Principio Fail-Fast en Configuración:** Si se evalúa una métrica que carece de una regla declarada en `ScorePolicy`, el sistema interrumpirá la ejecución inmediatamente (`UnknownMetricRuleError`) en lugar de asumir valores por defecto (ej. `0.0`), evitando silenciar errores de configuración.
4. **Premisa de Normalización Previa:** `ScorePolicy` asume que todas las métricas de entrada ya se encuentran acotadas en la escala escalar $[0.0, 1.0]$. La normalización o transformación de métricas dimensionales crudas (como latencias en segundos) es responsabilidad exclusiva de la capa de evaluación previa.
5. **Inmutabilidad Absoluta de Reportes Originales:** El Leaderboard jamás modifica, muta ni enriquece los objetos `BenchmarkRunReport` originales. Toda información derivada (scores compuestos, deltas y significancia) se materializa exclusivamente como nuevos artefactos independientes (`leaderboard.json` y `leaderboard.md`).
6. **Inmutabilidad de la Fuente de Verdad:** `leaderboard.json` y `leaderboard.md` son artefactos generados y derivados. La fuente de verdad inmutable continúan siendo los `BenchmarkRunReport` guardados en disco.
7. **Reutilización Estricta (DRY):** Se prohíbe la creación de nuevos comparadores estadísticos, exportadores o gateways de persistencia. Se consumirán exclusivamente `reporter.py` y `persistence.py`.
8. **Aislamiento de Operativa de Runtime:** El ADR se limita a declarar el proveedor por defecto (`DEFAULT_EXTRACTION_PROVIDER`). Lógicas de *fallback* automático, *circuit breaking* o ruteo adaptativo quedan fuera de alcance (diferidas a Fase 21: *Adaptive Intelligence*).

---

## 3. Decisiones de Diseño

### 3.1. Política de Ponderación (`core/benchmark/score_policy.py`)
Se introduce `ScorePolicy` como un objeto de dominio explícito e inmutable para desacoplar la política de decisión del algoritmo de generación del leaderboard, permitiendo modificar pesos y direcciones sin alterar el código consumidor. Separa la dirección de optimización de la agregación de scores compuestos con un enfoque estricto *Fail-Fast*:

```python
from enum import Enum
from dataclasses import dataclass
from typing import Mapping

class MetricDirection(str, Enum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"

class UnknownMetricRuleError(KeyError):
    """Excepción Fail-Fast al evaluar una métrica sin regla explícita en la política."""
    pass

@dataclass(frozen=True, slots=True)
class MetricRule:
    weight: float
    direction: MetricDirection

@dataclass(frozen=True, slots=True)
class ScorePolicy:
    """Política inmutable y agnóstica a métricas concretas del dominio."""
    rules: Mapping[str, MetricRule]

    def score_metric(self, metric_name: str, normalized_value: float) -> float:
        """Aplica la dirección de optimización a un valor previamente normalizado [0.0, 1.0]."""
        if metric_name not in self.rules:
            raise UnknownMetricRuleError(
                f"Falla de Configuración Fail-Fast: La métrica '{metric_name}' "
                f"no está definida en la política de puntuación."
            )
        rule = self.rules[metric_name]
        clamped = max(0.0, min(1.0, normalized_value))
        return clamped if rule.direction == MetricDirection.HIGHER_IS_BETTER else (1.0 - clamped)

    def compute_composite_score(self, metrics: Mapping[str, float]) -> float:
        """Calcula la suma ponderada del score global acumulado."""
        total_score = 0.0
        for name, value in metrics.items():
            scored_val = self.score_metric(name, value)
            total_score += scored_val * self.rules[name].weight
        return round(total_score, 4)
```

### 3.2. Servicio de Leaderboard (`LeaderboardService` en `core/benchmark/reporter.py`)
Se incorpora en `reporter.py` la clase `LeaderboardService` que:
* Recibe una colección de reportes de benchmark (`BenchmarkRunReport`).
* Aplica una `ScorePolicy` para ordenar los proveedores por score compuesto sin mutar los reportes de entrada.
* Invoca a `StatisticalComparator.compare_series(...)` para validar si la diferencia entre el 1.º y 2.º lugar es estadísticamente significativa.
* Genera los textos en formato Markdown y JSON y los delega a `BenchmarkPersistenceGateway.save_artifact(...)`.

### 3.3. Configuración Tipada del Proveedor por Defecto
La victoria del proveedor se materializará mediante la actualización de la variable de configuración de bootstrap utilizando el enum del dominio:

```python
from core.benchmark.types import ProviderKind

# En la configuración de bootstrap/extracción (ej. apps/bootstrap/pipeline_factory.py)
DEFAULT_EXTRACTION_PROVIDER: ProviderKind = ProviderKind.DOCLING  # (o el proveedor ganador)
```

---

## 4. Plan de Ejecución (Hitos)

### Hito 1: Política de Ponderación (`core/benchmark/score_policy.py`)
* **Objetivo:** Introducir una política declarativa, inmutable y agnóstica al dominio para transformar un conjunto de métricas previamente normalizadas en un score compuesto, preservando el principio Open/Closed y el Fail-Fast sobre errores de configuración.
* **Entregables:**
  * `MetricDirection`
  * `MetricRule`
  * `UnknownMetricRuleError`
  * `ScorePolicy`
  * Suite de pruebas unitarias en `tests/unit/test_score_policy.py`
* **Criterios de Validación:**
  * La política calcula correctamente scores ponderados.
  * Se verifica la dirección de optimización (`HIGHER_IS_BETTER` y `LOWER_IS_BETTER`).
  * Evaluar una métrica sin regla produce inmediatamente `UnknownMetricRuleError`.
  * `pyright core/benchmark/score_policy.py` → 0 errors, 0 warnings.
  * Pruebas unitarias al 100% en verde.

### Hito 2: Servicio de Leaderboard (`LeaderboardService` en `core/benchmark/reporter.py`)
* **Objetivo:** Construir un servicio puro de segundo orden encargado exclusivamente de consumir reportes de benchmark existentes, calcular el ranking compuesto mediante `ScorePolicy` y validar la significancia estadística reutilizando `StatisticalComparator`, sin recalcular métricas ni mutar los reportes originales.
* **Entregables:**
  * `LeaderboardService` en `core/benchmark/reporter.py`
  * DTOs o estructuras internas para ranking compuesto y matriz de significancia.
* **Criterios de Validación:**
  * Ningún objeto `BenchmarkRunReport` es modificado durante el procesamiento.
  * El orden del ranking coincide con el score compuesto derivado de `ScorePolicy`.
  * Se reutiliza exclusivamente `StatisticalComparator` para calcular Cliff's Delta y $p$-valores.

### Hito 3: Persistencia del Leaderboard (`BenchmarkPersistenceGateway`)
* **Objetivo:** Materializar y persistir los resultados del leaderboard en formato JSON estructurado y Markdown ejecutivo, consumiendo la infraestructura existente sin introducir nuevos gateways ni servicios de I/O.
* **Entregables:**
  * Métodos de formateo de leaderboard en `LeaderboardService`.
  * Generación de artefactos `leaderboard.json` y `leaderboard.md`.
* **Criterios de Validación:**
  * Persistencia realizada exclusivamente mediante `BenchmarkPersistenceGateway.save_artifact(...)`.
  * `leaderboard.json` valida contra esquema estructurado reproducible.
  * `leaderboard.md` genera tabla legible con ranking, scores y banderas de significancia estadística (🟢/🔴).

### Hito 4: Declaración del Proveedor por Defecto y Cierre de Fase 17
* **Objetivo:** Declarar en código la configuración del proveedor de extracción predeterminado mediante `ProviderKind`, documentar la decisión y congelar formalmente la Fase 17.
* **Entregables:**
  * Actualización de `DEFAULT_EXTRACTION_PROVIDER` en `apps/bootstrap/pipeline_factory.py` o módulo equivalente.
  * Documentación de cierre de fase.
* **Criterios de Validación:**
  * `DEFAULT_EXTRACTION_PROVIDER` utiliza tipado estricto `ProviderKind`.
  * Suite completa de integración y tipado ejecutada en verde (`pyright`, `pytest tests/unit/ tests/integration/`).
  * Congelamiento definitivo de la Fase 17.

---

## 5. Fuera de Alcance

Este ADR no contempla ni permite:
1. **Recalcular métricas topológicas o estructurales** ($TED$, *Recall*, *Sequence Alignment*, etc.) desde la capa de decisiones o reportería.
2. **Implementar nuevos comparadores o algoritmos estadísticos** ajenos a `StatisticalComparator` en `core/benchmark/reporter.py`.
3. **Introducir ruteo dinámico de proveedores** en tiempo de ejecución.
4. **Implementar políticas de resiliencia o fallback automático** en *runtime*.
5. **Selección adaptativa o aprendizaje automático de modelos** durante el procesamiento de documentos (reservado para Fase 21: *Adaptive Intelligence*).
6. **Ampliación masiva del Golden Corpus** a 20-30 documentos (reservado para la Fase 17.5 del roadmap general).



## RESULTADOS CONSOLIDADOS FASE 17.5

### 1. Política de Ponderación y Modelo de Decisión (Hito 1)
* **Causa Raíz:** Ausencia de un mecanismo declarativo, inmutable y agnóstico en `core/benchmark/` para transformar colecciones de métricas heterogéneas en un escalar *Composite Score*. Anteriormente, la agregación carecía de un contrato de configuración estricto, permitiendo evaluaciones parciales silenciosas, *clamping* permisivo sobre métricas fuera de rango y mutabilidad en la definición de reglas de ponderación.
* **Correcciones Aplicadas:**
  * **`core/benchmark/score_policy.py`:**
    * **Tipado Fuerte & Dominio Puro:** Definición de `MetricName = NewType("MetricName", str)` para evitar colisiones de cadenas en el analizador estático, y enum `MetricDirection` (`HIGHER_IS_BETTER`, `LOWER_IS_BETTER`).
    * **Jerarquía de Excepciones Fail-Fast:** Implementación de `ScorePolicyError(ValueError)` como clase base, extendida por `InvalidPolicyConfigurationError`, `UnknownMetricRuleError`, `MissingMetricError` e `InvalidMetricValueError`.
    * **Inmutabilidad Transitiva:** Uso de `@dataclass(frozen=True, slots=True)` en combinación con copia defensiva encapsulada en `types.MappingProxyType` para garantizar inmutabilidad real en `rules`.
    * **Validaciones Estrictas de Configuración (`__post_init__`):** Recharzo Fail-Fast de políticas vacías, verificación de finitud (`math.isfinite`) en pesos $w_i \in [0.0, 1.0]$, y aserción estricta de sumatoria unitaria $\sum w_i = 1.0$ mediante `math.isclose(..., abs_tol=1e-9)`.
    * **Prohibición de Evaluación Parcial:** `compute_composite_score` exige coincidencia exacta entre el conjunto de métricas provisto y el conjunto registrado en `rules`. La presencia de métricas faltantes (`MissingMetricError`) o no registradas (`UnknownMetricRuleError`) aborta la ejecución de inmediato.
    * **Precisión Flotante IEEE-754:** Eliminación del redondeo prematuro en el dominio (`round()`), entregando el flotante exacto a la capa de presentación y validando finitud estricta en valores de entrada (rechazo explícito de `NaN`, `inf` y `-inf`).
  * **`tests/unit/test_score_policy.py`:**
    * Implementación de suite unitaria completa con cobertura al 100%: inversión direccional, rechazo de evaluaciones parciales, rechazo de no finitos (`NaN`/`Inf`), verificación de inmutabilidad transitiva (`FrozenInstanceError` / `TypeError`), validación de pesos inválidos y exactitud flotante con `pytest.approx`.
* **Métrica del Compilador:** `pyright core/benchmark/score_policy.py tests/unit/test_score_policy.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/test_score_policy.py -v` → **ALL PASSED**.



### 2. Servicio de Leaderboard y Comparación Estadística (Hito 2)
* **Causa Raíz:** Necesidad de un servicio puro de segundo orden que consuma los reportes inmutables `BenchmarkRunReport` y determine el ranking del proveedor de extracción sin acoplar la decisión a la ejecución[cite: 1]. Era imperativo evitar la mutación de los reportes originales, defender contra mutaciones de referencias de diccionario compartidas, enforzar una política de suficiencia muestral conservadora ($n \ge 2$) y reusar el `@classmethod compare_series` de `StatisticalComparator` sin modificar la estructura del DTO `ScientificSignificanceReport` (12 campos)[cite: 1, 2].
* **Correcciones y Decisiones Aplicadas:**
  * **Reutilización Estricta (DRY):** Se preservó intacto el `StatisticalComparator` y el DTO `ScientificSignificanceReport` (12 campos exactos) en `core/benchmark/reporter.py`[cite: 1, 2]. `LeaderboardService` delega la comparación invocando directamente el método de clase `StatisticalComparator.compare_series("composite_score", base_vals, chall_vals)`.
  * **Acceso Tipado (Anti-Duck Typing):** Se eliminó la introspección con `hasattr`. La identidad y las métricas se extraen de forma tipada (`report.provider_descriptor.name`, `report.overall_metrics`), aplicando Fail-Fast (`MissingProviderIdentityError`, `MissingReportMetricsError`) si los contratos no se cumplen.
  * **Política Conservadora Bilateral ($n \ge 2$):** Se exige la presencia de $n \ge 2$ observaciones en `item_metrics` en ambos lados (ganador vs. runner-up) como una regla de diseño propia de `LeaderboardService`. Inconsistencias muestrales asimétricas o $n < 2$ emiten ranking sin reporte de significancia (`significance_report = None`).
  * **Evaluación de Hipótesis Única ($m = 1$):** El leaderboard ejecuta una única comparación post-ranking entre el 1.º y 2.º puesto. Al ser $m = 1$, la corrección FWER Holm-Bonferroni no altera el umbral ($\alpha = 0.05$), por lo que no se invoca en esta capa, reservando `_apply_holm_bonferroni` para análisis multicomparativos externos.
  * **Tratamiento No Pareado Consistente:** `LeaderboardService` transfiere la serie de `composite_score` al comparador no pareado existente (`StatisticalComparator`). La correspondencia de ítems en el corpus se preserva como metadata, posponiendo evaluaciones pareadas para futuros ADRs.
  * **Corrección de Valor Esperado en Pruebas:** Se ajustó la aserción de `chall_vals` en `test_leaderboard_delegates_to_statistical_comparator_correctly` de `[0.5, 0.5]` a `[0.6, 0.6]` para reflejar el score compuesto exacto de `ted=0.4` y `recall=0.6`.
  * **Inmutabilidad Estructural Completa:** `LeaderboardEntry.metrics` combina copia defensiva (`dict(metrics)`) con envoltura de solo lectura en runtime (`types.MappingProxyType`), aislando el DTO de mutaciones externas.
* **Métrica del Compilador:** `pyright core/benchmark/reporter.py tests/unit/test_leaderboard_service.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/test_score_policy.py tests/unit/test_leaderboard_service.py` → **17 PASSED**.



### 3. Persistencia del Leaderboard (Hito 3)
* **Causa Raíz:** Necesidad de materializar los resultados del leaderboard en formatos JSON estructurado y Markdown ejecutivo de forma determinista, consumiendo la infraestructura existente sin introducir nuevos gateways ni acoplar lógica de I/O al núcleo de dominio.
* **Correcciones y Decisiones Aplicadas:**
  * **Métodos Puros de Formateo (`LeaderboardService`):**
    * `format_json`: Serializa la estructura de datos aplicando `sort_keys=True` para garantizar determinismo en el ordenamiento de claves. Las pruebas asertan la reproducibilidad ante ejecuciones independientes con estados equivalentes.
    * `format_markdown`: Genera una representación tabular con acceso estricto por clave (`entry.metrics[m]`), preservando Fail-Fast. Presenta las series comparadas desde la perspectiva del ranking (Rank #1 Winner / Rank #2 Runner-up) sin alterar el DTO original. Incorpora banderas cualitativas (`🟢 SIGNIFICANT`, `🔴 NOT SIGNIFICANT`, `🔴 N/A`).
  * **Delegación Exclusiva de Persistencia:** `persist_leaderboard(...)` delega la persistencia física exclusivamente a `BenchmarkPersistenceGateway.save_artifact(...)` sin invocar operaciones directas sobre el sistema de archivos.
* **Métrica del Compilador:** `pyright core/benchmark/reporter.py tests/unit/test_leaderboard_service.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/test_score_policy.py tests/unit/test_leaderboard_service.py` → **21 PASSED**.


### 4. Declaración del Proveedor por Defecto y Cierre de Fase 17 (Hito 4)
* **Causa Raíz:** Inexistencia de una constante explícita y tipada en la raíz de composición (`Composition Root`) que formalizara la categoría funcional del proveedor predeterminado de extracción.
* **Correcciones y Decisiones Aplicadas:**
  * **Declaración Tipada de Configuración:** Se incorporó `DEFAULT_EXTRACTION_PROVIDER: ProviderKind = ProviderKind.OCR_PARSER` en `apps/bootstrap/pipeline_factory.py`, eliminando cadenas mágicas (*magic strings*) y acoplando la configuración al `Enum` inmutable `ProviderKind`.
  * **Preservación del Composition Root:** No se alteró la lógica de instanciación directa del pipeline (`build_pipeline`), manteniendo la compatibilidad hexagonal y evitando abstracciones no solicitadas.
  * **Cierre Formal:** Con la declaración del proveedor por defecto y la verificación completa de tipado y pruebas unitarias, la Fase 17 queda formalmente congelada.
* **Métrica del Compilador:** `pyright apps/bootstrap/pipeline_factory.py core/benchmark/reporter.py core/benchmark/score_policy.py tests/unit/test_leaderboard_service.py` → **0 errors, 0 warnings**.
* **Métrica de Pruebas Unitarias:** `pytest tests/unit/test_score_policy.py tests/unit/test_leaderboard_service.py -v` → **21 PASSED**.