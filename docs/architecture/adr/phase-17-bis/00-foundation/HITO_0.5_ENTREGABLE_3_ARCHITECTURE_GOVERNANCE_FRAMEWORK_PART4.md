# HITO_0.5_ENTREGABLE_3_ARCHITECTURE_GOVERNANCE_FRAMEWORK_PART4.md
## Architecture Governance Framework & NADR Part IV

* **Framework Version:** 1.0.0
* **Framework Digest:** `[Generated automatically by CI Pipeline]`
* **Freeze Commit:** `[Target Git SHA]`
* **Signed By:** Architecture Board / Principal Engineering
* **Status:** NORMATIVE BASELINE (Final RC) / Hito 0.5 — Entregable 3 (Parte 4)
* **Date:** 2026-08-01

---

## PART I: ARCHITECTURE GOVERNANCE FRAMEWORK (AGF) DEFINITIONS

Este marco rige la creación, evolución y cumplimiento de todas las decisiones arquitectónicas del sistema. Los Normative Architectural Decision Records (NADR) son artefactos subordinados a este marco.

### 1.1 Taxonomy of Compliance Levels
* **`MANDATORY`:** Cumplimiento estricto. La violación bloquea el despliegue (CI Rejection).
* **`RECOMMENDED`:** Fuerte preferencia arquitectónica. Desviaciones requieren justificación escrita y aprobación de un *Reviewer*.
* **`OPTIONAL`:** Patrones sugeridos sin penalización por omisión.
* **`EXPERIMENTAL`:** Patrones bajo prueba (A/B testing arquitectónico); restringidos a contextos aislados.
* **`DEPRECATED`:** Prohibido para nuevo desarrollo. El código existente entra en fase de migración.

### 1.2 Decision Lifecycle
* **`DRAFT`:** En fase de diseño y debate.
* **`CANDIDATE`:** Sometido a revisión del Architecture Board.
* **`APPROVED`:** Congelado y activo.
* **`SUPERSEDED`:** Reemplazado por una versión superior.
* **`DEPRECATED` / `ARCHIVED`:** Retirado del marco normativo activo.

### 1.3 Verification vs. Validation Definitions
* **Verification (Static/Mechanic):** Pruebas que demuestran que el sistema cumple el diseño (Linters, Type Checkers, Property-based testing).
* **Validation (Dynamic/Behavioral):** Pruebas que demuestran que el sistema resuelve el problema del dominio (Golden Corpus Benchmark, E2E).

---

## PART II: NORMATIVE ADRs (RELEASE 17-BIS)

