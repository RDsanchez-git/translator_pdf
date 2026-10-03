# FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED.md

**Documento:** `docs/architecture/adr/phase-17-bis/reports/FASE_17BIS_DEFERRED_FINDINGS_CONSOLIDATED.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-30
**Alcance:** Consolidación transversal de todos los hallazgos diferidos (DF), observaciones (O) y hallazgos de curaduría (H) de las Fases 1 a 6 de Phase 17-BIS.
**Propósito:** Proporcionar una visión unificada de la deuda técnica, limitaciones aceptadas y prerequisitos pendientes antes de iniciar la Fase 18 (Advanced Local Runtime) o futuras re-baselines.

---

## 1. EXECUTIVE SUMMARY

Al cierre de la Fase 6 (Continuous Verification), la Phase 17-BIS concluye con un veredicto global de **CONDITIONAL PASS**. Se materializó el Corpus Canónico v3.9, se blindó la identidad criptográfica y se establecieron los Regression Gates. 

Sin embargo, el análisis forense transversal revela **15 items pendientes** agrupados en 4 categorías estratégicas:
1. **Sinergias con Fase 18 (4 items):** Deuda técnica de runtime y composición que debe resolverse si la Fase 18 modifica el pipeline de ejecución.
2. **Re-baseline v4.0 (3 items):** Documentos del corpus actual que son tautológicos o tienen curaduría degradada, candidatos a sustitución.
3. **Gobernanza y Calibración (3 items):** Limitaciones operativas del enforcement de CI y la necesidad de recalibración estadística de thresholds (DC-6.6).
4. **Deuda Técnica Menor / Fases 19-21 (5 items):** Mejoras de schema, tests o capacidades de extracción que no bloquean el roadmap actual.

**Nota de resolución:** Varios hallazgos de fases tempranas (ej. DF-18 de Fase 2 sobre exit codes, DF-04 de Fase 4 sobre ZhangShasha vs APTED, y DF-11 de Fase 6 sobre manejo de errores de manifest) fueron **resueltos o superseded** por el trabajo de las Fases 5 y 6, y se excluyen de esta lista de pendientes.

---

## 2. CONSOLIDATED FINDINGS TABLE

| ID | Fase Origen | Descripción | Destino | Bloquea | Prioridad |
|----|-------------|-------------|---------|---------|:---:|
| **DF-06** | Fase 6 | `core.benchmark.__main__` importa `apps/` (cadena transitiva a infra) | **Fase 18** (Refactor de composición del benchmark) | Nada operativo (mitigado con `ignore_import`) | 🟡 Media |
| **DF-12-C/D/E** | Fase 1 | Migrar `FlatASTBuilder` → `list[LayoutBlock]` directo (eliminar `LayoutBlockDraft`/`Collection`) | **Fase 18** (Refactor de runtime) | Nada (deuda técnica de mapeo) | 🟢 Baja |
| **DF-18** | Fase 1 | `ExecutionContext` unificado transversal | **Fase 18 / 20** (Coordinación u Observabilidad) | Nada (bounded contexts actuales son correctos) | 🟢 Baja |
| **DF-24** | Fase 1 | `CircuitBreakerStore` persistente (distribuido) | **Fase 18** (Solo si se demuestra necesidad multi-proceso) | Nada (single-node hoy) | 🟢 Baja |
| **H-5.3-3** | Fase 5 | Curaduría real de `doc_07` (tablas Type 3 sin ToUnicode) | **Re-baseline v4.0** | Nada | 🟡 Media |
| **H-5.5-2** | Fase 5 | Sustitución de `doc_09`, `doc_10` (tautológicos por curaduría original) | **Re-baseline v4.0** | Nada | 🟡 Media |
| **H-5.6-1** | Fase 5 | Curaduría sobrescrita en `doc_11-13` (regenerados como degradados, NSS=1.0000) | **Re-baseline v4.0** | Nada (mitigado por gate O2) | 🟡 Media |
| **DF-09** | Fase 6 | Enforcement de merge de CV diferido (checks CV informativos hasta cláusula 6.1/6.3) | **Fase 6+** (Activación condicionada por basal PASS o DC-6.6) | Promoción de checks CV a required | 🟡 Media |
| **DF-10** | Fase 6 | PASS path no demostrable: estado basal HARD_FAIL (NSS 0.7208, 163 Critical FN) | **Fase futura / DC-6.6** (Mejora de extractor o recalibración gobernada) | Cierre completo del enforcement (CONDITIONAL PASS) | 🔴 Alta |
| **DF-34** | Fase 1 | `ProfileStore` durable (no `InMemoryProfileStore`) | **Fase 18** (Recovery Gate) | Recovery Gate (si se implementa daemon de recuperación) | 🔴 Alta |
| **DF-17** | Fase 1 | Extracción de imágenes (PyMuPDF type==1 descartado) | **Fase 21** (Parser Routing / Asset Management) | Nada (dominio ya soporta IMAGE conceptualmente) | 🟢 Baja |
| **DF-04** | Fase 1 | `HARD_BREAK` en chunking requiere semántica de contexto cruzado en AST | **Post-Fase 18** | Nada (ALLOW es correcto hoy) | 🟢 Baja |
| **O-5.3-1** | Fase 5 | `NodeMetadata` sin campo `note` para footnotes | **Fase 18+** (Extensión de schema) | Nada | 🟢 Baja |
| **O-5.4-1** | Fase 5 | Enum `ExtractionChallengeTrait` sin trait `code` | **Fase 18+** (Extensión de catálogo) | Nada | 🟢 Baja |
| **DF-01 (F2/F4)**| Fase 2/4 | Deuda en tests: copias de helper `_make_node` y tests tautológicos (`test_golden_parser`) | **Fase 18** (Refactor test-infra) | Nada | 🟢 Baja |

---

## 3. CRITICAL PATH & ACTION PLAN

### 3.1 Prerrequisitos para Fase 18 (Advanced Local Runtime)
Si la Fase 18 toca el runtime o la composición del benchmark, **debe** abordar:
1. **Resolver DF-06:** Eliminar la dependencia transitiva de `core.benchmark.__main__` hacia `apps/` mediante inyección de dependencias o un puerto de extracción. Al hacerlo, eliminar el `ignore_import` del contrato 3 de import-linter.
2. **Resolver DF-34:** Implementar `SQLiteProfileStore` (o mecanismo de re-inferencia desde AST) para que el Recovery Gate pueda sobrevivir a crashes de daemon sin perder perfiles en cola.
3. **Evaluar DF-12-C/D/E:** Si se refactoriza el pipeline de ensamblaje, eliminar la capa transicional `LayoutBlockDraft`/`LayoutBlockCollection` y pasar `list[LayoutBlock]` directo al `FlatASTBuilder`.

### 3.2 Plan de Re-baseline v4.0 (Curaduría)
Para elevar la calidad del corpus y eliminar la tautología (~28.6% de los documentos), se debe ejecutar un batch de sustitución:
- **Reemplazar:** `doc_07`, `doc_09`, `doc_10`, `doc_11`, `doc_12`, `doc_13`.
- **Requisito:** Los nuevos documentos deben pasar el gate O2 de curaduría *antes* del sellado, garantizando que no sean regenerados automáticamente por `generate_golden_draft.py` con tipos degradados.
- **Impacto:** Requerirá re-sellado del manifiesto (nuevo `manifest_hash`) y re-ejecución de la FINAL EVALUATION para validar si el NSS basal mejora.

### 3.3 Gobernanza y Calibración (DC-6.6)
- **DF-10 / H-5.3-1 / H-5.3-2:** La divergencia masiva (163 Critical FN, NSS 0.7208) es una limitación empírica del extractor PyMuPDFProvider, no un fallo del control de regresión. 
- **Acción:** No modificar thresholds en código. Cualquier recalibración de los valores 0.80/0.95 debe seguir el protocolo de gobernanza DC-6.6 (curvas precision-recall + bootstrap CI + human verdicts sobre N=21), o bien, la Fase 18/21 debe integrar un extractor alternativo (Marker, Docling, Nougat) que reduzca la divergencia estructural.

---

## 4. RESOLVED / SUPERSEDED FINDINGS (Histórico)

Los siguientes hallazgos fueron identificados en fases tempranas pero **ya no están pendientes** debido al trabajo de las Fases 5 y 6. Se listan para evitar duplicación de esfuerzo:

| ID Original | Descripción | Estado Actual | Resolución |
|---|---|---|---|
| **DF-18 (Fase 2)** | Entry points retornan exit code 0 en fallo | ✅ RESOLVED | Fase 5 implementó "Semántica de fallo uniforme" (exit codes 0-4) en todos los runners. |
| **DF-19 (Fase 2)** | Migración de formato de hash del manifiesto (4 → 6 dimensiones) | ✅ RESOLVED | Fase 5 materializó el Corpus v3.9 con el formato de 6 dimensiones (`oracle_hash`, `ground_truth_state`). |
| **DF-04 (Fase 4)** | Dualidad ZhangShasha/APTED — benchmark comparativo | ✅ RESOLVED | Fase 5 ejecutó el benchmark (divergencia 8.56%). Se decidió: ZhangShasha es canónico (integra criticidad), APTED es experimental no-normativo. |
| **DF-11 (Fase 6)** | Manifest corrupto escapaba del except de Pasos 1-2b | ✅ RESOLVED | Gate 4 extendió el catch a `OSError` + `ValueError`, garantizando exit 3 con evidencia. |
| **GF-03 (Fase 5)** | Onboarding sin curaduría previa (doc_09, doc_10) | ✅ MITIGADO | Fase 5 implementó el gate O2 en `freeze_ground_truth.py` que bloquea el sellado si no existe `curation_checklist.json`. |

---

## 5. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente en una nueva conversación para continuar el trabajo en Fase 18 o Re-baseline v4.0.

```text
FASE 17-BIS DEFERRED FINDINGS — CONSOLIDADO (v1.0.0)
====================================================

