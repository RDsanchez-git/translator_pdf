# HITO_5.0_ARCHITECTURE_AND_CONTRACT_AUDIT.md

**Estado:** FROZEN v1.0.2
**Fecha de emisión:** 2026-09-03
**Fecha de congelamiento:** 2026-09-03
**Fase:** 17-BIS — Fase 5 (Baseline Certification)
**Tipo de artefacto:** Compliance Audit + Discovery
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), NADR-F17BIS-12, NADR-F17BIS-13, NADR-F17BIS-14, NADR-F17BIS-16, NADR-F17BIS-17 (FROZEN, auditados directamente), NADR-F17BIS-15 (referencial, identidad), NADR-F17BIS-19 §5.5 R20 (referenciado, reutilización de build_extraction_pipeline), NADR-F17BIS-18 (fuera de alcance material, Fase 4), FASE_2_HANDOFF (FROZEN), FASE_3_HANDOFF (FROZEN), FASE_4_HANDOFF (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN), ENGINEERING_PRINCIPLES.md (FROZEN), código fuente auditado en core/benchmark/corpus/, core/benchmark/ground_truth/, tools/evaluation/.
**Mandato:** ¿Los contratos de dominio, puertos, servicios, tooling CLI y estado físico del repositorio están alineados con los NADRs FROZEN aplicables y los principios de ingeniería vigentes, de forma que habiliten la materialización y certificación de la baseline canónica?
**Síntesis:** La arquitectura de dominio está mayoritariamente alineada con los NADRs auditados. Se identifican 3 gaps (2 P1, 1 P2), 5 observaciones y 1 finding pre-certificación. Los gaps P1 son: (1) semántica de fallo heterogénea en tooling CLI (DF-18 carry-forward), (2) ausencia de configuración explícita de corpus_path en entry points. La conclusión central es que Fase 5 no necesita rediseñar el dominio fundamental de Ground Truth: es una fase de demostrar que los contratos existentes sobreviven al contacto con un corpus físico real y pueden producir una autoridad científica reproducible.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-03 | Emisión inicial. Auditoría de contratos, tooling y estado físico. |
| 1.0.0-FROZEN | 2026-09-03 | Verificación pyright de hipótesis H-5.0-A y H-5.0-B. Verificación forense de OracleSemanticIdentityCalculator.calculate(). Reclasificación de GAP-5.0-01 (P0→P1) y GAP-5.0-02 (P1→P2). Eliminación de DC-5.0-05. |
| 1.0.1-FROZEN | 2026-09-03 | Revisión epistemológica: (1) Separación de atomicidad lógica vs física del sellado; (2) Reformulación de DF-18 con 3 patrones heterogéneos de fallo; (3) Recalificación de NADR-14 R9 como discrepancia potencial; (4) GAP-5.0-04 reclasificado como Finding/DC; (5) Verificación de document_id en framing de manifest_hash; (6) Pilar 5 renombrado a "Operational Certification Tooling". |
| 1.0.2-FROZEN | 2026-09-03 | Corrección metodológica final: (1) Eliminación de P3 (no existe en metodología); GAP-5.0-06 → OBS-5.0-03; (2) Evidencias de verificación reclasificadas de P0 a P2 con columna Tipo; (3) GAP-5.0-02 → OBS-5.0-04 (no hay discrepancia contra contrato vigente); (4) GAP-5.0-03 reformulado como gap operacional con relación normativa TO BE VERIFIED; (5) Metadata NADR corregida a lista específica con aplicabilidad; (6) Reintroducción de E-5.0-023 y E-5.0-024; (7) Riesgo CorpusVersion eliminado por falta de evidencia propia en este HITO; (8) Cierre alineado con sección epistemológica; (9) Formulación de atomicidad física ampliada a Zero Partial Sealing como propiedad de estado observable; (10) Preguntas para ADR descompuestas por categoría de error; (11) Cobertura NADR explícita con tabla de aplicabilidad. |

---

## 1. RESUMEN EJECUTIVO

Se auditó el subsistema de baseline científica (core/benchmark/corpus, core/benchmark/ground_truth, tools/evaluation) y el estado físico del repositorio contra los contratos normativos de los NADRs FROZEN aplicables (12, 13, 14, 16, 17), el ADR Maestro F17-BIS, y los principios de ENGINEERING_PRINCIPLES.md. La auditoría cubrió 12 archivos fuente, el inventario de directorios y artefactos del corpus, y el código de OracleSemanticIdentityCalculator.

**Hallazgo central:**

> La Fase 5 no necesita rediseñar el dominio fundamental de Ground Truth. Los contratos de dominio (ontología, ciclo de vida, validez, completitud, identidad, asimetría de puertos) están materializados y presentan evidencia de cumplimiento en las superficies inspeccionadas. El problema real que queda para Fase 5 es demostrar que estos contratos sobreviven al contacto con un corpus físico real y pueden producir una autoridad científica reproducible. Los gaps identificados se concentran en la superficie operacional: tooling CLI sin semántica de fallo uniforme ni configurabilidad explícita de corpus_path, y estado físico del corpus en configuración pre-certificación.

**Defectos dominantes confirmados:**

1. **Semántica de fallo heterogénea en tooling CLI (E-5.0-002, E-5.0-003, E-5.0-004):** Los tres entry points de certificación presentan tres patrones de fallo distintos: `freeze_ground_truth.py` captura excepciones y retorna exit code 0; `generate_golden_draft.py` captura excepciones por documento y continúa con exit code 0; `bootstrap_corpus.py` no captura excepciones y produce exit code 1 por propagación. No existe una taxonomía explícita y uniforme de exit codes de certificación. DF-18 carry-forward de Fase 2.

2. **Ausencia de configuración explícita de corpus_path (E-5.0-005):** Los tres entry points tienen la ruta `tests/corpus/benchmark_v1` hardcodeada sin argumentos CLI configurables. Esto impide seleccionar de forma operacional el corpus a certificar sin modificar código. La relación exacta con NADR-14 §5.3 R9 queda como TO BE VERIFIED / DC-5.0-03.

3. **Estructura física del corpus en configuración pre-certificación (E-5.0-006):** `tests/corpus/benchmark_v1/` vacío; `tests/corpus/calibration_v1/` contiene 5 documentos con manifest, ground_truth y candidatos. Este es el estado natural pre-certificación que Fase 5 existe para resolver, no un defecto técnico.

**Veredicto:** El dominio de baseline (corpus, ground_truth, lifecycle, validity, completeness, sealing) está alineado con los NADRs auditados. La atomicidad lógica del caso de uso de sellado está verificada. La atomicidad física de la persistencia y la unidad mínima de commit de una baseline certificada permanecen TO BE VERIFIED. Los gaps operacionales deben ser analizados y resueltos o formalmente clasificados antes de que la baseline pueda considerarse apta para integración automatizada; la condición normativa exacta de bloqueo será establecida por ADR_F17-BIS_05.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. Su función es observar, clasificar y reconciliar evidencia.

Lo que este HITO **puede** concluir:
- Qué contratos existen en el código y si están alineados con los NADRs auditados.
- Qué gaps existen entre el estado observado y el estado requerido.
- Qué riesgos operacionales presenta el tooling CLI.
- Cuál es el estado físico del repositorio respecto al corpus canónico.
- Qué campos participan en identidades criptográficas (verificado en código).
- Si la atomicidad lógica del dominio está verificada.

Lo que este HITO **no puede** concluir:
- Si la escritura física del manifiesto es atómica (infra/fs/ fuera de scope).
- Cuál es la unidad física mínima de commit de una baseline certificada ni qué estados observables pueden existir si el proceso termina abruptamente en cualquier punto.
- La validez científica del contenido de los Ground Truths existentes (eso requiere curaduría humana).
- Si un gap bloquea o no la certificación (eso lo decide el ADR_F17-BIS_05 y el Execution Plan).
- Qué solución arquitectónica debe aplicarse para resolver los gaps.
- El comportamiento de los motores topológicos (core/benchmark/topology/ fuera de scope; auditado en Fase 4).

