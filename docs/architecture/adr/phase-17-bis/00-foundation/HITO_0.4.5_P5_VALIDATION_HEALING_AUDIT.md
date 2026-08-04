# HITO_0.4.5_P5_VALIDATION_HEALING_AUDIT.md
## Validation, Healing & Revalidation Boundary — Reporte Consolidado Bloque P5

* **Estado:** AUDIT CLOSED / REMEDIATION BACKLOG OPEN (Bloque P5)
* **Fecha de Emisión:** 2026-07-28
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4.5 (Production Pipeline Audit — Bloque P5)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Auditoría analítica y forense estricta sustentada en el análisis AST del código fuente de producción y el Grafo de Validación y Auto-Reparación (`P5_VALIDATION_HEALING_GRAPH.md`), aplicando metodología de 15 capas de aislamiento. Cero mutaciones en código productivo.

---

## 1. MARCO EPISTEMOLÓGICO Y DIAGNÓSTICO DEL BUCLE DE CONTROL

El escrutinio forense del **Bloque P5** aborda la frontera de control de calidad post-inferencia: el ciclo de **Validación $\rightarrow$ Análisis de Falla $\rightarrow$ Auto-Reparación (*Healing*) $\rightarrow$ Revalidación**.

Aplicando la Capa 11 (Falsación Sistemática) y la Capa 5 (Cambios de Representación) sobre la evidencia del grafo y el código fuente de producción, se ha logrado confirmar que **el bucle iterativo de curación y revalidación funciona y está correctamente cableado**, lo cual es un hito de ingeniería positivo. Asimismo, la investigación directa por código permitió **refutar la hipótesis previa de contaminación ontológica**, demostrando que `ValidationPipeline` es un contenedor puro de validación de texto.

```text
==================================================================================================
                 MECÁNICA REAL DE VALIDACIÓN Y CURACIÓN EN RUNTIME (P5)
==================================================================================================

  [LLM Worker] ──► InferenceResult (content: str)
                         │
                         ▼
  [AsyncDispatcher._process_validation_and_healing()]
                         │
                         ▼
  (1) ValidationContext (source_text, target_text)
                         │
                         ▼
  (2) ValidationPipeline.validate_chunk(ctx)
         ├── LegacyValidatorAdapter(StructuralValidator)
         ├── PreservationValidator
         ├── PerimeterValidator
         ├── SemanticValidator
         └── VolumetricValidator
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
   [NO HARD FAILS]                [HARD FAIL DETECTADO]
         │                               │
         │ (Aceptado)                    ▼
         │                 (3) HealingContext(hard_fails[0])
         │                               │
         │                               ▼
         │                 (4) HealingPipeline.heal_and_revalidate()
         │                        ├── Búsqueda O(1) de Strategy por invariant_family
         │                        ├── Ejecución: strategy.heal()
         │                        └── Revalidación atómica: validate_chunk()
         │                               │
         │                ┌──────────────┴──────────────┐
         │                ▼                             ▼
         │        [HEALING SUCCESS]             [HEALING FAILURE / ROLLBACK]
         │                │                             │
         │                ├─────────────────────┐       │ (Mantiene payload original)
         │                ▼                     ▼       ▼
         │    (5) Revalidación Local   ValueError("HARD_FAIL no resuelto")
         │        en AsyncDispatcher            │
         │                │                     ▼
         │                │            [AsyncDispatcher._worker()]
         │                │            ChunkOutcome(
         │                │              status=FAILED,
         │                │              failure_reason=VALIDATION_FAILURE
         │                │            )
         │                │                     │
         │                │                     ▼
         │                │            [DocumentAssembler]
         │                │            RECHAZO DE DOCUMENTO (AssemblyPolicy)
         ▼                ▼
   TranslatedUnit(payload_final)
```

---

## 2. REGISTRO EXHAUSTIVO DE EVIDENCIA FORENSE Y HALLAZGOS TÉCNICOS (P5-H01 A P5-H06)

### P5-H01: Falsación de Contaminación de Dominios en `ValidationPipeline` [FALSACIÓN DEMOSTRADA]
* **Hipótesis previa:** Se infería del grafo estático que `ValidationPipeline` estaba "contaminado" invocando validadores del motor de AST (`StructuralEquationValidator` y `PassthroughIntegrityValidator`) durante la evaluación de texto post-LLM.
* **Demostración por Código Fuente:**
  En `apps/bootstrap/pipeline_factory.py` (`_build_default_validation_pipeline()`), los únicos validadores registrados en `ValidationPipeline` son:
  1. `LegacyValidatorAdapter(StructuralValidator)`
  2. `PreservationValidator()`
  3. `PerimeterValidator()`
  4. `SemanticValidator()`
  5. `VolumetricValidator()`
