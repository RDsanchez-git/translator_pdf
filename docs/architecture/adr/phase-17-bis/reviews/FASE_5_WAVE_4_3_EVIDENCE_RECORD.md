# FASE 5 — WAVE 4.3 FASE B: EVIDENCE & POST-RUN RECORD

**Documento:** docs/architecture/adr/phase-17-bis/reviews/FASE_5_WAVE_4_3_EVIDENCE_RECORD.md
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** 2026-09-12
**Gate:** Gate 4 — Certification Tooling & Execution Safety
**Wave:** 4.3 Fase B — Evidence Completeness & POST-RUN (Tasks 4.3.3, 4.3.4)
**Reglas:** NADR-24 §5.7 R29-R31, §5.9 R36-R37 | NADR-20 §5.1, §5.6 | NADR-23 R18

---

## 1. IDENTIDAD: CROSSWALK NORMATIVO (GF-02)

NADR-23 R18 define corpus_identity como "SHA-256 del manifest" para el Calibration
Provenance Record. NADR-24 R29 exige corpus identity y manifest identity como
entidades distintas conforme a NADR-20. NADR-20 define identidad por contenido por
documento (§5.1 R1-R4) y manifest_hash como identidad del manifest (§5.6 R24/R26),
pero no define un compuesto de nivel corpus: el corpus ES el conjunto de
identidades de contenido (§5.1-§5.5).

Resolución (interpretación normativa congelada, sin re-freeze de artefactos):

| Entidad | Fundamento | Valor en corpus v1.0 | Nombre en records NADR-23 (Wave 3.3) | Nombre en CertificationEvidence (NADR-24) |
|:---|:---|:---|:---|:---|
| Identidad de contenido por documento | NADR-20 §5.1 R1 | sha256 por PDF | (dentro del manifest) | insumo de corpus_identity |
| corpus_identity (compuesto de contenido) | NADR-20 §5.1-§5.5 (interpretación) | compute_corpus_content_identity(6 sha256) | no presente | corpus_identity |
| manifest_identity | NADR-20 §5.6 R24/R26 | 0fda7690... | corpus_identity (per R18) | manifest_identity |
| configuration_identity | NADR-22 §5.6 | b942fc95... | metric_configuration | configuration_identity |
| frozen_parameters_identity | NADR-23 §5.6 R24 | 67841171... | parameter_identity | frozen_parameters_identity |

Los artefactos de Wave 3.3 permanecen válidos: su valor es inequívoco y este
crosswalk documenta el mapeo entre diccionarios de ambos scopes.

**Reserva de serie de identificadores:** GF- = conflictos e interpretaciones
normativas (GF-01 taxonomía NADR-19/NADR-24, GF-02 crosswalk de identidades).
O- = observaciones sin conflicto normativo (O-4.2-1 BOM, O-4.3-1 legacy
benchmark_archive, O-4.3-2 SealedOracle Pydantic frozen).

## 2. EVIDENCE COMPLETENESS (Task 4.3.3)

core/benchmark/certification/evidence.py: CertificationEvidence (dataclass frozen)
con los 7 elementos mínimos R29 + evaluation_kind y result_identity (trazabilidad
R31). Functional Core puro: no lee disco; las identidades llegan computadas por el
Shell con calculadores existentes (Reuse Before Invent). serialize_evidence es
determinista (sort_keys, indent fijo, ensure_ascii=False): auditable sin
re-ejecución (R31). compute_corpus_content_identity es insensible al orden y
falla duro ante corpus vacío (NADR-20 R1).

## 3. POST-RUN VALIDATION (Task 4.3.4)

core/benchmark/certification/post_run.py: validate_post_run verifica
(a) Evaluation Provenance disponible, (b) biyección veredictos-manifest,
(c) aggregate result presente, (d) identidades R29 completas y consistentes
con las esperadas (incluida corpus_identity). Toda violación nombra el
elemento (R30/R37). El wiring con disco y con el runner de certificación
pertenece a Gate 5 (Task 5.2.1): no existe RUN de certificación que
post-validar hasta ese punto; el Functional Core queda implementado y
testeado en esta Wave.

## 4. TRAZABILIDAD

| Task | Reglas | Estado |
|:---|:---|:---:|
| 4.3.3 Evidence completeness | NADR-24 §5.7 R29-R31 | DONE |
| 4.3.4 POST-RUN VALIDATION | NADR-24 §5.9 R36-R37 | DONE |

**Nota de Gobernanza:** GF-02 es una interpretación normativa de crosswalk entre
scopes (NADR-23 vs NADR-24 vs NADR-20). No redefine reglas; documenta el mapeo
de entidades entre diccionarios de records distintos.
