# HITO_0.5_ENTREGABLE_2_GOVERNANCE_FRAMEWORK.md
## Architecture Constitution & Release 17-BIS Governance Contract

* **Framework Version:** 1.0.0
* **Framework Digest:** `[Generated automatically by CI Pipeline]`
* **Freeze Commit:** `[Target Git SHA]`
* **Signed By:** Architecture Board / Principal Engineering
* **Estado:** APPROVED AS CONSTITUTIONAL BASELINE (Final RC) / Hito 0.5 — Entregable 2
* **Fecha de Emisión:** 2026-08-01
* **Límite Epistemológico:** Este documento consolida el *Architecture Governance Framework* del sistema. Se divide estructuralmente en dos dimensiones: la **Constitución Arquitectónica** (estable y fundacional) y el **Governance Contract Map** (específico para el Release 17-BIS). No prescribe detalles de implementación, sino que define Capacidades (`CAP-XXX`), Invariantes, Riesgos Arquitectónicos y Mecanismos de Verificación.

---

## PART I: ARCHITECTURE CONSTITUTION

Las siguientes propiedades arquitectónicas son **constitucionales**. Su modificación está estrictamente prohibida en el ciclo de desarrollo regular y solo podrán ser alteradas mediante la formulación, debate y aprobación de un nuevo Architectural Decision Record (ADR) a nivel de Board, desencadenando un incremento mayor en la versión de este framework.

1. **Canonical AST Identity:** La identidad de un nodo sintáctico se define exclusivamente por su tipo semántico, su profundidad y su contenido normalizado; jamás por identificadores efímeros inyectados en runtime.
2. **Semantic Hash Determinism:** La firma criptográfica de un documento o sub-árbol debe ser determinista, reproducible de forma aislada y completamente agnóstica a la infraestructura de I/O o al orden de inicialización del proceso.
3. **Golden Corpus Bijectivity:** Las barreras de regresión (*Regression Gates*) operarán mediante la comparación estricta contra un oráculo criptográficamente sellado, garantizando cardinalidad biyectiva real. Queda prohibida la autogeneración silente de baselines.
4. **Pipeline Idempotency & Determinism:** Dada una entrada física estática y una misma versión de las políticas de dominio, el pipeline de producción emitirá invariablemente una topología lógica idéntica y un grafo de ejecución idéntico.
5. **Event Sourcing & CQRS Strictness:** Todas las mutaciones de estado se rigen por un Event Log inmutable en modo *Append-Only*. Las lecturas se realizan exclusivamente sobre proyecciones materializadas asíncronamente; la rematerialización debe preservar el linaje generacional exacto.
6. **FSM State Machine Exclusivity:** El ciclo de vida transaccional de un documento es gobernado únicamente por una Máquina de Estados Finita persistente, utilizando operaciones atómicas *Compare-And-Swap* (CAS) como mecanismo de exclusión mutua.
7. **Hexagonal Boundary Enforcement:** El dominio interior no poseerá dependencias de infraestructura, I/O local ni librerías de terceros no abstractas. Los adaptadores gestionarán exclusivamente la mutación tecnológica en las fronteras.

---

## PART II: CAPABILITY CATALOG & OWNERSHIP MATRIX

El sistema se descompone en **Capacidades Arquitectónicas (`CAP-XXX`)**, las cuales poseen un ciclo de vida independiente de los archivos de código que las implementan. Toda implementación, test o ADR debe referenciar estas capacidades.

| Cap ID | Capability Name | Architectural Risk | Owner (Domain) | Approver | Steward |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`CAP-001`** | **Atomic Persistence & Serialization** | `HIGH` | Foundation Domain | Architecture Board | Infra Lead |
| **`CAP-002`** | **Semantic Hashing & Identity** | `CRITICAL` | AST Domain | Architecture Board | Core Maintainer |
| **`CAP-003`** | **Event-Sourced CQRS Integrity** | `CRITICAL` | Runtime Domain | Architecture Board | Runtime Lead |
| **`CAP-004`** | **Topological Materialization** | `HIGH` | AST Domain | AST Maintainer | Core Maintainer |
| **`CAP-005`** | **Hexagonal Physical Abstraction** | `HIGH` | Layout Domain | Infra Maintainer | Extraction Lead |
| **`CAP-006`** | **Orational & Boundary Segmentation** | `MEDIUM` | Segment Domain | Text Processing Lead | Core Maintainer |
| **`CAP-007`** | **Budgeting & Token Estimation** | `HIGH` | FinOps Domain | LLM Ops Lead | FinOps Steward |
| **`CAP-008`** | **Unified Execution Plane** | `CRITICAL` | Dispatch Domain | Runtime Maintainer | LLM Ops Lead |
| **`CAP-009`** | **Sandboxed Artifact Compilation** | `CRITICAL` | Compiler Domain | Infra Maintainer | Compiler Lead |
| **`CAP-010`** | **TeX Syntax Protection** | `HIGH` | Render Domain | Compiler Maintainer | Core Maintainer |