### 2.2 Método forense

La auditoría siguió el método:

1. Cargar fuentes normativas: ADR Maestro, NADRs aplicables, METHODOLOGY, ENGINEERING_PRINCIPLES.
2. Cargar HITOs previos y handoffs de Fases 1-4 como evidencia forense heredada.
3. Inspeccionar código fuente de core/benchmark/corpus/, core/benchmark/ground_truth/, tools/evaluation/.
4. Inspeccionar estado físico del repositorio (directorios, PDFs, manifests, JSONs).
5. Separar Observed / Required / Decision para cada tema auditado.
6. Registrar evidencia estable con IDs normalizados.
7. Consolidar gaps solo cuando existe discrepancia demostrada contra contrato vigente.
8. Verificar participación de campos en framing criptográfico (OracleSemanticIdentityCalculator y ManifestFingerprintCalculator).
9. Declarar TO BE VERIFIED cuando la evidencia es insuficiente.
10. Derivar Decision Candidates solo si la evidencia los exige.
11. Distinguir explícitamente entre atomicidad lógica del dominio y atomicidad física de la persistencia.
12. Clasificar hallazgos como GAP solo si existe discrepancia demostrada contra contrato vigente; como OBSERVACIÓN si no hay contrato afectado; como FINDING/DC si requiere decisión arquitectónica.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos | Estado |
|---|---|---|
| core/benchmark/corpus/models.py | DocumentFingerprint, CorpusVersion, CorpusDocumentMetadata, CorpusManifest | Auditado |
| core/benchmark/corpus/ports.py | DocumentMetadataExtractorPort, CorpusManifestReaderPort, CorpusManifestWriterPort | Auditado |
| core/benchmark/corpus/services.py | ManifestFingerprintCalculator, ManifestLineageSealer | Auditado |
| core/benchmark/ground_truth/models.py | GroundTruthLifecycleState, DraftSubState, GroundTruthDraft, SealedOracle, hydrate_ground_truth | Auditado |
| core/benchmark/ground_truth/ports.py | GroundTruthReaderPort, GroundTruthDraftWriterPort, ASTExtractionPort, GroundTruthArtifactPort | Auditado |
| core/benchmark/ground_truth/lifecycle.py | LifecycleTransitionAuthority | Auditado |
| core/benchmark/ground_truth/validity.py | OracleValidityContract | Auditado |
| core/benchmark/ground_truth/use_cases.py | LoadGroundTruthUseCase, GenerateGoldenDraftUseCase, SealGroundTruthUseCase | Auditado |
| core/benchmark/ground_truth/identity.py | OracleSemanticIdentityCalculator | Auditado |
| tools/evaluation/bootstrap_corpus.py | main() | Auditado |
| tools/evaluation/freeze_ground_truth.py | main() | Auditado |
| tools/evaluation/generate_golden_draft.py | main() | Auditado |
| Estado físico: tests/corpus/ | Directorios, PDFs, JSONs, manifests | Auditado |
| core/benchmark/corpus/dtos.py | RawDocumentEntryDTO, RawCorpusManifestDTO | Referenciado (uso en services.py) |
| core/benchmark/corpus/enums.py | ExtractionChallengeTrait | Referenciado (uso en models.py) |
| core/benchmark/ground_truth/errors.py | Taxonomía de errores | Referenciado (uso en use_cases.py, validity.py) |
| core/benchmark/ground_truth/completeness.py | BaselineCompletenessVerifier | Referenciado (FASE_2_HANDOFF, no re-auditado) |
| core/shared/identity_contracts.py | DocumentId, NodeId, GroundTruthState | Referenciado (FASE_3_HANDOFF, no re-auditado) |
| core/benchmark/topology/ | Todo el subpaquete | Fuera de scope (Fase 4, no re-auditado en este HITO) |
| infra/fs/ | Corpus repository, ground truth store | Fuera de scope (infraestructura de persistencia, no contratos de dominio) |
| tests/ | Suites de tests | Fuera de scope (no se auditan tests en este HITO) |

**Nota de claridad sobre cobertura NADR:**

| NADR | Aplicabilidad en HITO 5.0 | Justificación |
|---|---|---|
| NADR-F17BIS-12 | Directa — auditado | Ontología del oráculo, ciclo de vida |
| NADR-F17BIS-13 | Directa — auditado | Validez, completitud, atomicidad |
| NADR-F17BIS-14 | Directa — auditado | Asimetría de puertos, autoridad de sellado, tooling |
| NADR-F17BIS-15 | Referencial — no auditado | Identidad semántica del oráculo; consumido indirectamente vía identity.py |
| NADR-F17BIS-16 | Directa — auditado | Semántica de dimensiones de identidad |
| NADR-F17BIS-17 | Directa — auditado | Contratos de dominio para identidades criptográficas |
| NADR-F17BIS-18 | Fuera de alcance material — no auditado | Taxonomía de criticidad; pertenece a Fase 4, auditado en FASE_4_HANDOFF |
| NADR-F17BIS-19 | Referencial — §5.5 R20 verificado | Reutilización de build_extraction_pipeline(); resto de NADR-19 auditado en Fase 4 |

**Nota sobre DF-04:** Este HITO identifica que DF-04 (dualidad ZhangShasha/APTED) existe como carry-forward de Fase 4, pero NO audita los motores topológicos. La auditoría de DF-04 pertenece a HITO 5.3.

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER.md | Fuente normativa: invariantes, alcance, separación de conceptos |
| NADR | NADR-F17BIS-12 (Ontología del Oráculo) | Regla normativa: tipos disjuntos, ciclo de vida |
| NADR | NADR-F17BIS-13 (Validez y Completitud) | Regla normativa: contrato de validez, Zero Partial Sealing |
| NADR | NADR-F17BIS-14 (Asimetría de Puertos) | Regla normativa: puertos segregados, autoridad única |
| NADR | NADR-F17BIS-16 (Semántica de Identidad) | Regla normativa: dimensiones de identidad |
| NADR | NADR-F17BIS-17 (Contratos de Dominio) | Regla normativa: dominios formalmente definidos |
| NADR | NADR-F17BIS-15 (Identidad Semántica) | Referencial: identidad del oráculo |
| NADR | NADR-F17BIS-19 §5.5 R20 | Referencial: reutilización de pipeline |
| Handoff | FASE_4_HANDOFF.md | Estado de fase previa, carry-forwards |
| Handoff | FASE_3_HANDOFF.md | Estado de fase previa, contratos de dominio |
| Handoff | FASE_2_HANDOFF.md | Estado de fase previa, ontología del oráculo, DF-18 |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 | Estructura canónica del HITO |
| Metodología | METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md v1.3.0 | Jerarquía de gobernanza |
| Principios | ENGINEERING_PRINCIPLES.md | Ley inmutable de ingeniería |
| Código | core/benchmark/corpus/ (3 archivos) | Observación directa |
| Código | core/benchmark/ground_truth/ (6 archivos) | Observación directa |
| Código | tools/evaluation/ (3 archivos) | Observación directa |
| Disco | tests/corpus/ (inventario de archivos) | Estado físico del repositorio |
| Verificación | pyright (2 ejecuciones) | Resolución de hipótesis H-5.0-A y H-5.0-B |

---

## 5. MAPA DE FLUJOS OBSERVADOS

### FLUJO A — Bootstrap del corpus

```text
tools/evaluation/bootstrap_corpus.py::main()
  -> LocalFileSystemCorpusLoader(base_path)          [OK]
  -> PyMuPdfDocumentMetadataExtractor()               [OK]
  -> BootstrapCorpusManifestUseCase(reader, writer, extractor)  [OK]
  -> use_case.execute(base_path / "pdf")              [OK]
  -> print("[SUCCESS]...")                            [GAP: sin taxonomía de exit codes]

Patrón de fallo: excepción no capturada → propagación → exit code 1 (no diferenciado)

Leyenda:
  [OK] flujo sano observado
  [GAP] gap confirmado
```

