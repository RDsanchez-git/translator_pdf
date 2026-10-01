# FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 0.8.0
**Estado:** FROZEN
**Fecha:** 2026-09-30
**Última actualización:** 2026-09-30
**Derivado de:** `PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.11 — Gate 4 Exit Review (COMPLETED: CONDITIONAL PASS)
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review de Fase 6 (Continuous Verification). Cada finding
incluye los archivos auditados, el análisis, los gaps confirmados, la justificación
normativa y la clasificación final.

> **Este documento NO es:**
> - El Findings Register (registro de decisiones y resultados de implementación)
> - El Execution Plan (secuencia de tareas)
> - Un documento de gobernanza normativa (NADRs/ADRs)
>
> **Este documento SÍ es:**
> - La evidencia forense que justifica cada clasificación del Findings Register
> - El registro auditable de qué se auditó y por qué se decidió lo que se decidió
> - Un documento de consulta futura para no re-derivar conclusiones

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1.0 | 2026-09-26 | Emisión inicial DRAFT. Esqueleto del Evidence Log para Fase 6. |
| 0.2.0 | 2026-09-26 | Gate 1 Exit Review completado. Evidencia forense de DF-05, DF-06, DF-07 documentada. Referencias actualizadas a Execution Plan v1.0.5. |
| 0.3.0 | 2026-09-26 | Wave 2.1 completada (Tasks 2.1.1-2.1.3). Sin hallazgos nuevos registrados. Gate 2 → IN PROGRESS. Referencias actualizadas a Execution Plan v1.0.6. |
| 0.4.0 | 2026-09-26 | Wave 2.2 completada (Tasks 2.2.1-2.2.3). Sin hallazgos nuevos registrados. Gate 2 → COMPLETED (69/69 reglas, 6/6 Tasks). Referencias actualizadas a Execution Plan v1.0.7. |
| 0.5.0 | 2026-09-30 | Wave 3.1 completada (Tasks 3.1.1-3.1.3). Sin hallazgos nuevos registrados. Gate 3 → IN PROGRESS (31/35 reglas NADR-29 DONE). Referencias actualizadas a Execution Plan v1.0.8. |
| 0.6.0 | 2026-09-30 | Wave 3.2 completada (Tasks 3.2.1-3.2.3). Sin hallazgos nuevos registrados. GAP-6.3-01 (P0) resuelto: CI invoca el verification entry point real. Gate 3 → IN PROGRESS (35/35 reglas NADR-29 DONE, Wave 3.3 validación end-to-end pendiente). Referencias actualizadas a Execution Plan v1.0.9. |
| 0.7.0 | 2026-09-30 | Wave 3.3 completada (Tasks 3.3.1-3.3.3). DF-08 identificado y resuelto: PDF orphan `doc_06_johnstone.pdf` movido a `tests/corpus/archive/`. Baseline sellada invariante. Gate 3 → COMPLETED (35/35 reglas NADR-29, 9/9 Tasks). Referencias actualizadas a Execution Plan v1.0.10. |
| 0.8.0 | 2026-09-30 | Gate 4 Exit Review completado (CONDITIONAL PASS). Evidencia forense de DF-09, DF-10, DF-11 registrada; DF-06 reclasificado a RECLASSIFIED_FUTURE_PHASE con evidencia de no-encaje en Fase 18. Task 4.1.3 RESOLVED con evidencia server-side (MIG-01/MIG-04). Referencias actualizadas a Execution Plan v1.0.11 y Findings Register v0.10.0. |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER  >  ADR_F17_BIS_06 v1.2.0  >  NADR-F17BIS-25..30  >  PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.11
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que Continuous Verification sea
> un control operativo efectivo, reproducible y arquitectónicamente fiel
> sobre el pipeline productivo, con enforcement demostrable sobre la
> integración de cambios?"*

### 0.3 Reglas transversales aplicables

- **ENGINEERING_PRINCIPLES §I (Reuse Before Invent):** Ningún finding puede justificar la creación de un mecanismo paralelo si existe capacidad normativa que lo resuelve.
- **ENGINEERING_PRINCIPLES §II (Functional Core / Imperative Shell):** Los hallazgos deben respetar la separación entre lógica de dominio e infraestructura.
- **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):** Ningún finding puede cerrarse como NAR si existe un fallo no indexable asociado. Todo fallo debe ser explícito o derivar en implementación.
- **NADR-F17BIS-27 §5.1 R1-R5:** La semántica de resultados distingue evaluación científica de estado operacional. Un finding sobre ambigüedad semántica no puede cerrarse como NAR.
- **NADR-F17BIS-30 §5.5 R14-R16:** NO DEMOSTRADO no es una forma alternativa de DONE. Un finding sobre enforcement sin evidencia externa no puede cerrarse como RESOLVED sin evidencia server-side.
- **ADR_F17_BIS_MASTER §5 (Determinismo y Reproducibilidad):** Todo hallazgo que afecte la reproducibilidad de la verificación debe clasificarse como IMPLEMENTATION_REQUIRED o ACCEPTED_LIMITATION con justificación explícita.
- **ADR_F17_BIS_06 v1.2.0 D1 (Integración, No Creación):** Ningún finding puede justificar la creación de un segundo mecanismo de verificación.
- **PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.11 §8 (Global DoD):** Un finding que afecta una regla normativa solo se cierra cuando es trazable a una implementación commiteada, un mecanismo de verification superado y un mecanismo de validation superado.

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-{XX}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado con evidencia |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida, documentada y aceptada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `PENDING_REVIEW` | Pendiente de análisis en Exit Review |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding **DEBE** distinguir entre: (a) gap objetivo confirmado, (b) hipótesis pendiente de demostración, (c) no-gap (comportamiento correcto por diseño).
- No se implementa código durante el Exit Review. La implementación se agrupa en un batch posterior.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.

### 1.4 Árbol de decisión del Gate Exit Review

```text
1. ¿Sigue siendo válido el hallazgo?
   → NO: CLOSED (NAR)
   → SÍ: continuar

2. ¿Puede resolverse dentro del Gate actual?
   → SÍ: RESOLVED
   → NO: continuar

3. ¿Es un problema técnico?
   → SÍ: RECLASIFICADO a Gate futuro
   → NO: continuar

4. ¿Es un conflicto normativo?
   → SÍ: CONVERTIDO EN GF
   → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE
```

---

## 2. ESTRUCTURA POR FINDING

Los findings DF-01, DF-05, DF-06 y DF-07 fueron identificados en Wave 1.1 (Task 1.1.3).
Wave 1.2 no registró hallazgos nuevos. Gate 1 cierra con 4 findings analizados.

Wave 2.1 (Tasks 2.1.1, 2.1.2, 2.1.3) y Wave 2.2 (Tasks 2.2.1, 2.2.2, 2.2.3)
no registraron hallazgos nuevos. La evidencia de implementación está documentada
en las Notas de Implementación del Execution Plan v1.0.11 (§3.1, §3.2), no en
este Evidence Log (que registra únicamente evidencia forense de findings).

Wave 3.1 (Tasks 3.1.1-3.1.3) y Wave 3.2 (Tasks 3.2.1-3.2.3) no registraron
hallazgos nuevos. Wave 3.3 (Task 3.3.1) registró DF-08: PDF orphan en el
directorio canonical, resuelto moviendo el archivo a `tests/corpus/archive/`.
Gate 3 cierra con 1 finding analizado (DF-08 RESOLVED).

Wave 4.1 registró DF-09 (enforcement de merge de CV diferido condicionalmente).
Wave 4.2 registró DF-10 (PASS path no demostrable con estado basal del extractor,
Task 4.2.1 BLOCKED) y DF-11 (manifest corrupto escapaba del except de Pasos 1-2b,
resuelto en la misma Wave). Gate 4 reclasificó DF-06 (de ACCEPTED_LIMITATION a
RECLASSIFIED_FUTURE_PHASE) tras verificar que el refactor de composición del
benchmark no encaja en Gate 4 ni en Fase 18. Gate 4 cierra con 4 findings
analizados (DF-09, DF-10, DF-11 nuevos; DF-06 reclasificado) y veredicto
CONDITIONAL PASS.

---

### 2.0 DF-01 — Contrato OCR providers roto por include_external_packages

| Campo | Valor |
|-------|-------|
| **ID** | DF-01 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 1.1 / Task 1.1.3 |
| **Gate destino original** | Gate 1 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — agregar `include_external_packages = true` |
| **¿Bloquea Continuous Verification?** | Sí — `lint-imports` falla con exit code 1 |

#### 2.0.1 Texto original del DF

> *"El contrato 'Domain must not import from Infrastructure' falla porque
> `forbidden_modules` incluye librerías externas (fitz, pymupdf, docling, PIL)
> pero import-linter 2.15 requiere `include_external_packages = true` en la
> configuración top-level para evaluar estos módulos."*

#### 2.0.2 Reformulación corregida

No requiere reformulación.

#### 2.0.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `pyproject.toml` §[tool.importlinter] | Configuración top-level sin `include_external_packages` |
| 2 | Contrato 1 `forbidden_modules` | Lista: `fitz`, `pymupdf`, `docling`, `PIL` |
| 3 | Salida de `lint-imports` | Error: "External packages not included in analysis" |
| 4 | Documentación import-linter 2.15 | Requiere `include_external_packages = true` para `forbidden_modules` externos |

#### 2.0.4 Análisis

La condición original existe. import-linter 2.x cambió el comportamiento respecto a 1.x: ahora requiere `include_external_packages = true` explícito cuando `forbidden_modules` incluye librerías externas al proyecto. Sin esta configuración, el linter no analiza imports de librerías externas y reporta error de configuración.

No es violación normativa de los NADRs de Fase 6. Es un problema de migración de herramienta (import-linter 1.x → 2.x).

#### 2.0.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Falta `include_external_packages = true` en configuración top-level | `lint-imports` error | Alta |

#### 2.0.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| `forbidden_modules` incluye librerías externas | ✅ Correcto por diseño | Protege a `core/` de imports directos de librerías de extracción |
| Contrato "Domain must not import from Infrastructure" | ✅ Correcto | Protege arquitectura hexagonal |

#### 2.0.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Configuración de linter |
| Reproducibilidad | ⚠️ Sí (menor) | `lint-imports` falla, bloqueando CI |
| Corrección funcional | ❌ No | No afecta evaluación de regresión |
| Enforcement demostrable | ❌ No | No afecta contratos de merge protection |
| Bloquea Fase 18 | ❌ No | Resolución en Task 1.1.3 |

#### 2.0.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 6 | ✅ Sí |
| Bloquea Continuous Verification | ✅ Sí (bloquea CI) |
| Clasificación | `RESOLVED` |
| Prioridad | Alta |

#### 2.0.9 Regla aplicada

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Todo fallo debe ser explícito o derivar en implementación."*

La falta de `include_external_packages = true` causaba que `lint-imports` fallara con error de configuración, bloqueando CI. La resolución hace que el linter funcione correctamente y detecte violaciones reales.

---

### 2.1 DF-05 — ignore_imports huérfanos en pyproject.toml

| Campo | Valor |
|-------|-------|
| **ID** | DF-05 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 1.1 / Task 1.1.3 |
| **Gate destino original** | Gate 1 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — eliminación de configuración muerta |
| **¿Bloquea Continuous Verification?** | No — config de linter, no afecta runtime |

#### 2.1.1 Texto original del DF

> *"Los `ignore_imports` del contrato 1 en pyproject.toml referencian
> módulos `core.extraction.ocr_providers.*` que no existen. import-linter
> reporta 'No matches for ignored import' y exit code 1."*

#### 2.1.2 Reformulación corregida

No requiere reformulación.

#### 2.1.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `pyproject.toml` §[tool.importlinter] | Contrato 1 contiene 3 `ignore_imports` hacia `core.extraction.ocr_providers.*` |
| 2 | `core/extraction/ocr_providers/` | Directorio NO existe. Confirmado con `Get-Content` → `PathNotFound` |
| 3 | `infra/extraction/providers/` | Contiene `pymupdf_provider.py`, `docling_provider.py`, `tesseract_provider.py`. Los providers fueron migrados aquí |
| 4 | Salida de `lint-imports` | 3 warnings: "No matches for ignored import core.extraction.ocr_providers.* -> core.extraction.provider" |

#### 2.1.4 Análisis

La condición original existe: los `ignore_imports` hacen referencia a módulos que fueron eliminados durante una migración previa. Los providers se movieron de `core/extraction/ocr_providers/` a `infra/extraction/providers/`. La configuración de import-linter no fue actualizada tras la migración, dejando `ignore_imports` que apuntan a rutas inexistentes.

No es violación normativa de los NADRs de Fase 6. Es un problema de higiene de configuración. import-linter 2.15 trata los `ignore_imports` sin coincidencia como condición de fallo (exit code 1).

#### 2.1.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | `ignore_imports` hacia `core.extraction.ocr_providers.*` sin módulo destino | `Get-Content` → `PathNotFound` | Baja |
| G2 | `core.extraction.provider` referenciado como destino no existe | `Select-String` → 0 resultados en filesystem actual | Baja |

#### 2.1.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Migración de providers a `infra/` | ✅ Correcto por diseño | Los providers pertenecen a la capa de infraestructura (arquitectura hexagonal) |
| Contrato "Domain modules must not import concrete OCR provider implementations" | ✅ Correcto | Protege a `core/` de imports directos de librerías de extracción |

#### 2.1.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Configuración de linter, no afecta runtime |
| Reproducibilidad | ⚠️ Sí (menor) | `lint-imports` falla con exit code 1, bloqueando CI |
| Corrección funcional | ❌ No | No afecta evaluación de regresión |
| Enforcement demostrable | ❌ No | No afecta contratos de merge protection |
| Bloquea Fase 18 | ❌ No | Resolución en Task 1.1.3 |

#### 2.1.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 6 | ✅ Sí |
| Bloquea Continuous Verification | ❌ No |
| Clasificación | `RESOLVED` |
| Prioridad | Media |

#### 2.1.9 Regla aplicada

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Todo fallo debe ser explícito o derivar en implementación."*

Los `ignore_imports` huérfanos generaban warnings silenciosos en import-linter que podían ocultar violaciones reales. La eliminación de la configuración muerta restablece la señal limpia del linter.

---

### 2.2 DF-06 — core.benchmark.__main__ importa de apps/

| Campo | Valor |
|-------|-------|
| **ID** | DF-06 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` (reclasificado en Gate 4; previamente `ACCEPTED_LIMITATION` en Gate 1) |
| **Origen** | Wave 1.1 / Task 1.1.3 |
| **Gate destino original** | Gate 1 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Alta (deuda técnica) |
| **¿Requiere implementación?** | Sí — fuera de scope de Gate 1 |
| **¿Bloquea Continuous Verification?** | No — resuelto con ignore_import temporal |

#### 2.2.1 Texto original del DF

> *"core/benchmark/__main__.py importa apps.bootstrap.pipeline_factory,
> generando cadena transitiva hacia fitz (PyMuPDF) que viola los contratos
> 'Domain must not import from Infrastructure' y 'Domain modules must not
> import concrete OCR provider implementations'."*

#### 2.2.2 Reformulación corregida

No requiere reformulación.

