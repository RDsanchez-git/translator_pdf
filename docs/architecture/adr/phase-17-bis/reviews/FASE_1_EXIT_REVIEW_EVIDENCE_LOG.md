# FASE_1_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-17-bis/reviews/FASE_1_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-08-19
**Última actualización:** 2026-08-19
**Derivado de:** `PHASE_17BIS_EXECUTION_PLAN.md` v3.0.0 — Gate 4 Exit Review
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review. Cada finding incluye los archivos auditados, el análisis,
los gaps confirmados, la justificación normativa y la clasificación final.

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
| 1.0.0 | 2026-08-19 | Emisión inicial. Migración desde `FASE_1_REVIEW_FINDINGS_REGISTER.md` v1.0.0 a plantilla canónica v1.2.0 de METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md. |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
ADR_F17_BIS_MASTER  >  ADR_F17_BIS_01  >  NADR-01..11  >  PHASE_17BIS_EXECUTION_PLAN
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"¿La existencia de este finding impide que la Scientific Baseline sea
> una representación determinista, reproducible y arquitectónicamente fiel
> del pipeline productivo que vamos a certificar?"*

### 0.3 Reglas transversales aplicables

> **Regla de separación Benchmark/Producción (ADR_F17_BIS_01 §4):**
> *"Lo que el benchmark evalúa es exactamente lo que producción ejecuta,
> y lo que producción ejecuta es exactamente lo que la arquitectura declara."*

> **Corolario forense P2 (regla transversal del Exit Review):**
> `REUSED ≠ IDENTICAL` y `TRANSFORM ≠ VIOLATION`. El benchmark es un
> subproducto controlado del production pipeline, no una segunda
> implementación. No confundir reutilización de capacidades con identidad
> de pipelines.

> **Separación de identidades (ADR Maestro §3 y §5):**
> *"Integridad no implica Identidad."* La arquitectura mantiene diferenciados
> los conceptos de AST Schema Version, Corpus Version e Identity Hash.
> No todos los hashes deben colapsarse en un único mecanismo.

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
| `RESOLVED` | Implementado y cerrado |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `RESOLVED — PRODUCTION ALIGNMENT` | Alineado con stack de producción |
| `RESOLVED — SQLITE_RATE_LIMIT_STORE` | Backend persistente implementado |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida y documentada |
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

## 2. EVIDENCIA FORENSE POR FINDING

### 2.1 GF-01 — RateLimitStore vs ADR Maestro §4

| Campo | Valor |
|-------|-------|
| **ID** | GF-01 |
| **Tipo** | Governance Finding |
| **Estado** | `CLOSED — NORMATIVE COMPATIBILITY ESTABLISHED WITHIN PROJECT SCOPE` |
| **Origen** | Task 3.2.2 (Wave 3.2) — 2 reglas DEFERRED de Gate 3 (NADR-08 §5.1 R3, R4) |
| **Gate destino original** | Gate 4 |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — SQLiteRateLimitStore (implementado en Batch 3 / DF-27) |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.1.1 Texto original del DF

> *"Execution Plan Task 3.2.2 requiere 'adaptador distribuido', pero ADR Maestro §4 prohíbe infraestructura distribuida durante Production Alignment. Implementation intentionally deferred due to governance conflict."*

#### 2.1.2 Reformulación corregida

**Formulación correcta:**

> *"Existe una tensión semántica en el lenguaje de NADR-08 ('distributed execution plane', 'horizontal scaling', 'all nodes'), pero la obligación funcional válida puede satisfacerse dentro del scope constitucional del ADR Maestro mediante un backend de persistencia local (SQLite WAL) con operaciones atómicas cableado desde Composition Root."*

#### 2.1.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `ADR_F17_BIS_MASTER.md` §4 (Out of Scope) | *"NO introducir infraestructura distribuida (Redis, Message Brokers, Kubernetes, DBs remotas)."* |
| 2 | `ADR_F17_BIS_MASTER.md` §9 (Governance Framework) | Cláusula de Jerarquía Normativa. |
| 3 | `ROADMAP_ARQUITECTONICO_LP.md` §I (Principios) | *"Optimize Before Distribution: Los cuellos de botella se resuelven exprimiendo la eficiencia del hardware local antes de considerar sistemas distribuidos."* |
| 4 | `ROADMAP_ARQUITECTONICO_LP.md` §V (Matriz de Infraestructura) | SQLite (WAL) = Core Engine. Redis / Message Brokers = *"No requerido para el alcance actual"*. Microservicios = *"Fuera del alcance arquitectónico"*. Kubernetes = *"No requerido"*. |
| 5 | `PROJECT_SCOPE.md` §3 (Out of Scope) | El proyecto es un pipeline batch local. No se mencionan requisitos multi-nodo. |
| 6 | `core/resilience/rate_limit_store.py` | Puerto `RateLimitStore` con `load()`/`save()`. Docstring: *"La interfaz operativa de coordinación (try_consume, CAS, refill) se definirá en Gate 4 cuando se resuelva el mecanismo de coordinación multi-proceso. Ver GF-01."* |
| 7 | `apps/llm_workers/rate_limiter.py` | `TokenBucket` con estado en `self.tokens` (memoria local). `QuotaManager` con `asyncio.Lock()`. `RateLimitStore` NO está cableado. |
| 8 | Grep: `RateLimitStore` en `apps/` | **0 resultados.** El puerto no está cableado en ningún Composition Root. |
| 9 | Grep: `multiprocess\|Process(` en `core,apps` | Solo `psutil.Process(os.getpid())` en runners de benchmark (telemetría de memoria). Sin evidencia de multi-proceso para coordinación de cuotas. |

#### 2.1.4 Análisis

**Pregunta:** ¿NADR-08 §5.1 R3/R4 y el ADR Maestro §4 son incompatibles?

**Respuesta:** Existe una tensión semántica en el lenguaje de NADR-08, pero la obligación funcional válida puede satisfacerse dentro del scope constitucional del ADR Maestro:

| Obligación de NADR-08 | ¿Compatible con ADR Maestro? | Justificación |
|------------------------|------------------------------|---------------|
| R1: Puerto abstracto desacoplado del backend | ✅ Sí | No requiere infra distribuida |
| R2: Operaciones atómicas de reserva/liberación | ✅ Sí | Pueden implementarse con SQLite WAL local |
| R3: No estado exclusivamente en RAM | ✅ Sí | Un backend local (SQLite) satisface "no exclusivamente en RAM" sin ser infra distribuida |
| R4: Selección de backend desde Composition Root | ✅ Sí | Es un principio de DI, no requiere distribución |
| §7: Múltiples instancias concurrentes coordinan | 🟡 Multi-proceso local: compatible. Multi-nodo: fuera de scope | SQLite WAL soporta concurrencia local (ROADMAP §V) |

**Conclusión:** La obligación válida del NADR-08 puede satisfacerse dentro del scope constitucional del ADR Maestro. Lo que estaba mal era la materialización del Execution Plan Task 3.2.2 al prescribir *"adaptador distribuido"*.

#### 2.1.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Execution Plan Task 3.2.2 prescribe "adaptador distribuido" contradiciendo ADR Maestro §4 | Task 3.2.2 texto original | Alta — conflicto normativo |
| G2 | RateLimitStore tiene 0 implementaciones y 0 consumidores | Grep en infra/ y apps/ | Media — puerto sin materializar |
| G3 | QuotaManager opera 100% en memoria | `apps/llm_workers/rate_limiter.py` | Media — NADR-08 §5.1 R3 insatisfecho |

#### 2.1.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| NADR-08 §5.1 R1-R2 | ✅ Correcto | Puerto abstracto definido. Operaciones load/save definidas. |
| Exclusión intra-proceso | ✅ Correcto | `asyncio.Lock()` en QuotaManager |
| ADR Maestro §4 | ✅ Correcto | Prohíbe infra distribuida, no persistencia local |

#### 2.1.7 Impacto en Scientific Baseline

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | Cuotas son resiliencia operativa, no funcional |
| Reproducibilidad | ❌ No | No interviene en extracción/traducción |
| Corrección funcional | ❌ No | Pipeline funciona sin persistencia de cuotas |
| Bloquea Fase 2 | ❌ No | La Baseline no certifica rate limiting |

#### 2.1.8 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — conflicto normativo real |
| Es violación arquitectónica | ⚠️ Sí — Execution Plan contradice ADR Maestro |
| Es violación de gobernanza | ✅ Sí — jerarquía normativa violada |
| Es problema técnico | ✅ Sí — requiere implementación |
| Pertenece a F17-BIS | ✅ Sí |
| Bloquea Scientific Baseline | ❌ No |
| Clasificación | `CLOSED — NORMATIVE COMPATIBILITY ESTABLISHED` |
| Prioridad | Alta |

#### 2.1.9 Regla aplicada

> **ADR Maestro §9 (Governance Framework):**
> *"No lower governance level is authorized to redefine or contradict decisions established by an upper level."*

> **ROADMAP §I Principio 8 (Optimize Before Distribution):**
> *"Los cuellos de botella se resuelven exprimiendo la eficiencia del hardware local antes de considerar sistemas distribuidos."*

La resolución reinterpreta Task 3.2.2: "adaptador distribuido" → "backend de persistencia local con operaciones atómicas cableado desde Composition Root". No se supersede NADR-08. No se crea nuevo ADR. No se modifica la jerarquía.

---

### 2.2 DF-01 — Identidad semántica del AST en Benchmark