### FLUJO B — Generación de golden drafts

```text
tools/evaluation/generate_golden_draft.py::main()
  -> LocalFileSystemCorpusLoader(base_path)           [OK]
  -> build_extraction_pipeline()                      [OK: reutilización NADR-19 §5.5 R20]
  -> BenchmarkParserBridge(pdf_directory, pipeline)   [OK]
  -> LocalFileSystemGroundTruthDraftWriter(base_path) [OK]
  -> GenerateGoldenDraftUseCase(extractor, writer, corpus_reader)  [OK: DF-14 resuelto]
  -> corpus_reader.load_raw_manifest()                [OK: fail-fast FileNotFoundError]
  -> loop: use_case.execute(doc_id)                   [OK]
    -> SealedOracleOverwriteError -> logger.warning + skip  [OBS-5.0-01]
    -> FileNotFoundError -> logger.warning + skip     [OK]
    -> EmptyGroundTruthDraftError -> logger.error     [OK]
    -> Exception -> logger.error + continúa           [OBS-5.0-02]
  -> return                                           [GAP: exit code 0 ante fallo]

Patrón de fallo: captura todas las excepciones → continúa → exit code 0

Leyenda:
  [OK] flujo sano observado
  [OBS] observación (requiere decisión en ADR)
  [GAP] gap confirmado
```

### FLUJO C — Sellado de Ground Truth (freeze)

```text
tools/evaluation/freeze_ground_truth.py::main()
  -> LocalFileSystemCorpusLoader(base_path)           [OK]
  -> LocalFileSystemGroundTruthArtifactAdapter(base)  [OK]
  -> LocalFileSystemGroundTruthReader(base_path)      [OK]
  -> corpus_reader.load_raw_manifest()                [OK]
  -> artifact_adapter.list_artifact_ids()             [OK]
  -> BaselineCompletenessVerifier.verify(...)         [OK: biyección bidireccional]
  -> loop: reader.load_ground_truth(doc_id)           [OK]
    -> OracleValidityContract.validate(doc_id, nodes) [OK: NADR-13 §5.1]
    -> GroundTruthDraft(document_id, nodes, DRAFT)    [OK]
    -> LifecycleTransitionAuthority.audit(draft)      [OK: NADR-12 §5.2]
    -> LifecycleTransitionAuthority.validate(audited) [OK]
  -> SealGroundTruthUseCase(corpus_reader, corpus_writer, artifact_port)  [OK: NADR-14 §5.2]
    -> Verificar completitud bidireccional            [OK]
    -> Verificar estado VALIDATED                     [OK]
    -> LifecycleTransitionAuthority.seal(draft)       [OK]
    -> OracleSemanticIdentityCalculator.calculate()   [OK: NADR-16 §5.2 R8]
    -> ManifestLineageSealer.seal_manifest_with_ground_truth()  [OK]
    -> corpus_writer.save_manifest_dto(sealed_manifest)  [TO BE VERIFIED: atomicidad física]
  -> logger.info("Cryptographic lock complete...")    [OBS-5.0-03: duplicado]
  -> return                                           [GAP: exit code 0 ante fallo]

Patrón de fallo: captura excepciones → logger.critical → return → exit code 0

Leyenda:
  [OK] flujo sano observado
  [OBS] observación
  [GAP] gap confirmado
  [TO BE VERIFIED] requiere auditoría de infra/fs/
```

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| # | Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|---|
| 1 | Contrato de dominio en document_id de ground_truth | GroundTruthDraft.document_id y SealedOracle.document_id usan str con min_length=1 | NADR-17 §5.1 R1 aplica solo a campos en identidad criptográfica. document_id NO participa en framing de oracle_hash (E-5.0-025). Framing de manifest_hash protegido por DocumentId en CorpusDocumentMetadata (E-5.0-026). | FASE_3_HANDOFF AD-01: contratos centralizados. | COMPLIANT (N/A: no participa en framing) | E-5.0-001, E-5.0-025, E-5.0-026 |
| 2 | Semántica de fallo en tooling CLI de certificación | Tres patrones heterogéneos: (a) freeze_ground_truth.py captura y retorna 0; (b) generate_golden_draft.py captura por doc y continúa con 0; (c) bootstrap_corpus.py no captura y propaga con 1. | NADR-14 §5.3 R8: fallos de integridad MUST propagarse como errores explícitos. ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos. | FASE_2_HANDOFF DF-18: "Entry points retornan exit code 0 en fallo. Destino: Fase 5." Debate P1-P5: DF-18 es BLOQUEANTE. | DISCREPANCY | E-5.0-002, E-5.0-003, E-5.0-004 |
| 3 | Configurabilidad de corpus_path en tooling CLI | Los 3 entry points tienen pathlib.Path("tests/corpus/benchmark_v1") hardcodeada. Sin argumentos CLI. | NADR-14 §5.3 R9: parámetros que determinan la identidad de la baseline MUST NO quedar fijados implícitamente. | Ninguna fase previa abordó la configurabilidad de rutas. | DISCREPANCY POTENCIAL — pendiente de confirmar si corpus_path constituye un parámetro de identidad/control de baseline bajo el alcance exacto de R9. | E-5.0-005 |
| 4 | Estado físico del corpus | tests/corpus/benchmark_v1/ vacío. tests/corpus/calibration_v1/ contiene 5 PDFs + 5 GT + manifest.json. 3 PDFs legacy en tests/corpus/ raíz sin manifest. | ADR Maestro §6 Fase 5: "Materialización de 20-30 documentos catalogados y sellados en disco bajo la firma global H_baseline." | FASE_4_HANDOFF §6.1: "Selección de los 20-30 documentos del corpus canónico." | FINDING (estado pre-certificación, no defecto) | E-5.0-006, E-5.0-007 |
| 5 | Autoridad única de sellado | SealGroundTruthUseCase es la única autoridad. ManifestGroundTruthUpdater eliminado. freeze_ground_truth.py delega en el use case. | NADR-14 §5.2 R4-R6: autoridad única, sin duplicación. | FASE_2_HANDOFF AD-08. | COMPLIANT | — |
| 6 | Completitud biyectiva (Zero Partial Sealing) | SealGroundTruthUseCase verifica orphan_drafts y missing_drafts. BaselineCompletenessVerifier verifica bidireccionalmente. | ADR Maestro §5: Zero Partial Sealing. NADR-13 §5.2 R4-R8. | FASE_2_HANDOFF: 10/10 reglas de NADR-13 materializadas. | COMPLIANT | — |
| 7 | Inmutabilidad de entidades de ciclo de vida | GroundTruthDraft, SealedOracle con frozen=True. LifecycleTransitionAuthority retorna nueva instancia en cada transición. | NADR-12 §5.3 R7-R9: inmutabilidad estricta. | FASE_2_HANDOFF: 9/9 reglas de NADR-12 materializadas. | COMPLIANT | — |
| 8 | Asimetría de puertos corpus | CorpusManifestReaderPort (solo load_raw_manifest) y CorpusManifestWriterPort (solo save_manifest_dto) segregados. | NADR-14 §5.1 R1-R3. | FASE_2_HANDOFF AD-07. | COMPLIANT | — |
| 9 | Validez estructural del oráculo | OracleValidityContract con 4 invariantes. | NADR-13 §5.1 R1-R3. | FASE_2_HANDOFF: 10/10 reglas de NADR-13 materializadas. | COMPLIANT | — |
| 10 | Ciclo de vida gobernado | LifecycleTransitionAuthority con 5 transiciones válidas y rechazo de transiciones ilegales. | NADR-12 §5.2 R4-R6. | FASE_2_HANDOFF: 9/9 reglas de NADR-12 materializadas. | COMPLIANT | — |
| 11 | Protección contra sobrescritura de oráculo sellado | GenerateGoldenDraftUseCase verifica ground_truth_state antes de escribir. Lanza SealedOracleOverwriteError. | NADR-12 §5.3 R9. | FASE_2_HANDOFF. | COMPLIANT | — |
| 12 | Formato de hash del manifiesto | ManifestFingerprintCalculator usa formato de 6 dimensiones. Sentinel "none" para valores None. DF-19 documentado. | NADR-16 §5.4 R13-R16. | FASE_2_HANDOFF AD-10. | COMPLIANT | — |
| 13 | Participación de document_id en framing de oracle_hash | OracleSemanticIdentityCalculator.calculate() NO incluye document_id. | N/A | N/A | VERIFIED | E-5.0-025 |
| 14 | Participación de document_id en framing de manifest_hash | ManifestFingerprintCalculator SÍ incluye doc.document_id, protegido por DocumentId. | N/A | N/A | VERIFIED | E-5.0-026 |
| 15 | Atomicidad del sellado | Atomicidad lógica verificada: BaselineContractError sin mutar estado en memoria. Único punto de I/O: save_manifest_dto (paso 8). Atomicidad física y unidad mínima de commit no verificadas (infra/fs/ fuera de scope). | NADR-13 §5.3 R9-R10: atomicidad del sellado. | FASE_2_HANDOFF: sellado atómico. | ATOMICIDAD LÓGICA: COMPLIANT. ATOMICIDAD FÍSICA: TO BE VERIFIED. | E-5.0-027 |

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación, P1 = defecto estructural, P2 = riesgo latente. Tipo: DEFECTO = discrepancia demostrada, VERIFICACIÓN = resolución de hipótesis, LIMITACIÓN = frontera epistemológica.