#### 2.2.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/benchmark/__main__.py` L68 | `from apps.bootstrap.pipeline_factory import build_extraction_pipeline` |
| 2 | `apps/bootstrap/pipeline_factory.py` L47 | Import de `apps.bootstrap.provider_factory` |
| 3 | `apps/bootstrap/provider_factory.py` L3 | Import de `infra.extraction.providers.pymupdf_provider` |
| 4 | `infra/extraction/providers/pymupdf_provider.py` L5 | `import fitz` |
| 5 | Salida de `lint-imports --verbose` | Cadena completa: `core.benchmark.__main__ → apps.bootstrap.pipeline_factory → apps.bootstrap.provider_factory → infra.extraction.providers.pymupdf_provider → fitz` |

#### 2.2.4 Análisis

La condición original existe. La cadena transitiva es real y verificable. `core/` (dominio) alcanza transitivamente `fitz` (librería de extracción) a través de `apps/`. Esto viola dos contratos de arquitectura hexagonal:

1. **"Domain must not import from Infrastructure":** `core` no debe alcanzar `infra` ni siquiera transitivamente.
2. **"Domain modules must not import concrete OCR provider implementations":** `core` no debe alcanzar librerías de extracción concretas.

La resolución completa requiere refactorizar `core/benchmark/__main__.py` para eliminar la dependencia directa de `apps/`. Esto implica rediseñar cómo el benchmark accede al pipeline de extracción, probablemente mediante inyección de dependencias o un puerto. Esta refactorización está fuera del scope de Gate 1 y Gate 3, y se planifica para Gate 4.

#### 2.2.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | `core.benchmark.__main__` L68 importa `apps.bootstrap.pipeline_factory` | Línea 68 del archivo | Alta |
| G2 | Cadena transitiva alcanza `fitz` | `lint-imports --verbose` muestra la cadena completa | Alta |

#### 2.2.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| `apps.bootstrap.pipeline_factory` como composition root | ✅ Correcto por diseño | Es el único punto de construcción del pipeline (NADR-11 §5.1 R1) |
| `infra.extraction.providers` en capa de infraestructura | ✅ Correcto por diseño | Los providers pertenecen a infra (arquitectura hexagonal) |

#### 2.2.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | La deuda no afecta determinismo del pipeline |
| Reproducibilidad | ❌ No | La cadena transitiva no afecta reproducibilidad de la evaluación |
| Corrección funcional | ❌ No | El pipeline funciona correctamente |
| Enforcement demostrable | ⚠️ Sí (menor) | El contrato de import-linter requiere `ignore_import` temporal |
| Bloquea Fase 18 | ❌ No | Deuda técnica documentada, no impide operación |

#### 2.2.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ✅ Sí (transitiva) |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 6 | ❌ No — scope de Gate 3-4 |
| Bloquea Continuous Verification | ❌ No |
| Clasificación | `ACCEPTED_LIMITATION` |
| Prioridad | Alta (deuda técnica) |

#### 2.2.9 Regla aplicada

> **ENGINEERING_PRINCIPLES §III (Fail Fast & Explicit Errors):**
> *"No se aceptan soluciones temporales no documentadas ni silenciosas."*

La deuda se acepta como limitación documentada con `ignore_import` explícito en pyproject.toml. No es una solución silenciosa: está rastreada como DF-06 y planificada para Gate 3-4. La justificación cumple el requisito de explicitud.

> **ENGINEERING_PRINCIPLES §VII (No Big Bang / YAGNI):**
> *"No se reescribe el sistema completo de golpe."*

La refactorización completa de `core/benchmark/__main__.py` se difiere a Gate 3-4 para no bloquear el avance de Gate 1 con una refactorización de alto riesgo fuera de scope.

#### 2.2.10 Reclasificación en Gate 4 (2026-09-30)

**Estado previo:** `ACCEPTED_LIMITATION` con destino "Gate 3-4".
**Estado nuevo:** `RECLASSIFIED_FUTURE_PHASE` con destino "fase futura no faseada (refactor de composición del benchmark)".

**Evidencia de la reclasificación:**
- Gate 3 cerró sin resolver DF-06: su scope era perfiles de ejecución e integración CI, no refactor del benchmark (Execution Plan v1.0.10 §4).
- Gate 4 verificó contra ROADMAP_ARQUITECTONICO_LP que Fase 18 (Advanced Local Runtime) tiene entregables de asincronía pura, memory efficiency/streaming y backpressure/batching: **no incluye** rediseño de composición de `core/benchmark/__main__.py`. Fase 17 está congelada y completada (PyMuPDF elegido por benchmark estadístico).
- Resolver el refactor dentro de Gate 4 (scope: enforcement de merge, NADR-30) introduciría riesgo en el entry point del benchmark sin beneficio para ninguna regla de NADR-30.

**Mitigación vigente:** `ignore_import` explícito y documentado en el contrato 3 de `pyproject.toml`; el contrato permanece KEPT (4/4) en todas las verificaciones de Gate 4. La deuda es visible, trazable y no silenciosa (ENGINEERING_PRINCIPLES §III).

**Regla aplicada:**

> **ENGINEERING_PRINCIPLES §VII (No Big Bang / YAGNI):** no se reescribe composición
> fuera de su fase natural. **METHODOLOGY §3.5.2:** los hallazgos diferidos deben
> tener destino explícito; "Gate 3-4" dejó de ser un destino válido al cerrar ambos
> Gates sin resolución, y se sustituye por destino honesto.

---

### 2.3 DF-07 — Contrato 3 sin ignore_imports para cadena DF-06

| Campo | Valor |
|-------|-------|
| **ID** | DF-07 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 1.1 / Task 1.1.3 |
| **Gate destino original** | Gate 1 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — agregar ignore_import |
| **¿Bloquea Continuous Verification?** | No — config de linter |

#### 2.3.1 Texto original del DF

> *"Al eliminar los ignore_imports huérfanos (DF-05), el contrato 3 detectó
> la cadena transitiva de DF-06 y reportó BROKEN. El contrato 3 no tenía
> ignore_imports para esa cadena."*

#### 2.3.2 Reformulación corregida

No requiere reformulación.

#### 2.3.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `pyproject.toml` §[tool.importlinter] contrato 3 | Contrato "Domain modules must not import concrete OCR provider implementations" sin `ignore_imports` para `core.benchmark.__main__` |
| 2 | Salida de `lint-imports` post-DF-05 | Contrato 3 BROKEN: cadena `core.benchmark.__main__ → ... → fitz` |
| 3 | `pyproject.toml` contrato 1 | El contrato 1 ya tenía `ignore_import` para la misma cadena (por eso estaba "oculta") |

#### 2.3.4 Análisis

La condición original existe y es un hallazgo derivado de DF-05. Los `ignore_imports` huérfanos del contrato 1 estaban ocultando la cadena transitiva de DF-06. Al eliminar los ignores huérfanos (resolución de DF-05), el contrato 3 detectó la cadena que previamente estaba enmascarada.

La resolución es agregar un `ignore_import` explícito al contrato 3 para la cadena `core.benchmark.__main__ -> apps.bootstrap.pipeline_factory`, consistente con el tratamiento de DF-06 como ACCEPTED_LIMITATION.

Hallazgo adicional durante la resolución: import-linter 2.15 requiere `include_external_packages = true` en la configuración top-level cuando hay `forbidden_modules` externos. Esto se agregó como parte de la resolución.

#### 2.3.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Contrato 3 sin `ignore_import` para cadena DF-06 | `lint-imports` → BROKEN | Media |
| G2 | Falta `include_external_packages = true` | `lint-imports` → error de configuración | Media |

#### 2.3.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Contrato 3 como protección de dominio | ✅ Correcto por diseño | Protege a `core/` de imports de librerías de extracción |
| `forbidden_modules` externos (fitz, pymupdf, etc.) | ✅ Correcto por diseño | Son librerías que no deben ser importadas por el dominio |

