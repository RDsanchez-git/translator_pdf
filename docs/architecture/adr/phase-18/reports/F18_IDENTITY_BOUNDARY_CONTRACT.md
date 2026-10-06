# F18_IDENTITY_BOUNDARY_CONTRACT.md

**Documento:** `docs/architecture/adr/phase-18/decisions/F18_IDENTITY_BOUNDARY_CONTRACT.md`
**Estado:** FROZEN v1.0.1
**Fecha:** 2026-10-05
**Tipo:** Contrato provisional de identidad científica (DC-02-A)
**Naturaleza:** Read-only. Define la frontera entre scientific identity, execution
  identity y operational state para el guard diferencial (DC-12).
**Evidencia vinculante:** HITO_0.4 v1.3.0 (E-0.4-001 a E-0.4-005);
  HITO_0.11 v1.0.1 (§7 contratos de comparación);
  HITO_0.12 v1.0.1 (§5.3 DC-02, §4.2 DAG);
  ADR_F18_MASTER §3 (separación de conceptos);
  NADR-F18-01 §5.2 R8 (execution identity excluida de scientific identity);
  `core/benchmark/verification/identity_chain.py` (build_identity_chain);
  `core/benchmark/verification/report.py` (ContinuousVerificationReport).
**Mandato:** Definir qué parámetros pertenecen a scientific identity y cuáles a
  operational metadata. Establecer el contrato de comparación para el guard
  diferencial (DC-12).
**Alcance:** DC-02-A (contrato provisional). DC-02-B (consolidación definitiva)
  queda pendiente post DC-12 según HITO_0.12 §4.2.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-05 | Emisión inicial. |
| 1.0.1 | 2026-10-05 | Corrección de 6 puntos: (C1) Contradicción de execution_id resuelta; DF-13 derivado al Findings Register. (C2) Cláusula de invalidación fortalecida con 3 condiciones concretas + proceso de escalación. (C3) Sección de gobernanza de modificaciones agregada. (C4) Identidad de workload y GAP-0.3-03 documentados. (C5) Matriz de verificación regla-por-regla de las 10 reglas de Wave 2.1 agregada. (C6) Documento movido a decisions/. |

---

## 1. RESUMEN EJECUTIVO

Se define la frontera de identidad para Fase 18 en tres dimensiones ortogonales:

| Dimensión | Naturaleza | Tolerancia en guard | Ejemplo |
|---|---|---|---|
| **Scientific Identity** | Invariante, intocable | Tolerancia cero (bit-exact) | baseline hash, config hash, AST hash |
| **Execution Identity** | Identificable, reproducible | Puede diferir entre ejecuciones | execution_id, subject_identity, model_de_execution |
| **Operational State** | Observable, variable | Puede diferir libremente | timestamps, RSS, scheduling order, retry timing |

**Principio rector:** *Misma baseline + misma config + mismo profile ⇒ misma
scientific identity, independiente de execution identity y operational state.*

---

## 2. FRONTERA DE IDENTIDAD

### 2.1 Scientific Identity (invariante, tolerancia cero)

La scientific identity es el conjunto mínimo de parámetros que determinan
unívocamente el resultado científico. Dos ejecuciones con la misma scientific
identity DEBEN producir el mismo resultado científico (INV-SCI-1).

| Componente | Fuente | Hash function | Incluido en `identity_chain` |
|---|---|---|---|
| `baseline_identity` | SHA-256 del manifest sellado (CorpusManifest) | `ManifestFingerprintCalculator.compute_hash()` | ✅ Sí |
| `configuration_identity` | Fingerprint de configuración canónica | `ConfigurationFingerprintCalculator.calculate()` | ✅ Sí |
| `profile_identity` | Hash de perfil + document_ids (ordenado) | `build_profile_identity()` | ✅ Sí |
| `result_identity` | Hash de outcome + verdict + regression_report | `build_result_identity()` | ✅ Sí |

**Componentes de `configuration_identity`:**
- `matching_policy`: DefaultNodeMatchingPolicy
- `cost_context`: CriticalityAwareCostContext weights (CRITICAL, WARNING, INFO)
- `engine_configuration`: build_canonical_engine_configuration output