| ID | Tipo | Sev | Evidencia (archivo → código) | Hallazgo |
|---|---|---|---|---|
| **E-5.0-001** | DEFECTO | P2 | core/benchmark/ground_truth/models.py::GroundTruthDraft.document_id → document_id: str = Field(..., min_length=1) | **Asimetría de contrato de dominio en document_id.** GroundTruthDraft y SealedOracle usan str simple; CorpusDocumentMetadata usa DocumentId. NO viola NADR-17 porque document_id no participa en framing criptográfico de oracle_hash (E-5.0-025). Framing de manifest_hash protegido por DocumentId (E-5.0-026). Deuda defensiva menor. |
| **E-5.0-002** | DEFECTO | P1 | tools/evaluation/freeze_ground_truth.py::main → logger.critical(...); return | **Exit code 0 ante fallo crítico.** freeze_ground_truth.py captura excepciones y retorna None implícito en 5 puntos de fallo. Patrón: captura → log → return → exit 0. |
| **E-5.0-003** | DEFECTO | P1 | tools/evaluation/generate_golden_draft.py::main → except Exception as e: logger.error(...); (sin sys.exit) | **Exit code 0 ante fallo.** generate_golden_draft.py captura todas las excepciones por documento y continúa. Patrón: captura → log → continúa → exit 0. |
| **E-5.0-004** | DEFECTO | P1 | tools/evaluation/bootstrap_corpus.py::main → (sin try/except, sin sys.exit) | **Exit code no diferenciado.** bootstrap_corpus.py no captura excepciones. Un fallo produciría exit code 1 por unhandled exception, sin diferenciación de tipos de fallo. Patrón: excepción no capturada → propagación → exit 1. |
| **E-5.0-005** | DEFECTO | P1 | tools/evaluation/bootstrap_corpus.py::main → base_path = pathlib.Path("tests/corpus/benchmark_v1") | **Ausencia de configuración explícita de corpus_path.** Los 3 entry points tienen la misma ruta hardcodeada. Sin argumentos CLI. Impide seleccionar de forma operacional el corpus a certificar sin modificar código. |
| **E-5.0-006** | DEFECTO | P2 | tests/corpus/benchmark_v1/ → directorio vacío (0 archivos) | **Corpus benchmark_v1 vacío.** El directorio referenciado por los 3 entry points no contiene manifest.json, PDFs ni ground truths. Estado pre-certificación que Fase 5 existe para resolver. |
| **E-5.0-007** | DEFECTO | P2 | tests/corpus/ → johnstone00distribution_3hoja.pdf, marchenko_pastur_1967_3hoja.pdf, [Amoretal_2023]_3hojas.pdf + .ast.json | **PDFs legacy sin gobernanza de corpus.** 3 PDFs con sus AST JSON en la raíz de tests/corpus/ sin manifest ni estructura de corpus canónico. |
| **E-5.0-008** | DEFECTO | P2 | tools/evaluation/freeze_ground_truth.py::main → logger.info("Cryptographic lock complete...") duplicado en líneas consecutivas | **Logging duplicado.** El mensaje aparece dos veces consecutivas. No afecta funcionalidad ni contratos. Limpieza menor. |
| **E-5.0-023** | VERIFICACIÓN | P2 | pyright core/benchmark/ground_truth/lifecycle.py → 0 errors, 0 warnings, 0 informations | **H-5.0-A rechazada.** lifecycle.py es sintácticamente correcto. El truncamiento observado en Get-Content era artefacto del display de PowerShell. |
| **E-5.0-024** | VERIFICACIÓN | P2 | pyright tools/evaluation/freeze_ground_truth.py → 0 errors, 0 warnings, 0 informations | **H-5.0-B rechazada.** freeze_ground_truth.py es sintácticamente correcto. El truncamiento observado en Get-Content era artefacto del display de PowerShell. |
| **E-5.0-025** | VERIFICACIÓN | P2 | core/benchmark/ground_truth/identity.py::OracleSemanticIdentityCalculator.calculate → framing: node_id:node_type:strategy:payload_hash | **document_id NO participa en framing de oracle_hash.** Cierra H-5.0-C. El método recibe Tuple[ASTNode, ...] y NO incluye document_id. |
| **E-5.0-026** | VERIFICACIÓN | P2 | core/benchmark/corpus/services.py::ManifestFingerprintCalculator.compute_hash → document_payload incluye f"{doc.document_id}:..." | **document_id SÍ participa en framing de manifest_hash, pero está protegido.** CorpusDocumentMetadata.document_id usa DocumentId (prohíbe ':'). Cierra H-5.0-C. |
| **E-5.0-027** | LIMITACIÓN | P1 | core/benchmark/ground_truth/use_cases.py::SealGroundTruthUseCase.execute → self._corpus_writer.save_manifest_dto(sealed_manifest) | **Atomicidad del sellado: lógica verificada, física TO BE VERIFIED.** El caso de uso solo escribe UN archivo: el manifiesto. La atomicidad lógica está verificada. La atomicidad física y la unidad mínima de commit de una baseline certificada requieren auditoría de infra/fs/ (excluida del scope). La pregunta para HITO 5.2 / Gate 3 es: ¿cuál es la unidad física mínima de commit de una baseline certificada y qué estados observables pueden existir si el proceso termina abruptamente en cualquier punto? |

---

### Evidencia E-5.0-025: document_id NO participa en framing de oracle_hash

* **Archivo Fuente Primario:** core/benchmark/ground_truth/identity.py
* **Símbolo Auditado:** OracleSemanticIdentityCalculator.calculate()
* **Declaración Observada:**

```python
@staticmethod
def calculate(nodes: Tuple[ASTNode, ...]) -> str:
    parts = []
    for node in nodes:
        payload_json = node.payload.model_dump_json()
        payload_hash = compute_sha256(payload_json.encode("utf-8"))
        
        node_identity = (
            f"{node.node_id}:"              # ← node_id del ASTNode
            f"{node.node_type.value}:"      # ← tipo del nodo
            f"{node.strategy.value}:"       # ← estrategia de traducción
            f"{payload_hash}"               # ← hash del payload
        )
        parts.append(node_identity.encode("utf-8"))
    
    return compute_sha256(b"".join(parts))
```