#### 2.3.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Configuración de linter |
| Reproducibilidad | ⚠️ Sí (menor) | `lint-imports` reporta BROKEN, bloqueando CI |
| Corrección funcional | ❌ No | No afecta evaluación de regresión |
| Enforcement demostrable | ❌ No | No afecta contratos de merge protection |
| Bloquea Fase 18 | ❌ No | Resolución en Task 1.1.3 |

#### 2.3.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No — es configuración |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 6 | ✅ Sí |
| Bloquea Continuous Verification | ❌ No |
| Clasificación | `RESOLVED` |
| Prioridad | Media |

#### 2.3.9 Regla aplicada

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Todo fallo debe ser explícito."*

El contrato 3 BROKEN era una señal explícita de que la configuración estaba incompleta. La resolución hace que el contrato pase con un `ignore_import` documentado que rastrea la deuda de DF-06. La señal del linter queda limpia y cualquier violación futura será detectada.

---

### 2.4 DF-08 — PDF orphan en directorio canonical (Wave 3.3)

| Campo | Valor |
|-------|-------|
| **ID** | DF-08 |
| **Tipo** | Deferred Finding — Hallazgo de gobernanza del corpus |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 3.3 / Task 3.3.1 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — mover PDF orphan a archive |
| **¿Bloquea Continuous Verification?** | Sí — exit 3 (BASELINE_INTEGRITY_FAILURE) en toda ejecución |

#### 2.4.1 Texto original del DF

> *"tests/corpus/canonical/pdf/ contiene doc_06_johnstone.pdf que no está
> listado en manifest.json v3.9. BaselineCompletenessVerifier.verify_pdf_ids()
> falla con 'Orphan PDF (not in manifest): doc_06_johnstone' y exit code 3
> en toda ejecución del entry point de Continuous Verification, tanto en
> tests locales e2e como en CI."*

#### 2.4.2 Reformulación corregida

No requiere reformulación.

#### 2.4.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `tests/corpus/canonical/manifest.json` | Lista 21 documentos. `doc_06_johnstone` NO está listado |
| 2 | `tests/corpus/canonical/pdf/doc_06_johnstone.pdf` | Archivo existe (Test-Path: True), 563,435 bytes |
| 3 | `tests/corpus/canonical/ground_truth/doc_06_johnstone.json` | Archivo NO existe (Test-Path: False) |
| 4 | `manifest_hash` del DTO | `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d` (21 documentos) |
| 5 | Salida de `run_regression.py` (tests e2e) | `BASELINE_INTEGRITY_FAILURE: PDF completeness violations: Orphan PDF (not in manifest): doc_06_johnstone` |
| 6 | `BaselineCompletenessVerifier.verify_pdf_ids()` | Requiere biyección perfecta manifest ↔ PDFs (NADR-26 §5.3 R11-R12) |
| 7 | Documentación histórica de Fase 5 | Múltiples referencias a `doc_06_johnstone` en HITO_6.2, FASE_5_EXECUTION_PLAN, FASE_5_DEFERRED_FINDINGS_REGISTER |
| 8 | Tests que dependen del directorio pdf/ | Verificación previa: ningún test cuenta archivos en `canonical/pdf/` (solo tests de stress standalone no incluidos en suite) |
| 9 | `tools/evaluation/` | Verificación previa: ningún script asume presencia de `doc_06_johnstone` |

#### 2.4.4 Análisis

La condición original existe y es verificable empíricamente:
- El manifest v3.9 lista 21 documentos con Ground Truth sellado
- El directorio `tests/corpus/canonical/pdf/` contenía 22 PDFs (1 orphan)
- El Ground Truth correspondiente a `doc_06_johnstone` NO existe (no fue sellado en Fase 5)
- `BaselineCompletenessVerifier.verify_pdf_ids()` implementa NADR-26 §5.3 R11-R12: biyección perfecta manifest ↔ PDFs. Detecta el orphan y falla fail-fast con exit 3.

El PDF es orphan por diseño: en Fase 5 el documento se curó pero no se selló su Ground Truth correspondiente. Sin GT sellado, no puede incluirse en el manifest canónico. La documentación histórica de Fase 5 referencia `doc_06_johnstone` como documento del corpus en curación, pero el sellado no se completó.

No es violación de NADRs de Fase 6 por la implementación: la defensa en profundidad funciona correctamente (detecta la inconsistencia fail-fast con mensaje explícito). Es un problema de gobernanza del corpus que se resuelve moviendo el archivo fuera del directorio canónico.

Verificaciones previas al movimiento (empíricas):
1. Ningún test en `tests/unit/` ni `tests/integration/` depende de los 22 PDFs
2. Ningún script en `tools/evaluation/` asume presencia de `doc_06_johnstone`
3. El `manifest_hash` se calcula sobre el contenido del `manifest.json`, no sobre los PDFs del directorio → mover el PDF no altera el hash
4. `Test-Path` confirmó que el PDF existe y el GT no existe

#### 2.4.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | PDF orphan en directorio canonical | Test-Path: existe en `pdf/`, no en manifest | Alta (bloquea toda ejecución) |
| G2 | Ground Truth no sellado para doc_06 | Test-Path: no existe en `ground_truth/` | Media (limitación de Fase 5, aceptada) |

#### 2.4.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Manifest v3.9 con 21 documentos | ✅ Correcto | Refleja los documentos con GT sellado |
| `BaselineCompletenessVerifier.verify_pdf_ids()` | ✅ Correcto | Implementa NADR-26 §5.3 R11-R12 correctamente |
| Exit code 3 para orphan | ✅ Correcto | NADR-26 §5.6 R25: fallo de integridad ≠ regresión |
| manifest_hash invariante | ✅ Correcto | Hash calculado sobre `manifest.json`, no sobre PDFs |
| Documentación histórica de Fase 5 | ✅ Correcto | Referencia al documento en curación, no implica sellado |

#### 2.4.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | El hash del manifest es determinista e invariante |
| Reproducibilidad | ⚠️ Sí (antes de resolver) | Bloquea ejecución; resuelto con movimiento del PDF |
| Corrección funcional | ❌ No | La defensa fail-fast funciona correctamente |
| Enforcement demostrable | ❌ No | No afecta contratos de merge protection |
| Bloquea Fase 18 | ❌ No | Resolución simple: mover PDF |

#### 2.4.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No (defensa funciona correctamente) |
| Es violación de gobernanza | ✅ Sí (higiene del corpus canonical) |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 6 | ✅ Sí (detección por defensa de Fase 6) |
| Bloquea Continuous Verification | ✅ Sí (exit 3 en toda ejecución) |
| Clasificación | `RESOLVED` |
| Prioridad | Alta |

#### 2.4.9 Regla aplicada

> **NADR-F17BIS-26 §5.3 R11-R12:**
> *"La baseline canónica MUST presentar biyección perfecta entre los
> documentos listados en el manifest y los artefactos materializados en
> el entorno de ejecución."*

El PDF orphan violaba esta biyección. La resolución (mover el PDF fuera del
directorio canonical) restablece la biyección sin modificar la baseline sellada
(manifest v3.9 y su hash `727782fe...19f7d` permanecen invariados).

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> *"Todo fallo debe ser explícito o derivar en implementación."*