**Regla de no-colapso:** Ningún parámetro de execution identity u operational
state puede formar parte de scientific identity (NADR-F18-01 §5.2 R8).

### 2.2 Execution Identity (identificable, reproducible)

La execution identity identifica el modo/política de ejecución. Es reproducible
(dado el mismo modo, se puede reproducir) pero NO forma parte de scientific
identity. Dos ejecuciones con distinta execution identity pueden producir la
misma scientific identity.

| Componente | Fuente | Determinismo | Incluido en `identity_chain` | Nota |
|---|---|---|---|---|
| `execution_id` | Hash de baseline + config + profile + result | Determinista | ✅ Sí | **Identificador de resultado derivado.** NO es un discriminador de modo de ejecución. Dos ejecuciones con los mismos parámetros científicos y el mismo resultado producen el MISMO execution_id, independientemente del modo de ejecución. |
| `subject_identity` | Commit SHA del pipeline (git rev-parse HEAD) | Determinista por commit | ✅ Sí | Identifica el sujeto de la verificación. |
| `model_de_execution` | Modo de ejecución ("hybrid_sequential", "async_concurrent", etc.) | Configuración | ❌ **No incluido actualmente** | **DF-13:** El discriminador de modo NO está incluido en `identity_chain`. El testing diferencial (DC-12) no puede distinguir modos de ejecución por execution_id alone. Requiere evaluación de extensión de `build_identity_chain` en Gate 3 (Task 3.4.2). |
| `telemetry_execution_id` | uuid4 generado en entry point | No determinista | ❌ No | Evidencia operacional, NO scientific identity. |

**Regla de no-colapso:** La execution identity habilita testing diferencial
(INV-EXEC-IDENTIFIABILITY) pero no altera la scientific identity.

**Nota sobre `execution_id` vs `model_de_execution`:** El `execution_id` es un
hash determinista derivado de los componentes de scientific identity (baseline,
config, profile, result). NO captura el modo de ejecución. El discriminador de
modo es `model_de_execution`, que actualmente NO está incluido en
`identity_chain`. Esto significa que INV-EXEC-IDENTIFIABILITY está
**parcialmente satisfecha**: el modo de ejecución es identificable en la
configuración del sistema, pero no está presente en el identity_chain del
reporte de verificación. Ver DF-13 en el Findings Register.

### 2.3 Operational State (observable, puede diferir)

El operational state es el conjunto de propiedades que varían durante la
ejecución sin afectar el resultado científico. Dos ejecuciones con la misma
scientific identity pueden tener operational states completamente diferentes.

| Componente | Naturaleza | Puede diferir | Ejemplo |
|---|---|---|---|
| Timestamps | Temporal | ✅ Sí | execution timestamps, stage latencies |
| Scheduling order | Orden de completitud | ✅ Sí | orden en que tasks completan |
| Resource utilization | Métricas de recursos | ✅ Sí | RSS peak, CPU time, wall time |
| Retry timing | Timing de reintentos | ✅ Sí | backoff delays, retry counts |
| Cache hit/miss | Estado de cache | ✅ Sí | hit rate, cache lookups |
| Provider latency | Latencia de red | ✅ Sí | per-call latency, timeout events |
| Worker ID | Identidad de worker | ✅ Sí | thread ID, process ID |
| Queue timings | Timing de colas | ✅ Sí | enqueue time, dequeue time |

**Regla de no-colapso:** El operational state vive en evidencia operacional
separada (INV-OPS-1). Nunca contamina la scientific identity.

### 2.4 Workload Identity (GAP-0.3-03)

La identidad de workload está parcialmente cubierta por `profile_identity`
(hash de perfil + document_ids). Sin embargo, HITO_0.12 §5.3 (DC-02) exige
"fórmula de identidad de workload" como parte del acceptance criterion.

**Estado actual:**
- `profile_identity` cubre la identidad del perfil de ejecución (FULL, SMOKE)
  y los document_ids evaluados.