# NADR-F17BIS-10: Strict Regression Gates, Scientific Benchmark Alignment & CI Automation

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-10`
* **Title:** Strict Regression Gates, Scientific Benchmark Alignment & CI Automation
* **Decision Class:** `OPERATIONAL` / `DATA`
* **Compliance Level:** `MANDATORY`
* **Decision Version:** 1.0.0
* **Lifecycle:** `APPROVED`
* **Effective Since:** Phase 17-BIS
* **Decision Authority:** Architecture Board
* **Technical Owner:** QA & CI/CD Lead
* **Related Capability:** `CAP-004` (Topological Materialization)
* **Cross References:**
  * **Depends On:** `NADR-F17BIS-03` (Semantic Hashing)
  * **Influences:** All future pull requests.
  * **Conflicts With:** Any bypass of read-only testing or dynamic oracle assignment.
  * **Superseded By:** N/A

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Operational:** 5 (CI silently passes broken builds)
* **Maintainability:** 5 (Tautological tests hide regressions)
* **Recoverability:** 4 (Lost baselines are hard to recreate)
* **Security:** 1 | **Financial:** 1 | **Total Score: 16/25**

## 3. EXECUTIVE DECISION
The Architecture Board dictates that all Continuous Integration (CI) and benchmarking pipelines **MUST** operate as strict, automated quality gates. Tautological test assertions ($A == A$) and silent self-creating baseline snapshots are **FORBIDDEN**. The scientific benchmark laboratory **SHALL** measure the exact canonical parsing pipeline used in production, deprecating all legacy parsers from evaluation workflows.

## 4. DECISION DRIVERS & METRICS
| Primary Driver | Success Metric | Target Goal |
| :--- | :--- | :--- |
| **Scientific Accuracy** | Alignment between benchmark ingestion and production ingestion. | $100\%$ shared modules in execution path. |
| **Reliability** | CI Pipeline rejection rate of structurally flawed PRs. | Block $100\%$ of unintended schema mutations. |
| **Reproducibility** | Rate of "FileNotFound" errors during fresh environment test runs. | Force manual intervention ($0\%$ silent auto-creations). |

## 5. CONTEXT & FORENSIC EVIDENCE
* **Observed Failures:** Architectural regressions pass tests because oracles dynamically overwrite expected results. 
* **Forensic Proof:** `GAP-0.4-09` (Tautology: `expected_fingerprint = current_fingerprint`); `P3-H04` (Benchmark points to obsolete `core/ast/parser.py`); `E-0.4-389` (Remote execution gates missing entirely).

## 6. DECISION NORMATIVE STATEMENTS (RFC 2119)
1. **Benchmark Alignment:** The evaluation benchmark **MUST** instantiate the exact extraction and builder patterns wired in the production composition root.
2. **Anti-Tautology Rule:** Integration tests **MUST NOT** mutate, reassign, or conditionally bypass the expected oracle variables during test execution.
3. **Fail-Fast Snapshots:** Missing baseline files during automated test execution **MUST** throw a terminal error. Snapshot creation **SHALL** be strictly isolated to manual developer invocations via an explicit CLI flag.
4. **CI Enforcement:** A declarative CI automation platform **MUST** be implemented, blocking merges to the main branch if any regression gate fails.

## 7. IMPLEMENTATION CONSTRAINTS
* **MUST** guarantee that the Golden Corpus is mounted as Read-Only during remote CI execution.
* **MUST NOT** rely on environment-specific tooling (CI pipelines must be declarative and vendor-agnostic in logic).

## 8. TRADE-OFFS
* **Pros:** Mathematical certainty against regressions; true measurement of production performance.
* **Cons:** Higher friction for developers when making intentional structural changes, requiring explicit manual regeneration of the Golden Corpus.

## 9. VERIFICATION & VALIDATION
* **Verification Mechanisms (Are we building it right?):**
  * **Static Linter:** CI configuration exists and enforces branch protection rules.
  * **Code Review:** Assert `test_golden_parser.py` lacks oracle reassignments.
* **Validation Mechanisms (Are we building the right thing?):**
  * **Mutation Testing:** Deliberately corrupt the parser output in a PR and validate that the CI platform successfully catches and fails the build.

## 10. ACCEPTANCE EVIDENCE (DONE WHEN)
* [ ] `expected_fingerprint = current_fingerprint` is permanently removed. *(Evidence Source: Code Audit)*
* [ ] Benchmark invokes the production adapter. *(Evidence Source: Architecture Review)*
* [ ] The continuous integration platform successfully blocks intentionally broken PRs. *(Evidence Source: CI Platform Logs)*

---
---

# NADR-F17BIS-11: Composition Root Exclusivity & Hexagonal Boundary Enforcement

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-11`
* **Title:** Composition Root Exclusivity, Strict Hexagonal Boundaries & Wiring Parity
* **Decision Class:** `STRUCTURAL`
* **Compliance Level:** `MANDATORY`
* **Decision Version:** 1.0.0
* **Lifecycle:** `APPROVED`
* **Effective Since:** Phase 17-BIS
* **Decision Authority:** Architecture Board
* **Technical Owner:** Platform Architecture Maintainer
* **Related Capability:** `CAP-008` (Unified Execution Plane)
* **Cross References:**
  * **Depends On:** All domain NADRs.
  * **Influences:** `NADR-F17BIS-04` (Validation Wiring), `NADR-F17BIS-05` (Context Wiring).
  * **Conflicts With:** Dynamic runtime module resolution or procedural wiring deep in domains.
  * **Supersedes:** Phase 15 Wiring Architecture.

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Maintainability:** 5 (Spaghetti wiring, hidden dependencies)
* **Operational:** 4 (CLI vs Daemon logic discrepancies)
* **Recoverability:** 3 (Complex to debug miswired states)
* **Financial:** 2 | **Security:** 2 | **Total Score: 16/25**