---

## PART III: RELEASE 17-BIS GOVERNANCE CONTRACT MAP

El siguiente mapa contractual establece la **Decisión de Ciclo de Vida (`Lifecycle Decision`)** para cada componente del repositorio bajo el Release 17-BIS, vinculándolos a su capacidad y a sus mecanismos de verificación normativos.

### Definición de Lifecycle Decisions:
* **`IMMUTABLE`:** Arquitectura validada. No admite alteraciones.
* **`PROTECTED`:** Arquitectura conforme. Solo admite *behavior-preserving changes* (refactorizaciones sin alteración de interfaz o invariantes).
* **`EVOLVABLE`:** Arquitectura base correcta. Admite extensión de puertos o wiring bajo inyección de dependencias estricta.
* **`REBUILD`:** Responsabilidad válida, pero implementación actual corrupta o insegura. Requiere reescritura total garantizando el contrato E/S.
* **`REMOVE`:** Purga inmediata del repositorio. Código inalcanzable, zombi o bypasses tóxicos.
* **`DECISION_BLOCKED`:** Destino congelado a la espera de un ADR formal.

### NODO A: Foundation, Identity & State (Bloqueante para Todo el Sistema)

| Cap ID | Component / Module | Status | Lifecycle Decision | Architectural Invariant | Verification Mechanism | Acceptance Evidence | ADR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAP-001` | `infra/serialization/ast_json.py` | `Frozen` | **`IMMUTABLE`** | Atomic POSIX persistence; Stateless execution. | SRE Fault Injection / Chaos Testing | Survival under process kill; Zero-byte file prevention. | `ADR-01` |
| `CAP-002` | `core/ast/hashing.py` | `Stable` | **`REBUILD`** | Node-ID independent semantic hashing. | Property-based Testing | Hashes match pre-established Golden baselines across executions. | `ADR-03` |
| `CAP-003` | `core/execution/handlers.py` | `Stable` | **`EVOLVABLE`** | Strict lineage projection in Read Models. | CQRS Materialization Audit | Real `ast_hash` propagated to DB; `"unknown_ast_hash"` eliminated. | `ADR-08` |
| `CAP-003` | `core/pipeline/state_store.py` | `Legacy` | **`REBUILD`** | Hexagonal boundary isolation. | Static Architecture Linter (Dependency Check) | Zero imports from `infra/` inside `core/`. | `ADR-11` |

### NODO B: AST, Ingestion & Layout

| Cap ID | Component / Module | Status | Lifecycle Decision | Architectural Invariant | Verification Mechanism | Acceptance Evidence | ADR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAP-004` | `core/ast/builder.py` | `Stable` | **`PROTECTED`** | $O(n)$ complexity; Deterministic logical mapping. | Automated Benchmark Profiling | Topological metrics remain stable; Profiler confirms linear bounds. | `ADR-03` |
| `CAP-005` | `infra/adapters/pdf_parser.py` | `Stable` | **`EVOLVABLE`** | Pure Hexagonal boundary; Type-strict mapping. | Static Type Checking (`pyright` strict mode) | Zero duck-typing or `Any` bypasses in mapping functions. | `ADR-11` |
| `CAP-004` | `core/ast/parser.py` | `Legacy` | **`REMOVE`** | Benchmark measures real production pipeline. | Static Dependency Graph Analysis | Module purged; Benchmark suite points to `PdfParserAdapter`. | `ADR-10` |

### NODO C: Transformation & Routing