| Campo | Valor |
|-------|-------|
| **ID** | DF-01 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — REFACTORED` (DF-01-A) / `CLOSED (NAR)` (DF-01-B, DF-01-D) / `DEFERRED — FASE 2/3` (DF-01-C) |
| **Origen** | Wave 1.2 (Gate 1) |
| **Gate destino original** | Gate 4 |
| **Prioridad** | Alta |
| **¿Requiere implementación?** | Sí — DF-01-A implementado. DF-01-C diferido. |
| **¿Bloquea Scientific Baseline?** | ⚠️ Condicional — si la cadena de identidad es requisito de Fase 2 |

#### 2.2.1 Texto original del DF

> *"core/benchmark/__main__.py computa su propio SHA-256 por nodo en lugar de usar compute_ast_hash(). Identidad criptográfica desconectada del hash canónico."*

#### 2.2.2 Reformulación corregida

La formulación original era ambigua y podía interpretarse como *"Benchmark debería seguir la ruta de Production"*, lo cual es incorrecto por diseño (ver §0 corolario P2).

**Formulación correcta:**

> *"La identidad semántica utilizada por Benchmark no está demostrablemente alineada con el contrato canónico de identidad del AST."*

La pregunta no es *"¿por qué benchmark no sigue la ruta de producción?"* sino *"¿la identidad semántica del AST del benchmark está gobernada por el mismo contrato canónico?"*

#### 2.2.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/benchmark/__main__.py` (líneas 86, 111, 116, 120, 129) | `node_sha = hashlib.sha256(safe_content.encode('utf-8')).hexdigest()` — hash de contenido individual. `doc_sha = hashlib.sha256(pdf_target_path.read_bytes()).hexdigest()` — hash físico del PDF. Usados como `chunk_fingerprint` y `payload_sha256`. |
| 2 | `core/benchmark/runners/gemini_runner.py` (línea 163) | `sha256_hash = hashlib.sha256(text_payload.encode('utf-8')).hexdigest()` |
| 3 | `core/benchmark/runners/groq_runner.py` (línea 164) | `sha256_hash = hashlib.sha256(text_payload.encode('utf-8')).hexdigest()` |
| 4 | `core/benchmark/corpus/services.py` (`ManifestFingerprintCalculator.compute_hash()`) | `hasher = hashlib.sha256()` — calcula hash global del manifiesto con hashlib directo. |
| 5 | `core/benchmark/ground_truth/use_cases.py` (línea 6) | `from core.shared.crypto import compute_sha256` — único punto del benchmark que usa el módulo canónico. |
| 6 | `core/ast/hashing.py` (`compute_ast_hash()`) | NADR-03 §5.1: Hash semántico determinista del AST. Excluye `node_id`, `sequence_id`, `metadata`. Incluye solo `node_type` + `payload`. Usa `compute_sha256()` de `core/shared/crypto`. |
| 7 | `core/shared/crypto.py` | Punto canónico: `compute_sha256()` y `compute_md5()`. |
| 8 | `core/benchmark/corpus/models.py` | `DocumentFingerprint(sha256)` — representa la huella física del documento. `CorpusManifest` con `corpus_version` y `documents`. |
| 9 | `core/benchmark/orchestrator.py` (líneas 46-54) | `DatasetIntegrityValidator.verify()` calcula SHA-256 del archivo PDF para verificación de integridad física. |
| 10 | `ADR_F17_BIS_MASTER.md` §3 (Separación de Conceptos) | Tres dimensiones ortogonales: INTEGRIDAD (hash físico), IDENTIDAD (hash compuesto encadenado), REGRESIÓN (evaluación topológica). *"Integridad no implica Identidad."* |
| 11 | `ADR_F17_BIS_MASTER.md` §5 (Invariantes) | *"Desacoplamiento de Identidades: La arquitectura debe mantener diferenciados los conceptos de AST Schema Version, Corpus Version e Identity Hash."* |
| 12 | `ADR_F17_BIS_01.md` §4 (Objetivo) | *"Lo que el benchmark evalúa es exactamente lo que producción ejecuta, y lo que producción ejecuta es exactamente lo que la arquitectura declara."* |
| 13 | Auditoría forense P2 (documento interno) | El benchmark reutiliza componentes de producción (`ExtractionProvider`, `DocumentLayout`) pero tiene su propio modelo (`LayoutBlockDraft`). `REUSED ≠ IDENTICAL`, `TRANSFORM ≠ VIOLATION`. |

#### 2.2.4 Análisis

El ADR Maestro §3 establece explícitamente que existen **tres dimensiones ortogonales** que no deben colapsarse:

| Dimensión | Mecanismo | Qué representa |
|-----------|-----------|----------------|
| **INTEGRIDAD** | SHA-256 directo sobre artefacto físico | ¿El archivo en disco es el sellado? |
| **IDENTIDAD** | Hash compuesto / encadenado determinista | ¿Qué versión inmutable de la verdad representa esta colección? |
| **REGRESIÓN** | Evaluación topológica (TED) + Criticidad | ¿El runtime se desvió del Oráculo? |

Esto implica que **no todos los hashes deben ser `compute_ast_hash()`**. Existen al menos estas identidades distintas:

| Identidad | Mecanismo correcto | ¿Es `compute_ast_hash()`? |
|-----------|-------------------|--------------------------|
| PDF físico (integridad) | SHA-256 del archivo | ❌ No |
| Contenido de chunk (payload) | SHA-256 del payload | ❌ No |
| AST semántico | `compute_ast_hash()` | ✅ Sí |
| Corpus manifest | Hash compuesto encadenado | ❌ No |
| Ground Truth | SHA-256 del artefacto | ❌ No |

#### 2.2.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | `hashlib.sha256()` usado directamente en lugar de `compute_sha256()` de `core/shared/crypto.py` | `__main__.py`, runners, `ManifestFingerprintCalculator` | Media — gap de centralización criptográfica, no de corrección matemática |
| G2 | `compute_ast_hash()` no se calcula en el benchmark para el AST generado | `__main__.py` genera `TranslationUnit` desde `ast_nodes` pero nunca calcula el hash semántico del AST | Alta — la identidad semántica del AST no está encadenada al lineage del benchmark |
| G3 | No existe encadenamiento demostrable: AST hash → corpus → ground truth → benchmark run | El `ManifestFingerprintCalculator` encadena `doc_id + fingerprint + traits + page_count`, pero NO el hash semántico del AST | Alta — la Baseline no puede demostrar la cadena completa de identidad |

#### 2.2.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| Benchmark tiene ruta diferente a Producción | ✅ Correcto por diseño | P2: el benchmark es subproducto controlado, no segunda implementación |
| `LayoutBlock ≠ LayoutBlockDraft` | ✅ Correcto | P2: transformación explícita, no identidad de tipos |
| Hash físico del PDF ≠ hash semántico del AST | ✅ Correcto | ADR Maestro §3: Integridad ≠ Identidad |
| Benchmark usa `TranslationUnit` con hash propio | ✅ Aceptable | Representa identidad del chunk, no del AST |

#### 2.2.7 Impacto en Scientific Baseline

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ✅ Sí | SHA-256 es determinista |
| Reproducibilidad | ⚠️ Parcial | Falta encadenamiento completo |
| Corrección funcional | ❌ No | El código funciona correctamente |
| Bloquea Fase 2 | ⚠️ Condicional | Si la cadena de identidad es requisito de Fase 2 |

#### 2.2.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-01-A | Migrar todos los `hashlib.sha256()` genéricos del benchmark a `compute_sha256()` de `core/shared/crypto.py` | `RESOLVED — REFACTORED` | Benchmark |
| DF-01-B | Auditoría formal del modelo de identidad | `CLOSED (NAR)` — Falso positivo: propósitos ortogonales | Benchmark |
| DF-01-C | Determinar dónde debe viajar `compute_ast_hash(ast)` en el lineage del benchmark | `DEFERRED — FASE 2/3` | Benchmark/Corpus |
| DF-01-D | Determinar si el Corpus Manifest Hash debe incorporar el `ast_hash` | `CLOSED (NAR)` — Violaría ADR Maestro §3 | Corpus |

#### 2.2.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Hashing canónico bypassed | ✅ Sí (G1) |
| `compute_ast_hash()` utilizado por benchmark | ❌ No (G2) |
| Identidad semántica AST integrada al corpus | ❌ No demostrado (G3) |
| Es violación arquitectónica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es problema técnico | ✅ Sí |
| Pertenece a F17-BIS | ✅ Sí |
| Bloquea Scientific Baseline | ⚠️ Condicional |
| Clasificación | `RESOLVED — REFACTORED` (DF-01-A) / `DEFERRED — FASE 2/3` (DF-01-C) |
| Prioridad | Alta |

#### 2.2.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §III (Explicit over Implicit):**
> *"Cero 'magia' en el código. Uso de factorías explícitas y tipado estricto estático."*

> **Corolario forense P2:**
> *"No confundir reutilización de capacidades con identidad de pipelines."*

La pregunta no es *"¿por qué benchmark no sigue la ruta de producción?"* sino *"¿la identidad semántica del AST del benchmark está gobernada por el mismo contrato canónico?"*

---

### 2.3 DF-02 — Patrón defensivo `hasattr(node_type, "value")` en consumidores del AST