La detección fail-fast con exit 3 y mensaje explícito ("Orphan PDF:
doc_06_johnstone") cumplió correctamente este principio. No hubo fallo
silencioso. El assert contra BASELINE_INTEGRITY_FAILURE en los tests e2e
distinguió correctamente un problema de baseline de una divergencia
topológica real.

#### 2.4.10 Resolución y evidencia post-movimiento

**Acción ejecutada:**
- `doc_06_johnstone.pdf` movido de `tests/corpus/canonical/pdf/` a `tests/corpus/archive/`
- Creado `tests/corpus/archive/README.md` documentando el archivo

**Evidencia post-movimiento:**
- `manifest_hash` idéntico: `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`
- Tests e2e: 13/13 passed (antes del movimiento: 8 FAILED con exit 3)
- Suite completa: 906 passed, 5 skipped
- Import-linter: 4/4 KEPT
- Pyright: 0 errors

**Nota sobre el movimiento:** Durante la ejecución inicial de `Move-Item`, el destino `tests/corpus/archive/` no existía como directorio, y PowerShell interpretó el destino como nuevo nombre del archivo. El archivo fue renombrado a `archive` en `tests/corpus/`. Se corrigió con `Rename-Item` + `New-Item -ItemType Directory` + `Move-Item` al directorio correcto. Verificación post-corrección: el PDF está en `tests/corpus/archive/doc_06_johnstone.pdf` y NO está en `tests/corpus/canonical/pdf/`.

**Precisión terminológica (v0.8.1):** el forense demuestra que el conjunto
sellado (manifest v3.9, 21 GTs, manifest_hash 727782fe...19f7d) no fue mutado,
aumentado ni re-sellado. Lo que cambió fue el perímetro físico que debía ser
conforme con la baseline: se extrajo de él un artefacto intruso
(`doc_06_johnstone.pdf`) que nunca perteneció al conjunto sellado, restaurando
la biyección (NADR-26 §5.3 R11-R12).

---

### 2.5 DF-09 — Enforcement de merge de Continuous Verification diferido condicionalmente (Wave 4.1)

| Campo | Valor |
|-------|-------|
| **ID** | DF-09 |
| **Tipo** | Deferred Finding — Limitación operativa de enforcement |
| **Estado** | `ACCEPTED_LIMITATION` |
| **Origen** | Wave 4.1 / Tasks 4.1.1-4.1.2 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Media |
| **¿Requiere implementación?** | No inmediata — activación condicionada (cláusula 6.1 del contrato) |
| **¿Bloquea Continuous Verification?** | No — la verificación ejecuta y evidencia; lo diferido es el bloqueo de merge por regresión estructural |

#### 2.5.1 Texto original del DF

> *"Con branch protection activa, el único required check es static-analysis.
> regression-gates (SMOKE) y cv-full-profile (FULL) son informativos porque el
> estado basal del extractor es HARD_FAIL (exit 2): promoverlos a required hoy
> congelaría main con un rojo permanente que no distingue regresiones nuevas
> del estado basal. Una regresión estructural que no rompa static-analysis no
> bloquea integración hoy."*

#### 2.5.2 Reformulación corregida

No requiere reformulación. Se precisa el alcance: el hueco de push directo
originalmente considerado parte de este finding quedó **cerrado** por la
activación de required status checks (un commit nuevo sin checks pasados es
rechazado); DF-09 cubre exclusivamente el diferimiento del bloqueo por
regresión estructural (checks CV informativos).

#### 2.5.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `plans/FASE_6_ENFORCEMENT_CONTRACT.md` §3 | Tabla de checks: `static-analysis` REQUIRED; `regression-gates` y `cv-full-profile` informativos |
| 2 | `plans/FASE_6_ENFORCEMENT_CONTRACT.md` §4 y §6.1 | Trade-off sin eufemismos; cláusula de activación (basal PASS o recalibración gobernada DC-6.6); WARNING bloqueará al promocionar; wrapper prohibido (NADR-27 §5.6 R32) |
| 3 | `reports/evidence/branch-protection-main.png` y `-detail.png` | Regla activa sobre `main` con único required check "Static Analysis (pyright + import-linter)" |
| 4 | Salidas de ejecución FULL y SMOKE (2026-09-30) | exit code 2 en ambos perfiles (rojo basal confirmado empíricamente) |
| 5 | `.github/workflows/ci.yml` y `continuous-verification.yml` | Jobs CV existentes y operativos; producen artifacts con `if: always()` |
| 6 | Texto de UI GitHub "Require status checks to pass before merging" | Commits sin checks pasados son rechazados: hueco de push directo cerrado |

#### 2.5.4 Análisis

La condición existe y es una **decisión de diseño documentada**, no un defecto
oculto: con estado basal HARD_FAIL, promover checks CV a required produciría un
gate que bloquea el 100% de los merges sin distinguir regresiones nuevas
(teatro de enforcement, que termina bypasseado por frustración: peor que no
tener gate). La alternativa de gate relativo (bloquear solo si empeora el basal)
fue evaluada y rechazada: cambia la semántica de veredicto de NADR-19/NADR-27
sin gobernanza que lo autorice (cláusula de jerarquía normativa del ADR Maestro)
e introduce comparación entre ejecuciones que complica reproducibilidad (NADR-28).

#### 2.5.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Checks CV no bloquean merge hoy | Contrato §3 + branch protection detail | Media (regresión estructural no gateada) |
| G2 | ~~Hueco de push directo~~ | **CERRADO** por required status checks (UI text + rechazo de commits sin checks) | — |

#### 2.5.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Branch protection activa con required check | ✅ Correcto | MIG-01/MIG-04 con evidencia server-side; entrada sin checks rechazada |
| `static-analysis` como required | ✅ Correcto | Basal verde, determinista, rápido; bloquea errores de tipo y violaciones de arquitectura |
| Checks CV operativos e informativos | ✅ Correcto | Ejecutan, evidencian y artifactean; su promoción está condicionada y fechada por cláusula |
| Declaración del trade-off en contrato | ✅ Correcto | ENGINEERING_PRINCIPLES §IV: limitación explícita, no silenciosa |

#### 2.5.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Configuración de enforcement, no del mecanismo de verificación |
| Reproducibilidad | ❌ No | Evidencia completa persistida en todos los paths |
| Corrección funcional | ❌ No | CV detecta y clasifica correctamente (paths REGRESSION y FAILURE verificados) |
| Enforcement demostrable | ⚠️ Sí (parcial) | Bloqueo de merge activo para static-analysis; diferido para checks CV |
| Bloquea Fase 18 | ❌ No | Activación condicionada documentada; no impide operación |

#### 2.5.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No (decisión dentro de jerarquía: contrato deriva de NADR-30 y documenta desviación operativa) |
| Es problema técnico | ✅ Sí (operativo) |
| Pertenece a Fase 6 | ✅ Sí |
| Bloquea Continuous Verification | ❌ No |
| Clasificación | `ACCEPTED_LIMITATION` |
| Prioridad | Media |

#### 2.5.9 Regla aplicada

> **NADR-F17BIS-30 §5.3 R7-R10:** la relación resultado → integración está
> declarada y es verificable; su activación operativa para checks CV queda
> condicionada a cláusula 6.1 y documentada como limitación.
> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):** la limitación consta
> en contrato, Findings Register y Exit Review; no hay enforcement fantasma.

---

### 2.6 DF-10 — PASS path end-to-end no demostrable con estado basal del extractor (Wave 4.2)

| Campo | Valor |
|-------|-------|
| **ID** | DF-10 |
| **Tipo** | Deferred Finding — Precondición externa no satisfecha |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Wave 4.2 / Task 4.2.1 (BLOCKED) |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí, pero fuera de Fase 6 (mejora de extractor o recalibración gobernada) |
| **¿Bloquea Continuous Verification?** | No — bloquea el cierre completo de Gate 4 (CONDITIONAL PASS) |

#### 2.6.1 Texto original del DF

> *"Task 4.2.1 requiere una ejecución legítima del verification subject que
> produzca PASS contra la baseline sellada. FULL y SMOKE producen exit code 2
> (HARD_FAIL / REGRESSION) en ambos perfiles. No existe escenario PASS legítimo."*

#### 2.6.2 Reformulación corregida

No requiere reformulación.