* **Observed:** OracleSemanticIdentityCalculator.calculate() recibe Tuple[ASTNode, ...] (los nodos del oráculo). NO recibe document_id como parámetro. El framing incluye: node_id:node_type:strategy:payload_hash por cada nodo. document_id es metadata del contenedor (GroundTruthDraft/SealedOracle), no de los nodos AST.
* **Required:** NADR-17 §5.1 R1 aplica solo a campos que participan en identidad criptográfica.
* **Decision:** N/A
* **Hallazgo Forense:** document_id NO participa en el framing criptográfico del oracle_hash. La asimetría de contrato (str vs DocumentId) en GroundTruthDraft/SealedOracle es deuda técnica menor (P2), no un defecto estructural (P1).
* **Consecuencia Arquitectónica:** H-5.0-C cerrada. GAP-5.0-02 reclasificado a OBS-5.0-04. DC-5.0-05 eliminado.
* **Estado:** CLOSED — Verificación completa

---

### Evidencia E-5.0-026: document_id en manifest_hash está protegido por DocumentId

* **Archivo Fuente Primario:** core/benchmark/corpus/services.py
* **Símbolo Auditado:** ManifestFingerprintCalculator.compute_hash()
* **Declaración Observada:**

```python
document_payload = (
    f"{doc.document_id}:"          # ← document_id de CorpusDocumentMetadata
    f"{doc.fingerprint.sha256}:"
    f"{traits_str}:"
    f"{doc.page_count}:"
    f"{oracle_hash_str}:"
    f"{gt_state_str}"
)
```

* **Observed:** ManifestFingerprintCalculator.compute_hash() incluye doc.document_id en el payload del framing. CorpusDocumentMetadata.document_id usa DocumentId (contrato que prohíbe ':'). Si un GroundTruthDraft con document_id conteniendo ':' llegara al SealGroundTruthUseCase, fallaría al construir CorpusDocumentMetadata.
* **Required:** NADR-17 §5.1 R1: campos en identidad criptográfica deben tener dominio formalmente definido.
* **Decision:** FASE_3_HANDOFF AD-01: contratos centralizados en core/shared/identity_contracts.py.
* **Hallazgo Forense:** El framing de manifest_hash SÍ está protegido porque CorpusDocumentMetadata usa DocumentId. La protección defensiva es suficiente.
* **Consecuencia Arquitectónica:** Confirma que la asimetría str vs DocumentId en ground_truth es P2 (deuda defensiva), no P1.
* **Estado:** CLOSED — Verificación completa

---

### Evidencia E-5.0-027: Atomicidad del sellado — lógica verificada, física TO BE VERIFIED

* **Archivo Fuente Primario:** core/benchmark/ground_truth/use_cases.py
* **Símbolo Auditado:** SealGroundTruthUseCase.execute()
* **Declaración Observada:**

```python
def execute(self, validated_drafts: Tuple[GroundTruthDraft, ...]) -> str:
    # Pasos 1-7: verificación y sellado en memoria (sin I/O)
    # ...
    # Paso 8: ÚNICO punto de persistencia
    self._corpus_writer.save_manifest_dto(sealed_manifest)
    return sealed_manifest.manifest_hash
```

* **Observed:** SealGroundTruthUseCase.execute() realiza 7 pasos de verificación y sellado en memoria (sin I/O). El único punto de persistencia es el paso 8: save_manifest_dto(sealed_manifest). Los oráculos NO se escriben durante el sellado (ya están en disco, escritos por GenerateGoldenDraftUseCase).
* **Required:** NADR-13 §5.3 R9-R10: "El sellado MUST ser una operación atómica: o bien se certifica la baseline completa y válida, o bien no se certifica nada."
* **Decision:** FASE_2_HANDOFF: "sellado atómico."
* **Hallazgo Forense:** La atomicidad lógica está verificada: si cualquier verificación falla, BaselineContractError se lanza antes de cualquier mutación o I/O. La atomicidad física depende de la implementación de save_manifest_dto en infra/fs/corpus_repository.py. Además, la pregunta de Zero Partial Sealing no se reduce a write-then-rename: requiere determinar cuál es la unidad física mínima de commit de una baseline certificada y qué estados observables pueden existir si el proceso termina abruptamente en cualquier punto (incluyendo durante GenerateGoldenDraftUseCase, antes del sellado).
* **Consecuencia Arquitectónica:** El HITO no puede cerrar la pregunta de Zero Partial Sealing físico. La verificación debe realizarse en HITO 5.2 / Gate 3.
* **Estado:** ATOMICIDAD LÓGICA: CLOSED. ATOMICIDAD FÍSICA: TO BE VERIFIED.

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| **OBS-5.0-01** | generate_golden_draft.py captura SealedOracleOverwriteError y logea como logger.warning, continuando con el siguiente documento. Este comportamiento puede ser válido para campañas batch idempotentes donde se espera que algunos documentos ya estén sellados. La protección contra sobrescritura es una propiedad explícita del modelo existente. Requiere decisión arquitectónica: ¿es un expected per-document skip válido? | Medio | OPEN |
| **OBS-5.0-02** | generate_golden_draft.py captura Exception genérica y logea como error pero continúa. Fallos no tipados (PermissionError, JSONDecodeError, corrupción de disco, bugs inesperados) pasan desapercibidos. Esto es cualitativamente diferente de OBS-5.0-01: no es un skip esperado sino una captura ciega. Requiere decisión: ¿qué errores son campaign-fatal vs process-fatal vs expected per-document skips? | Medio | OPEN |
| **OBS-5.0-03** | freeze_ground_truth.py contiene logger.info("Cryptographic lock complete. Manifest verified under global SHA-256: %s", global_manifest_hash) duplicado en líneas consecutivas. No afecta funcionalidad ni contratos. Limpieza menor. | Bajo | OPEN |
| **OBS-5.0-04** | Asimetría defensiva de contrato de dominio: GroundTruthDraft.document_id y SealedOracle.document_id usan str simple; CorpusDocumentMetadata.document_id usa DocumentId. NO viola NADR-17 porque document_id no participa en framing de oracle_hash (E-5.0-025) y manifest_hash está protegido por DocumentId (E-5.0-026). Deuda técnica menor. Considerar unificación en Fase 18 si se refactoriza test-infra. | Bajo | DEFERRED |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Ontología del Oráculo y Ciclo de Vida (NADR-12)

| Elemento | Estado | Evidencia |
|---|---|---|
| Tipos disjuntos (GroundTruthDraft, SealedOracle) | EXISTENTE | models.py: clases separadas |
| Ciclo de vida gobernado (LifecycleTransitionAuthority) | EXISTENTE | lifecycle.py: 5 transiciones válidas |
| Inmutabilidad de entidades | EXISTENTE | models.py: frozen=True |
| Fábrica de hidratación | EXISTENTE | models.py: hydrate_ground_truth() |
| Protección contra sobrescritura de sellado | EXISTENTE | use_cases.py: SealedOracleOverwriteError |

**Veredicto del pilar:** COMPLETO. Las 9 reglas de NADR-12 están materializadas y alineadas.

### Pilar 2 — Validez y Completitud Biyectiva (NADR-13)

| Elemento | Estado | Evidencia |
|---|---|---|
| Contrato de validez estructural | EXISTENTE | validity.py: OracleValidityContract con 4 invariantes |
| Completitud biyectiva bidireccional | EXISTENTE | completeness.py: BaselineCompletenessVerifier |
| Atomicidad lógica del sellado | EXISTENTE | use_cases.py: BaselineContractError sin mutar |
| Atomicidad física del sellado | TO BE VERIFIED | E-5.0-027: requiere HITO 5.2 / Gate 3 |
| Rechazo explícito de oráculos inválidos | EXISTENTE | use_cases.py: BaselineContractError con lista de errores |

**Veredicto del pilar:** COMPLETO con 1 elemento TO BE VERIFIED. Las reglas de dominio están materializadas. La atomicidad física y la unidad mínima de commit de una baseline certificada requieren verificación en HITO 5.2 / Gate 3.

### Pilar 3 — Asimetría de Puertos y Autoridad Única (NADR-14)