## 3. EXECUTIVE DECISION
The Architecture Board decrees that Dependency Injection **MUST** be governed exclusively by a unified, centralized Composition Root (`pipeline_factory.py`). The pure domain layer (`core/`) **MUST NOT** import concrete infrastructure implementations. Application daemons and CLI entrypoints **SHALL** converge on a unified execution plane, eliminating operational divergence.

## 4. DECISION DRIVERS & METRICS
| Primary Driver | Success Metric | Target Goal |
| :--- | :--- | :--- |
| **Maintainability** | Domain-to-Infrastructure import violations. | Zero boundary leaks (0 violations). |
| **Operational Parity** | Code path divergence between CLI and Daemon execution. | $100\%$ shared orchestration logic. |
| **Determinism** | Post-construction dependency mutation. | Zero mutative assignments for DI. |

## 5. CONTEXT & FORENSIC EVIDENCE
* **Observed Failures:** The platform behaves differently depending on how it is invoked. Core domain cannot execute without specific persistent database implementations present.
* **Forensic Proof:** `P1-01` (Direct import of persistent DB repository inside `core/`); `P4-02` (Divergence between CLI in-process semaphores and Daemon CQRS planes); `P4-06` (Mutating `dispatcher.validation_pipeline` post-instantiation).

## 6. DECISION NORMATIVE STATEMENTS (RFC 2119)
1. **Hexagonal Purity:** Files residing in `core/` **MUST NOT** contain concrete infrastructure imports. All infrastructure must be abstracted via abstract ports/protocols.
2. **Immutable Injection:** Dependencies **MUST** be supplied entirely via component constructors (`__init__`). Post-construction attribute mutation for wiring purposes is **FORBIDDEN**.
3. **Execution Parity:** The CLI execution mode **MUST** initialize and utilize the exact same orchestration pipeline and State Machine/CQRS logic as the Daemon mode.
4. **Encapsulation:** The Application layer (Daemons/CLI) **MUST NOT** access private internal states (e.g., `_cache`) of Domain Registries.

## 7. IMPLEMENTATION CONSTRAINTS
* **MUST NOT** rely on runtime reflection (e.g., `inspect`) to wire components; wiring must be explicit and statically analyzable.
* **MUST** abstract the persistent materialized cache and limiters behind pure domain interfaces.

## 8. TRADE-OFFS
* **Pros:** Flawless unit testing capability via mocks; guaranteed operational parity between CLI and production environments.
* **Cons:** Higher initial verbosity to define explicit Protocols and map them in the Composition Root.

## 9. VERIFICATION & VALIDATION
* **Verification Mechanisms (Are we building it right?):**
  * **Static Architecture Linter:** Enforce contract ensuring `core/` -> `infra/` imports are flagged as errors.
  * **Static Type Checker:** Ensure all dependencies are injected strictly via constructors.
* **Validation Mechanisms (Are we building the right thing?):**
  * **Integration E2E Test:** Execute a full end-to-end translation via CLI and validate that the output artifacts and Event Log entries identically match a Daemon-based execution.

## 10. ACCEPTANCE EVIDENCE (DONE WHEN)
* [ ] **Hexagonal Purity:** Static import linter passes with zero boundary violations. *(Evidence Source: CI Static Analysis)*
* [ ] **Immutable DI:** No mutable dependency assignments exist outside of constructors. *(Evidence Source: Manual Code Review)*
* [ ] **Execution Parity:** The CLI populates the State Machine and CQRS planes successfully without bypassing them. *(Evidence Source: CI Validation Test)*