| Campo | Valor |
|-------|-------|
| **ID** | DF-02 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — REFACTORED` |
| **Origen** | Wave 1.2 (Gate 1) |
| **Gate destino original** | Gate 2 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — implementado en Batch 4 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.3.1 Texto original del DF

> *"Patrón `hasattr(n.node_type, "value")` persiste en múltiples archivos. Código defensivo innecesario si `ContentNodeType` está tipado definitivamente."*

#### 2.3.2 Reformulación corregida

**Formulación correcta:**

> *"Existencia de coerción defensiva Enum | str en consumidores de `ASTNode.node_type`, pese a que el contrato canónico de ASTNode declara `node_type: ContentNodeType`. El patrón introduce una representación dual donde el contrato exige una única representación canónica."*

#### 2.3.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/ast/models.py` (ASTNode) | `node_type: ContentNodeType` — tipado estricto en modelo Pydantic `frozen=True`. No admite `str` crudo post-construcción. |
| 2 | `core/ast/enums.py` (ContentNodeType) | `class ContentNodeType(str, Enum)` — enum con 11 miembros. `.value` siempre disponible. |
| 3 | `core/ast/hashing.py:35` | `type_str = n.node_type.value` — acceso directo correcto. |
| 4 | `core/benchmark/topology/models.py:135` | `tuple(n.node_type.value for n in self.nodes)` — acceso directo correcto. |
| 5 | `core/pipeline/orchestrator.py:139,141` | `node.node_type.value.upper()` — acceso directo correcto. |
| 6 | `apps/compiler/tex_builder.py:24` | `unit.node_type.value` — acceso directo correcto. |
| 7 | `core/benchmark/__main__.py:93` | `node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type)` — **GAP** |
| 8 | `core/normalization/classifier.py:146` | Mismo patrón defensivo — **GAP: código de producción** |
| 9 | `core/normalization/pipeline.py:44` | Mismo patrón defensivo — **GAP: código de producción** |
| 10 | `tools/evaluation/topology/fingerprint.py:20-22` | Mismo patrón defensivo — **GAP: afecta fingerprint/topología** |
| 11 | `tools/benchmark_archive/run_calibration_v1.py:39` | Opera sobre `LayoutBlockDraft.logical_type: Optional[str]` |
| 12 | `tools/evaluation/services/candidate_generator.py:87` | Mismo patrón sobre `block.logical_type` |
| 13 | `tools/evaluation/generate_pymupdf_candidate.py:32` | Mismo patrón sobre `block.logical_type` |
| 14 | `infra/adapters/ast_profiling.py:71-78` | `getattr(node, "node_type", None)` + fallback — adaptador de frontera |
| 15 | `tests/helpers/fakes.py:34` | Fake tolerante en tests |
| 16 | `tests/integration/test_chunker_snapshot.py:68` | Mismo patrón en tests |
| 17 | `tests/integration/test_golden_parser.py:31` | Mismo patrón en tests |
| 18 | `tests/integration/test_pipeline_orchestration.py:42` | Mismo patrón en tests |
| 19 | `core/domain/document.py` (LayoutBlockType) | `class LayoutBlockType(str, Enum)` — enum canónico del dominio físico con 19 miembros |
| 20 | `core/layout/models.py` (LayoutBlockDraft) | `logical_type: Optional[str] = None` — tipado como str, NO como LayoutBlockType |
| 21 | `core/benchmark/reporter.py:85,89` | `hasattr(mw_res, 'pvalue')` — compatibilidad con scipy, NO relacionado |

#### 2.3.4 Análisis

La evidencia demuestra que el patrón aparece en tres universos distintos que NO deben tratarse uniformemente:

| Universo | Modelo | Tipado | ¿El `hasattr` es gap? |
|----------|--------|--------|----------------------|
| **AST V2 (producción)** | `ASTNode` | `node_type: ContentNodeType` (estricto) | ✅ SÍ — innecesario |
| **Benchmark/Tools** | `LayoutBlockDraft` | `logical_type: Optional[str]` (débil) | ⚠️ Parcialmente |
| **Infrastructure adapters** | `NodeSemanticAdapter` | Recibe objeto genérico | ❌ NO — frontera legítima |
| **Tests/Fakes** | Varios | Fake deliberadamente tolerante | ❌ NO |

#### 2.3.5 Gaps objetivos confirmados

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | Patrón defensivo sobre `ASTNode.node_type` en `core/benchmark/__main__.py` | `:93` | Baja |
| G2 | Patrón defensivo sobre `ASTNode.node_type` en `core/normalization/classifier.py` | `:146` | Baja |
| G3 | Patrón defensivo sobre `ASTNode.node_type` en `core/normalization/pipeline.py` | `:44` | Baja |
| G4 | Patrón defensivo en fingerprint topológico | `tools/evaluation/topology/fingerprint.py:20-22` | Media |
| G5 | `LayoutBlockDraft.logical_type` tipado como `Optional[str]` | `core/layout/models.py` | Baja — sub-finding de diseño |

#### 2.3.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| `core/ast/hashing.py` usa `.value` directo | ✅ Correcto | Cumple el contrato |
| `core/pipeline/orchestrator.py` usa `.value` directo | ✅ Correcto | Cumple el contrato |
| `infra/adapters/ast_profiling.py` usa `getattr` + conversión | ✅ Aceptable | Adaptador de frontera legítimo |
| `core/benchmark/reporter.py` usa `hasattr(mw_res, 'pvalue')` | ✅ No relacionado | Compatibilidad con scipy |
| Tests con `hasattr` sobre `chunk_type` | ✅ Aceptable | Fakes deliberadamente tolerantes |
| `tools/benchmark_archive/` | ✅ Fuera de alcance | Archivo archivado (DF-03 NAR) |

#### 2.3.7 Impacto en Scientific Baseline

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ⚠️ Marginal | G4: fingerprint podría serializar dos representaciones |
| Reproducibilidad | ⚠️ Marginal | Solo si `str()` produce output diferente a `.value` |
| Corrección funcional | ❌ No | El código funciona correctamente |
| Bloquea Fase 2 | ❌ No | No impide la certificación |

#### 2.3.8 Sub-acciones identificadas

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| DF-02-A | Eliminar `hasattr` en `core/benchmark/__main__.py`, `core/normalization/classifier.py`, `core/normalization/pipeline.py` | `RESOLVED — REFACTORED` | Producción + benchmark |
| DF-02-B | Eliminar `hasattr` en `tools/evaluation/topology/fingerprint.py` | `RESOLVED — REFACTORED` | Tooling |
| DF-02-C | Evaluar re-tipado de `LayoutBlockDraft.logical_type` | Pendiente de decisión | Benchmark/Tools |
| DF-02-D | Conservar `infra/adapters/ast_profiling.py` como frontera legítima | Cerrado como ACCEPTED | Infra |
| DF-02-E | No modificar `tools/benchmark_archive/` ni tests/fakes | Cerrado como NAR | Fuera de alcance |

#### 2.3.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación arquitectónica del AST | ❌ No |
| Es violación criptográfica | ❌ No |
| Es violación de gobernanza | ❌ No |
| Es contract drift defensivo | ✅ Sí |
| Es problema de representación canónica | ✅ Sí |
| Pertenece a F17-BIS | ✅ Sí |
| Bloquea Scientific Baseline | ❌ No |
| Clasificación | `RESOLVED — REFACTORED` |
| Prioridad | Baja |

#### 2.3.10 Regla aplicada

> **ENGINEERING_PRINCIPLES §III (Explicit over Implicit):**
> El `hasattr` introduce un fallback implícito donde el tipo ya está garantizado por el contrato Pydantic.

> **ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos):**
> Si `node_type` no fuera `ContentNodeType`, eso sería una violación de contrato que debería fallar con Raise, no degradarse silenciosamente a `str(node_type)`.

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> La defensa `else str(node_type)` responde a una necesidad no demostrada para `ASTNode`.

---

### 2.4 DF-04 — `StructuralChunkBoundaryPolicy.can_group()` retorna siempre ALLOW

| Campo | Valor |
|-------|-------|
| **ID** | DF-04 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Wave 1.2 (Gate 1) |
| **Gate destino original** | Gate 2 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | No — diferido a fase futura |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.4.1 Texto original del DF

> *"StructuralChunkBoundaryPolicy.can_group() siempre retorna ALLOW. Falta implementar reglas de HARD_BREAK cuando el AST incorpore semántica de contexto cruzado."*

#### 2.4.2 Reformulación corregida

**Formulación correcta:**

> *"La política `StructuralChunkBoundaryPolicy` está diseñada con un enum de tres estados (`ALLOW`, `HARD_BREAK`, `SOFT_BREAK`) pero actualmente solo produce `ALLOW`. El valor `HARD_BREAK` quedará activo cuando el AST V2 incorpore metadata semántica de contexto cruzado."*

#### 2.4.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/chunking/policies.py:28-46` | `can_group()` retorna SIEMPRE `BoundaryDecision.ALLOW`. Contiene TODO explícito. |
| 2 | `core/chunking/models.py` | `BoundaryDecision(StrEnum)` con `ALLOW`, `HARD_BREAK`, `SOFT_BREAK`. |
| 3 | `core/chunking/protocols.py:15-20` | `ChunkBoundaryPolicy` puerto abstracto correctamente definido. |
| 4 | `core/chunking/chunker.py:58-64` | Consumidor en producción preparado para `HARD_BREAK`. |
| 5 | `core/ast/models.py` (ASTNode) | **No tiene** campos de semántica de contexto cruzado. |
| 6 | `core/ast/cross_page.py` | `BoundaryDetector` es para normalización cross-page, NO para chunking. |
| 7 | `ENGINEERING_PRINCIPLES.md` §I (YAGNI) | *"No se implementará lógica asumiendo necesidades futuras no demostradas."* |

#### 2.4.4 Análisis

El DF establece un condicional explícito:

| Premisa | Estado |
|---------|--------|
| AST tiene semántica de contexto cruzado | ❌ No se cumple |
| `can_group()` retorna solo ALLOW | ✅ Se cumple |
| El enum BoundaryDecision está completo | ✅ Se cumple |
| El chunker está preparado para HARD_BREAK | ✅ Se cumple |

**Conclusión:** El DF describe una capacidad arquitectónica correcta pero **prematura**. Implementar heurísticas ad-hoc sin datos suficientes sería violación de YAGNI.