| Elemento | Estado | Evidencia |
|---|---|---|
| Puertos segregados Reader/Writer | EXISTENTE | corpus/ports.py |
| Autoridad única de sellado | EXISTENTE | use_cases.py: SealGroundTruthUseCase |
| Duplicación eliminada | EXISTENTE | ManifestGroundTruthUpdater eliminado |
| Entry points componen dependencias | PARCIAL | Tooling CLI compone inline, no vía composition root dedicado |
| Fallos como errores explícitos | PARCIAL | **GAP-5.0-01:** semántica de fallo heterogénea |
| Parámetros no fijados implícitamente | PARCIAL | **GAP-5.0-03:** corpus_path hardcodeado; relación con R9 TO BE VERIFIED |

**Veredicto del pilar:** PARCIAL. Las reglas de dominio (R1-R6) están completas. Las reglas de tooling CLI (R7-R9) presentan gaps.

### Pilar 4 — Contratos de Dominio Criptográfico (NADR-17)

| Elemento | Estado | Evidencia |
|---|---|---|
| DocumentId en CorpusDocumentMetadata | EXISTENTE | corpus/models.py |
| GroundTruthState en CorpusDocumentMetadata | EXISTENTE | corpus/models.py |
| DocumentId en GroundTruthDraft/SealedOracle | DEUDA TÉCNICA (P2) | ground_truth/models.py: str simple. NO viola NADR-17 (E-5.0-025, E-5.0-026). |
| Inyectividad del framing verificada | EXISTENTE | FASE_3_HANDOFF: property-based tests |

**Veredicto del pilar:** COMPLETO con deuda técnica menor (OBS-5.0-04). El framing criptográfico está protegido.

### Pilar 5 — Operational Certification Tooling

**Nota:** Este pilar es una superficie operacional, no un bounded context de dominio.

| Elemento | Estado | Evidencia |
|---|---|---|
| Entry point de bootstrap | EXISTENTE | bootstrap_corpus.py |
| Entry point de sellado | EXISTENTE | freeze_ground_truth.py |
| Entry point de generación de borradores | EXISTENTE | generate_golden_draft.py |
| Entry point de regresión | EXISTENTE | run_regression.py (Fase 4, con exit codes 0/1/2) |
| Semántica de fallo uniforme | FALTANTE | **GAP-5.0-01:** Tres patrones heterogéneos. Sin taxonomía explícita. |
| Configurabilidad de corpus_path | FALTANTE | **GAP-5.0-03:** Rutas hardcodeadas sin argumentos CLI. |

**Veredicto del pilar:** PARCIAL. Los entry points existen y son funcionales para curaduría local, pero no están listos para certificación automatizada ni integración en CI.

---

## 14. GAPS CONSOLIDADOS

| GAP | Sev | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|---|
| **GAP-5.0-01** | **P1** | Semántica de fallo heterogénea en tooling CLI (DF-18 carry-forward). Tres patrones distintos: freeze_ground_truth.py captura y retorna 0; generate_golden_draft.py captura por documento y continúa con 0; bootstrap_corpus.py no captura y propaga con 1 no diferenciado. No existe taxonomía explícita y uniforme de exit codes de certificación. Impacto provisional: potencialmente bloqueante para certificación automatizada. Si ADR_F17-BIS_05 define freeze_ground_truth.py como mecanismo oficial de certificación, GAP-5.0-01 puede elevarse a bloqueante de Fase 5; en caso contrario, bloquea Fase 6 (CI). Clasificación definitiva pendiente de ADR_F17-BIS_05. | E-5.0-002, E-5.0-003, E-5.0-004 | NADR-14 §5.3 R8 / Pilar 3, 5 | **HITO 5.2** | OPEN |
| **GAP-5.0-03** | **P1** | Los entry points de curaduría no exponen configuración explícita de corpus_path. Esto impide seleccionar de forma operacional el corpus a certificar sin modificar código. La relación exacta con NADR-14 §5.3 R9 queda como TO BE VERIFIED / DC-5.0-03: requiere confirmar si corpus_path constituye un parámetro de identidad/control de baseline bajo el alcance exacto de R9 o un default operacional. | E-5.0-005 | Operational Certification Tooling / Pilar 3, 5 | **HITO 5.2** | OPEN |
| **GAP-5.0-05** | **P2** | 3 PDFs legacy en tests/corpus/ raíz sin manifest ni gobernanza. Riesgo de confusión con corpus canónico. | E-5.0-007 | ADR Maestro §5 / Pilar 2 | **HITO 5.1** | OPEN |

**Nota sobre reclasificaciones:**
- El item previamente identificado como GAP-5.0-02 (asimetría document_id) ha sido reclasificado como OBS-5.0-04. No existe discrepancia contra contrato vigente: NADR-17 §5.1 R1 no aplica porque document_id no participa en framing criptográfico (E-5.0-025, E-5.0-026).
- El item previamente identificado como GAP-5.0-04 (inconsistencia benchmark_v1 vs calibration_v1) ha sido reclasificado como FINDING / DC-5.0-01. No es un defecto técnico; es el estado natural pre-certificación que Fase 5 existe para resolver.
- El item previamente identificado como GAP-5.0-06 (logging duplicado) ha sido reclasificado como OBS-5.0-03. No existe discrepancia arquitectónica; es ruido operacional menor. La metodología no define P3.

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-5.0-A | El método seal() de LifecycleTransitionAuthority tiene un error de sintaxis. | **RECHAZADA** | E-5.0-023 | No hay acción requerida. |
| H-5.0-B | freeze_ground_truth.py tiene un error de sintaxis. | **RECHAZADA** | E-5.0-024 | No hay acción requerida. |
| H-5.0-C | GAP-5.0-02 (asimetría document_id) viola NADR-17 §5.1 R1 y es P1. | **RECHAZADA** | E-5.0-025, E-5.0-026 | Reclasificado a OBS-5.0-04. DC-5.0-05 eliminado. |
| H-5.0-D | La atomicidad del sellado es completa (lógica y física). | **RECHAZADA (parcialmente)** | E-5.0-027 | Atomicidad lógica verificada. Atomicidad física y unidad mínima de commit TO BE VERIFIED en HITO 5.2 / Gate 3. |

---

## 17. VERIFICACIÓN DE CUMPLIMIENTO ADR/NADR