#### 2.6.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | Salida de `run_regression.py --profile FULL` (2026-09-30) | exit code 2; stderr `REGRESSION:` |
| 2 | Salida de `run_regression.py --profile SMOKE` (2026-09-30) | exit code 2; stderr `REGRESSION:` |
| 3 | CV reports persistidos (`reports/full-check/`, `reports/smoke-check/`) | `corpus_verdict: HARD_FAIL`; `scientific_verdict: HARD_FAIL` |
| 4 | Estado basal documentado desde Fase 5 | NSS 0.7208 < threshold 0.80; 163 Critical FN |
| 5 | ADR_F17_BIS_MASTER §6 / DC-6.6 | Recalibración de thresholds es decisión de gobernanza separada, fuera de scope de Fase 6 |
| 6 | ROADMAP_ARQUITECTONICO_LP | Fase 17 congelada/completada; Fase 18 = Advanced Local Runtime (no fidelidad de extracción) |
| 7 | NADR-F17BIS-26 §5.5 R20-R22 | Fixtures o mini-corpus sintéticos no son baseline canónica: fabricar PASS los violaría |

#### 2.6.4 Análisis

La precondición de Task 4.2.1 (ejecución legítima PASS) es **verificable y falsa**
con el estado actual del extractor. El veredicto HARD_FAIL es científicamente
correcto (NADR-19 DoubleProtectionMechanism: NSS < 0.80 o ≥1 Critical FN ⇒
HARD_FAIL): el control detecta divergencias topológicas reales del pipeline
(doble columna, tablas anidadas, figuras, math), las mismas que producen texto
ilegible para traducción. Las tres vías para obtener PASS fueron descartadas
con justificación normativa: recalibrar (DC-6.6, fuera de scope), fabricar con
fixtures (NADR-26 §5.5 R20-R22), mockear (ENGINEERING_PRINCIPLES §IV).

#### 2.6.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | No existe ejecución legítima PASS contra baseline sellada | Exit 2 en FULL y SMOKE; NSS 0.7208 | Alta (impide validar path PASS → integration allowed) |

#### 2.6.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Veredicto HARD_FAIL basal | ✅ Correcto por diseño | NADR-19: el control funciona y detecta divergencia real |
| Paths REGRESSION y FAILURE | ✅ Correctos | Verificados end-to-end en Tasks 4.2.2 y 4.2.3 (exit 2 y exit 3 con evidencia) |
| Exit codes y evidencia en HARD_FAIL | ✅ Correctos | CV report completo con identity chain y regression_report |

#### 2.6.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | El veredicto es determinista para el estado basal |
| Reproducibilidad | ❌ No | Evidencia reproducible con identity chain completa |
| Corrección funcional | ❌ No | El control clasifica correctamente |
| Enforcement demostrable | ⚠️ Sí (parcial) | El path "PASS → integration allowed" no pudo ejercitarse en vivo |
| Bloquea Fase 18 | ❌ No | Destino explícito fuera de Fase 6 |

#### 2.6.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí (del extractor, no del control) |
| Pertenece a Fase 6 | ❌ No — resolución fuera de scope |
| Bloquea Continuous Verification | ❌ No (bloquea cierre completo del Gate) |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Prioridad | Alta |
| **Destino** | Fase futura no faseada de mejora de fidelidad de extracción, o recalibración gobernada de thresholds (DC-6.6). NO Fase 17 (congelada) ni Fase 18 (runtime) |

#### 2.6.9 Regla aplicada

> **Execution Plan v1.0.11 §5.2:** "No se fabrica un PASS para cerrar el gate."
> **NADR-F17BIS-27 §5.1 R1-R5:** el veredicto científico es independiente del
> estado operacional; HARD_FAIL basal no es un fallo del control.
> **NADR-F17BIS-30 §5.5 R14-R16 (por analogía):** un path no demostrado no se
> declara validado; se documenta como BLOCKED con finding derivado.

**Precisión factual (v0.8.1):** la limitación opera desde el cierre de Gate 4;
lo diferido es su retiro, condicionado a las cláusulas 6.1/6.3 del
ENFORCEMENT_CONTRACT (evidencia: contrato §3-§6 y branch protection activa con
static-analysis required).
**Referencia de clasificación:** conforme a la regla semántica de Findings
Register v0.10.1 §1.2. La evidencia de esta entrada permanece sin cambios.

---

### 2.7 DF-11 — Manifest corrupto escapaba del except de Pasos 1-2b (Wave 4.2)

| Campo | Valor |
|-------|-------|
| **ID** | DF-11 |
| **Tipo** | Deferred Finding — Hueco en manejo de errores |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 4.2 / Task 4.2.3 (detección durante diseño de tests) |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING_REVIEW |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — fix acotado en `run_regression.py` |
| **¿Bloquea Continuous Verification?** | Sí (potencial): exit 1 por excepción no controlada sin evidencia persistida |

#### 2.7.1 Texto original del DF

> *"El catch-all de EXECUTION_FAILURE (Task 2.1.3) envuelve `_run_evaluation()`
> (Pasos 3-7), no los Pasos 1-2b. Una `pydantic.ValidationError` o
> `json.JSONDecodeError` al cargar el manifest escapaba del except de
> precondiciones ⇒ traceback, exit 1 de Python, sin CV report persistido."*

#### 2.7.2 Reformulación corregida

No requiere reformulación.

#### 2.7.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `tools/evaluation/run_regression.py` (pre-fix) | `except (BaselineIntegrityError, IncompleteBaselineError, FileNotFoundError)` en Pasos 1-2b |
| 2 | Jerarquía de excepciones Python | `pydantic.ValidationError` ⊂ `ValueError`; `json.JSONDecodeError` ⊂ `ValueError`; ninguna ⊂ del tuple pre-fix |
| 3 | `run_regression.py` (pre-fix) Pasos 3-7 | Catch-all `except Exception` → EXIT_EXECUTION_FAILURE: no cubre Pasos 1-2b |
| 4 | `verify_ground_truth_preconditions` (Gate 1, Task 1.2.3) | Precedente del patrón correcto: `except (OSError, ValueError)` |
| 5 | `tests/integration/test_cv_failure_path.py` (post-fix) | `TestCorruptManifestPath`: JSON inválido y schema inválido ⇒ exit 3 + CV report |
| 6 | Traceability Appendix §10.2 | NADR-27 §5.6 R34 marcada DONE desde Wave 2.1: el hueco era contraejemplo vivo de una regla DONE |

#### 2.7.4 Análisis

La condición existe y es un hueco de cobertura del manejo de errores, no un
defecto de semántica: las precondiciones de baseline (Pasos 1-2b) tenían un
catch más estrecho que el resto del flujo. Con manifest corrupto, el proceso
moría con traceback y exit 1 (colisionando con WARNING, NADR-27 §5.6 R30) y sin
evidencia persistida (NADR-28 §5.3 R14). Diferir el fix habría hecho que Task
4.3.3 (traceability closure) certificara como DONE una regla con contraejemplo
demostrado: inaceptable bajo ENGINEERING_PRINCIPLES §IV.

#### 2.7.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Catch de Pasos 1-2b sin `OSError`/`ValueError` | Código pre-fix + reproducción con manifest corrupto | Alta |

#### 2.7.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Catch-all de Pasos 3-7 → exit 4 | ✅ Correcto | Cubre evaluación; no era el hueco |
| Exit codes 0/1/2/3/4 y su precedencia | ✅ Correctos | Sin cambios por el fix |
| `FileNotFoundError` como caso de exit 3 | ✅ Correcto | Queda cubierto por `OSError` (superclase), sin cambio de comportamiento |

#### 2.7.7 Impacto en Continuous Verification

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | El fix no introduce estado ni aleatoriedad |
| Reproducibilidad | ⚠️ Sí (pre-fix) | Sin evidencia persistida no hay reproducibilidad del fallo; corregido |
| Corrección funcional | ✅ Sí (pre-fix) | Exit 1 ambiguo y sin evidencia; corregido a exit 3 con evidencia |
| Enforcement demostrable | ❌ No | El exit code correcto propaga a CI sin reinterpretar |
| Bloquea Fase 18 | ❌ No | Resuelto en Gate 4 |