- La identidad de workload como concepto independiente (fórmula que capture
  características del corpus: tamaño, complejidad, distribución de tipos de
  nodo) NO está definida aún.

**GAP-0.3-03:** "Identidad versionada del workload" está OPEN según
HITO_0.11 v1.0.1 §12. La resolución completa de la fórmula de identidad de
workload queda pendiente y se documenta como limitación de este contrato
provisional (DC-02-A). DC-02-B (consolidación definitiva) incorporará la
resolución de GAP-0.3-03.

---

## 3. CONTRATO DE COMPARACIÓN (Guard Diferencial DC-12)

### 3.1 Scientific Equality (strict, tolerancia cero)

El guard diferencial compara scientific identity con tolerancia cero:

| Comparación | Función | Tolerancia |
|---|---|---|
| Hash del AST por nodo | `compute_ast_hash(node)` | Bit-exact |
| Hash del artefacto ensamblado | SHA-256 del documento científico | Bit-exact |
| Métricas científicas por documento | NSS, Critical FN (DoubleProtectionMechanism) | Exact match |
| `baseline_identity` | Manifest hash | Bit-exact |
| `configuration_identity` | Config fingerprint | Bit-exact |
| `profile_identity` | Profile hash | Bit-exact |
| `result_identity` | Result hash | Bit-exact |

**Regla:** Si scientific identity es idéntica, el resultado científico DEBE
ser idéntico (INV-SCI-1). Cualquier diferencia en scientific identity entre
dos ejecuciones con los mismos parámetros de entrada es una regresión.

### 3.2 Operational Evidence (not required, puede diferir)

El guard diferencial NO compara operational evidence:

| Dimensión | ¿Se compara? | Justificación |
|---|---|---|
| Timestamps | ❌ No | Varían por naturaleza temporal |
| execution_id | ❌ No | Identificador de resultado derivado; mismo para misma scientific identity + mismo resultado |
| scheduling order | ❌ No | Puede variar por concurrencia |
| RSS, CPU, wall time | ❌ No | Métricas operacionales |
| Cache hit/miss | ❌ No | Estado operacional |
| Provider latency | ❌ No | Latencia de red variable |
| Retry timing | ❌ No | Timing operacional |
| Worker ID | ❌ No | Identidad operacional |

**Regla:** Diferencias en operational evidence NO constituyen regresión
científica (INV-OPS-1).

### 3.3 Subset canónico de evidencia de verificación/lineage

El guard diferencial SÍ compara este subset canónico (de HITO_0.4 §16.1):

| Componente | ¿Se compara? | Justificación |
|---|---|---|
| Exit codes | ✅ Sí | Semántica operacional bien definida (0-4) |
| Coverage de perfil | ✅ Sí | Determina qué documentos se evaluaron |
| corpus_verdict | ✅ Sí | Resultado científico agregado |
| corpus_nss | ✅ Sí | Métrica científica agregada |

---

## 4. COMPATIBILIDAD CON DC-12 (Guard Diferencial)

### 4.1 Prerrequisitos verificados (HITO_0.4 v1.3.0)

| Prerrequisito | Estado | Evidencia |
|---|---|---|
| Hashing de AST determinista | ✅ VERIFIED | E-0.4-001: `compute_ast_hash()` es determinista |
| Ensamblado determinista | ✅ VERIFIED (prerrequisito) | E-0.4-002: merge por identidad/lineage |
| Métricas científicas deterministas | ✅ VERIFIED | E-0.4-003: NSS y Critical FN reproducibles |
| Exit codes operacionales | ✅ VERIFIED (boundary) | E-0.4-004: mapeo 0-4 bien definido |

### 4.2 Propiedades end-to-end pendientes de M1

| Propiedad | Estado | Justificación |
|---|---|---|
| Neutralidad científica end-to-end | ⏳ PENDIENTE M1 | Requiere ejecutar dos modos y comparar |
| INV-ASSEMBLY-ORDER end-to-end | ⏳ PENDIENTE M1 | Requiere permutaciones forzadas |
| INV-NO-RESOURCE-SIGNAL end-to-end | ⏳ PARCIAL | Boundary verified; propagación interna pendiente F0-C |