* **Veredicto Metodológico:** **HIPÓTESIS REFUTADA / DISEÑO CORRECTO**. `ValidationPipeline` (en `core/validation/pipeline.py`) opera como un **contenedor puro de validación de texto a nivel de Chunk/Documento**. No ejecuta validadores de AST. Los validadores de AST pertenecen a `core/validation/ast/`, los cuales están totalmente aislados.

---

### P5-H02: Orfandad del Motor de Validación Polimórfica (`PolymorphicValidationEngine`) [DEMOSTRADO]
* **Ubicación:** `core/validation/ast/engine.py` vs `apps/bootstrap/pipeline_factory.py` / `apps/llm_workers/dispatcher.py`
* **Demostración por Código Fuente:**
  La inspección de `pipeline_factory.py` y `dispatcher.py` confirma que ni `PolymorphicValidationEngine` ni `build_default_validation_engine()` son importados ni instanciados en ninguna parte del pipeline activo.
* **Impacto Arquitectónico:** **[P0 - CRÍTICO]**. El motor de validación estática de nodos AST pre-inferencia es un **componente $100\%$ zombi/unreachable** en producción. Las unidades entran a la etapa de despacho sin una validación polimórfica previa de sus payload.

---

### P5-H03: Garantía de Rollback Atómico y Revalidación Obligatoria en `HealingPipeline` [DEMOSTRADO]
* **Ubicación:** `core/healing/pipeline.py` (`heal_and_revalidate()`)
* **Demostración por Código Fuente:**
  En `HealingPipeline.heal_and_revalidate()`:
  ```python
  if active_hard_fails:
      logger.warning(f"HEALING_REJECTED: Rollback aplicado. Errores: {failures_summary}")
      return HealingResult(
          invariant_family=family,
          strategy_id=strat_id,
          outcome=HealingOutcome.FAILURE,
          original_text=context.validation_context.target_text, # <--- PRESERVA TEXTO ORIGINAL
          message=f"Revalidation failed. Errors: {failures_summary}"
      )
  ```
  Y en `AsyncDispatcher._process_validation_and_healing()`:
  ```python
  if healing_result.outcome == HealingOutcome.SUCCESS:
      translated = replace(translated, translated_payload=healing_result.final_text)
  ```
  Si la estrategia falla o si la revalidación arroja un nuevo `HARD_FAIL`, `healing_result.outcome` es `FAILURE`. Por ende, `AsyncDispatcher` **jamás actualiza `translated` con el texto mutado**. El texto corrupto producido por el *healing* es descartado y se preserva el error original.
* **Veredicto Metodológico:** **SOTA / APROBADO**. Invariante de seguridad de datos verificado al $100\%$.

---

### P5-H04: Mecánica de Aborto por `HARD_FAIL` e Incompatibilidad con `AssemblyPolicy` [DEMOSTRADO]
* **Ubicación:** `apps/llm_workers/dispatcher.py` (`_process_validation_and_healing()` y `_worker()`)
* **Demostración por Código Fuente:**
  Cuando un `HARD_FAIL` no puede ser curado por el `HealingPipeline`:
  1. `_process_validation_and_healing()` lanza `ValueError(f"[{res.invariant_id}] {res.message}")`.
  2. En `_worker()`, la excepción es capturada:
     ```python
     except ValueError as e:
         results[unit.chunk_index] = ChunkOutcome(
             chunk_index=unit.chunk_index,
             chunk_id=unit.chunk_id,
             status=ExecutionStatus.FAILED,
             original_payload_sha256=unit.payload_sha256,
             translated_unit=None,
             failure_reason=FailureReason.VALIDATION_FAILURE,
             error_message=str(e),
             telemetry=envelope.telemetry
         )
     ```
  3. En `pipeline_factory.py`, la política de ensamblado declara:
     ```python
     degradable_failures=frozenset([
         FailureReason.CONTEXT_OVERFLOW,
         FailureReason.PROVIDER_FAILURE,
         FailureReason.RETRY_EXHAUSTED
     ])
     ```
* **Impacto Arquitectónico:** **[P0 - CRÍTICO / DISEÑO CORRECTO DE SEGURIDAD]**. `FailureReason.VALIDATION_FAILURE` **no forma parte de las fallas degradables**. Por lo tanto, si un solo chunk falla la validación y no puede ser reparado, el `DocumentAssembler` **restringe y aborta el ensamblado del documento entero**. Un fallo de integridad frena la compilación final.