#### 2.4.5 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| `can_group()` siempre retorna ALLOW | ✅ Correcto para el AST actual | No hay datos para decidir otra cosa |
| `BoundaryDecision.HARD_BREAK` nunca se produce | ✅ Consecuencia lógica | El enum existe para cuando se necesite |
| El chunker está preparado para HARD_BREAK | ✅ Diseño OCP correcto | Abierto a extensión sin modificación |

#### 2.4.6 Impacto en Scientific Baseline

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | ❌ No | ALLOW siempre es determinista |
| Reproducibilidad | ❌ No | Comportamiento consistente |
| Corrección funcional | ❌ No | El pipeline produce chunks válidos |
| Bloquea Fase 2 | ❌ No | La Baseline puede certificarse sin HARD_BREAK |

#### 2.4.7 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| AST tiene semántica de contexto cruzado | ❌ No |
| Implementar ahora sería YAGNI | ✅ Sí |
| Es violación arquitectónica | ❌ No |
| Pertenece a F17-BIS | ❌ No (pertenece a fase futura) |
| Bloquea Scientific Baseline | ❌ No |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Prioridad | Baja |
| Fase destino | Post-Fase 18 |

#### 2.4.8 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> *"No se implementará lógica, atributos o infraestructuras asumiendo necesidades futuras no demostradas."*

---

### 2.5 DF-07 — AsyncDispatcher con 5 dependencias en constructor

| Campo | Valor |
|-------|-------|
| **ID** | DF-07 |
| **Tipo** | Deferred Finding |
| **Estado** | `CLOSED (NAR)` |
| **Origen** | Wave 2.1 |
| **Gate destino original** | Gate 3+ |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.5.1 Texto original del DF

> *"El constructor de AsyncDispatcher acumula 6 dependencias. A futuro, introducir DispatcherFactory en `apps/bootstrap/`."*

#### 2.5.2 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `apps/llm_workers/dispatcher.py` | Constructor con 5 dependencias + `concurrency`. Todas inyectadas por constructor. |
| 2 | `apps/bootstrap/pipeline_factory.py:105` | `AsyncDispatcher` construido en Composition Root. |
| 3 | `core/benchmark/runners/gemini_runner.py:112` | Construcción propia con `DummyContextResolver` (legítimo por P2). |
| 4 | Grep `DispatcherFactory` en `apps/bootstrap/` | **0 resultados.** |
| 5 | NADR-11 §5.1 R1-R2 | Exige inyección por constructor. El dispatcher cumple. |
| 6 | ENGINEERING_PRINCIPLES §I (YAGNI) | Crear `DispatcherFactory` sin necesidad demostrada violaría YAGNI. |

#### 2.5.3 Análisis

**Conteo real:** 5 dependencias inyectadas + 1 parámetro de configuración (`concurrency`). No 6.

| Dependencia | NADR | Rol |
|-------------|------|-----|
| `context_resolver` | NADR-05 | Resolución de contexto |
| `prompt_builder` | NADR-06 | Construcción de prompts |
| `provider_stack` | NADR-08/11 | Routing de proveedores |
| `validation_pipeline` | NADR-04 | Validación obligatoria |
| `healing_pipeline` | NADR-07 | Healing obligatorio |

La heurística "muchas dependencias = problema" es una preferencia estética, no un invariante comprobable.

#### 2.5.4 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcialmente — 5 dependencias, no 6 |
| Es violación SOLID | ❌ No |
| Es violación de NADR-11 | ❌ No — el constructor cumple |
| DispatcherFactory es necesario | ❌ No — YAGNI |
| Clasificación | `CLOSED (NAR)` |
| Prioridad | N/A |

#### 2.5.5 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> *"No se implementará lógica, atributos o infraestructuras asumiendo necesidades futuras no demostradas."*

> **ENGINEERING_PRINCIPLES §I (Cero Sesgo de Confirmación):**
> *"Las decisiones arquitectónicas deben basarse en métricas, invariantes comprobables y escalabilidad real, no en preferencias estéticas."*

---

### 2.6 DF-10 — PDFRouter wrapper transicional

| Campo | Valor |
|-------|-------|
| **ID** | DF-10 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — DELETE` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — implementado en Batch 1 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.6.1 Texto original del DF

> *"core/ast/router.py (PDFRouter) es un wrapper transicional. Eliminar una vez que todos los consumidores migren a PdfTypeDetectorPort."*

#### 2.6.2 Archivos y documentos auditados

| # | Verificación | Resultado |
|---|-------------|-----------|
| 1 | Consumidores en `core/`, `apps/`, `infra/`, `tools/` | 0 |
| 2 | Consumidores en `tests/` | 0 |
| 3 | Imports de módulo en todo el árbol | 1 (referencia interna) |
| 4 | `detect_pdf_type()` con llamadas reales | 0 |
| 5 | `PyMuPdfTypeDetector` cableado en Composition Root | 0 |

#### 2.6.3 Archivos eliminados

1. `core/ast/router.py` — Wrapper `PDFRouter`
2. `core/ast/ports.py` — Puerto `PdfTypeDetectorPort`
3. `infra/adapters/pdf_router.py` — Adaptador `PyMuPdfTypeDetector`

#### 2.6.4 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — wrapper transicional |
| Consumidores activos | ❌ 0 |
| Es código muerto | ✅ Sí |
| Clasificación | `RESOLVED — DELETE` |
| Prioridad | Baja |

#### 2.6.5 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Un puerto sin consumidores ni cableado activo constituye código muerto y debe eliminarse.

---

### 2.7 DF-11 — Providers OCR concretos en core/extraction/ocr_providers/

| Campo | Valor |
|-------|-------|
| **ID** | DF-11 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — MOVE` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 2 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — implementado en Batch 2 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.7.1 Texto original del DF

> *"core/extraction/ocr_providers/ contiene implementaciones concretas dentro del dominio. Migrar a infra/extraction/providers/."*

#### 2.7.2 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/extraction/ocr_providers/pymupdf_provider.py:5` | `import fitz` — infraestructura directa en core/ |
| 2 | `core/extraction/ocr_providers/tesseract_provider.py:2` | `import pytesseract` — infraestructura directa en core/ |
| 3 | `core/extraction/ocr_providers/docling_provider.py:5-7` | `from docling.document_converter import DocumentConverter` — infraestructura directa en core/ |
| 4 | `core/extraction/provider.py:16` | Puerto `ExtractionProvider(ABC)` — correctamente ubicado en core/ |
| 5 | `apps/bootstrap/provider_factory.py:3,25` | `ExtractionProviderFactory` instancia `PyMuPDFProvider` — Composition Root correcto |
| 6 | ENGINEERING_PRINCIPLES §II | *"Separación estricta entre el Dominio y la Infraestructura."* |
| 7 | ADR_F17_BIS_MASTER §4 | *"NO integrar nuevos adaptadores de extracción."* — Los existentes permanecen. |

#### 2.7.3 Lo que SÍ se cumple

| Aspecto | Estado |
|---------|--------|
| Puerto abstracto en core/ | ✅ |
| Dominio consume solo el puerto | ✅ |
| Instanciación en Composition Root | ✅ |
| Factory explícita | ✅ |

#### 2.7.4 Lo que NO se cumple

| Aspecto | Estado |
|---------|--------|
| Adaptadores concretos en infra/ | ❌ Están en core/ |
| core/ libre de imports de infraestructura | ❌ fitz, pytesseract, docling |

#### 2.7.5 Movimientos ejecutados

1. `core/extraction/ocr_providers/pymupdf_provider.py` → `infra/extraction/providers/pymupdf_provider.py`
2. `core/extraction/ocr_providers/tesseract_provider.py` → `infra/extraction/providers/tesseract_provider.py`
3. `core/extraction/ocr_providers/docling_provider.py` → `infra/extraction/providers/docling_provider.py`

#### 2.7.6 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación de Arquitectura Hexagonal | ✅ Sí — ENGINEERING_PRINCIPLES §II |
| Es violación de NADR-02 | ✅ Sí |
| Puerto abstracto existe | ✅ Sí |
| Composition Root correcto | ✅ Sí |
| Clasificación | `RESOLVED — MOVE` |
| Prioridad | Media |

#### 2.7.7 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal):**
> *"Separación estricta entre el Dominio (Lógica pura, AST, Modelos) y la Infraestructura (OCR, LLMs, File I/O)."*

---

### 2.8 H-11-A — core/metrics/measure_density.py importa fitz

| Campo | Valor |
|-------|-------|
| **ID** | H-11-A |
| **Tipo** | Hallazgo derivado (de DF-11) |
| **Estado** | `RESOLVED — DELETE` |
| **Origen** | Batch 2 (auditoría de DF-11) |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — implementado como eliminación |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.8.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/metrics/measure_density.py:1` | `import fitz` — infraestructura directa en core/ |
| 2 | Grep consumidores de `measure_pdf_density` | **0 resultados** |
| 3 | Grep imports de `measure_density` | **0 resultados** |
| 4 | Grep tests de `measure_density` | **0 resultados** |
| 5 | `core/metrics/` (otros archivos) | `metrics.py`, `pricing.py`, `summary.py`, `exporters.py` son componentes activos |

#### 2.8.2 Análisis

- **Violación NADR-02:** `import fitz` directamente en la capa `core/`.
- **Violación ENGINEERING_PRINCIPLES §II:** Functional Core contaminado con I/O de terceros.
- **Código zombi completo:** 0 consumidores, 0 imports, 0 tests.
- **No pertenece a `core/metrics/`:** Los otros archivos son componentes activos del pipeline.

#### 2.8.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — import fitz en core/ |
| Consumidores activos | ❌ 0 |
| Es código muerto | ✅ Sí |
| Es violación de frontera hexagonal | ✅ Sí |
| Clasificación | `RESOLVED — DELETE` |
| Prioridad | Baja |

#### 2.8.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal):**
> *"Separación estricta entre el Dominio y la Infraestructura."*

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Código sin consumidores ni tests es código muerto.

---

### 2.9 DF-12 — LayoutBlockCollection y LayoutBlockDraft / DocumentLayoutBuilder zombi

| Campo | Valor |
|-------|-------|
| **ID** | DF-12 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — DELETE` (DF-12-A, DF-12-B) / `RECLASSIFIED_FUTURE_PHASE` (DF-12-C/D/E) |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — DF-12-A y DF-12-B implementados. DF-12-C/D/E diferidos. |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.9.1 Texto original del DF