### 4.3 Cláusula de invalidación (NADR-F18-01 §5.4 R17)

Si la frontera de identidad definida en este contrato cambia, el guard
diferencial (DC-12) queda invalidado y requiere reevaluación.

**Condiciones concretas de invalidación:**

1. **DC-12 M1 revela que una dimensión clasificada como Operational State
   afecta scientific equality.** Si el experimento M1 demuestra que un
   componente clasificado como operational (ej. scheduling order) produce
   variación en el resultado científico, la clasificación de ese componente
   debe migrar a Scientific Identity y el guard debe recalibrarse.

2. **Una técnica de DC-06b introduce variación científica no anticipada.**
   Si la evaluación de una técnica candidata (object pools, zero-copy,
   lazy loading, batching) revela que altera el resultado científico bajo
   condiciones normales, la frontera de identidad queda invalidada para esa
   técnica hasta que se demuestre neutralidad.

3. **INV-SCI-1 no se cumple bajo la clasificación provisional.** Si el
   experimento M1 demuestra que dos ejecuciones con la misma scientific
   identity producen resultados científicos diferentes, la clasificación
   provisional es insuficiente y requiere revisión.

**Proceso de escalación:**
- Cualquier condición de invalidación detectada se registra como hallazgo
  en el Findings Register con severidad P0.
- Se escala al Architecture Board para reevaluación de la frontera.
- El guard diferencial (DC-12) se suspende hasta que la frontera sea
  recalibrada y re-verificada.
- Se emite una nueva versión de este contrato con la corrección.

**Regla:** Cualquier modificación a los componentes de scientific identity
(§2.1) requiere recalibración del guard diferencial y re-ejecución de M1-M3.

---

## 5. GOBERNANZA DE MODIFICACIONES (NADR-F18-01 §5.4 R16)

### 5.1 Autoridad de modificación

| Nivel | Autoridad | Alcance |
|---|---|---|
| Scientific Identity (§2.1) | Architecture Board | Cualquier cambio requiere aprobación del Board + nueva versión del contrato + recalibración de DC-12 |
| Execution Identity (§2.2) | Architecture Board / Staff Engineering | Cambios en componentes de execution identity requieren evaluación de impacto en INV-EXEC-IDENTIFIABILITY |
| Operational State (§2.3) | Staff Engineering | Cambios en la lista de operational state no requieren aprobación del Board, pero deben documentarse |
| Workload Identity (§2.4) | Architecture Board | Resolución de GAP-0.3-03 requiere aprobación del Board |

### 5.2 Proceso de modificación

1. **Propuesta:** Se propone el cambio con evidencia forense que lo justifique.
2. **Evaluación de impacto:** Se evalúa el impacto en DC-12, INV-SCI-1,
   INV-OPS-1, INV-EXEC-IDENTIFIABILITY.
3. **Aprobación:** Según el nivel de autoridad (§5.1).
4. **Emisión:** Se emite nueva versión del contrato con changelog.
5. **Recalibración:** Si el cambio afecta scientific identity, se recalibra
   DC-12 y se re-ejecutan M1-M3.

### 5.3 Versionado

- Cada modificación emite una nueva versión (v1.0.1 → v1.0.2 → ...).
- El changelog documenta cada cambio con evidencia.
- Versiones anteriores quedan preservadas para trazabilidad.
- La cláusula de invalidación (§4.3) aplica a cualquier cambio.

### 5.4 Restricciones

- ❌ No se puede modificar scientific identity sin aprobación del Board.
- ❌ No se puede modificar la cláusula de invalidación sin evaluación de impacto.
- ❌ No se puede migrar un componente de Operational State a Scientific Identity
  sin evidencia forense de que afecta el resultado científico.
- ❌ No se puede eliminar un componente de Scientific Identity sin demostrar
  que no afecta INV-SCI-1.

---

## 6. TRAZABILIDAD NORMATIVA