Total Items Pendientes: 15

CRÍTICOS (Bloqueantes o de Alta Prioridad para Fase 18):
- DF-06: Refactor composición benchmark (core importa apps/). Sinergia natural con Fase 18.
- DF-34: ProfileStore durable (Recovery Gate).
- DF-10: PASS path no demostrable (NSS 0.7208). Requiere DC-6.6 o nuevo extractor.

RE-BASELINE v4.0 (Sustitución de documentos tautológicos):
- H-5.3-3: doc_07 (tablas Type 3)
- H-5.5-2: doc_09, doc_10 (curaduría original degradada)
- H-5.6-1: doc_11, doc_12, doc_13 (sobrescritos por generate_golden_draft)

GOBERNANZA DIFERIDA:
- DF-09: Enforcement CV diferido (checks informativos hasta cláusula 6.1/6.3).

DEUDA TÉCNICA MENOR / FASES 19-21:
- DF-12-C/D/E, DF-18, DF-24, DF-17, DF-04(F1), O-5.3-1, O-5.4-1, DF-01(F2/F4).

RESUELTOS EN FASES 5-6 (No re-abrir):
- DF-18(F2) [Exit codes], DF-19(F2) [Hash 6 dimensiones], DF-04(F4) [ZhangShasha vs APTED], DF-11(F6) [Manifest error handling].

RESTRICCIONES CARRY-FORWARD OBLIGATORIAS:
1. No mutar oráculos sellados sin crear nueva versión de corpus (v4.0).
2. Calibration ≠ Evaluation (NADR-23).
3. Motor canónico único: ZhangShasha + CriticalityAwareCostContext.
4. Zero Partial Sealing: biyección N_PDF = N_GT obligatoria.
5. Exit codes 0-4 propagan sin reinterpretar (wrapper WARNING→0 prohibido).
```

**Nota de Gobernanza:** Este documento consolida la deuda técnica y los hallazgos diferidos de toda la Phase 17-BIS. No reemplaza los Findings Registers individuales de cada fase, sino que los complementa con una visión transversal orientada a la acción. Los items marcados como críticos deben evaluarse en el Gate 0 de la Fase 18; los demás pueden diferirse o resolverse según la evolución del roadmap.