> *"LayoutBlockCollection y LayoutBlockDraft pertenecen al legacy DocumentLayoutBuilder (zombi). FlatASTBuilder debe consumir list[LayoutBlock] directamente."*

#### 2.9.2 Reformulación corregida

**Formulación correcta:**

> *"DocumentLayoutBuilder es un zombi confirmado (0 instancias). Los stages del layout pipeline que orquestaba son zombis. LayoutBlockDraft y LayoutBlockCollection NO son zombis pero constituyen una capa de traducción innecesaria entre LayoutBlock (dominio) y FlatASTBuilder."*

#### 2.9.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/layout/models.py` | `LayoutBlockDraft` con `logical_type: Optional[str]`, `content: str`. |
| 2 | `core/layout/builder.py` | `DocumentLayoutBuilder` con `build()`. Orquesta stages. |
| 3 | `core/ast/builder.py` | `FlatASTBuilder.build(layout_collection: LayoutBlockCollection)`. |
| 4 | Grep `DocumentLayoutBuilder(` | **0 instancias** en todo el proyecto. |
| 5 | Grep `LayoutBlockDraft\|LayoutBlockCollection` | Consumido por FlatASTBuilder, stages, pipeline_factory, tools. |
| 6 | `apps/bootstrap/pipeline_factory.py:179-214` | Mapper `_layout_block_to_draft()` con comentario DF-12. |
| 7 | `core/layout/classifier.py`, `detector.py`, `identity.py`, `merger.py`, `normalizer.py`, `reading_order.py` | Stages sin orquestador activo. |

#### 2.9.4 Sub-acciones identificadas

| Sub-acción | Descripción | Estado |
|------------|-------------|--------|
| DF-12-A | Eliminar `DocumentLayoutBuilder` | `RESOLVED — DELETE` (Batch 2) |
| DF-12-B | Eliminar stages zombis del layout | `RESOLVED — DELETE` (Batch 4) |
| DF-12-C | Migrar `FlatASTBuilder` a `list[LayoutBlock]` | `RECLASSIFIED_FUTURE_PHASE` (Fase 18) |
| DF-12-D | Eliminar `LayoutBlockDraft` y `LayoutBlockCollection` | Depende de DF-12-C |
| DF-12-E | Actualizar `tools/evaluation/` | Depende de DF-12-D |

#### 2.9.5 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| DocumentLayoutBuilder es zombi | ✅ Sí — 0 instancias |
| Stages del layout son zombis | ✅ Sí — eliminados en Batch 4 |
| LayoutBlockDraft/Collection son zombis | ❌ No — FlatASTBuilder los consume |
| Migración FlatASTBuilder → LayoutBlock | ⚠️ Decisión de diseño pendiente |
| Clasificación | `RESOLVED — DELETE` (A, B) / `RECLASSIFIED_FUTURE_PHASE` (C, D, E) |
| Prioridad | Media |

#### 2.9.6 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> *"No se implementará lógica, atributos o infraestructuras asumiendo necesidades futuras no demostradas."*

---

### 2.10 DF-13 — TestRealPaperIntegration vs capacidades de PyMuPDFProvider

| Campo | Valor |
|-------|-------|
| **ID** | DF-13 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No — ya resuelto en Wave 2.2 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.10.1 Texto original del DF

> *"El contrato de TestRealPaperIntegration asume capacidades estructurales superiores a las declaradas por PyMuPDFProvider."*

#### 2.10.2 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `tests/integration/test_real_paper.py:40-60` | Test consulta `parser.capabilities` condicionalmente. |
| 2 | `core/extraction/provider.py:5-26` | `ExtractionCapabilities` con 8 capacidades binarias. |
| 3 | `core/extraction/ocr_providers/pymupdf_provider.py:51-64` | PyMuPDF declara `has_tables=False`, `has_images=False`, `supports_math=False`. |
| 4 | Grep `.capabilities` en tests/core/tools | Solo 6 consumidores. |

#### 2.10.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ❌ No — fue resuelta en Wave 2.2 |
| Test asume capacidades superiores | ❌ No — consulta capabilities |
| Clasificación | `RESOLVED` |
| Prioridad | N/A |

#### 2.10.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Open/Closed Principle):**
> El test está abierto a nuevos providers con diferentes capacidades sin requerir modificación.

---

### 2.11 DF-14 — LogicalClassifier zombi en core/layout/classifier.py

| Campo | Valor |
|-------|-------|
| **ID** | DF-14 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — DELETE` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — implementado en Batch 1 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.11.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/layout/classifier.py` | `LogicalClassifier(LayoutStage[...])` |
| 2 | `core/layout/classification.py` | `HeuristicLayoutClassifier` activo en producción |
| 3 | Grep `LogicalClassifier(` | **0 instancias** |
| 4 | Grep `HeuristicLayoutClassifier(` | 3 instancias activas |

#### 2.11.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| LogicalClassifier es zombi | ✅ Sí — 0 instancias |
| HeuristicLayoutClassifier activo | ✅ Sí |
| Auditoría de heurísticas necesaria | ❌ No |
| Clasificación | `RESOLVED — DELETE` |
| Prioridad | Baja |

#### 2.11.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Mantener código sin consumidores es mantener código muerto.

---

### 2.12 DF-15 — PyMuPDFProvider no detecta tablas, ecuaciones ni imágenes

| Campo | Valor |
|-------|-------|
| **ID** | DF-15 |
| **Tipo** | Deferred Finding |
| **Estado** | `ACCEPTED_LIMITATION` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No — limitación aceptada |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.12.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/extraction/ocr_providers/pymupdf_provider.py:51-62` | `has_tables=False`, `has_images=False`, `supports_math=False` |
| 2 | `core/extraction/ocr_providers/pymupdf_provider.py` (filtro) | `if raw_b.get("type") != 0: continue` |
| 3 | `apps/bootstrap/provider_factory.py:22-28` | Solo `PYMUPDF` cableado |
| 4 | ADR Maestro §4 | Prohíbe nuevos adaptadores en F17-BIS |
| 5 | ROADMAP §I Principio 7 | Benchmark Before Optimization |
| 6 | ROADMAP §IV Fase 21 | Parser Routing |

#### 2.12.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — limitación real |
| Es bug | ❌ No |
| Está documentada | ✅ Sí |
| Tests la manejan | ✅ Sí (DF-13) |
| Se puede resolver en F17-BIS | ❌ No — ADR Maestro §4 |
| Clasificación | `ACCEPTED_LIMITATION` |
| Resolución futura | Fase 21 (Parser Routing) |

#### 2.12.3 Regla aplicada

> **ADR Maestro §4 (Out of Scope):**
> *"NO integrar nuevos adaptadores de extracción de visión computacional."*

> **ROADMAP §I Principio 7 (Benchmark Before Optimization):**
> *"Ningún componente estructural se reemplaza sin evidencia estadística empírica."*

---

### 2.13 DF-16 — Dos taxonomías: LayoutBlockType y ContentNodeType

| Campo | Valor |
|-------|-------|
| **ID** | DF-16 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — ACCEPTED ARCHITECTURAL SEPARATION` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Fase 17-BIS |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.13.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/domain/document.py:10` | `LayoutBlockType(str, Enum)` con 19 miembros |
| 2 | `core/ast/enums.py:3` | `ContentNodeType(str, Enum)` con 11 miembros |
| 3 | `core/ast/builder.py:52-83` | `FlatASTBuilder._TYPE_MAPPING` — mapeo centralizado |
| 4 | `core/document_profile/detectors/semantic.py:8-11` | `HeuristicTypeDetector` usa `ContentNodeType` |

#### 2.13.2 Análisis

Las dos taxonomías son **ortogonales por diseño**:
1. `LayoutBlockType` (19 miembros) — capa de extracción/layout
2. `ContentNodeType` (11 miembros) — capa de AST/semántica
3. Mapeo muchos-a-uno con pérdida intencional
4. Correspondencia centralizada en `FlatASTBuilder._TYPE_MAPPING`

#### 2.13.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Taxonomías ortogonales | ✅ Sí |
| Correspondencia centralizada existe | ✅ Sí |
| Unificación justificada | ❌ No |
| Clasificación | `RESOLVED — ACCEPTED ARCHITECTURAL SEPARATION` |
| Prioridad | N/A |

#### 2.13.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal):**
> La separación entre capas exige que cada capa tenga su propia ontología.

---

### 2.14 DF-17 — PyMuPDFProvider filtra imágenes type!=0

| Campo | Valor |
|-------|-------|
| **ID** | DF-17 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Wave 2.2 |
| **Gate destino original** | Gate 3 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Media |
| **¿Requiere implementación?** | No — diferido |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.14.1 Análisis

DF-17 es distinto de DF-15. DF-15 describe una limitación del motor. DF-17 describe una capacidad disponible que el adapter descarta deliberadamente. Habilitar imágenes requiere infraestructura que no existe (asset management).

| Requisito para habilitar imágenes | ¿Existe? |
|-----------------------------------|----------|
| Extracción de bytes de imagen | ❌ No |
| Almacenamiento de archivos (asset dir) | ❌ No |
| Población de ImagePayload.asset_path | ❌ No |
| Referencia a archivo en compiler | ❌ No |
| Dominio soporta IMAGE conceptualmente | ✅ Sí |

#### 2.14.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — filtro deliberado |
| Es corrección local | ❌ No — requiere asset management |
| ADR Maestro §4 aplica | ✅ Sí |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Fase 21 (Parser Routing) o fase de asset management |

#### 2.14.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Habilitar imágenes requiere infraestructura de asset management que no existe.

---

### 2.15 DF-18 — ExecutionContext unificado del plano de ejecución

| Campo | Valor |
|-------|-------|
| **ID** | DF-18 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Wave 3.1 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | RECLASIFICADO → Gate 4 Exit Review |
| **Prioridad** | Media |
| **¿Requiere implementación?** | No — diferido |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.15.1 Análisis

`AssemblyExecutionContext` (Task 4.2.3) NO resuelve DF-18. Cubre exclusivamente la frontera Execution Plane → Compilation Plane. Actualmente existen 6 contextos distintos que fragmentan el Execution Plane. Sin embargo, esta fragmentación NO afecta la corrección funcional ni la Scientific Baseline.

#### 2.15.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — 6 contextos fragmentados |
| AssemblyExecutionContext resuelve DF-18 | ❌ No |
| Es violación arquitectónica | ❌ No — DDD bounded contexts correcto |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Fase 18 o Fase 20 |

#### 2.15.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Introducir un ExecutionContext unificado sin necesidad demostrada violaría YAGNI.

---

### 2.16 DF-19 — Separación de build_pipeline() en sub-fábricas

| Campo | Valor |
|-------|-------|
| **ID** | DF-19 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED` (resuelto por DF-26) |
| **Origen** | Wave 3.1 |
| **Gate destino original** | Gate 4 |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | No — resuelto por DF-26 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.16.1 Análisis