#### 2.7.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a Fase 6 | ✅ Sí |
| Bloquea Continuous Verification | ✅ Sí (potencial, pre-fix) |
| Clasificación | `RESOLVED` |
| Prioridad | Alta |

#### 2.7.9 Regla aplicada y resolución

> **NADR-F17BIS-27 §5.6 R34:** excepción no controlada ⇒ EXECUTION_FAILURE con
> evidencia; un crash con exit 1 en precondiciones violaba tanto R34 como R30
> (colisión con WARNING). **NADR-F17BIS-28 §5.3 R14:** toda ejecución persiste
> evidencia.

**Resolución:** except de Pasos 1-2b extendido a
`(BaselineIntegrityError, IncompleteBaselineError, OSError, ValueError)` con
comentario de trazabilidad (DF-11, R34, R14). Evidencia post-fix: 6/6 tests de
`test_cv_failure_path.py` passed (incluidos 2 de `TestCorruptManifestPath`);
suite completa 930 passed, 5 skipped; pyright 0 errors; import-linter 4/4 KEPT.

**Referencia de clasificación (v0.8.1):** DF-10 conserva
`RECLASSIFIED_FUTURE_PHASE`, conforme a la regla semántica definida en Findings
Register v0.10.1 §1.2 y al erratum de su §7.3 criterio 6. La evidencia de esta
entrada permanece sin cambios.

---

## 3. GATE EXIT REVIEW SUMMARY

### 3.1 Gate 1 Exit Review — Verification Foundation (2026-09-26)

**Gate:** Gate 1 — Verification Foundation
**NADRs:** NADR-F17BIS-25 (13 reglas), NADR-F17BIS-26 (28 reglas)
**Tasks:** 1.1.1, 1.1.2, 1.1.3, 1.2.1, 1.2.2, 1.2.3, 1.2.4
**Resultado:** ✅ COMPLETED — 41/41 reglas DONE, 7/7 Tasks DONE, 47 tests passed

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ✅ Sí (Task 1.1.3) | ✅ Sí | RESOLVED | Falta `include_external_packages = true` en configuración top-level |
| DF-05 | ✅ Sí | ✅ Sí (Task 1.1.3) | ✅ Sí | RESOLVED | `ignore_imports` huérfanos eliminados |
| DF-06 | ✅ Sí | ❌ No (deuda Gate 3-4) | ✅ Sí | ACCEPTED_LIMITATION | `core.benchmark.__main__` importa de `apps/` |
| DF-07 | ✅ Sí | ✅ Sí (Task 1.1.3) | ✅ Sí | RESOLVED | `ignore_import` agregado al contrato 3 |

**Resumen:**
- RESOLVED: 3 (DF-01, DF-05, DF-07)
- ACCEPTED_LIMITATION: 1 (DF-06)
- RECLASIFICADO → Gate {X}: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 4 (DF-01, DF-05, DF-06, DF-07 — todos de Wave 1.1)
- Hallazgos registrados en Wave 1.2: 0

---

### 3.2 Gate 2 Exit Review — Verification Contract (2026-09-29)

**Gate:** Gate 2 — Verification Contract
**NADRs:** NADR-F17BIS-27 (35 reglas), NADR-F17BIS-28 (34 reglas)
**Tasks:** 2.1.1, 2.1.2, 2.1.3, 2.2.1, 2.2.2, 2.2.3
**Resultado:** ✅ COMPLETED — 69/69 reglas DONE, 6/6 Tasks DONE, 835 tests passed (suite completa)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos en Gate 2 |

**Resumen:**
- RESOLVED: 0
- RECLASIFICADO → Gate {X}: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0 (ni en Wave 2.1 ni en Wave 2.2)

**Nota:** Gate 2 implementó la taxonomía operacional (NADR-27, Wave 2.1) y la
identity chain completa con evidencia persistente (NADR-28, Wave 2.2) sin
identificar hallazgos que requieran evidencia forense. Las decisiones
arquitectónicas congeladas están documentadas en el Findings Register v0.6.0
§2.2, y las notas de implementación en el Execution Plan v1.0.7 §3.1 y §3.2.

---

### 3.3 Gate 3 Exit Review — Continuous Verification Integration (2026-09-30)

