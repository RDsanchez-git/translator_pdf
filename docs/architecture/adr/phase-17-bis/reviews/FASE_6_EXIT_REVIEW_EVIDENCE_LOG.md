# FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 0.7.0
**Estado:** IN_PROGRESS
**Fecha:** 2026-09-30
**Última actualización:** 2026-09-30
**Derivado de:** `PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.10 — Gate 3 Exit Review (COMPLETED: Waves 3.1 + 3.2 + 3.3)
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


---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER  >  ADR_F17_BIS_06 v1.2.0  >  NADR-F17BIS-25..30  >  PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.10
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
- **PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.10 §8 (Global DoD):** Un finding que afecta una regla normativa solo se cierra cuando es trazable a una implementación commiteada, un mecanismo de verification superado y un mecanismo de validation superado.

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
en las Notas de Implementación del Execution Plan v1.0.10 (§3.1, §3.2), no en
este Evidence Log (que registra únicamente evidencia forense de findings).

Wave 3.1 (Tasks 3.1.1-3.1.3) y Wave 3.2 (Tasks 3.2.1-3.2.3) no registraron
hallazgos nuevos. Wave 3.3 (Task 3.3.1) registró DF-08: PDF orphan en el
directorio canonical, resuelto moviendo el archivo a `tests/corpus/archive/`.
Gate 3 cierra con 1 finding analizado (DF-08 RESOLVED).

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
| **Estado** | `ACCEPTED_LIMITATION` |
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

### 3.4 Gate 4 Exit Review — Enforcement & Phase Closure ({YYYY-MM-DD})

**Gate:** Gate 4 — Enforcement & Phase Closure
**NADRs:** NADR-F17BIS-30 (22 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-30
**Tasks:** 4.1.1, 4.1.2, 4.1.3, 4.2.1, 4.2.2, 4.2.3, 4.3.1, 4.3.2, 4.3.3

**Nota específica de Gate 4:** Este Gate incluye Tasks con precondiciones externas:
- **Task 4.1.3:** Evidencia server-side de branch protection. Si no se puede obtener, el finding se clasifica como `ACCEPTED_LIMITATION` o `RECLASSIFIED_FUTURE_PHASE` con justificación explícita. NO DEMOSTRADO no es RESOLVED.
- **Task 4.2.1:** PASS path end-to-end. Si no existe un escenario PASS legítimo, el finding se clasifica como `ACCEPTED_LIMITATION` o `IMPLEMENTATION_REQUIRED` según corresponda. No se fabrica un PASS para cerrar el gate.

**Árbol de decisión aplicado (5 pasos):**

```text
1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
5. ¿Es una limitación externa al perímetro del repositorio? → SÍ: ACCEPTED_LIMITATION con evidencia
```

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | {Pendiente de ejecución} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- ACCEPTED_LIMITATION: {N} ({DF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})

---

## 4. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 4 | DF-01, DF-05, DF-07, DF-08 |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 0 | — |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 1 | DF-06 |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RESOLVED` | Falta `include_external_packages = true` en configuración top-level (Task 1.1.3) |
| DF-05 | `RESOLVED` | `ignore_imports` huérfanos eliminados del contrato 1 (Task 1.1.3) |
| DF-06 | `ACCEPTED_LIMITATION` | `core.benchmark.__main__` importa de `apps/`; deuda técnica diferida a Gate 4 (MIG-01) |
| DF-07 | `RESOLVED` | `ignore_imports` agregado al contrato 3 para la cadena transitiva DF-06 (Task 1.1.3) |
| DF-08 | `RESOLVED` | PDF orphan `doc_06_johnstone.pdf` movido de `tests/corpus/canonical/pdf/` a `tests/corpus/archive/`; baseline sellada invariante (Wave 3.3, Task 3.3.1) |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [ ] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [ ] Ningún hallazgo está en estado `PENDING_REVIEW`
- [ ] La tabla consolidada final está completa
- [ ] Cada clasificación tiene al menos una regla normativa aplicada
- [ ] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [ ] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación
- [ ] Los hallazgos relacionados con enforcement server-side (NADR-F17BIS-30 §5.5 R14-R16) tienen evidencia externa o están documentados como NO DEMOSTRADO con justificación explícita

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
| Total de hallazgos analizados | 5 |
| Hallazgos resueltos | 4 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos aceptados como limitación | 1 |
| Estado del Exit Review | 🟡 IN PROGRESS |

### 6.1 Progreso por Gate

| Gate | Estado | Hallazgos | Secciones de evidencia |
|------|--------|-----------|---------|
| Gate 1 — Verification Foundation | ✅ COMPLETED (2026-09-26) | 4 (3 RESOLVED, 1 ACCEPTED_LIMITATION) | §2.0, §2.1, §2.2, §2.3 |
| Gate 2 — Verification Contract | ✅ COMPLETED (2026-09-29) | 0 | — |
| Gate 3 — Continuous Verification Integration | ✅ COMPLETED (2026-09-30) | 1 (DF-08 RESOLVED) | §2.4 |
| Gate 4 — Enforcement & Phase Closure | ⏳ PENDING | 0 | — |

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review de Fase 6. No tiene autoridad normativa. No redefine reglas
de NADRs ni ADRs. Su único propósito es documentar la evidencia que fundamenta
cada clasificación del Findings Register, para que futuras sesiones o fases
no tengan que re-derivar conclusiones.