La condición original existe parcialmente, pero la evidencia actual demuestra que el Composition Root ya fue parcialmente descompuesto. Tras la implementación de DF-26 (Batch 3), `build_pipeline()` recibe `provider_stack` como parámetro y ya no lo construye internamente.

| Pregunta | Respuesta |
|----------|-----------|
| ¿`build_pipeline()` debe ser el Composition Root? | ✅ Sí |
| ¿La descomposición solicitada ya existe parcialmente? | ✅ Sí |
| ¿God Factory demostrada? | ❌ No |
| ¿DF-26 resolvió la sub-responsabilidad de provider stack? | ✅ Sí |

#### 2.16.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcialmente |
| Sub-fábricas ya existentes | ✅ Sí |
| God Factory demostrada | ❌ No |
| Resuelto por DF-26 | ✅ Sí |
| Clasificación | `RESOLVED` |
| Prioridad | Baja |

#### 2.16.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> No debe confundirse un Composition Root con una God Factory.

---

### 2.17 DF-20 — Dispatcher resolviendo contexto

| Campo | Valor |
|-------|-------|
| **ID** | DF-20 |
| **Tipo** | Deferred Finding |
| **Estado** | `CLOSED (NAR)` |
| **Origen** | Wave 3.1 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.17.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `apps/llm_workers/dispatcher.py` | Constructor recibe `context_resolver: ContextResolverProtocol`. Llama `resolve_many()`. |
| 2 | `apps/bootstrap/pipeline_factory.py` | `_build_context_stack()` construye e inyecta resolver. |
| 3 | `core/context/context_resolver.py` | `ContextResolverProtocol` (puerto). |
| 4 | NADR-05 §5.1 R1-R3 | Exige resolver real, no Dummy. No especifica ubicación. |
| 5 | NADR-11 §5.1 R1 | Composition Root único punto de construcción. |

#### 2.17.2 Análisis

El dispatcher NO resuelve contexto por sí mismo. Delega a un puerto inyectado vía Dependency Inversion. El patrón de DI es correcto. NADR-05 está satisfecho.

#### 2.17.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ❌ No — el dispatcher no resuelve contexto |
| El dispatcher delega vía DI | ✅ Sí |
| NADR-05 satisfecho | ✅ Sí |
| NADR-11 satisfecho | ✅ Sí |
| Clasificación | `CLOSED (NAR)` |
| Prioridad | N/A |

#### 2.17.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §II (Arquitectura Hexagonal):**
> El dispatcher depende de un puerto abstracto, no de una implementación concreta.

---

### 2.18 DF-21 — Registros compartidos: evaluar infraestructura común

| Campo | Valor |
|-------|-------|
| **ID** | DF-21 |
| **Tipo** | Deferred Finding |
| **Estado** | `CLOSED (NAR)` |
| **Origen** | Wave 3.1 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.18.1 Análisis

El DF se basa en una similitud superficial. La evidencia demuestra que son componentes conceptualmente distintos de bounded contexts diferentes. 2 de los 4 registries mencionados no existen como tales.

#### 2.18.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcialmente |
| Misma responsabilidad de dominio | ❌ No |
| Contrato funcional común | ❌ No |
| Clasificación | `CLOSED (NAR)` |
| Prioridad | N/A |

#### 2.18.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> No hay necesidad demostrada de una abstracción común.

---

### 2.19 DF-22 — RuntimeContextMappingProvider: get() vs mappings

| Campo | Valor |
|-------|-------|
| **ID** | DF-22 |
| **Tipo** | Deferred Finding |
| **Estado** | `CLOSED (NAR)` |
| **Origen** | Wave 3.1 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | N/A |
| **¿Requiere implementación?** | No |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.19.1 Análisis

El único consumidor toma un snapshot en construcción (diseño deliberado para determinismo). El protocolo ya es mínimo. El snapshot es `MappingProxyType` (readonly). `DynamicContextResolver` NO usa este protocolo.

#### 2.19.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Parcialmente |
| Cambio a get() mejora la frontera | ❌ No |
| Protocolo ya es mínimo | ✅ Sí |
| Clasificación | `CLOSED (NAR)` |
| Prioridad | N/A |

#### 2.19.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (Cero Sesgo de Confirmación):**
> La preferencia "get() es más limpio que mappings" es estética.

---

### 2.20 DF-24 — GlobalCircuitBreaker en memoria local

| Campo | Valor |
|-------|-------|
| **ID** | DF-24 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Wave 3.2 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | No — diferido |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.20.1 Análisis

El proyecto es single-node (GF-01). ADR Maestro §4 prohíbe infraestructura distribuida. NADR-08 §5.2 está DONE. El DF no denuncia un incumplimiento normativo.

#### 2.20.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — estado en memoria |
| Multi-proceso requerido | ❌ No |
| NADR-08 §5.2 satisfecho | ✅ Sí |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Fase 18 si se demuestra necesidad |

#### 2.20.3 Regla aplicada

> **ADR Maestro §4 (Out of Scope):**
> *"NO introducir infraestructura distribuida."*

---

### 2.21 DF-25 — ReconcilerDaemon y CQRSReconciliationDaemon

| Campo | Valor |
|-------|-------|
| **ID** | DF-25 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — DELETE` |
| **Origen** | Wave 3.2 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — implementado en Batch 1 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.21.1 Análisis

`CQRSReconciliationDaemon` es un **subconjunto estricto** de `ReconcilerDaemon`. Tiene **0 consumidores** fuera de sí mismo. Es un zombie.

| Funcionalidad | CQRSReconciliationDaemon | ReconcilerDaemon |
|---------------|-------------------------|-----------------|
| Sweep tasks con lease expirado | ✅ Sí (simple) | ✅ Sí (con inercia + event_repo) |
| Vector 1: Zombie puro | ✅ | ✅ |
| Vector 2: CQRS anti-entropy | ❌ No | ✅ |
| FSM stall detection | ❌ No | ✅ |
| Liderazgo distribuido | ❌ No | ✅ |

#### 2.21.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Duplicación funcional | ✅ Sí — subconjunto estricto |
| CQRSReconciliationDaemon tiene consumidores | ❌ No — zombie |
| Clasificación | `RESOLVED — DELETE` |
| Prioridad | Baja |

#### 2.21.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Mantener dos daemons con solapamiento funcional sin justificación es mantener código residual.

---

### 2.22 DF-26 — Duplicación de provider stack en entry points

| Campo | Valor |
|-------|-------|
| **ID** | DF-26 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — FACTORY EXTRACTION` |
| **Origen** | Wave 3.2 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — implementado en Batch 3 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.22.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `apps/cli/main.py:88-103` | Construcción inline del stack |
| 2 | `apps/llm_workers/__main__.py:248-266` | Construcción inline del stack |
| 3 | `runtime/engine.py:101-103` | Tercera construcción inline |
| 4 | `apps/bootstrap/pipeline_factory.py:79` | `build_pipeline()` recibe `provider_stack` como parámetro |
| 5 | NADR-11 §5.1 R1 | *"Este es el ÚNICO punto de construcción del grafo de objetos."* |

#### 2.22.2 Hallazgo crítico: divergencia de configuración

| Entry point | QuotaManager rpm | QuotaManager tpm |
|-------------|-----------------|-----------------|
| CLI | `os.getenv("GROQ_RPM_LIMIT", "30")` | `os.getenv("GROQ_TPM_LIMIT", "6000")` |
| Worker | Hardcodeado 30 | Hardcodeado 6000 |

#### 2.22.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — 3 puntos de construcción |
| Duplicación real | ✅ Sí |
| Divergencia de configuración | ⚠️ Sí |
| Viola NADR-11 §5.1 R1 | ✅ Sí |
| Clasificación | `RESOLVED — FACTORY EXTRACTION` |
| Prioridad | Media |