| Regla | Fuente | Required | Observed | Estado | Evidencia |
|---|---|---|---|---|---|
| NADR-12 §5.1 R1 | NADR-12 | Ground Truth modelado como entidad de dominio | GroundTruthDraft y SealedOracle son entidades con document_id | PASS | models.py |
| NADR-12 §5.1 R2 | NADR-12 | Tipos disjuntos sin conversión implícita | Clases separadas. hydrate_ground_truth() retorna según state. | PASS | models.py |
| NADR-12 §5.1 R3 | NADR-12 | Artefacto no tratado como oráculo sin hidratación | hydrate_ground_truth() es el único punto de construcción. | PASS | models.py |
| NADR-12 §5.2 R4 | NADR-12 | Ciclo de vida explícito | LifecycleTransitionAuthority con 5 transiciones. | PASS | lifecycle.py |
| NADR-12 §5.2 R5 | NADR-12 | No inferencia de estado | hydrate_ground_truth() requiere state explícito. | PASS | models.py |
| NADR-12 §5.2 R6 | NADR-12 | Transiciones gobernadas | LifecycleTransitionAuthority única autoridad. | PASS | lifecycle.py |
| NADR-12 §5.3 R7 | NADR-12 | Inmutabilidad | frozen=True en ambas entidades. | PASS | models.py |
| NADR-12 §5.3 R8 | NADR-12 | Reemplazo, no mutación | Transiciones retornan nueva instancia. | PASS | lifecycle.py |
| NADR-12 §5.3 R9 | NADR-12 | Oráculo sellado no alterado | SealedOracleOverwriteError. | PASS | use_cases.py |
| NADR-13 §5.1 R1 | NADR-13 | Contrato de validez | OracleValidityContract con 4 invariantes. | PASS | validity.py |
| NADR-13 §5.1 R2 | NADR-13 | Invariantes mínimas | 4 invariantes implementadas. | PASS | validity.py |
| NADR-13 §5.1 R3 | NADR-13 | Rechazo explícito | OracleValidityError ante fallo. | PASS | validity.py |
| NADR-13 §5.2 R4 | NADR-13 | Biyección completa | BaselineCompletenessVerifier bidireccional. | PASS | completeness.py |
| NADR-13 §5.2 R5 | NADR-13 | Ambas direcciones | orphan_drafts y missing_drafts. | PASS | use_cases.py |
| NADR-13 §5.2 R6 | NADR-13 | Ausencia aborta sellado | BaselineContractError con missing_drafts. | PASS | use_cases.py |
| NADR-13 §5.2 R7 | NADR-13 | Oráculo huérfano aborta | BaselineContractError con orphan_drafts. | PASS | use_cases.py |
| NADR-13 §5.2 R8 | NADR-13 | No degradación a warnings | raise BaselineContractError. | PASS | use_cases.py |
| NADR-13 §5.3 R9 | NADR-13 | Atomicidad del sellado | Lógica: PASS. Física: TO BE VERIFIED. | PARTIAL | E-5.0-027 |
| NADR-13 §5.3 R10 | NADR-13 | Sin baseline parcial | BaselineContractError antes de mutación (lógica). Física: TO BE VERIFIED. | PARTIAL | E-5.0-027 |
| NADR-14 §5.1 R1 | NADR-14 | Puertos distintos | Reader/Writer segregados. | PASS | corpus/ports.py |
| NADR-14 §5.1 R2 | NADR-14 | Reader sin escritura | Solo load_raw_manifest(). | PASS | corpus/ports.py |
| NADR-14 §5.1 R3 | NADR-14 | Curaduría no consumida por runtime | TO BE VERIFIED — requiere análisis de imports. | TO BE VERIFIED | — |
| NADR-14 §5.2 R4 | NADR-14 | Autoridad única | SealGroundTruthUseCase. | PASS | use_cases.py |
| NADR-14 §5.2 R5 | NADR-14 | Sin duplicación | ManifestGroundTruthUpdater eliminado. | PASS | FASE_2_HANDOFF |
| NADR-14 §5.2 R6 | NADR-14 | Delegación en autoridad | freeze_ground_truth.py delega. | PASS | freeze_ground_truth.py |
| NADR-14 §5.3 R7 | NADR-14 | Composición vía raíz | PARTIAL — compone inline. | PARTIAL | tools/evaluation/ |
| NADR-14 §5.3 R8 | NADR-14 | Fallos como errores explícitos | PARTIAL — semántica heterogénea. | PARTIAL | E-5.0-002 a E-5.0-004 |
| NADR-14 §5.3 R9 | NADR-14 | Parámetros no fijados implícitamente | PARTIAL — corpus_path hardcodeado. Relación normativa TO BE VERIFIED. | PARTIAL | E-5.0-005 |
| NADR-17 §5.1 R1 | NADR-17 | Dominios para campos criptográficos | PASS — document_id NO participa en oracle_hash (E-5.0-025). manifest_hash protegido (E-5.0-026). | PASS | E-5.0-025, E-5.0-026 |
| NADR-17 §5.1 R3 | NADR-17 | Validación en construcción | PASS — Corpus valida vía DocumentId. Ground_truth no requiere (no participa en framing). | PASS | E-5.0-025, E-5.0-026 |
| NADR-17 §5.2 R5 | NADR-17 | Inyectividad del encoding | PASS — property-based tests Fase 3. | PASS | FASE_3_HANDOFF |
| NADR-19 §5.5 R20 | NADR-19 | Reutilización de build_extraction_pipeline() | PASS — generate_golden_draft.py lo usa. | PASS | generate_golden_draft.py |

---

## 18. MATRIZ DE TRAZABILIDAD DC

| DC | Tema | Evidencia HITO vinculada | Estado operativo en código | Fase destino |
|---|---|---|---|---|
| **DC-5.0-01** | Estructura física del corpus aún no canónica. benchmark_v1 vacío; calibration_v1 contiene 5 documentos. Requiere decisión de nomenclatura y estructura canónica. | E-5.0-006 | Ausente: no hay decisión previa | **ADR_F17-BIS_05** |
| **DC-5.0-02** | Semántica de fallo y taxonomía de exit codes para entry points de curaduría. ¿Qué errores son expected per-document skips? ¿Qué errores son campaign-fatal? ¿Qué errores son process-fatal? ¿Cómo se refleja cada categoría en exit code? ¿Puede una campaña terminar con éxito parcial? ¿Qué significa success de un batch? | E-5.0-002 a E-5.0-004, GAP-5.0-01, OBS-5.0-01, OBS-5.0-02 | Ausente: DF-18 sin resolver | **HITO 5.2 / ADR_F17-BIS_05** |
| **DC-5.0-03** | Configurabilidad de corpus_path: ¿argparse? ¿config file? ¿environment variables? ¿corpus_path es parámetro de identidad/control de baseline o default operacional? | E-5.0-005, GAP-5.0-03 | Ausente: rutas hardcodeadas | **HITO 5.2 / ADR_F17-BIS_05** |
| **DC-5.0-04** | Clasificación de PDFs sueltos en tests/corpus/: ¿candidatos para corpus canónico o residuos? | E-5.0-007 | Ausente: sin clasificación | **HITO 5.1** |
| ~~DC-5.0-05~~ | ~~Unificación de contrato document_id en ground_truth~~ | ~~E-5.0-001~~ | ~~No requerido~~ | **ELIMINADO** — document_id no participa en framing de oracle_hash (E-5.0-025). Framing de manifest_hash protegido (E-5.0-026). |

**Deferred Finding:** DF-5.0-01 — Considerar unificación de DocumentId en ground_truth en Fase 18 si se refactoriza test-infra. Vinculado a OBS-5.0-04.

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia relacionada |
|---|---|---|---|
| Sellado corrupto invisible en CI | Si DF-18 no se resuelve antes de Fase 6, un sellado fallido en freeze_ground_truth.py retornará exit code 0 y CI lo tratará como éxito. | Alto: corrupción silenciosa de baseline en CI | E-5.0-002, GAP-5.0-01 |
| Confusión de corpus | La coexistencia de benchmark_v1 (vacío) y calibration_v1 (con contenido) puede generar que el corpus se materialice en la ubicación incorrecta si no se decide la nomenclatura canónica en ADR_F17-BIS_05. | Medio: retrabajo operativo | E-5.0-006, DC-5.0-01 |
| PDFs legacy sin gobernanza | Los 3 PDFs en tests/corpus/ raíz podrían ser accidentalmente incluidos en una certificación de baseline sin pasar por el protocolo de curaduría. | Bajo: ruido en curaduría | E-5.0-007, GAP-5.0-05 |
| Atomicidad física y estados intermedios no caracterizados | Si el proceso de sellado termina abruptamente (crash, pérdida de energía), no está caracterizado qué estados observables puede presentar la baseline. Esto incluye no solo la escritura del manifiesto sino también la ventana entre GenerateGoldenDraftUseCase (que escribe artefactos GT) y SealGroundTruthUseCase (que sella el manifiesto). | Medio: requiere verificación en HITO 5.2 / Gate 3 | E-5.0-027 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

Con base en este HITO, el ADR_F17-BIS_05 (Baseline Certification) deberá responder:

1. ¿Cuál es la nomenclatura canónica y la estructura física del corpus materializado? (DC-5.0-01)

2. ¿Qué semántica de fallo y taxonomía de exit codes se aplicará a los entry points de curaduría? (DC-5.0-02) Descomposición:
   - ¿Qué errores son expected per-document skips (ej: SealedOracleOverwriteError)?
   - ¿Qué errores son campaign-fatal (ej: todos los documentos fallan)?
   - ¿Qué errores son process-fatal (ej: corrupción de disco, permisos)?
   - ¿Cómo se refleja cada categoría en exit code?
   - ¿Puede una campaña terminar con éxito parcial?
   - ¿Qué significa success de un batch?