| Fuente | Regla/Sección | Cómo se cumple |
|---|---|---|
| ADR_F18_MASTER §3 | Scientific Identity ≠ Execution Identity ≠ Operational State | Tres dimensiones ortogonales definidas en §2 |
| NADR-F18-01 §5.2 R8 | Execution identity MUST NOT formar parte de scientific identity | §2.1 excluye execution_id, subject_identity, model_de_execution |
| NADR-F18-01 §5.3 R12 | Diferencias operacional no falsifican evidencia científica | §3.2: operational evidence no se compara |
| NADR-F18-01 §5.4 R16 | Frontera documentada, versionada y gobernada | §5: Gobernanza de modificaciones |
| NADR-F18-01 §5.4 R17 | Cláusula de invalidación con dimensiones relevantes | §4.3: 3 condiciones concretas + proceso de escalación |
| NADR-F18-01 §5.4 R18 | Clasificación estable durante comparación | §5.4: Restricciones de modificación |
| INV-SCI-1 (ADR_F18_MASTER §5.1) | Misma baseline + mismos params ⇒ misma salida científica | §3.1: tolerancia cero en scientific identity |
| INV-OPS-1 (ADR_F18_MASTER §5.1) | Diferencias operacional no alteran resultado científico | §3.2: operational evidence puede diferir |
| INV-EXEC-IDENTIFIABILITY (ADR_F18_MASTER §5.1) | Modo de ejecución identificable y reproducible | §2.2: execution identity definida; DF-13 documenta limitación parcial |
| HITO_0.4 v1.3.0 §16.1 | Scientific equality vs operational evidence | §3.1 y §3.2 implementan esta separación |
| HITO_0.12 §4.2 | DC-02-A → DC-12 → DC-02-B | Este documento es DC-02-A (contrato provisional) |

---

## 7. VERIFICACIÓN REGLA-POR-REGLA DE WAVE 2.1

Las reglas asignadas a Wave 2.1 según PHASE_18.1_EXECUTION_PLAN v1.0.1:

### 7.1 Task 2.1.1: Definir frontera provisional

| Regla | Texto | Cómo se cumple | Evidencia |
|---|---|---|---|
| NADR-F18-01 §5.1 R1 | Toda propiedad que determine el resultado científico MUST pertenecer a scientific identity | §2.1 define los 4 componentes de scientific identity | Tabla §2.1 |
| NADR-F18-01 §5.1 R2 | Scientific identity MUST incluir baseline sellada, params congelados y representación estructural canónica | §2.1 incluye baseline_identity (manifest sellado), configuration_identity (params congelados), y hash AST por nodo (representación estructural) | Tabla §2.1, §3.1 |
| NADR-F18-01 §5.1 R3 | Scientific identity MUST NOT incluir mecanismo de ejecución, scheduling, concurrencia, resource allocation, ni operational state | §2.1 no incluye ninguno de estos componentes; §2.2 los clasifica como execution identity; §2.3 como operational state | Tabla §2.1, §2.2, §2.3 |
| NADR-F18-01 §5.1 R5 | Toda variación en scientific identity MUST constituir nueva versión científica | §5.2 requiere nueva versión del contrato para cualquier cambio | §5.2 |
| NADR-F18-01 §5.2 R6 | Toda propiedad que determine el modo/política de ejecución MUST ser clasificada como execution identity | §2.2 define execution_id, subject_identity, model_de_execution, telemetry_execution_id | Tabla §2.2 |
| NADR-F18-01 §5.2 R8 | Execution identity MUST NOT formar parte de scientific identity | §2.2 explícitamente excluido de §2.1; regla de no-colapso | §2.1, §2.2 |
| NADR-F18-01 §5.3 R10 | Toda propiedad que varíe durante ejecución sin afectar resultado científico MUST ser clasificada como operational state | §2.3 define 8 componentes de operational state | Tabla §2.3 |

### 7.2 Task 2.1.2: Validar compatibilidad con DC-12