#### 2.22.4 Regla aplicada

> **NADR-11 §5.1 R1:**
> *"Este es el ÚNICO punto de construcción del grafo de objetos."*

---

### 2.23 DF-27 — Backend persistente para cuotas multi-proceso

| Campo | Valor |
|-------|-------|
| **ID** | DF-27 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — SQLITE_RATE_LIMIT_STORE` |
| **Origen** | Wave 3.2 |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — implementado en Batch 3 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.23.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/resilience/rate_limit_store.py` | Protocol con load()/save(). 0 implementaciones. |
| 2 | Grep RateLimitStore en infra/ | **0 implementaciones.** |
| 3 | `apps/llm_workers/rate_limiter.py` | TokenBucket en RAM. Sin persistencia. |
| 4 | ROADMAP §V | SQLite (WAL) = Core Engine. |
| 5 | ADR Maestro §4 | Prohíbe infraestructura distribuida. |

#### 2.23.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí — 0 implementaciones |
| NADR-08 §5.1 R3-R4 satisfechos | ❌ No (antes de implementación) |
| Multi-proceso requerido | ❌ No — single-node |
| Persistencia local requerida | ⚠️ Sí |
| Clasificación | `RESOLVED — SQLITE_RATE_LIMIT_STORE` |
| Prioridad | Media |

#### 2.23.3 Regla aplicada

> **ROADMAP §V (Matriz de Decisiones de Infraestructura):**
> *"SQLite (WAL): Core Engine."*

---

### 2.24 DF-28 — DummyContextResolver en runners de benchmark

| Campo | Valor |
|-------|-------|
| **ID** | DF-28 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — PRODUCTION ALIGNMENT` |
| **Origen** | Gate 3 (auditoría) |
| **Gate destino original** | Gate 4 |
| **Estado previo** | RECLASIFICADO → Gate 4 |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — implementado como DF-28 |
| **¿Bloquea Scientific Baseline?** | ⚠️ Condicional |

#### 2.24.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/benchmark/runners/groq_runner.py` | `DummyContextResolver` con `resolve_many()` retorna `{}` |
| 2 | `core/benchmark/runners/gemini_runner.py` | Mismo patrón |
| 3 | `core/benchmark/__main__.py:41-42` | Único consumidor |
| 4 | `apps/bootstrap/pipeline_factory.py` | `_build_context_stack()` construye resolver real |
| 5 | ADR_F17_BIS_01 §4 | *"Lo que el benchmark evalúa es exactamente lo que producción ejecuta."* |
| 6 | NADR-10 §5.3 R9-R10 | Benchmark consumidor del Composition Root |

#### 2.24.2 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| NADR-05 §5.1 R2 violado | ❌ No | Los runners no son ruta de producción |
| DummyContextResolver como concepto | ✅ Legítimo | El benchmark puede tener resolutores propios |
| Regla P2 violada | ❌ No | REUSED ≠ IDENTICAL aplica |

#### 2.24.3 Lo que SÍ es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| ADR_F17_BIS_01 §4 violado | ✅ Sí | Benchmark evalúa sin contexto real |
| NADR-10 §5.3 R9 parcialmente violado | ⚠️ Sí | Benchmark reconstruye dispatcher |
| Métricas no representativas | ✅ Sí | Sin contexto, sin CB, sin cache |

#### 2.24.4 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Viola NADR-05 directamente | ❌ No |
| Viola ADR_F17_BIS_01 §4 | ✅ Sí |
| Afecta representatividad | ✅ Sí |
| Clasificación | `RESOLVED — PRODUCTION ALIGNMENT` |
| Prioridad | Media |

#### 2.24.5 Regla aplicada

> **ADR_F17_BIS_01 §4:**
> *"Lo que el benchmark evalúa es exactamente lo que producción ejecuta."*

---

### 2.25 DF-29 — FSM_TO_PIPELINE_RESUME con dependencia inversa