3. ¿Los entry points de curaduría deben aceptar argumentos CLI, un archivo de configuración, o ambos? ¿corpus_path es un parámetro de identidad/control de la baseline o un default operacional? (DC-5.0-03)

4. ¿Los 3 PDFs sueltos en tests/corpus/ son candidatos para el corpus canónico de Fase 5? (DC-5.0-04)

5. ¿Los candidatos en calibration_v1/candidates/ (docling, pymupdf) son insumos de curaduría o deben formar parte del corpus sellado?

6. ¿Se requiere un protocolo de curaduría formal antes del sellado, o la validación estructural existente (OracleValidityContract) es suficiente como criterio de curaduría?

7. ¿Cómo se resuelve DF-19 (migración de formato de hash 4 a 6 dimensiones) para manifiestos existentes?

8. ¿Cuál es la unidad física mínima de commit de una baseline certificada y qué estados observables pueden existir si el proceso termina abruptamente en cualquier punto? (E-5.0-027)

9. Si ADR_F17-BIS_05 define freeze_ground_truth.py como mecanismo oficial de certificación, ¿GAP-5.0-01 se eleva a bloqueante de Fase 5?

---

## 21. CIERRE DEL HITO 5.0

Este HITO confirma que las reglas de dominio auditadas están materializadas y presentan evidencia de cumplimiento en las superficies inspeccionadas. La arquitectura de dominio de la baseline científica (corpus, ground_truth, lifecycle, validity, completeness, sealing) está mayoritariamente alineada con los NADRs auditados (12, 13, 14, 16, 17). La atomicidad física del sellado, la unidad mínima de commit de una baseline certificada, y la validez científica de los artefactos permanecen fuera de lo demostrable en este HITO.

**La Fase 5 no necesita, en principio, rediseñar el dominio fundamental de Ground Truth.** El problema real que queda para Fase 5 es demostrar que los contratos existentes sobreviven al contacto con un corpus físico real y pueden producir una autoridad científica reproducible:

```text
          FASES 2–4
              │
              ▼
      "Tenemos contratos"
              │
              ▼
          FASE 5
              │
       ¿funcionan sobre
        realidad física?
              │
       ┌──────┴──────┐
       ▼             ▼
   corpus real    GT real
       │             │
       └──────┬──────┘
              ▼
       sealing real
              │
              ▼
       calibración real
              │
              ▼
     BASELINE CERTIFICADA
```

Los gaps identificados se concentran en la superficie operacional (Operational Certification Tooling):

1. **GAP-5.0-01 (P1):** Semántica de fallo heterogénea en tooling CLI. Los gaps P1 deben ser analizados y resueltos o formalmente clasificados antes de que la baseline pueda considerarse apta para integración automatizada; la condición normativa exacta de bloqueo será establecida por ADR_F17-BIS_05.

2. **GAP-5.0-03 (P1):** Ausencia de configuración explícita de corpus_path. La relación con NADR-14 §5.3 R9 queda como TO BE VERIFIED.

3. **GAP-5.0-05 (P2):** PDFs legacy sin gobernanza. Requiere clasificación en HITO 5.1.

**Estado del HITO:** FROZEN v1.0.2
**Condición de cierre cumplida:**
- [x] Metadata completa y consistente
- [x] Changelog actualizado a versión de cierre
- [x] Límite epistemológico declarado
- [x] Todas las superficies explícitamente incluidas en el scope de este HITO fueron inspeccionadas
- [x] Fuentes de evidencia listadas
- [x] Todas las evidencias tienen ID estable
- [x] Todas las evidencias tienen severidad clasificada (P0/P1/P2; sin P3)
- [x] Todas las evidencias tienen tipo clasificado (DEFECTO/VERIFICACIÓN/LIMITACIÓN)
- [x] Todas las evidencias relevantes separan Observed / Required / Decision
- [x] Todos los gaps tienen evidencia vinculada
- [x] Todos los gaps tienen fase destino explícita
- [x] Todos los gaps tienen discrepancia demostrada contra contrato vigente
- [x] Items sin discrepancia contra contrato vigente reclasificados como OBS o Finding/DC
- [x] Todas las hipótesis cerradas (H-5.0-A: RECHAZADA, H-5.0-B: RECHAZADA, H-5.0-C: RECHAZADA, H-5.0-D: RECHAZADA parcialmente)
- [x] Cero hipótesis abiertas
- [x] Cero contradicciones con HITOs previos
- [x] Todos los IDs E, GAP, OBS, H estables y no reasignados
- [x] Resumen ejecutivo completo con hallazgo central y veredicto
- [x] Cadena de gobernanza verificada
- [x] Siguiente paso recomendado declarado
- [x] Cobertura NADR explícita con tabla de aplicabilidad
- [x] Separación explícita de atomicidad lógica vs física
- [x] Formulación de Zero Partial Sealing como propiedad de estado observable
- [x] Preguntas para ADR descompuestas por categoría de error
- [x] Cierre alineado con sección epistemológica

**Verificación de cadena de gobernanza:**
ADR_F17_BIS_MASTER → NADRs 12, 13, 14, 16, 17 → HITO 5.0 (este) → Gaps y DCs → (pendiente) ADR_F17-BIS_05 → NADRs de Fase 5 → Execution Plan.

**Contradicciones con HITOs previos:** Ninguna. Los hallazgos son consistentes con los carry-forwards de FASE_2_HANDOFF (DF-18, DF-19) y FASE_4_HANDOFF (DF-04).

**Decision Candidates generados:** DC-5.0-01 a DC-5.0-04. DC-5.0-05 eliminado tras verificación E-5.0-025 y E-5.0-026.

**Deferred Finding:** DF-5.0-01 — Unificación de DocumentId en ground_truth. Destino: Fase 18 (refactor test-infra). Vinculado a OBS-5.0-04.

**Siguiente paso recomendado:**
- **HITO 5.1** (Physical Corpus & Candidate Baseline Inventory): clasificar los PDFs sueltos, decidir nomenclatura del corpus canónico, resolver DC-5.0-01 y DC-5.0-04.
- **HITO 5.2** (CLI Tooling & Operational Integrity Audit): resolver DF-18, definir semántica de fallo y argumentos CLI (DC-5.0-02, DC-5.0-03). Verificar atomicidad física y unidad mínima de commit de una baseline certificada.
- **HITO 5.3** (Algorithmic Comparability Audit): resolver DF-04 (ZhangShasha vs APTED).
- **HITO 5.4** (Ground Truth Curation & Scientific Calibration Infrastructure Audit): auditar infraestructura de calibración.
- **SYNTHESIS**: ADR_F17-BIS_05 con insumos de HITO 5.0, 5.1, 5.2, 5.3, 5.4.

**Elementos TO BE VERIFIED pendientes:**

| Elemento | Razón de no resolución | Destino |
|---|---|---|
| NADR-14 §5.1 R3: Curaduría no consumida por runtime | Requiere análisis de imports en runtime que excede el scope de este HITO. | HITO 5.2 |
| NADR-13 §5.3 R9-R10: Atomicidad física y unidad mínima de commit | Requiere auditoría de infra/fs/ y caracterización de estados intermedios. | HITO 5.2 / Gate 3 |
| NADR-14 §5.3 R9: corpus_path como parámetro de identidad | Requiere decisión normativa sobre si corpus_path constituye parámetro de identidad/control de baseline. | ADR_F17-BIS_05 |
| OBS-5.0-01: SealedOracleOverwriteError como expected skip | Requiere decisión arquitectónica sobre semántica batch. | ADR_F17-BIS_05 |
| OBS-5.0-02: Captura de Exception genérica | Requiere decisión arquitectónica sobre categorías de error. | ADR_F17-BIS_05 |