**Gate:** Gate 3 — Continuous Verification Integration
**NADRs:** NADR-F17BIS-29 (35 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-29
**Tasks:** 3.1.1, 3.1.2, 3.1.3, 3.2.1, 3.2.2, 3.2.3, 3.3.1, 3.3.2, 3.3.3
**Resultado:** ✅ COMPLETED — 35/35 reglas DONE, 9/9 Tasks DONE, 906 tests passed (suite completa, incluye 13 e2e)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-08 | ✅ Sí | ✅ Sí (Task 3.3.1) | ✅ Sí | RESOLVED | PDF orphan movido a `tests/corpus/archive/`; baseline sellada invariante |

**Resumen:**
- RESOLVED: 1 (DF-08)
- RECLASIFICADO → Gate {X}: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 1 (DF-08 en Wave 3.3)

**Nota:** Waves 3.1 y 3.2 implementaron los perfiles de ejecución (FULL y SMOKE)
con `profile_identity` en la identity chain, `coverage` en el reporte, y la
integración completa de CI (resolviendo GAP-6.3-01 P0), sin identificar
hallazgos. Wave 3.3 validó end-to-end contra el corpus canónico real y detectó
DF-08 (PDF orphan), resuelto en la misma Task. Las decisiones arquitectónicas
congeladas están documentadas en el Findings Register v0.9.0 §2.3, y las
notas de implementación en el Execution Plan v1.0.10 §4.1, §4.2 y §4.3.

**Decisiones de diseño destacadas (documentadas en Findings Register):**

1. **Wave 3.1:** La selección del perfil SMOKE usa lista hardcoded de 5 documentos
   representativos en lugar de criterio por traits, basado en auditoría forense
   del corpus canonical que reveló que el criterio inicial producía solo 2
   documentos calificantes.

2. **Wave 3.2:** NO renombrar `regression-gates` a legacy para preservar branch
   protection existente (MIG-01 de Gate 4 actualizará después). FULL sin
   pull_request trigger (costo ~4 min por PR degrada experiencia; SMOKE ~1 min
   cubre PRs). Invocación como módulo (`python -m`) resuelve imports absolutos
   sin PYTHONPATH. `if: always()` en upload-artifact crítico para debugging de
   EXECUTION_FAILURE y BASELINE_INTEGRITY_FAILURE.

3. **Wave 3.3:** Marker `@pytest.mark.e2e` para tests lentos (~25s total).
   Veredicto científico válido sin asumir HARD_FAIL (robusto ante mejora futura
   de baseline). Assert contra fallos operacionales como defensa en profundidad.
   PDF orphan movido a archive/ (no eliminado) para preservar trazabilidad
   histórica del corpus.

**GAP-6.3-01 (P0) resuelto:** El job `regression-gates` ahora invoca
`python -m tools.evaluation.run_regression --profile SMOKE` en lugar de
`pytest -m "regression"` (que seleccionaba 0 tests). El workflow separado
`continuous-verification.yml` ejecuta el perfil FULL en push [main] +
workflow_dispatch. Esto cumple NADR-25 §5.2 R5-R7 y NADR-29 §5.5 R27
(entry point no omitido).

**Validación end-to-end (Wave 3.3):** Los 13 tests e2e verificaron contra el
corpus canónico real (21 documentos del manifest v3.9):
- FULL produce veredicto científico válido (REGRESSION: NSS ~0.72 < threshold 0.80)
- FULL coverage = 21 documentos
- SMOKE coverage = 5 documentos específicos
- smoke ⊂ full (subconjunto estricto)
- execution_id diferente entre perfiles (NADR-29 §5.6 R31)
- profile_identity diferente entre perfiles (NADR-29 §5.6 R28-R29)
- Determinismo de execution_id en dos ejecuciones equivalentes (NADR-28 §5.2 R8)
- exit code consistente con veredicto científico (NADR-27 §5.6 R29-R35)

---

### 3.4 Gate 4 Exit Review — Enforcement & Phase Closure (2026-09-30)

**Gate:** Gate 4 — Enforcement & Phase Closure
**NADRs:** NADR-F17BIS-30 (22 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-30
**Tasks:** 4.1.1-4.1.3, 4.2.1-4.2.3, 4.3.1-4.3.3
**Resultado:** ✅ COMPLETED — **CONDITIONAL PASS**: 22/22 reglas DONE, 8/9 Tasks DONE, 1 BLOCKED (4.2.1 → DF-10). 930 tests passed (suite completa), pyright 0 errors, import-linter 4/4 KEPT. MIG-01/MIG-04 con evidencia server-side (Task 4.1.3 RESOLVED).

**Árbol de decisión aplicado (5 pasos):**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | ¿Limitación externa? | Decisión | Motivo |
|----|----------|-------------|-----------|---------------------|----------|--------|
| DF-06 | ✅ Sí | ❌ No (fuera de scope Fase 6) | ✅ Sí | ❌ | RECLASSIFIED_FUTURE_PHASE | Refactor de composición del benchmark; no encaja en Gate 4 ni en Fase 18 |
| DF-09 | ✅ Sí | ❌ No (condicionado a basal PASS o DC-6.6) | ✅ Sí | ❌ | ACCEPTED_LIMITATION | Checks CV informativos hasta cláusula 6.1 del contrato |
| DF-10 | ✅ Sí | ❌ No (requiere mejora de extractor o recalibración) | ✅ Sí | ❌ | RECLASSIFIED_FUTURE_PHASE | PASS path no demostrable: HARD_FAIL basal legítimo en FULL y SMOKE |
| DF-11 | ✅ Sí | ✅ Sí (Task 4.2.3) | ✅ Sí | ❌ | RESOLVED | Except de Pasos 1-2b extendido a OSError + ValueError |

**Resumen:**
- RESOLVED: 1 (DF-11)
- RECLASIFICADO → fase futura: 2 (DF-06, DF-10)
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- ACCEPTED_LIMITATION: 1 (DF-09)
- Nuevos hallazgos registrados: 3 (DF-09, DF-10, DF-11) + 1 reclasificado (DF-06)

**Justificación del CONDITIONAL PASS:** Task 4.2.1 queda BLOCKED porque el estado
basal del extractor produce HARD_FAIL legítimo (NSS 0.7208 < 0.80, 163 Critical
FN); no existe PASS legítimo sin recalibración gobernada (DC-6.6) ni fabricación
de fixtures (NADR-26 §5.5 R20-R22). DF-09 documenta el diferimiento condicional
del enforcement de merge de CV. DoD Nivel B del ADR Maestro: satisfecho en
implementación local, verificación estática, corpus materializado y evidencia
server-side de enforcement; parcialmente satisfecho en PASS path end-to-end y en
bloqueo de merge por regresión estructural. Ambos con destino explícito.

**Nota:** Las decisiones arquitectónicas congeladas y lecciones aprendidas de
Gate 4 están documentadas en el Findings Register v0.10.0 §2.4; las notas de
implementación en el Execution Plan v1.0.11 §5.1-§5.3. La evidencia binaria
server-side vive en `docs/architecture/adr/phase-17-bis/reports/evidence/`
(`branch-protection-main.png`, `branch-protection-main-detail.png`, y
`branch-protection-pr-gate.png` al merge del PR de cierre).

---

## 4. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 5 | DF-01, DF-05, DF-07, DF-08, DF-11 |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 2 | DF-06, DF-10 |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 1 | DF-09 |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RESOLVED` | Falta `include_external_packages = true` en configuración top-level (Task 1.1.3) |
| DF-05 | `RESOLVED` | `ignore_imports` huérfanos eliminados del contrato 1 (Task 1.1.3) |
| DF-06 | `RECLASSIFIED_FUTURE_PHASE` | Refactor de composición de `core.benchmark.__main__`; destino: fase futura no faseada (reclasificado en Gate 4; ver §2.2.10) |
| DF-07 | `RESOLVED` | `ignore_imports` agregado al contrato 3 para la cadena transitiva DF-06 (Task 1.1.3) |
| DF-08 | `RESOLVED` | PDF orphan movido a `tests/corpus/archive/`; baseline sellada invariante (Wave 3.3) |
| DF-09 | `ACCEPTED_LIMITATION` | Enforcement de merge de CV diferido condicionalmente; activación por cláusula 6.1/6.3 del contrato (Wave 4.1) |
| DF-10 | `RECLASSIFIED_FUTURE_PHASE` | PASS path no demostrable con estado basal del extractor; destino: mejora de fidelidad o recalibración DC-6.6 (Wave 4.2, Task 4.2.1 BLOCKED) |
| DF-11 | `RESOLVED` | Except de Pasos 1-2b extendido a OSError + ValueError; manifest corrupto ⇒ exit 3 con evidencia (Wave 4.2) |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [x] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [x] Ningún hallazgo está en estado `PENDING_REVIEW`
- [x] La tabla consolidada final está completa
- [x] Cada clasificación tiene al menos una regla normativa aplicada
- [x] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito (DF-06: fase futura no faseada; DF-10: mejora de fidelidad o DC-6.6)
- [x] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación (N/A: ninguno en ese estado)
- [x] Los hallazgos relacionados con enforcement server-side (NADR-F17BIS-30 §5.5 R14-R16) tienen evidencia externa o están documentados como NO DEMOSTRADO con justificación explícita (evidencia externa obtenida: screenshots MIG-01/MIG-04; Task 4.1.3 RESOLVED)

**Freeze efectivo:** el documento pasa a `FROZEN` al merge del commit atómico de
cierre de Fase 6 (rama `gate-4-closure` → PR → main). Hasta ese momento permanece
`IN_PROGRESS` por protocolo.

### 5.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** (`FASE_6_DEFERRED_FINDINGS_REGISTER.md`) | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

---

## 6. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 8 |
| Hallazgos resueltos | 5 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos aceptados como limitación | 1 |
| Hallazgos reclasificados a fase futura | 2 |
| Estado del Exit Review | ✅ COMPLETED (Gate 4 CONDITIONAL PASS; FROZEN al merge del commit de cierre) |

### 6.1 Progreso por Gate

| Gate | Estado | Hallazgos | Secciones de evidencia |
|------|--------|-----------|---------|
| Gate 1 — Verification Foundation | ✅ COMPLETED (2026-09-26) | 4 (3 RESOLVED, 1 ACCEPTED_LIMITATION→reclasificado en Gate 4) | §2.0, §2.1, §2.2, §2.3 |
| Gate 2 — Verification Contract | ✅ COMPLETED (2026-09-29) | 0 | — |
| Gate 3 — Continuous Verification Integration | ✅ COMPLETED (2026-09-30) | 1 (DF-08 RESOLVED) | §2.4 |
| Gate 4 — Enforcement & Phase Closure | ✅ CONDITIONAL PASS (2026-09-30) | 4 (DF-11 RESOLVED, DF-09 ACCEPTED_LIMITATION, DF-10 RECLASSIFIED, DF-06 reclasificado) | §2.5, §2.6, §2.7 (+ §2.2.10) |

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review de Fase 6. No tiene autoridad normativa. No redefine reglas
de NADRs ni ADRs. Su único propósito es documentar la evidencia que fundamenta
cada clasificación del Findings Register, para que futuras sesiones o fases
no tengan que re-derivar conclusiones.