| Campo | Valor |
|-------|-------|
| **ID** | DF-29 |
| **Tipo** | Deferred Finding |
| **Estado** | `RESOLVED — DELETE` |
| **Origen** | Task 4.1.1 (auditoría) |
| **Gate destino original** | Gate 4 |
| **Estado previo** | PENDING |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | Sí — implementado en Batch 1 |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.25.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/execution/state_mapping.py` | 3 símbolos: 1 activo + 2 zombies |
| 2 | Grep `FSM_TO_PIPELINE_RESUME` | Solo definición. 0 consumidores |
| 3 | Grep `PIPELINE_TO_FSM` | Solo definición. 0 consumidores |
| 4 | Grep `RecoveredJobSnapshot` | Consumido por `state_store.py:12` y 1 test |
| 5 | `runtime/resumer.py` | NO usa `state_mapping` |

#### 2.25.2 Análisis

La dependencia inversa existe técnicamente pero solo en código zombie. `RecoveredJobSnapshot` es activo y agnóstico del pipeline.

#### 2.25.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ⚠️ Técnicamente sí, pero solo en código zombie |
| Consumidores de dicts eliminados | ❌ 0 |
| `RecoveredJobSnapshot` activo | ✅ Sí |
| Clasificación | `RESOLVED — DELETE` |
| Prioridad | Baja |

#### 2.25.4 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> Mantener diccionarios de mapeo sin consumidores es YAGNI inverso.

---

### 2.26 DF-31 — Detección de proyecciones huérfanas no observable desde el port

| Campo | Valor |
|-------|-------|
| **ID** | DF-31 |
| **Tipo** | Deferred Finding |
| **Estado** | `ACCEPTED_LIMITATION` |
| **Origen** | Task 4.2.3 (auditoría) |
| **Gate destino original** | Gate 4 Exit Review |
| **Estado previo** | PENDING |
| **Prioridad** | Baja |
| **¿Requiere implementación?** | No — limitación aceptada |
| **¿Bloquea Scientific Baseline?** | No |

#### 2.26.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `infra/db/materialized_repo.py:44-58` | `get_assemblable_chunks` con `WHERE node_id IN (expected)` |
| 2 | `core/execution/ports.py:82` | `MaterializedPlanePort` con 3 métodos. Ninguno detecta huérfanos. |
| 3 | Grep `get_assemblable_chunks` | 2 consumidores |
| 4 | NADR-06 §5.3 R3 | Valida topología, no huérfanos |

#### 2.26.2 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Es violación funcional | ❌ No |
| Es violación normativa | ❌ No |
| Modificar el port es necesario | ❌ No — YAGNI |
| Clasificación | `ACCEPTED_LIMITATION` |
| Destino natural | Fase 20 (Local Observability) |

#### 2.26.3 Regla aplicada

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> La detección de huérfanos es una capacidad de observabilidad sin necesidad demostrada.

---

### 2.27 DF-34 — ProfileStore requiere backend durable para AssemblerWorkerDaemon

| Campo | Valor |
|-------|-------|
| **ID** | DF-34 |
| **Tipo** | Deferred Finding |
| **Estado** | `RECLASSIFIED_FUTURE_PHASE` |
| **Origen** | Task 4.2.3 (auditoría) |
| **Gate destino original** | Gate 4 Exit Review / Fase 18 |
| **Prioridad** | Media |
| **¿Requiere implementación?** | Sí — diferido a Recovery Gate / Fase 18 |
| **¿Bloquea F17-BIS?** | No |
| **¿Bloquea Recovery Gate?** | ✅ Sí — condición explícita |

#### 2.27.1 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `core/document_profile/ports.py` | `ProfileStore` Protocol con `save()`/`get()` |
| 2 | `infra/db/profile_store.py` | `InMemoryProfileStore` con dict en RAM |
| 3 | `apps/compiler/__main__.py` | `AssemblerWorkerDaemon` instancia `InMemoryProfileStore` |
| 4 | `core/compiler/service.py:77` | `CompilationService` lanza `ProfileNotFoundError` si `get()` retorna None |
| 5 | `core/document_profile/profiler.py` | `HeuristicDocumentProfiler` produce `InferredDocumentProfile` |
| 6 | `core/ast/registry.py` | `ASTRegistry` puede cargar AST para re-inferencia |

#### 2.27.2 Análisis

Tres conceptos distintos:
1. **Persistencia del perfil**: `InMemoryProfileStore` → dict RAM → no durable
2. **Re-inferencia del perfil**: AST → `HeuristicDocumentProfiler` → posible
3. **Recovery automático**: `get()` → None → re-inferir → `save()` → retry (NO existe)

La pieza 3 es la que impide afirmar que el problema está resuelto.

#### 2.27.3 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | ✅ Sí |
| Bloquea F17-BIS | ❌ No |
| Bloquea Gate 4 | ❌ No |
| Bloquea Recovery Gate | ✅ Sí — condición explícita |
| Requiere implementación | ✅ Sí — nuevo adapter o re-inferencia |
| Clasificación | `RECLASSIFIED_FUTURE_PHASE` |
| Destino | Recovery Gate (Gate I) / Fase 18 |

#### 2.27.4 Regla aplicada

> **ROADMAP §IV Fase 18 (Advanced Local Runtime):**
> *"Exprimir el rendimiento computacional local eliminando bloqueos I/O."*

> **ENGINEERING_PRINCIPLES §I (YAGNI):**
> La recuperación ante crashes del daemon de ensamblado pertenece al contrato operacional del runtime, no al contrato funcional de la Scientific Baseline.

---

## 3. GATE EXIT REVIEW SUMMARY

### 3.1 Gate 3 Exit Review (2026-08-07)

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-02 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Revisión tardía: Gate 2 cerrado sin Gate Exit Review. |
| DF-04 | ⚠️ Parcial | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Requiere semántica de contexto cruzado. |
| DF-07 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | `DispatcherFactory` no existe. |
| DF-10 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | `PDFRouter` sigue en tree. |
| DF-11 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Migración hexagonal. |
| DF-12 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Refactor grande de `FlatASTBuilder`. |
| DF-13 | ⚠️ Parcial | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Decisión de benchmark pendiente. |
| DF-14 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Zombi no eliminado. |
| DF-15 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Limitación conocida. |
| DF-16 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Unificación de taxonomías. |
| DF-17 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Flujo de imágenes. |
| DF-23 | ❌ No | — | — | RESOLVED | Archivo eliminado en Wave 3.2. |
| DF-28 | ✅ Sí (nuevo) | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 | Hallazgo nuevo. |

**Resumen:**
- RESOLVED: 1 (DF-23)
- RECLASIFICADO → Gate 4: 12 (DF-02, 04, 07, 10, 11, 12, 13, 14, 15, 16, 17, 28)
- CLOSED (NAR): 0
- CONVERTIDO EN GF: 0
- Nuevos hallazgos registrados: 1 (DF-28)
- Revisiones tardías documentadas: 2 (DF-02, DF-11)

### 3.2 Gate 4 Partial Exit Review — Wave 4.2 (2026-08-08)

**Nota:** Gate 4 alcanza 24/24 reglas propias DONE. GF-01 (2 reglas de Gate 3) sigue pendiente como Governance Finding.

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-01 | ✅ Sí | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review | Hashing propio persiste. |
| DF-18 | ✅ Sí | ⚠️ Parcial | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review | `AssemblyExecutionContext` no lo reemplaza. |
| DF-31 | ✅ Sí (nuevo) | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review | Hallazgo nuevo. |
| DF-33 | ❌ No | — | — | RESUELTO | Grep confirmó alcance completo. |
| DF-34 | ✅ Sí (nuevo) | ❌ No | ✅ Sí | RECLASIFICADO → Gate 4 Exit Review / Fase 18 | Hallazgo nuevo. |

**Resumen Wave 4.2:**
- RESUELTO: 1 (DF-33)
- RECLASIFICADO → Gate 4 Exit Review: 3 (DF-01, DF-18, DF-31)
- RECLASIFICADO → Gate 4 Exit Review / Fase 18: 1 (DF-34)
- Nuevos hallazgos registrados: 2 (DF-31, DF-34)

#### Decisiones arquitectónicas congeladas en Gate 4

| Decisión | Task | Justificación |
|----------|------|---------------|
| `ExactBPEEstimator` como estimador canónico único | 4.2.1 | NADR-06 §5.1. Sin fallback heurístico. |
| `TextRenderStrategy` con protección local de math | 4.2.2 | NADR-06 §5.2. |
| `DispatchResult` deja de ser contrato inter-stage | 4.2.3 | NADR-06 §5.3. Objeto efímero. |
| `AssemblyExecutionContext` como frontera Execution → Compilation | 4.2.3 | VO inmutable. Resolver valida, Assembler decide, Service materializa. |
| `TranslationPipeline` termina en `MarkAssemblyReadyCommand` | 4.2.3 | NADR-09 §5.1. Separación de planos. |
| `TranslationAuditSummary` describe solo Dispatch Plane | 4.2.3 | Sin mezcla de telemetría. |
| `ProfileStore` canónico | 4.2.3 | Eliminado duplicado. |
| Validación topológica sobre AST completo antes del filtro OMIT | 4.2.3 | Gaps de OMIT son legales. |

#### Lecciones aprendidas Gate 4

- El enfoque audit-first (census → diseño → implementación) previno 3 bloqueadores arquitectónicos.
- La separación de planos eliminó la doble materialización de contenido.
- `DispatchResult` como contrato inter-stage era la raíz del acoplamiento.
- Los tests que dependían del ensamblado lógico quedaron obsoletos correctamente.

---

## 4. TABLA CONSOLIDADA FINAL

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | 9 | DF-03, DF-07, DF-20, DF-21, DF-22, GF-01, DF-01-B, DF-01-D, DF-33 |
| `RESOLVED — DELETE` | 5 | DF-10, DF-14, DF-25, DF-29, H-11-A |
| `RESOLVED — MOVE` | 1 | DF-11 |
| `RESOLVED — REFACTORED` | 2 | DF-01-A, DF-02 |
| `RESOLVED — FACTORY EXTRACTION` | 1 | DF-26 |
| `RESOLVED — SQLITE_RATE_LIMIT_STORE` | 1 | DF-27 |
| `RESOLVED — PRODUCTION ALIGNMENT` | 1 | DF-28 |
| `RESOLVED` | 3 | DF-13, DF-16, DF-19 |
| `RECLASSIFIED_FUTURE_PHASE` | 7 | DF-04, DF-17, DF-18, DF-24, DF-34, DF-01-C, DF-12-C/D/E |
| `ACCEPTED_LIMITATION` | 2 | DF-15, DF-31 |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| GF-01 | `CLOSED — NORMATIVE COMPATIBILITY ESTABLISHED` | Reconciliación normativa. SQLite WAL local satisface NADR-08. |
| DF-01-A | `RESOLVED — REFACTORED` | Centralización criptográfica en `core/shared/crypto.py`. |
| DF-01-B | `CLOSED (NAR)` | Falso positivo: propósitos ortogonales. |
| DF-01-C | `DEFERRED — FASE 2/3` | Requiere ADR de diseño sobre linaje de identidad semántica. |
| DF-01-D | `CLOSED (NAR)` | Violaría ADR Maestro §3. |
| DF-02 | `RESOLVED — REFACTORED` | Patrón `hasattr` eliminado en 4 archivos. |
| DF-03 | `CLOSED (NAR)` | `tools/benchmark_archive/` archivado. |
| DF-04 | `RECLASSIFIED_FUTURE_PHASE` | HARD_BREAK requiere semántica de contexto cruzado. Destino: post-Fase 18. |
| DF-07 | `CLOSED (NAR)` | 5 dependencias legítimas. NADR-11 cumplido. YAGNI aplica. |
| DF-10 | `RESOLVED — DELETE` | 3 archivos eliminados. |
| DF-11 | `RESOLVED — MOVE` | 3 providers movidos a `infra/extraction/providers/`. |
| DF-12-A | `RESOLVED — DELETE` | `DocumentLayoutBuilder` eliminado. |
| DF-12-B | `RESOLVED — DELETE` | 6 stages zombis eliminados. |
| DF-12-C/D/E | `RECLASSIFIED_FUTURE_PHASE` | Migración `FlatASTBuilder` → `list[LayoutBlock]`. Destino: Fase 18. |
| DF-13 | `RESOLVED` | Test consulta `parser.capabilities`. |
| DF-14 | `RESOLVED — DELETE` | `LogicalClassifier` eliminado. |
| DF-15 | `ACCEPTED_LIMITATION` | Limitación de PyMuPDF. Destino: Fase 21. |
| DF-16 | `RESOLVED — ACCEPTED SEPARATION` | Taxonomías ortogonales. Mapeo centralizado. |
| DF-17 | `RECLASSIFIED_FUTURE_PHASE` | Extracción de imágenes requiere asset management. Destino: Fase 21. |
| DF-18 | `RECLASSIFIED_FUTURE_PHASE` | `ExecutionContext` unificado. Destino: Fase 18/20. |
| DF-19 | `RESOLVED` | Resuelto por DF-26 (factory extraction). |
| DF-20 | `CLOSED (NAR)` | Dispatcher delega vía DI. NADR-05 satisfecho. |
| DF-21 | `CLOSED (NAR)` | Registries de bounded contexts distintos. |
| DF-22 | `CLOSED (NAR)` | Snapshot intencional. Protocolo mínimo. |
| DF-24 | `RECLASSIFIED_FUTURE_PHASE` | CB en memoria suficiente. Destino: Fase 18 si se demuestra necesidad. |
| DF-25 | `RESOLVED — DELETE` | `CQRSReconciliationDaemon` eliminado (subconjunto zombie). |
| DF-26 | `RESOLVED — FACTORY EXTRACTION` | `build_provider_stack()` extraído a `apps/bootstrap/`. |
| DF-27 | `RESOLVED — SQLITE_RATE_LIMIT_STORE` | `SQLiteRateLimitStore` implementado. NADR-08 §5.1 R1-R4 cumplidos. |
| DF-28 | `RESOLVED — PRODUCTION ALIGNMENT` | Runners alineados con Composition Root. `DummyContextResolver` eliminado. |
| DF-29 | `RESOLVED — DELETE` | Dicts zombies eliminados. `RecoveredJobSnapshot` preservado. |
| DF-31 | `ACCEPTED_LIMITATION` | Port no detecta huérfanos. Funcionalmente correcto. Destino: Fase 20. |
| DF-33 | `RESOLVED` | Grep de consumidores confirmó alcance completo. |
| DF-34 | `RECLASSIFIED_FUTURE_PHASE` | `InMemoryProfileStore` no sobrevive crash. Destino: Recovery Gate / Fase 18. |
| H-11-A | `RESOLVED — DELETE` | `measure_density.py` eliminado. Frontera hexagonal restaurada. |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [x] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [x] Ningún hallazgo está en estado `PENDING_REVIEW`
- [x] La tabla consolidada final está completa
- [x] Cada clasificación tiene al menos una regla normativa aplicada
- [x] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [x] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación

### 5.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review. No tiene autoridad normativa. No redefine reglas de NADRs
ni ADRs. Su único propósito es documentar la evidencia que fundamenta cada
clasificación del Findings Register, para que futuras sesiones o fases no
tengan que re-derivar conclusiones.