| Regla | Texto | Cómo se cumple | Evidencia |
|---|---|---|---|
| NADR-F18-01 §5.4 R17 | Cualquier modificación que afecte dimensiones de comparación MUST invalidar evidencia dependiente y MUST requerir reevaluación conforme a gobernanza de Subfase 18.5 | §4.3: cláusula de invalidación con 3 condiciones concretas + proceso de escalación | §4.3 |
| NADR-F18-01 §5.4 R18 | Clasificación MUST ser estable durante vigencia de comparación diferencial | §5.4: restricciones de modificación; §4.3: cláusula de invalidación | §4.3, §5.4 |

### 7.3 Task 2.1.3: Documentar contrato

| Regla | Texto | Cómo se cumple | Evidencia |
|---|---|---|---|
| NADR-F18-01 §5.4 R16 | Frontera MUST estar explícitamente documentada, versionada y gobernada | Este documento (v1.0.1) + §5 Gobernanza de Modificaciones | Documento completo + §5 |

---

## 8. MATRIZ DE TRAZABILIDAD DC

| DC | Relación con este contrato | Estado |
|---|---|---|
| **DC-02-A** | Este documento resuelve DC-02-A (contrato provisional) | ✅ RESUELTO |
| **DC-12** | Usa este contrato como base de comparación | ⏳ PENDIENTE (usa DC-02-A) |
| **DC-02-B** | Consolidación definitiva post DC-12 | ⏳ PENDIENTE (post DC-12) |
| **DC-01** | El modelo de concurrencia NO afecta scientific identity | ⏳ PENDIENTE (Wave 2.2) |
| **DC-05** | Los contextos especializados NO afectan scientific identity | ⏳ PENDIENTE (Wave 2.3) |

---

## 9. HALLAZGOS DERIVADOS

| ID | Descripción | Severidad | Estado | Gate destino |
|---|---|---|---|---|
| **DF-13** | `model_de_execution` (modo de ejecución) NO está incluido en `identity_chain` de `build_identity_chain()`. El testing diferencial (DC-12) no puede distinguir modos de ejecución por execution_id alone. INV-EXEC-IDENTIFIABILITY está parcialmente satisfecha: el modo es identificable en configuración del sistema, pero no presente en el identity_chain del reporte de verificación. Requiere evaluación de extensión de `build_identity_chain` en Gate 3 (Task 3.4.2, trazabilidad de identidad). | Media | REVIEW_REQUIRED | Gate 3 |

---

## 10. CIERRE

**Estado:** FROZEN v1.0.1
**Condición de cierre:** Contrato provisional de identidad científica definido
con 3 dimensiones ortogonales y reglas de no-colapso; tolerancia cero en
scientific identity; operational evidence excluida; cláusula de invalidación
con 3 condiciones concretas y proceso de escalación; gobernanza de
modificaciones documentada; identidad de workload y GAP-0.3-03 documentados;
matriz de verificación regla-por-regla de las 10 reglas de Wave 2.1 completa;
trazabilidad normativa completa; hallazgo DF-13 derivado al Findings Register.
**Próximo paso:** DC-12 (guard diferencial) usa este contrato como base de
comparación. DC-02-B (consolidación definitiva) se ejecuta post DC-12.
**Numeración de hallazgos:** DF-13 asignado conforme a la regla de numeración
de Fase 18 (DF-06, DF-10, DF-11, DF-12, DF-19, DF-24, DF-34 ocupados por
fases anteriores).

**Nota de colisión de numeración (DF-09):** DF-09 de Fase 18 (resultado
contraintuitivo del benchmark de SyncProviderBridge, REVIEW_REQUIRED) **NO es
el mismo hallazgo** que DF-09 de Fase 17-BIS (enforcement CV diferido,
ACCEPTED_LIMITATION, cláusula 6.1). Ambos hallazgos son independientes y
pertenecen a fases diferentes. La numeración se reinicia por fase, pero los IDs
de fases anteriores que se trasladaron permanecen ocupados y no se reutilizan.
En este caso, DF-09 fue asignado en F18 antes de verificar colisión con el
histórico de Fase 17-BIS. Esta colisión se documenta aquí para evitar ambigüedad
en referencias cruzadas. El siguiente ID libre en F18 es DF-13, usado para el
hallazgo de `model_de_execution` ausente de `identity_chain`.