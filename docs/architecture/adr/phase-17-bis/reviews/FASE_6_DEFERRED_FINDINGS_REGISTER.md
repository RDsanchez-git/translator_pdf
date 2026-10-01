# FASE_6_DEFERRED_FINDINGS_REGISTER.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_6_DEFERRED_FINDINGS_REGISTER.md`
**Versión:** 0.10.1
**Estado:** IN_PROGRESS
**Fecha de creación:** 2026-09-25
**Última actualización:** 2026-09-30
**Derivado de:** `PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.11
**Propósito:** Registro auditable de hallazgos identificados durante la implementación
del Execution Plan de Fase 6 (Continuous Verification), su clasificación, resolución
y evidencia empírica de los batches.

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

ADR_F17_BIS_MASTER > ADR_F17_BIS_06 v1.2.0 > NADR-F17BIS-25..30 > PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.11

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
| `RECLASSIFIED_FUTURE_PHASE` | Diferido a fase futura con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `DEFERRED — FASE {X}` | Diferido a fase específica con ADR pendiente |

**Regla semántica de clasificación (v0.10.1):**

- `ACCEPTED_LIMITATION`: la limitación se acepta como condición operativa del
  sistema entregado. Su retiro no constituye trabajo de ingeniería comprometido
  dentro de esta fase; depende de un cambio de estado o de una cláusula de
  activación ya documentada. El sistema opera con la limitación y la declara.
- `RECLASSIFIED_FUTURE_PHASE`: la resolución del hallazgo requiere trabajo de
  ingeniería o decisión de gobernanza asignado a una fase futura. El hallazgo no
  se acepta como condición permanente: se difiere con destino explícito y
  condición de cierre.
- **Criterio discriminante (vía principal de resolución):**
  ¿El hallazgo tiene trabajo de resolución asignado a una fase futura?
  → `RECLASSIFIED_FUTURE_PHASE` (caso DF-10: mejora de fidelidad del extractor
  o decisión gobernada DC-6.6).
  ¿Su retiro depende únicamente de un cambio de estado o de una cláusula ya
  documentada, sin trabajo asignado al hallazgo?
  → `ACCEPTED_LIMITATION` (caso DF-09: el basal PASS activa la cláusula 6.1 sin
  desarrollo comprometido bajo este hallazgo).
- Se recomienda propagar esta definición a `6_METH_DEFERRED_FINDINGS_REGISTER`
  en la próxima revisión de metodología.

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir lista de archivos/documentos auditados.
- Cada finding **DEBE** distinguir: (a) gap confirmado, (b) hipótesis pendiente, (c) no-gap.
- Ningún finding se cierra sin evidencia de código o documental.
- No se implementa código durante el Exit Review. La implementación se agrupa en batches posteriores.

### 1.4 Protocolo de actualización dinámica

| Evento | Acción |
|--------|--------|
| Nuevo hallazgo identificado | Agregar entrada con ID secuencial, estado `PENDING_REVIEW` |
| Gate Exit Review ejecutado | Actualizar tabla del Gate, reclasificar hallazgos |
| Batch de implementación completado | Agregar sección de resultados con evidencia |
| Hallazgo reclasificado | Actualizar estado + justificación en tabla consolidada |
| Fase cerrada | Estado del documento → `ARCHIVED` |

### 1.5 Relación con el Execution Plan

Este registro es la **autoridad única** para el ciclo de vida de hallazgos.
El Execution Plan (`PHASE_17BIS_FASE6_EXECUTION_PLAN.md` v1.0.11) referencia
hallazgos por ID pero no los clasifica ni los resuelve.

Execution Plan (Task)
    ↓ identifica hallazgo
Deferred Findings Register (este documento)
    ↓ clasifica y resuelve
Findings Register (autoridad)
    ↓ registra batches
Commits / Tests (evidencia)

---

## 2. GATE EXIT REVIEWS

{Una sub-sección por cada Gate ejecutado. Se agregan dinámicamente conforme avanza la implementación.}

### 2.1 Gate 1 Exit Review — Verification Foundation (2026-09-26)

**Gate:** Gate 1 — Verification Foundation
**NADRs:** NADR-F17BIS-25 (13 reglas), NADR-F17BIS-26 (28 reglas)
**Tasks:** 1.1.1, 1.1.2, 1.1.3, 1.2.1, 1.2.2, 1.2.3, 1.2.4
**Estado:** ✅ COMPLETED (Wave 1.1 + Wave 1.2)
**Resultado:** 41/41 reglas DONE, 7/7 Tasks DONE, 47 tests passed, pyright 0 errors, import-linter 4/4 KEPT.

**Árbol de decisión aplicado:**

1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ✅ Sí (resuelto en Task 1.1.3) | ✅ Sí | RESOLVED | Contrato OCR providers roto por `include_external_packages`; resuelto con `ignore_imports` para cadena transitiva DF-06 |
| DF-05 | ✅ Sí | ✅ Sí (resuelto en Task 1.1.3) | ✅ Sí | RESOLVED | `ignore_imports` huérfanos eliminados del contrato 1 |
| DF-06 | ✅ Sí | ❌ No (deuda Gate 3-4) | ✅ Sí | ACCEPTED_LIMITATION | `core.benchmark.__main__` importa de `apps/`; se resolverá en Gate 3-4 |
| DF-07 | ✅ Sí | ✅ Sí (resuelto en Task 1.1.3) | ✅ Sí | RESOLVED | `ignore_imports` agregado al contrato 3 para la cadena transitiva DF-06 |

**Resumen Gate 1 (Wave 1.1 + Wave 1.2):**
- RESOLVED: 3 (DF-01, DF-05, DF-07)
- ACCEPTED_LIMITATION: 1 (DF-06)
- RECLASIFICADO → Gate {X}: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 4 (DF-01, DF-05, DF-06, DF-07 — todos de Wave 1.1)
- Hallazgos registrados en Wave 1.2: 0
- Revisiones tardías documentadas: 0

#### Decisiones arquitectónicas congeladas en Gate 1

| Decisión | Task | Justificación |
|----------|------|---------------|
| Función simple `verify_baseline_materialized` en Imperative Shell, no servicio de dominio | 1.2.1 | YAGNI (ENGINEERING_PRINCIPLES §I). La materialización se verifica en CI (MIG-02), no en el dominio |
| Funciones puras en `core/benchmark/corpus/integrity.py`, I/O en `run_regression.py` | 1.2.2 | Functional Core / Imperative Shell (ENGINEERING_PRINCIPLES §II) |
| `except (OSError, ValueError)` sin capturar `TypeError`/`AttributeError` | 1.2.3 | Cero Fallos Silenciosos (ENGINEERING_PRINCIPLES §IV). Errores de programación se propagan como bugs |
| `EXIT_BASELINE_INTEGRITY_FAILURE = 3` separado de exit codes de evaluación (0, 1, 2) | 1.2.4 | NADR-F17BIS-26 §5.6 R25. Fallo de integridad no es regresión |

#### Lecciones aprendidas

- import-linter 2.15 requiere `include_external_packages = true` cuando hay
  `forbidden_modules` externos (fitz, pymupdf, docling, PIL). La migración
  de import-linter 1.x a 2.x rompe contratos existentes si no se actualiza
  la configuración top-level.
- Los `ignore_imports` que referencian módulos inexistentes causan exit
  code 1 en import-linter 2.15. Deben eliminarse al migrar o refactorizar
  módulos.
- El `manifest_hash` vive en el DTO (`RawCorpusManifestDTO`), no en el modelo
  de dominio (`CorpusManifest`). Para verificar el hash, se debe extraer del
  DTO antes de la conversión. Esto es correcto por diseño: el hash es metadata
  del proceso de sellado, no identidad del contenido.
- `pydantic.ValidationError` es subclass de `ValueError` en Pydantic v2.
  `json.JSONDecodeError` también es subclass de `ValueError`. Capturar
  `except (OSError, ValueError)` cubre ambos sin capturar errores de programación.
- Un test de integración que mockea una función debe crear los artefactos
  previos necesarios para que el flujo llegue al mock. Un test que pasa
  por la razón equivocada (ej. `FileNotFoundError` antes del mock) es un bug.
- La combinación de propuestas puede ser necesaria para cubrir un rango
  completo de reglas. Ninguna propuesta individual puede ser suficiente
  si las reglas tienen dimensiones múltiples (completitud + legibilidad + orden).

---

### 2.2 Gate 2 Exit Review — Verification Contract (2026-09-29)

**Gate:** Gate 2 — Verification Contract
**NADRs:** NADR-F17BIS-27 (35 reglas), NADR-F17BIS-28 (34 reglas)
**Tasks:** 2.1.1, 2.1.2, 2.1.3, 2.2.1, 2.2.2, 2.2.3
**Estado:** ✅ COMPLETED (Wave 2.1 + Wave 2.2)
**Resultado:** 69/69 reglas DONE, 6/6 Tasks DONE, 835 tests passed (suite completa), pyright 0 errors, import-linter 4/4 KEPT.

**Árbol de decisión aplicado:**

1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| — | — | — | — | — | Sin hallazgos en Gate 2 |

**Resumen Gate 2 (Wave 2.1 + Wave 2.2):**
- RESOLVED: 0
- ACCEPTED_LIMITATION: 0
- RECLASIFICADO → Gate {X}: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 0
- Hallazgos registrados en Wave 2.1: 0
- Hallazgos registrados en Wave 2.2: 0
- Revisiones tardías documentadas: 0

#### Decisiones arquitectónicas congeladas en Gate 2

**Wave 2.1:**

| Decisión | Task | Justificación |
|----------|------|---------------|
| Bounded context `core/benchmark/verification/` separado de `topology/regression/` | 2.1.1 | NADR-27 §5.1 R1 exige separación científico/operacional. NADR-19 (científico) y NADR-27 (operacional) son bounded contexts distintos |
| `exit_code` como `@property` calculado en `ContinuousVerificationResult` | 2.1.2 | DRY: única fuente de verdad. Previene divergencia entre outcome y exit_code |
| `resolve_operational_outcome()` usa booleanos, no `Exception` | 2.1.2 | Functional Core puro (ENGINEERING_PRINCIPLES §II). No acopla el dominio a tipos de runtime |
| Extracción de `_run_evaluation()` + try/except → EXECUTION_FAILURE | 2.1.3 | NADR-27 §5.6 R34: excepción no controlada no es resultado científico válido |
| Única fuente de verdad para exit codes en `outcome.py` | 2.1.3 | ENGINEERING_PRINCIPLES §IV: elimina duplicación de constantes EXIT_* |

**Wave 2.2:**

| Decisión | Task | Justificación |
|----------|------|---------------|
| `IdentityChain` en bounded context `verification/`, no en `topology/regression/provenance.py` | 2.2.1 | Separación de bounded contexts NADR-28 (composición) vs NADR-23 (calculadores). Reutilización de calculadores existentes (ENGINEERING_PRINCIPLES §I) |
| `execution_id` = hash determinista de inputs (no UUID) | 2.2.1 | NADR-28 §5.2 R8: reproducibilidad. UUID aleatorio violaría determinismo |
| `result_identity` calculado DESPUÉS del reporte (evita circularidad) | 2.2.1 | Orden de construcción: execution_id no depende de result_identity; result_identity no depende de execution_id |
| `regression_report` opcional en `ContinuousVerificationReport` | 2.2.2 | NADR-27 §5.2 R8, R9: fallos operacionales no tienen resultado científico |
| `build_result_identity()` acepta `regression_report_json: str \| None` | 2.2.3 | Evolución de diseño: outcomes sin regression_report (BASELINE_INTEGRITY_FAILURE, EXECUTION_FAILURE) |
| Filename único `regression_report_{exec_id[:16]}_{timestamp}.json` sin `latest.json` (Opción C) | 2.2.3 | NADR-28 §5.4 R21: evitar sobrescritura de evidencia histórica. `latest.json` contradice el espíritu de R21 |
| `EvaluationArtifacts` dataclass en lugar de tuple | 2.2.3 | Tupla de 3 elementos posicionales es frágil. Dataclass es legible y extensible |
| Escritura de Markdown movida de `_run_evaluation()` a `main()` | 2.2.3 | ENGINEERING_PRINCIPLES §II: Imperative Shell centraliza I/O. Permite testear `main()` sin mocks internos |

#### Lecciones aprendidas

**Wave 2.1:**

- El test de determinismo para funciones puras es documentación del contrato,
  no verificación robusta. Su valor es documentar R29/R33 explícitamente.
  La garantía real de determinismo proviene de que la función es pura por
  construcción (sin I/O, sin estado, sin random, sin time).
- La duplicación de constantes entre módulos crea riesgo de divergencia
  silenciosa. Debe haber una única fuente de verdad, verificada con test AST.
- `except Exception` no captura `SystemExit` ni `KeyboardInterrupt` (son
  subclases de `BaseException`). Esto es correcto para el catch-all de
  EXECUTION_FAILURE: el `sys.exit()` del Paso 7 se propaga correctamente.
- Pyright requiere inicialización de variables que se asignan dentro de
  bloques try. Usar `manifest: CorpusManifest | None = None` y verificar
  `manifest is not None` antes de usarlo.
- Un test de integración que mockea una función debe asegurar que las
  precondiciones pasen para que el mock se ejecute. Si el manifest_hash
  no coincide, `verify_baseline_physical_integrity` lanza antes del mock.

**Wave 2.2:**

- La firma de una función puede necesitar evolución entre Tasks. `build_result_identity()`
  se diseñó con `regression_report_json` obligatorio en Task 2.2.1, pero Task 2.2.3
  identificó que outcomes sin evaluación (BASELINE_INTEGRITY_FAILURE, EXECUTION_FAILURE)
  requieren que sea opcional. Esto es evolución de diseño, no bug. Los tests de la
  Task original deben actualizarse cuando la firma cambia.
- Una tupla de 2 elementos es aceptable, pero si se necesita un tercer elemento,
  un dataclass es más SOTA que una tupla de 3 posicionales. La legibilidad y
  extensibilidad justifican el cambio.
- Los tests de entry point que mockean componentes individuales son frágiles
  ante cambios en el flujo interno. Mockear `_run_evaluation()` directamente
  es más robusto y aísla la lógica del entry point de los detalles internos.
- `mkdir(exist_ok=True)` es necesario en helpers de tests que pueden ejecutarse
  múltiples veces en el mismo `tmp_path`.
- La escritura de Markdown y JSON debe estar en `main()` (Imperative Shell),
  no en `_run_evaluation()`. Esto permite que `_run_evaluation()` sea más pura
  y que los tests mockeen sin perder la capacidad de verificar I/O.
- Al renombrar funciones privadas a públicas (`_serialize_evaluation_report` →
  `serialize_evaluation_report`), actualizar todas las llamadas internas y
  agregar al `__all__` del módulo. Esto mantiene la encapsulación explícita.

---

### 2.3 Gate 3 Exit Review — Continuous Verification Integration (2026-09-30)

**Gate:** Gate 3 — Continuous Verification Integration
**NADRs:** NADR-F17BIS-29 (35 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-29
**Tasks:** 3.1.1, 3.1.2, 3.1.3 (Wave 3.1), 3.2.1, 3.2.2, 3.2.3 (Wave 3.2), 3.3.1, 3.3.2, 3.3.3 (Wave 3.3)
**Estado:** ✅ COMPLETED (Waves 3.1 + 3.2 + 3.3)
**Resultado:** 35/35 reglas NADR-29 DONE, 9/9 Tasks DONE, 906 tests passed (suite completa, incluye 13 e2e), pyright 0 errors, import-linter 4/4 KEPT. GAP-6.3-01 (P0) resuelto.

**Árbol de decisión aplicado:**

1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-08 | ✅ Sí | ✅ Sí (resuelto en Task 3.3.1) | ✅ Sí | RESOLVED | PDF orphan `doc_06_johnstone.pdf` en `canonical/pdf/` sin entrada en manifest v3.9; movido a `tests/corpus/archive/` |

**Resumen Gate 3 (Waves 3.1 + 3.2 + 3.3):**
- RESOLVED: 1 (DF-08)
- ACCEPTED_LIMITATION: 0
- RECLASIFICADO → Gate {X}: 0
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 1 (DF-08 en Wave 3.3)
- Hallazgos registrados en Wave 3.1: 0
- Hallazgos registrados en Wave 3.2: 0
- Hallazgos registrados en Wave 3.3: 1 (DF-08)
- Revisiones tardías documentadas: 0

#### DF-08 — PDF orphan en directorio canonical (Wave 3.3)

| Campo | Valor |
|-------|-------|
| **ID** | DF-08 |
| **Tipo** | Deferred Finding — Hallazgo de gobernanza del corpus |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 3.3 / Task 3.3.1 (durante ejecución e2e de validación de perfiles) |
| **Gate destino** | Gate 3 (Continuous Verification Integration) |
| **Prioridad** | Alta (bloqueaba tests e2e y CI) |
| **¿Bloquea Continuous Verification?** | Sí — `verify_pdf_ids()` fallaba con `IncompleteBaselineError` (exit 3) |

**Texto del hallazgo:**

> `tests/corpus/canonical/pdf/` contiene `doc_06_johnstone.pdf` que NO está
> listado en `manifest.json` v3.9. Esto viola NADR-F17BIS-26 §5.3 R11-R12
> (biyección perfecta manifest ↔ PDFs), causando `IncompleteBaselineError`
> con mensaje "Orphan PDF (not in manifest): doc_06_johnstone" y exit code 3
> (BASELINE_INTEGRITY_FAILURE) en toda ejecución del entry point de
> Continuous Verification, tanto en tests locales e2e como en CI.

**Evidencia forense:**
- `manifest.json` v3.9 lista 21 documentos (hash `727782fe0df26d9dd401830a54785b03df5fd059ebf83cc422cb58d8a3d19f7d`)
- `tests/corpus/canonical/pdf/` contenía 22 PDFs (incluyendo `doc_06_johnstone.pdf`)
- `tests/corpus/canonical/ground_truth/` contiene 21 JSONs (sin `doc_06_johnstone.json`)
- `BaselineCompletenessVerifier.verify_pdf_ids()` requiere biyección perfecta
- Error observado: `BASELINE_INTEGRITY_FAILURE: PDF completeness violations: Orphan PDF (not in manifest): doc_06_johnstone`
- El Ground Truth correspondiente NO fue sellado en Fase 5 (limitación aceptada de esa fase)

**Resolución:**
- `doc_06_johnstone.pdf` movido a `tests/corpus/archive/`
- Creado `tests/corpus/archive/README.md` documentando el archivo
- Manifest v3.9 y su hash permanecen invariados (la baseline sellada no se modifica)
- Verificación post-movimiento: manifest_hash idéntico, tests e2e verdes, suite completa verde

**Impacto en baseline sellada:** NINGUNO. El `manifest_hash` se calcula sobre el contenido de `manifest.json`, no sobre los PDFs del directorio. Mover el PDF no altera la baseline sellada ni su identidad.
**Precisión terminológica (v0.10.1):** "baseline sellada invariante" refiere al
conjunto sellado (manifest v3.9, 21 GTs, manifest_hash 727782fe...19f7d). El
cambio físico consistió en extraer del perímetro canónico un artefacto que nunca
perteneció a ese conjunto sellado (intruso), restaurando la biyección
(NADR-26 §5.3 R11-R12). El conjunto sellado no fue mutado, aumentado ni re-sellado.

**Regla aplicada:**

> **NADR-F17BIS-26 §5.3 R11-R12:** "La baseline canónica MUST presentar
> biyección perfecta entre los documentos listados en el manifest y los
> artefactos materializados en el entorno de ejecución."

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):** La detección
> fail-fast con exit 3 y mensaje explícito cumplió correctamente este
> principio. No hubo fallo silencioso: el assert contra BASELINE_INTEGRITY_FAILURE
> en los tests e2e distinguió correctamente problema de pipeline de
> divergencia topológica real.

#### Decisiones arquitectónicas congeladas en Wave 3.1

| Decisión | Task | Justificación |
|----------|------|---------------|
| `VerificationProfile` enum en bounded context `verification/` | 3.1.1 | Consistente con Wave 2.1-2.2 (verification/outcome.py, verification/identity_chain.py) |
| Lista hardcoded de 5 docs para SMOKE en lugar de criterio por traits | 3.1.2 | El criterio por traits producía solo 2 documentos calificantes en el corpus actual; auditoría forense previa al diseño habría evitado esto |
| `profile_identity` incluido en `execution_id` (no solo en IdentityChain) | 3.1.3 | NADR-29 §5.6 R31: ejecuciones bajo perfiles diferentes producen execution_ids diferentes |
| `coverage: tuple[str, ...]` ordenado en reporte | 3.1.3 | `tuple` más explícito sobre ordenamiento determinista que `frozenset` |
| `--profile` flag en `run_regression.py` con filtrado en `_run_evaluation()` | 3.1.3 | Mecanismo común (NADR-29 §5.5 R24-R27): mismas verificaciones, misma semántica, diferente cobertura |

#### Decisiones arquitectónicas congeladas en Wave 3.2

| Decisión | Task | Justificación |
|----------|------|---------------|
| NO renombrar `regression-gates` a legacy | 3.2.1 | Preserva branch protection existente. Renombrado se hará en Gate 4 (MIG-01) cuando se actualice la configuración server-side |
| FULL sin pull_request trigger | 3.2.2 | Costo ~4 min por PR degrada experiencia de desarrollo. SMOKE (~1 min) cubre PRs (NADR-29 §5.4 R18) |
| Sin static-analysis en CV workflow | 3.2.2 | Separación de responsabilidades. Ambos workflows corren en paralelo |
| `python -m tools.evaluation.run_regression` | 3.2.1 | Invocación como módulo resuelve imports absolutos sin PYTHONPATH |
| Output dirs separados | 3.2.1, 3.2.2 | `reports/continuous-verification/` (FULL) vs `reports/continuous-verification-smoke/` (SMOKE) |
| Reemplazo total de `pytest -m "regression"` | 3.2.1 | El comando anterior seleccionaba 0 tests. No tiene sentido mantenerlo junto al nuevo |
| `if: always()` en upload-artifact | 3.2.1, 3.2.2 | Crítico para debugging de EXECUTION_FAILURE y BASELINE_INTEGRITY_FAILURE |
| Verificación de mutación del corpus | 3.2.1, 3.2.2 | NADR-26 §5.4 R16-R19: `git diff tests/corpus/canonical/` |

#### Decisiones arquitectónicas congeladas en Wave 3.3

| Decisión | Task | Justificación |
|----------|------|---------------|
| Marker `@pytest.mark.e2e` para tests lentos | 3.3.1 | ~25s de ejecución total; ejecutables bajo demanda sin ralentizar suite estándar |
| Veredicto científico válido sin asumir HARD_FAIL | 3.3.1 | Robusto ante mejora futura de baseline (Fase 18). El corpus actual produce REGRESSION (NSS ~0.72 < threshold 0.80), pero el test no acopla a ese estado específico |
| Assert contra fallos operacionales | 3.3.1 | Defensa en profundidad: distingue problema de pipeline de divergencia topológica real |
| PDF orphan movido a archive/ (no eliminado) | 3.3.1 | Preserva trazabilidad histórica del corpus. Reversible si se sella GT en el futuro |
| Sin fixture para tests e2e | 3.3.1 | El assert contra BASELINE_INTEGRITY_FAILURE es la defensa correcta. Un fixture sería redundante |

#### Lecciones aprendidas — Wave 3.1

- **Auditar datos reales antes de diseñar criterios.** La propuesta inicial de criterio por traits para SMOKE (`traits ⊆ {native_pdf}` + `page_count <= 5`) producía solo 2 documentos calificantes en el corpus actual. Una auditoría forense previa al diseño habría evitado este error. La lista hardcoded con justificación explícita es SOTA para este corpus específico.
- **Evolución de firmas entre Tasks es esperada, no un bug.** `build_execution_id()` se diseñó sin `profile_identity` en Wave 2.2 (Task 2.2.1), pero Wave 3.1 (Task 3.1.3) requirió agregarlo para cumplir NADR-29 §5.6 R31. Los tests de la Task original deben actualizarse cuando la firma cambia.
- **Combinar propuestas SOTA produce mejores resultados que elegir una sola.** Ni la primera ni la segunda propuesta de Task 3.1.3 eran completas por sí solas. La combinación (tests exhaustivos de una + CLI de la otra) produjo el resultado SOTA de grado producción.
- **`tuple[str, ...]` es preferible a `frozenset[str]` cuando el ordenamiento debe ser explícito.** Aunque `frozenset` es semánticamente correcto para un conjunto de document_ids, el ordenamiento determinista en JSON serializado requiere `tuple` ordenado.
- **Corrección de tipo Pyright `frozenset[Unknown]`.** Cuando se asigna `frozenset()` vacío en un branch condicional, Pyright infiere `frozenset[Unknown]`. La anotación explícita `profile_document_ids: frozenset[str]` resuelve el error de tipo.

#### Lecciones aprendidas — Wave 3.2

- **Branch protection es una dependencia implícita.** Renombrar jobs existentes sin considerar branch protection rompe CI hasta que MIG-01 actualice la configuración. Decisión pragmática: modificar contenido, no nombre.
- **Costo de CI impacta experiencia de desarrollo.** FULL (~4 min) en PRs es excesivo. SMOKE (~1 min) cumple NADR-29 §5.4 R18 (detección rápida).
- **Verificación de mutación del corpus es esencial.** `git diff tests/corpus/canonical/` es complemento necesario a `git diff tests/fixtures/` (oráculos).
- **Invocación como módulo (`python -m`) es obligatoria para scripts con imports absolutos.** Ejecutar `python tools/evaluation/run_regression.py` directamente causa `ModuleNotFoundError` porque Python agrega `tools/evaluation/` al PYTHONPATH, no el directorio raíz.
- **`if: always()` en upload-artifact es crítico para debugging.** Sin esto, los artifacts de evidencia no se suben cuando el job falla, impidiendo diagnosticar EXECUTION_FAILURE y BASELINE_INTEGRITY_FAILURE.
- **Tests de contrato de workflow son más robustos que yamllint.** Verificar la estructura semántica (invocación correcta, persist-credentials, upload-artifact) es más valioso que solo validar sintaxis YAML.

#### Lecciones aprendidas — Wave 3.3

- **La curación del corpus puede dejar artefactos orphans.** Fase 5 curó `doc_06_johnstone` pero no selló su Ground Truth. El PDF quedó en `canonical/pdf/` sin entrada en el manifest. La verificación de biyección `verify_pdf_ids()` (NADR-26 §5.3 R11-R12) detecta este tipo de inconsistencias fail-fast.
- **Mover un PDF fuera del directorio canonical NO modifica la baseline sellada.** El `manifest_hash` se calcula sobre el contenido de `manifest.json`, no sobre los PDFs del directorio. Esto permite limpieza de orphans sin re-sellar.
- **`Move-Item` de PowerShell interpreta destinos inexistentes como nuevo nombre de archivo.** Si el directorio destino no existe, `Move-Item -Destination "path/archive/"` renombra el archivo a `archive` en lugar de moverlo al directorio. Siempre crear el directorio destino antes con `New-Item -ItemType Directory`.
- **Tests e2e contra el pipeline real detectan problemas de gobernanza del corpus que los tests unitarios no ven.** El assert contra BASELINE_INTEGRITY_FAILURE en `_assert_scientific_verdict` distinguió correctamente un problema de baseline de una divergencia topológica real.
- **Simplificar tests ante estructuras serializadas complejas.** La versión inicial de `test_smoke_pass_does_not_imply_full_verification` intentaba comparar con `data["regression_report"]["documents"]` (lista de dicts no hashables). Simplificar a verificar `len(coverage) < EXPECTED_FULL_COVERAGE_SIZE` es más robusto y verifica la propiedad fundamental que R22 exige.
---

### 2.4 Gate 4 Exit Review — Enforcement & Phase Closure (2026-09-30)

**Gate:** Gate 4 — Enforcement & Phase Closure
**NADRs:** NADR-F17BIS-30 (22 reglas) + verificación transversal NADR-F17BIS-25 a NADR-F17BIS-30
**Tasks:** 4.1.1, 4.1.2, 4.1.3 (Wave 4.1), 4.2.1, 4.2.2, 4.2.3 (Wave 4.2), 4.3.1, 4.3.2, 4.3.3 (Wave 4.3)
**Estado:** ✅ COMPLETED (CONDITIONAL PASS) — 8/9 Tasks DONE, 1 BLOCKED (4.2.1)
**Resultado:** 22/22 reglas NADR-30 DONE, 930 tests passed (suite completa), pyright 0 errors, import-linter 4/4 KEPT. MIG-01/MIG-04 ejecutados con evidencia server-side (Task 4.1.3 RESOLVED, no NO DEMOSTRADO).

**Árbol de decisión aplicado:**

1. ¿Sigue siendo válido el hallazgo? → NO: CLOSED (NAR) / SÍ: continuar
2. ¿Puede resolverse dentro del Gate actual? → SÍ: RESOLVED / NO: continuar
3. ¿Es un problema técnico? → SÍ: RECLASIFICADO / NO: continuar
4. ¿Es un conflicto normativo? → SÍ: CONVERTIDO EN GF
5. ¿Es una limitación externa al perímetro del repositorio? → SÍ: ACCEPTED_LIMITATION con evidencia

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-06 | ✅ Sí | ❌ No (fuera de scope de Fase 6) | ✅ Sí | RECLASSIFIED_FUTURE_PHASE | Refactor de composición de `core.benchmark.__main__`; no encaja en Gate 4 (enforcement) ni en Fase 18 (runtime); destino: fase futura no faseada |
| DF-09 | ✅ Sí | ❌ No (condicionado a estado basal) | ✅ Sí | ACCEPTED_LIMITATION | Enforcement de merge de CV diferido condicionalmente (checks CV informativos hasta cláusula 6.1 del contrato) |
| DF-10 | ✅ Sí | ❌ No (requiere mejora de extractor o recalibración) | ✅ Sí | RECLASSIFIED_FUTURE_PHASE | PASS path no demostrable: FULL y SMOKE producen HARD_FAIL legítimo (NSS 0.7208 < 0.80) |
| DF-11 | ✅ Sí | ✅ Sí (resuelto en Task 4.2.3) | ✅ Sí | RESOLVED | Except de Pasos 1-2b extendido a OSError + ValueError; manifest corrupto ⇒ exit 3 con evidencia |

**Resumen Gate 4:**
- RESOLVED: 1 (DF-11)
- ACCEPTED_LIMITATION: 1 (DF-09)
- RECLASSIFIED_FUTURE_PHASE: 2 (DF-06 reclasificado desde Gate 1, DF-10 nuevo)
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 3 (DF-09, DF-10, DF-11) + 1 reclasificado (DF-06)
- Revisiones tardías documentadas: 0

#### DF-09 — Enforcement de merge de Continuous Verification diferido condicionalmente

| Campo | Valor |
|-------|-------|
| **ID** | DF-09 |
| **Tipo** | Deferred Finding — Limitación operativa de enforcement |
| **Estado** | `ACCEPTED_LIMITATION` |
| **Origen** | Wave 4.1 / Tasks 4.1.1-4.1.2 |
| **Gate destino** | Gate 4 |
| **Prioridad** | Media |
| **¿Bloquea Continuous Verification?** | No — la verificación ejecuta y evidencia; lo diferido es el bloqueo de merge por regresión estructural |

**Texto del hallazgo:**

> Con branch protection activa, el único required check es
> "Static Analysis (pyright + import-linter)". Los checks de Continuous
> Verification (`regression-gates` SMOKE, `cv-full-profile` FULL) son
> informativos porque el estado basal del extractor es HARD_FAIL (exit 2):
> promoverlos a required hoy congelaría `main` con un rojo permanente que no
> distingue regresiones nuevas del estado basal (teatro de enforcement).
> Consecuencia: una regresión estructural que no rompa static-analysis no
> bloquea integración hoy.

**Evidencia forense:**
- ENFORCEMENT_CONTRACT.md §3 (tabla de checks y estados), §4 (trade-off sin eufemismos), §6.1 (cláusula de activación)
- Ejecución empírica 2026-09-30: FULL y SMOKE ⇒ exit 2 contra corpus canónico
- Branch protection activa con único required check (screenshots en `reports/evidence/`)
- Nota: el hueco de push directo originalmente documentado quedó **cerrado** por la activación de required status checks (un commit nuevo sin checks pasados es rechazado); ver parche post-MIG-01 del contrato §4.2/§6.3

**Resolución (diferida, no cerrada):**
- Cláusula 6.1: promoción de checks CV a required cuando el estado basal sea PASS (exit 0 en FULL) o exista recalibración gobernada de thresholds (DC-6.6)
- Cláusula 6.3: migración opcional a PRs obligatorios + ruleset
- Comportamiento al promocionar declarado: WARNING (exit 1) también bloqueará; wrapper WARNING→0 prohibido por NADR-27 §5.6 R32

**Precisión terminológica (v0.10.1):** la limitación queda aceptada y vigente
desde el cierre de Gate 4; lo diferido es su *retiro*, condicionado a las
cláusulas 6.1/6.3 del ENFORCEMENT_CONTRACT (cambio de estado o configuración
documentada). No hay trabajo futuro comprometido dentro de Fase 6 bajo este
hallazgo. Conforme a la regla semántica de §1.2 (v0.10.1), este es el caso
canónico de ACCEPTED_LIMITATION.

**Regla aplicada:**

> **NADR-F17BIS-30 §5.3 R7-R10:** relación resultado → integración declarada y
> verificable; activación operativa condicionada y documentada.
> **ENGINEERING_PRINCIPLES §IV:** limitación documentada sin eufemismos, no silenciosa.

#### DF-10 — PASS path end-to-end no demostrable con estado basal del extractor

| Campo | Valor |
|-------|-------|
| **ID** | DF-10 |
| **Tipo** | Deferred Finding — Precondición externa no satisfecha |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Wave 4.2 / Task 4.2.1 (BLOCKED) |
| **Gate destino** | Gate 4 (Task 4.2.1 BLOCKED) |
| **Prioridad** | Alta |
| **¿Bloquea Continuous Verification?** | No — bloquea el cierre completo del Gate 4 (CONDITIONAL PASS) |

**Texto del hallazgo:**

> Task 4.2.1 requiere una ejecución legítima del verification subject que
> produzca PASS contra la baseline sellada. Verificación empírica 2026-09-30:
> `--profile FULL` y `--profile SMOKE` producen exit code 2 (HARD_FAIL /
> REGRESSION) en ambos perfiles (NSS 0.7208 < threshold 0.80, 163 Critical FN).
> No existe escenario PASS legítimo.

**Evidencia forense:**
- Ejecuciones empíricas: FULL exit 2, SMOKE exit 2 (stderr: `REGRESSION:`)
- Estado basal documentado desde Fase 5: NSS 0.7208, 163 Critical FN
- Alternativas descartadas: recalibrar thresholds (fuera de scope, DC-6.6 del ADR Maestro); fabricar PASS con fixtures (viola NADR-26 §5.5 R20-R22); mockear pipeline (viola ENGINEERING_PRINCIPLES §IV)

**Destino:** fase futura no faseada de mejora de fidelidad de extracción, o recalibración gobernada de thresholds (DC-6.6). **NO** Fase 17 (congelada y completada: PyMuPDF elegido por benchmark) ni Fase 18 (Advanced Local Runtime: asincronía/memoria/batching, no fidelidad de extracción).
**Nota de clasificación (v0.10.1):** conforme a la regla semántica de §1.2, la
vía principal de resolución es trabajo de ingeniería en fase futura (fidelidad
del extractor) o decisión de gobernanza DC-6.6 ⇒ RECLASSIFIED_FUTURE_PHASE. Ver
erratum de §7.3 criterio 6.

**Regla aplicada:**

> **Execution Plan v1.0.11 §5.2:** "No se fabrica un PASS para cerrar el gate."
> **NADR-F17BIS-27 §5.1 R1-R5:** el veredicto científico HARD_FAIL es correcto
> para el estado actual del extractor; no es un fallo del control.

#### DF-11 — Manifest corrupto escapaba del except de Pasos 1-2b

| Campo | Valor |
|-------|-------|
| **ID** | DF-11 |
| **Tipo** | Deferred Finding — Hueco en manejo de errores |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 4.2 / Task 4.2.3 (detección durante diseño) |
| **Gate destino** | Gate 4 |
| **Prioridad** | Alta |
| **¿Bloquea Continuous Verification?** | Sí (potencial): producía exit 1 por excepción no controlada sin evidencia |

**Texto del hallazgo:**

> El catch-all de EXECUTION_FAILURE (Task 2.1.3) envuelve `_run_evaluation()`
> (Pasos 3-7), no los Pasos 1-2b. Una `pydantic.ValidationError` o
> `json.JSONDecodeError` al cargar el manifest escapaba del except de
> precondiciones ⇒ traceback, exit 1 de Python, sin CV report persistido.
> Esto contradecía empíricamente NADR-27 §5.6 R34 (marcada DONE desde Wave 2.1)
> y reintroducía colisión con WARNING (R30).

**Evidencia forense:**
- Código: `except (BaselineIntegrityError, IncompleteBaselineError, FileNotFoundError)` en Pasos 1-2b de `run_regression.py` (pre-fix)
- `pydantic.ValidationError` ⊂ `ValueError`; `json.JSONDecodeError` ⊂ `ValueError`
- Precedente de patrón correcto: `verify_ground_truth_preconditions` (Gate 1, Task 1.2.3) ya usa `except (OSError, ValueError)`

**Resolución:**
- Except de Pasos 1-2b extendido a `(BaselineIntegrityError, IncompleteBaselineError, OSError, ValueError)` con comentario de trazabilidad (DF-11, NADR-27 §5.6 R34, NADR-28 §5.3 R14)
- `FileNotFoundError` ⊂ `OSError`: sin cambio de comportamiento para casos existentes
- 2 tests nuevos en `test_cv_failure_path.py` (`TestCorruptManifestPath`): JSON inválido y schema inválido ⇒ exit 3 + CV report persistido con clave `regression_report` ausente
- Catch-all exit 4 permanece para lo realmente inesperado fuera de precondiciones

**Regla aplicada:**

> **NADR-F17BIS-27 §5.6 R34:** excepción no controlada ⇒ EXECUTION_FAILURE, no
> exit 1 sin evidencia. **NADR-F17BIS-28 §5.3 R14:** evidencia siempre persistida.
> Decisión de no diferir: una regla marcada DONE no puede tener contraejemplos
> vivos al momento del traceability closure (Task 4.3.3).

#### Reclasificación de DF-06 (desde Gate 1)

| Campo | Valor previo | Valor nuevo |
|-------|-------------|-------------|
| Estado | `ACCEPTED_LIMITATION` (destino Gate 3-4) | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Gate 3-4 | Fase futura no faseada (refactor de composición del benchmark) |

**Justificación:** Gate 3 cerró sin resolver DF-06 (scope de Gate 3 era perfiles + CI, no refactor del benchmark). En Gate 4 se verificó que el refactor de `core/benchmark/__main__.py` (inyección de dependencias o puerto de extracción) **no encaja** en Fase 18 (Advanced Local Runtime: asincronía, memoria, batching) ni en el scope de enforcement de Gate 4. Resolverlo ahora introduciría riesgo innecesario sin beneficio para NADR-30. El `ignore_import` documentado en `pyproject.toml` permanece como mitigación explícita y trazable (contrato import-linter contrato 3).

#### Decisiones arquitectónicas congeladas en Gate 4

| Decisión | Task | Justificación |
|----------|------|---------------|
| Opción B transicional: `static-analysis` required, checks CV informativos | 4.1.1 | Evita teatro de enforcement con rojo basal permanente; activación condicionada documentada (cláusula 6.1) |
| Classic branch protection rule en transición, no ruleset | 4.1.1 | Ruleset con required checks rechaza push directo por chicken-and-egg; rompe el flujo sin aportar enforcement real al maintainer |
| Desviación de MIG-01 documentada: required check = "Static Analysis (pyright + import-linter)", no `regression-gates` | 4.1.3 | Coherente con Opción B; el texto original de MIG-01 predata la decisión del contrato §3 |
| Bypass de administradores: §9 del contrato declara ambos casos condicionalmente | 4.1.3 | Sin override no registrado; cualquier uso futuro de bypass debe registrarse como finding |
| DF-11 resuelto en Gate 4, no diferido | 4.2.3 | NADR-27 §5.6 R34 marcada DONE desde Wave 2.1; diferir el hueco haría que Task 4.3.3 certifique una regla con contraejemplo demostrado |
| Fix de imports `helpers.*` → `tests.helpers.*` en 3 tests de Fase 16, en vez de excluirlos | 4.3.2 | Excluir tests del pipeline por un import roto es burocracia, no ingeniería; fix de 2 líneas por archivo devuelve los tests a la suite |
| DF-06 y DF-10 reclasificados a fase futura no faseada | 4.3.3 | Ni Fase 17 (congelada) ni Fase 18 (runtime) son destino correcto; honestidad de trazabilidad |

#### Lecciones aprendidas — Gate 4

- **GitHub lista status checks por el nombre reportado (`name:` del job), no por el ID.** Buscar `static-analysis` en el selector de branch protection no devuelve resultados; el nombre real es "Static Analysis (pyright + import-linter)".
- **Con required status checks activos, el push directo de commits nuevos a `main` queda rechazado** (el commit aún no tiene checks pasados). La afirmación previa de que las classic rules "no muerden el push directo" era incorrecta; el flujo operativo pasa a rama → PR → merge, y eso cierra el hueco de entrada sin checks.
- **Un gate con rojo basal permanente es teatro de enforcement.** Promover checks CV a required con estado basal HARD_FAIL produciría un gate que bloquea todo sin distinguir regresiones nuevas; la cláusula de activación condicionada es la forma honesta de tener enforcement útil.
- **GitHub no tiene granularidad por exit code.** Al promocionar checks, WARNING (exit 1) también bloqueará merges; declararlo antes evita sorpresas y prohíbe wrappers que violarían NADR-27 §5.6 R32.
- **Las reglas marcadas DONE no pueden tener contraejemplos vivos.** DF-11 demostró un hueco empírico en NADR-27 §5.6 R34; resolverlo en el mismo Gate que lo detecta evita certificar trazabilidad falsa en el closure.
- **NO DEMOSTRADO se evita cuando existe camino alternativo de evidencia.** Sin `gh` CLI, el screenshot de la UI de GitHub es evidencia server-side válida para NADR-30 §5.5 R14-R16.
- **La letra chica de la UI es evidencia normativa.** El texto de "Require status checks" en GitHub corrige una suposición arquitectónica previa (refinamiento 6); leer la documentación del mecanismo antes de declarar huecos es parte del análisis forense.

---

## 3. TABLA CONSOLIDADA FINAL

Se actualiza al cierre del último Gate Exit Review.

### 3.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 0 | — |
| `RESOLVED — DELETE` | 0 | — |
| `RESOLVED` | 5 | DF-01, DF-05, DF-07, DF-08, DF-11 |
| `IMPLEMENTATION_REQUIRED` | 0 | — |
| `RECLASSIFIED_FUTURE_PHASE` | 2 | DF-06, DF-10 |
| `REVIEW_REQUIRED` | 0 | — |
| `ACCEPTED_LIMITATION` | 1 | DF-09 |

### 3.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| DF-01 | `RESOLVED` | Contrato OCR providers roto por `include_external_packages`; resuelto con `ignore_imports` para cadena transitiva DF-06 (Task 1.1.3) |
| DF-05 | `RESOLVED` | `ignore_imports` huérfanos eliminados del contrato 1 (Task 1.1.3) |
| DF-06 | `RECLASSIFIED_FUTURE_PHASE` | Refactor de composición de `core.benchmark.__main__`; destino: fase futura no faseada (antes ACCEPTED_LIMITATION con destino Gate 3-4; Gate 3 cerró sin resolverlo; Gate 4 verifica que no encaja en Fase 18) |
| DF-07 | `RESOLVED` | `ignore_imports` agregado al contrato 3 para la cadena transitiva DF-06 (Task 1.1.3) |
| DF-08 | `RESOLVED` | PDF orphan `doc_06_johnstone.pdf` movido de `tests/corpus/canonical/pdf/` a `tests/corpus/archive/`; baseline sellada invariante (Wave 3.3, Task 3.3.1) |
| DF-09 | `ACCEPTED_LIMITATION` | Enforcement de merge de CV diferido condicionalmente: checks CV informativos hasta cláusula 6.1 del ENFORCEMENT_CONTRACT (Wave 4.1) |
| DF-10 | `RECLASSIFIED_FUTURE_PHASE` | PASS path no demostrable con estado basal del extractor (NSS 0.7208 < 0.80); destino: mejora de fidelidad o recalibración gobernada DC-6.6 (Wave 4.2, Task 4.2.1 BLOCKED) |
| DF-11 | `RESOLVED` | Except de Pasos 1-2b extendido a OSError + ValueError; manifest corrupto ⇒ exit 3 con evidencia persistida (Wave 4.2, Task 4.2.3) |

---

## 4. RESULTADOS DE IMPLEMENTACIÓN POR BATCH

{Una sub-sección por cada batch ejecutado. Se agregan dinámicamente conforme avanza la implementación.}

### 4.1 Batches en Fase 6: ninguno planificado

**Estado:** N/A — no se planificaron ni requirieron batches de implementación.

**Justificación:** todos los hallazgos RESOLVED se resolvieron dentro de su
Wave/Task de origen, antes del Exit Review de su Gate: DF-01, DF-05, DF-07
(Task 1.1.3), DF-08 (Task 3.3.1), DF-11 (Task 4.2.3). El mecanismo de batches
("la implementación se agrupa en batches posteriores al Exit Review") aplica a
hallazgos cuya implementación se difiere más allá del Exit Review; en Fase 6 no
existió ninguno. DF-06, DF-09 y DF-10 no son batches: son diferimientos y
limitaciones sin implementación comprometida en esta fase.

**Efecto sobre §7.2 criterio 3 ("todos los batches planificados están
completados"):** el criterio se satisface porque el conjunto de batches
planificados es vacío (planificados = 0, completados = 0).



---

## 5. MÉTRICAS ACUMULADAS DE LA FASE

Se actualiza al cierre de cada batch.

| Métrica | Valor |
|---------|-------|
| Total de hallazgos analizados | 8 |
| Hallazgos resueltos | 5 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos reclasificados a fase futura | 2 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos aceptados como limitación | 1 |
| Batches completados | 0 |
| Archivos eliminados totales | 0 |
| Archivos movidos totales | 1 |
| Archivos creados totales | 33 |
| Archivos modificados totales | 16 |
| Tests finales | 930 passed, 5 skipped |
| Pyright final | 0 errors |

**Nota sobre "Archivos movidos totales: 1":** Corresponde a `doc_06_johnstone.pdf` movido de `tests/corpus/canonical/pdf/` a `tests/corpus/archive/` (DF-08, Wave 3.3).

**Nota sobre "Archivos creados totales: 33":** A los 25 previos se agregan en Gate 4 (8): `plans/FASE_6_ENFORCEMENT_CONTRACT.md`, `tests/helpers/cv_execution.py`, `tests/unit/test_enforcement_contract.py`, `tests/integration/test_cv_regression_path.py`, `tests/integration/test_cv_failure_path.py`, `handoff/FASE_6_HANDOFF.md`, `reports/evidence/branch-protection-main.png`, `reports/evidence/branch-protection-main-detail.png`. El artefacto `reports/evidence/branch-protection-pr-gate.png` se agregará en el commit del PR de cierre (evidencia MIG-04 de efectividad operativa).

**Nota sobre "Archivos modificados totales: 16":** A los 13 previos se agregan en Gate 4 (3): `tests/integration/test_translation_semantics.py`, `tests/integration/test_translation_structure.py`, `tests/integration/test_translation_technical.py` (fix de imports `helpers.*` → `tests.helpers.*`). `run_regression.py` y `pyproject.toml` ya estaban contabilizados por Gates previos.

Los "930 tests" son la suite completa del proyecto (incluye tests preexistentes de Fases anteriores). Tests nuevos de Fase 6: 47 (Gate 1) + 30 (Wave 2.1) + 38 (Wave 2.2) + 36 (Wave 3.1) + 22 (Wave 3.2) + 13 (Wave 3.3 e2e) + 24 (Gate 4: 12 contrato + 6 regression path + 6 failure path) = 210.

---

## 6. HALLAZGOS DIFERIDOS A FASES FUTURAS

| Hallazgo | Destino | Justificación |
|----------|---------|---------------|
| DF-06 | Fase futura no faseada | Refactor de composición de `core.benchmark.__main__` (inyección de dependencias o puerto de extracción); no encaja en Fase 18 (runtime) ni en scope de enforcement de Gate 4 |
| DF-10 | Fase futura no faseada, o recalibración gobernada DC-6.6 | PASS path no demostrable con estado basal del extractor; requiere mejora de fidelidad de extracción o decisión de gobernanza sobre thresholds |

**Vinculación operativa:** DF-09 (ACCEPTED_LIMITATION) no se difiere: permanece en Fase 6 con cláusula de activación propia (ENFORCEMENT_CONTRACT §6.1/§6.3). Su cierre operativo ocurre cuando DF-10 se resuelva (estado basal PASS) o exista recalibración gobernada.

### 6.1 Candidatos pre-identificados (resolución de anticipaciones)

| Escenario anticipado | Materializado | Resolución |
|---------------------|:---:|---|
| Evidencia server-side de branch protection no obtenible (Task 4.1.3) | ❌ No | MIG-01 ejecutado con screenshot de UI como evidencia válida (Task 4.1.3 RESOLVED); `gh` CLI ausente no impidió la evidencia |
| PASS path no demostrable (Task 4.2.1) | ✅ Sí | DF-10 (RECLASSIFIED_FUTURE_PHASE); Task 4.2.1 BLOCKED; Gate 4 CONDITIONAL PASS |
| Mecanismo de materialización de PDFs requiere infraestructura externa (MIG-02) | ❌ No | Corpus trackeado en git; el checkout materializa los PDFs (MIG-02 DONE) |
| Recalibración de thresholds para operatividad del gate | ⏳ Activo | Vinculado a DF-09/DF-10; decisión de gobernanza post-Fase 6 (DC-6.6) |

---

## 7. CRITERIOS DE CIERRE

### 7.1 Criterio de cierre por batch

Cada batch se considera cerrado cuando:
1. Todos los tests pasan (pytest → baseline mantenida)
2. Pyright reporta 0 errors
3. No se detectan imports huérfanos
4. Los cambios están commiteados

### 7.2 Criterio de cierre del Findings Register

El documento se considera cerrado (`ARCHIVED`) cuando:
1. No hay hallazgos en estado `IMPLEMENTATION_REQUIRED` sin batch asignado
2. No hay hallazgos en estado `REVIEW_REQUIRED` sin decisión
3. Todos los batches planificados están completados
4. Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito

### 7.3 Criterio específico de Fase 6

Adicionalmente, para Fase 6:
5. Los hallazgos relacionados con enforcement (NADR-F17BIS-30) tienen evidencia server-side o están documentados como NO DEMOSTRADO con justificación explícita.
6. Los hallazgos relacionados con el PASS path (Task 4.2.1) tienen evidencia de
   ejecución legítima, o están documentados como ACCEPTED_LIMITATION, o como
   RECLASSIFIED_FUTURE_PHASE con destino explícito y condición de cierre
   (consistente con §1.2 y §7.2 criterio 4).

   *Erratum v0.10.1:* la redacción original contemplaba únicamente
   ACCEPTED_LIMITATION porque precedía a la regla semántica de §1.2 y no
   consideraba RECLASSIFIED_FUTURE_PHASE, estado ya definido en §1.2 y gobernado
   por §7.2 criterio 4. Esta enmienda resuelve una inconsistencia interna de este
   documento (que no tiene autoridad normativa): no modifica Gate Exit Criteria,
   NADRs ni Execution Plan. Ningún nivel superior exige ACCEPTED_LIMITATION para
   DF-10 (Execution Plan §5.2/§5.4 solo exige BLOCKED + finding derivado +
   CONDITIONAL PASS). DF-10 conserva su clasificación: su vía principal de
   resolución es trabajo de ingeniería en fase futura.
7. Ningún hallazgo se cierra como RESOLVED si afecta una regla normativa sin cumplir los criterios de trazabilidad del Global DoD (PHASE_17BIS_FASE6_EXECUTION_PLAN v1.0.11 §8).

---

## 8. ESTADO DEL EXIT REVIEW

| Categoría | Cantidad |
|-----------|----------|
| Total de hallazgos analizados | 8 |
| Hallazgos resueltos | 5 |
| Hallazgos pendientes de implementación | 0 |
| Hallazgos pendientes de revisión | 0 |
| Hallazgos cerrados sin acción | 0 |
| Hallazgos aceptados como limitación | 1 |
| Hallazgos reclasificados a fase futura | 2 |
| Batches completados | 0/{Total} |
| Estado del Exit Review | ✅ COMPLETED (Gate 4 CONDITIONAL PASS; documento pasa a `ARCHIVED` tras el merge del commit de cierre de Fase 6) |

### 8.1 Progreso por Gate

| Gate | Estado | Hallazgos | Batches |
|------|--------|-----------|---------|
| Gate 1 — Verification Foundation | ✅ COMPLETED (2026-09-26) | 4 (3 RESOLVED, 1 ACCEPTED_LIMITATION→reclasificado en Gate 4) | 0 |
| Gate 2 — Verification Contract | ✅ COMPLETED (2026-09-29) | 0 | 0 |
| Gate 3 — Continuous Verification Integration | ✅ COMPLETED (2026-09-30) | 1 (DF-08 RESOLVED) | 0 |
| Gate 4 — Enforcement & Phase Closure | ✅ CONDITIONAL PASS (2026-09-30) | 4 (DF-11 RESOLVED, DF-09 ACCEPTED_LIMITATION, DF-10 RECLASSIFIED, DF-06 reclasificado) | 0 |

---

**Nota de Gobernanza:** Este documento es el registro operativo de trazabilidad
findings → clasificación → resolución → commit. No tiene autoridad normativa.
No redefine reglas de NADRs ni ADRs. Su único propósito es documentar la
evidencia empírica de los hallazgos identificados durante la implementación
del Execution Plan de Fase 6 y su resolución.