| Cap ID | Component / Module | Status | Lifecycle Decision | Architectural Invariant | Verification Mechanism | Acceptance Evidence | ADR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAP-006` | `core/segmenter/service.py` | `Stable` | **`EVOLVABLE`** | Provider-agnostic boundary; Idempotent partitioning. | End-to-End Orchestrator Integration Test | Dense paragraphs atomically split before reaching chunking phase. | `ADR-08` |
| `CAP-006` | `core/routing/*` | `Stable` | **`EVOLVABLE`** | Pure functional channel sorting. | Pipeline Flow Tracing | `PASSTHROUGH` nodes definitively bypass LLM inference queues. | `ADR-11` |
| `CAP-002` | `core/chunking/chunker.py` | `Stable` | **`EVOLVABLE`** | Domain segregation; Stateless sequence partitioning. | Code Coverage & Module Introspection | TokenBudget logic migrated; `hashing.py` purged of chunking logic. | `ADR-03` |

### NODO D: Operational Dispatch & FinOps

| Cap ID | Component / Module | Status | Lifecycle Decision | Architectural Invariant | Verification Mechanism | Acceptance Evidence | ADR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAP-008` | `apps/llm_workers/dispatcher.py` | `Stable` | **`REBUILD`** | Unified execution plane; Immutable initialization. | AST/Code Structure Analysis | Single entrypoint confirmed; CLI and Daemon utilize identical orchestration. | `ADR-11` |
| `CAP-007` | `core/validation/budget.py` | `Legacy` | **`REBUILD`** | Token estimation matches provider algorithm (BPE). | Provider Tokenization Parity Test | Zero `ContextOverflowError` anomalies on dense LaTeX document suites. | `ADR-06` |
| `CAP-008` | `apps/llm_workers/rate_limiter.py`| `Transit.` | **`REBUILD`** | Distributed atomic state for Quota Management. | Distributed Concurrency Test | Shared quota respected across multiple worker processes (e.g., via Redis/DB port). | `ADR-08` |

### NODO E: Compilation & Artifact Generation

| Cap ID | Component / Module | Status | Lifecycle Decision | Architectural Invariant | Verification Mechanism | Acceptance Evidence | ADR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAP-009` | `apps/compiler/docker_runner.py` | `Legacy` | **`REBUILD`** | Thread-safe ephemeral I/O sandbox. | Concurrency Chaos Testing | Zero race conditions under concurrent load; CWD pollution eliminated. | `ADR-08` |
| `CAP-009` | `apps/compiler/__main__.py` | `Legacy` | **`REBUILD`** | Compilation adheres to `AssemblyPolicy`. | Integration Testing | Daemon strictly invokes `CompilationService`; ad-hoc assembly removed. | `ADR-06` |
| `CAP-010` | `core/compiler/rendering/impl.py` | `Stable` | **`REFACTOR`** | Context-aware lexical parsing; Math delimiters protected. | TeX Compilation Validation | LaTeX commands survive escaping process and compile successfully. | `ADR-06` |

---

## PART IV: CAPABILITY-BASED IMPLEMENTATION DAG

El flujo de implementación se rige por un Grafo Acíclico Dirigido (DAG) de capacidades sistémicas, asegurando que las fundaciones tecnológicas estén certificadas antes de construir capas operacionales sobre ellas.

```text
[ CAP-001: Atomic Serialization ] ──┐
[ CAP-002: Semantic Identity ] ─────┴─► [ CAP-003: CQRS Integrity ] ──┐
                                                                      │
                                                                      ▼
    [ CAP-005: Physical Abstraction ] ──► [ CAP-004: Topological Materialization ]
                                                                      │
                                                                      ▼
  [ CI Automation & Regression Gates ] ──► [ CAP-006: Orational Segmentation ]
                                           [ Routing & Domain Chunking ]
                                                                      │
                                                                      ▼
                                           [ CAP-008: Unified Execution Plane ]
                                           [ CAP-007: Budgeting & FinOps ]
                                                                      │
                                                                      ▼
                                           [ CAP-009: Sandboxed Compilation ]
                                           [ CAP-010: TeX Syntax Protection ]
```
## PART V: CONTRACT COMPLIANCE RULES (PR REJECTION GATES)

Este Contrato de Gobernanza opera como la máxima autoridad técnica para la Integración Continua (CI). Todo esfuerzo de implementación (`Pull Request`) durante la Fase 1 / 17-BIS será sometido a las siguientes reglas de cumplimiento innegociables.

**A Pull Request is AUTOMATICALLY REJECTED by the Architecture Board if any of the following rules are violated, even if all standard automated tests pass:**

1. **Constitutional Violation:** Introduce I/O físico en un módulo de dominio, altera el modelo *Event-Sourced*, o rompe la definición del `Canonical AST Identity` inyectando estado efímero.
2. **Contract Map Defiance:** Altera un componente clasificado como `IMMUTABLE` o modifica un componente `PROTECTED` introduciendo cambios que no sean estrictamente *behavior-preserving*.
3. **Capability DAG Violation:** Intenta implementar o fusionar un requerimiento de un nodo terminal (ej. `CAP-009: Sandboxed Compilation`) cuando existen evidencias de aceptación (*Acceptance Evidence*) fallidas en sus capacidades bloqueantes predecesoras (ej. `CAP-003: CQRS Integrity`).
4. **Verification Mechanism Failure:** Los mecanismos de verificación arquitectónica (`Property-based Testing`, `Static Architecture Linter`, `Concurrency Chaos Testing`) reportan fallos.
5. **Regression Gate Tampering:** Se detecta aserción tautológica en las suites de testing o se modifica la línea de base del *Golden Corpus* sin un ADR y sin la aprobación del Steward correspondiente.
6. **ADR Non-Conformity:** La lógica de implementación contradice la normativa establecida en el *Architectural Decision Record* correspondiente para dicha capacidad.