---

### P5-H05: Limitación de Disparo de Healing Monofoco y Redundancia de Revalidación [DEMOSTRADO]
* **Ubicación:** `apps/llm_workers/dispatcher.py` (`_process_validation_and_healing()`)
* **Demostración por Código Fuente:**
  1. **Disparo Monofoco:** `AsyncDispatcher` ejecuta `healing_ctx = HealingContext(..., validation_result=hard_fails[0])`. Si un chunk posee múltiples `HARD_FAIL` de familias distintas (ej. Markdown leakage Y ambiente math desbalanceado), **solo se envía el primer fallo al pipeline de healing**. No existe un bucle iterativo multi-falla en una sola pasada.
  2. **Doble Revalidación Redundante:**
     - `HealingPipeline.heal_and_revalidate()` ejecuta `validate_chunk()` internamente.
     - Al regresar con éxito a `AsyncDispatcher`, este **vuelve a ejecutar** `self.validation_pipeline.validate_chunk()` por segunda vez sobre el mismo texto.
* **Impacto Arquitectónico:** **[P2 - MEDIO / INEFICIENCIA]**. La doble revalidación no compromete la seguridad pero duplica innecesariamente el tiempo de procesamiento en CPU. El disparo monofoco puede hacer que un chunk falle prematuramente si tenía dos errores reparables en lugar de uno.

---

### P5-H06: Persistencia de Deuda Técnica Activa (`LegacyValidatorAdapter`) [DEMOSTRADO]
* **Ubicación:** `apps/bootstrap/pipeline_factory.py` (`_build_default_validation_pipeline()`)
* **Demostración por Código Fuente:**
  La Composition Root de producción explícitamente inyecta y ejecuta el `LegacyValidatorAdapter` envolviendo al `StructuralValidator`.
* **Impacto Arquitectónico:** **[P1 - ALTO]**. Las reglas de validación heredadas de las Fases 11 y 12 siguen interrumpiendo el flujo de los documentos modernos. Al adaptar códigos de error desconocidos (`UnknownLegacyValidationCodeError`), se opaca la verdadera causa de los rechazos.

---

## 3. TRAZABILIDAD Y FLUJO DE DATOS OPERACIONAL EN P5

```text
==================================================================================================
                 TRAZABILIDAD DE ERRORES Y REVALIDACIÓN (CÓDIGO VERIFICADO)
==================================================================================================

  [TranslatedUnit (Inferencia LLM)]
                 │
                 ▼
  [ValidationPipeline.validate_chunk()] ──► ¿Hard Fails?
                 │                               │
             (No)│                           (Sí)│ hard_fails[0]
                 ▼                               ▼
         [Chunk Aprobado]             [HealingPipeline.heal_and_revalidate()]
                                                 │
                                                 ├── Strategy.heal()
                                                 │       │
                                                 │       ▼ (Texto Mutado)
                                                 ├── ValidationPipeline.validate_chunk()
                                                 │       │
                                                 │   (Hard Fail?)
                                                 │   ├── (Sí) ──► Outcome: FAILURE (Rollback a texto original)
                                                 │   └── (No) ──► Outcome: SUCCESS
                                                 │
                                                 ▼
                                     ¿Outcome == SUCCESS?
                                         │            │
                                     (Sí)│        (No)│
                                         ▼            ▼
                          AsyncDispatcher        raise ValueError(...)
                          Re-Validación               │
                          (Redundante)                ▼
                               │                 [AsyncDispatcher._worker()]
                               ▼                 ChunkOutcome(status=FAILED)
                      ChunkOutcome(SUCCESS)           │
                                                      ▼
                                                 [DocumentAssembler]
                                                 Documento RECHAZADO (Pila FSM)
```

---

## 4. TAXONOMÍA Y MATRIZ DE COMPONENTES DEL BLOQUE P5

| Componente / Módulo | Categoría Arquitectónica | Severidad | Diagnóstico Forense Clave | Disposición Hito 0.5 |
| :--- | :--- | :---: | :--- | :--- |
| `core/healing/pipeline.py` | Healing Engine | **Cero** | Rollback atómico e Invariante de Revalidación comprobados en código. | **CONSERVAR** |
| `core/healing/strategies/*` | Healing Strategies | **Cero** | Estrategias simétricas que emiten `HealingResult` inmutable. | **CONSERVAR** |
| `core/validation/pipeline.py` | Text Validation | **Cero** | Tubería pura de texto post-LLM; hipótesis de contaminación falsada. | **CONSERVAR** |
| `core/validation/ast/engine.py` | AST Validation | **P0 (Crítico)** | `PolymorphicValidationEngine` $100\%$ zombi; omitido en fábrica. | **ENLAZAR EN FACTORY** |
| `apps/llm_workers/dispatcher.py` | Dispatcher Core | **P2 (Medio)** | Ejecuta doble revalidación y solo evalúa `hard_fails[0]`. | **OPTIMIZAR BUCLE** |
| `core/validation/legacy_adapter.py`| Tech Debt | **P1 (Alto)** | Adapter de Fases 11/12 aún activo en `pipeline_factory.py`. | **DEPRECAR / PURGAR** |

---

## 5. MARCO NORMATIVO Y REGLAS DE REMEDIACIÓN FUTURA (P5-R01 A P5-R04)

Queda **estrictamente prohibida la modificación de código** durante la Fase 0. Las siguientes normativas forman el mandato técnico ineludible de remediación para el **Hito 0.5** y la **Fase 17_BIS**:

* **P5-R01 (Conexión Mandatoria de `PolymorphicValidationEngine` - P0):** Inyectar la validación estática de AST pre-inferencia en el pipeline antes del despacho de unidades, asegurando que nodos estructuralmente corruptos sean rechazados antes de incurrir en costos de inferencia.
* **P5-R02 (Eliminación de Redundancia en Revalidación - P2):** Refactorizar `AsyncDispatcher._process_validation_and_healing()` para confiar en el resultado de revalidación ya certificado por `HealingPipeline.heal_and_revalidate()`, eliminando la segunda llamada redundante a `validate_chunk()`.
* **P5-R03 (Sostenibilidad de Healing Iterativo Multi-Falla - P2):** Modificar el desencadenante de curación en `AsyncDispatcher` para permitir que el `HealingPipeline` aplique curación secuencial si un chunk reporta múltiples `HARD_FAIL` de familias de invariantes distintas.
* **P5-R04 (Deprecación de `LegacyValidatorAdapter` - P1):** Retirar la instanciación de `LegacyValidatorAdapter` en `_build_default_validation_pipeline()`, confiando la validación estructural al `StructuralValidator` nativo o al motor Post-LLM.

---

## 6. EVALUACIÓN DE CONFIABILIDAD OPERACIONAL Y VEREDICTO DE CIERRE

### 6.1 DIAGNÓSTICO DE CONFIABILIDAD OPERACIONAL
1. **Resiliencia Transaccional de Auto-Reparación (*Healing*):** **EXCEPCIONAL Y SOTA.** Se demostró por código que el bucle de curación posee un rollback robusto que previene la persistencia de textos corruptos y exige revalidación atómica antes de aceptar una mutación.
2. **Cobertura de Validación Pre-Inferencia:** **INCOMPLETA.** El motor de validación polimórfica de AST está desacoplado, aunque la validación Post-LLM funciona de manera consistente para detener documentos con errores graves de formato.

---

### 6.2 DECISIÓN FINAL DEL SUB-HITO 0.4.5-P5

The audit for **Block P5 (Validation $\rightarrow$ Healing $\rightarrow$ Revalidation)** is hereby declared **CLOSED**.

```text
====================================================================================
                  ESTADO DE AUDITORÍA: SUB-HITO 0.4.5-P5
====================================================================================
  Audit Status             | CLOSED (Auditoría Forense Finalizada)
  Code Remediation         | DEFERRED (Diferido a Hito 0.5)
  Production Certification | GRANTED WITH RESERVATIONS (Pre-LLM AST Engine desacoplado)
  Remediation Backlog      | OPEN (Reglas P5-R01 a P5-R04 Registradas)
====================================================================================
```

**Bitácora de Gobernanza:**
> *"Se da por concluida la auditoría del Bloque P5. Se certifica formalmente la corrección del bucle transaccional de auto-reparación (HealingPipeline) y la efectividad del aborto de documentos ante fallas no corregibles (VALIDATION_FAILURE). Mediante el examen de código fuente se falsó la hipótesis de contaminación en el ValidationPipeline, confirmando que opera exclusivamente sobre cadenas de texto. No obstante, se registra en el backlog la orfandad del PolymorphicValidationEngine pre-inferencia y la doble revalidación redundante. Queda estrictamente prohibido mutar código durante la Fase 0."*