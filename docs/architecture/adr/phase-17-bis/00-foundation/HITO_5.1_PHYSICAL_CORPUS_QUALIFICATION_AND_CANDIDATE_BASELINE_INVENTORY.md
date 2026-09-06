# HITO_5.1_PHYSICAL_CORPUS_QUALIFICATION_AND_CANDIDATE_BASELINE_INVENTORY.md

**Estado:** FROZEN v1.1.2
**Fecha de emisión:** 2026-09-03
**Fecha de congelamiento:** 2026-09-03
**Fase:** 17-BIS — Fase 5 (Baseline Certification)
**Tipo de artefacto:** Physical Corpus Qualification & Candidate Baseline Inventory
**Naturaleza:** Read-only. No se propone código de producción ni se materializan decisiones de implementación. No se certifica ningún artefacto. No se modifica ni se mueve ningún archivo.
**Evidencia Forense Vinculante:** ADR_F17_BIS_MASTER (FROZEN), NADR-F17BIS-12, NADR-F17BIS-13, NADR-F17BIS-14, NADR-F17BIS-16, NADR-F17BIS-17 (FROZEN, auditados directamente), HITO_5.0_ARCHITECTURE_AND_CONTRACT_AUDIT.md v1.0.2 (FROZEN), FASE_2_HANDOFF (FROZEN), FASE_3_HANDOFF (FROZEN), FASE_4_HANDOFF (FROZEN), METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 (FROZEN), ENGINEERING_PRINCIPLES.md (FROZEN), PROJECT_TREE.txt, código fuente auditado en core/benchmark/corpus/, core/benchmark/ground_truth/, tools/evaluation/, estado físico del repositorio auditado el 2026-09-03.
**Mandato:** Descubrir, inventariar, identificar, clasificar y calificar los artefactos físicos candidatos al corpus canónico, estableciendo su identidad criptográfica, procedencia, cobertura documental declarada, relación con Ground Truth/candidates existentes y elegibilidad física preliminar para avanzar al proceso de Baseline Certification, sin modificar ni certificar ningún artefacto.
**Síntesis:** Se descubrieron 15 artefactos PDF en el repositorio. Tras exclusión de 4 artefactos no candidatos (outputs de traducción, tests operacionales), quedan 11 artefactos candidatos. Tras deduplicación por SHA-256 (2 grupos: G1 con 4 copias, G2 con 2 copias; exceso total: 4), se obtienen 7 identidades de contenido únicas candidatas. calibration_v1 es un proto-corpus de 5 identidades con schema legacy (DF-19) cuyo hash almacenado NO coincide con el hash calculado por el algoritmo actual. calibration_v1 no es elegible para sealing bajo el contrato vigente; el tratamiento del artifact queda sujeto a decisión de ADR_F17_BIS_05. Pydantic ignora silenciosamente los campos legacy del manifest (violación de ENGINEERING_PRINCIPLES §IV). Los Ground Truths de calibration_v1 tienen node_id serializado en representación no canónica; la consecuencia sobre oracle_hash requiere verificación mediante hidratación + cálculo de identidad. La Coverage Declarada está limitada a native_pdf (1/7 traits). La Coverage Observada y la Coverage Requerida están fuera del scope de este HITO. Provenance no existe en el dominio actual.

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0-IN_PROGRESS | 2026-09-03 | Emisión inicial. Discovery físico completo. |
| 1.0.0-FROZEN | 2026-09-03 | Verificación de manifest hashes, deduplicación SHA-256, análisis de ground truth structure. Cierre formal. |
| 1.1.0-FROZEN | 2026-09-03 | Corrección forense crítica: (1) E-5.1-001 corregido con JSON real del archivo; (2) GAP-5.1-06 agregado (Pydantic silent ignore); (3) GAP-5.1-07 agregado (node_id no canónico); (4) GAP-5.1-03 y GAP-5.1-04 reclasificados como Finding/DC; (5) Matriz de Pilares y Matriz ORD agregadas; (6) Evidencias E-5.1-010 y E-5.1-011 agregadas. |
| 1.1.1-FROZEN | 2026-09-03 | Corrección de precisión epistemológica y neutralidad de gobernanza: (1) "elegibilidad física preliminar" en lugar de "elegibilidad para certificación"; (2) P0 precisado: bloquea calibration_v1, no toda la Fase 5; (3) node_id: consecuencia no verificada; (4) DC-5.1-06 mantiene neutralidad; (5) Dimensiones Declared/Observed/Required Coverage; (6) Límite 5.1 vs 5.4 reforzado; (7) "No elegible bajo contrato vigente" en lugar de "requiere migración"; (8) Nota de herencia DC-5.0-*; (9) Nota de secciones omitidas. |
| 1.1.2-FROZEN | 2026-09-03 | **Forensic Consistency Correction:** (1) Inventario físico reconciliado matemáticamente: 15 artefactos → 4 excluidos → 11 candidatos → 4 duplicados → 7 identidades únicas; (2) Separación explícita de niveles: PhysicalArtifact vs ContentIdentity vs CorpusDocument; (3) Taxonomía de calificación formalizada: ADVANCE_CANDIDATE / CONDITIONAL_CANDIDATE / TO_BE_VERIFIED / EXCLUDED; (4) "Coverage Declarada subrepresentada" corregido a "Coverage Declarada limitada"; (5) "Todas las hipótesis cerradas" corregido a "Todas las hipótesis tienen veredicto y destino explícitos"; (6) Pilar 3: "extra='forbid'" corregido a "Mecanismo de rechazo/detección explícita de campos desconocidos"; (7) "Estado DRAFT implícito" corregido a "ground_truth_state no materializado"; (8) Estimación 12-19 adquisiciones eliminada (no derivable); (9) Trazabilidad DF-19 → GAP-5.1-01 → E-5.1-001 formalizada; (10) Fecha corregida a 2026-09-03; (11) Tabla de reconstrucción aritmética del inventario agregada. |

**Nota metodológica sobre estructura:** Este HITO omite las secciones 6 (Inventario de Dimensiones), 8 (Mutation Semantics Matrix), 9 (Canonicalization Audit), 12 (Matriz de Triaje) y 17 (Verificación de Cumplimiento ADR/NADR) de la estructura canónica de METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0. Justificación: estas secciones aplican a Dimension & Mutation Semantics Audits, Canonicalization Audits y Compliance Audits respectivamente, no a un Discovery físico de inventario y calificación. La numeración de secciones presentes mantiene correspondencia con la estructura canónica sin reordenamiento.

**Nota de herencia de Decision Candidates:** HITO 5.1 referencia Decision Candidates heredados de HITO 5.0 (DC-5.0-01, DC-5.0-04) sin reasignar su identidad. Los DCs generados por HITO 5.1 usan prefijo DC-5.1-*. Los IDs son estables y no se reasignan entre versiones ni entre HITOs.

---

## 1. RESUMEN EJECUTIVO

Se ejecutó el discovery físico completo del repositorio contra las 8 preguntas forenses definidas en el mandato. La auditoría cubrió tests/corpus/, tests/fixtures/, datasets/, raíz del repositorio y tests/output/, excluyendo explícitamente venv/, .git/ y __pycache__/.

**Hallazgo central:**

> El repositorio contiene 15 artefactos PDF, de los cuales 4 son excluidos (outputs de traducción, tests operacionales) y 11 son candidatos. Tras deduplicación por SHA-256 (exceso: 4 copias redundantes en 2 grupos), se obtienen 7 identidades de contenido únicas candidatas. El proto-corpus calibration_v1 presenta tres condiciones que impiden su avance directo bajo el contrato vigente: (1) el hash almacenado del manifest no coincide con el hash calculado por el algoritmo actual de 6 dimensiones (DF-19 activo, P0 — bloquea la certificación de calibration_v1 como baseline, no bloquea la Fase 5 si se adquieren documentos nuevos); (2) Pydantic ignora silenciosamente los campos legacy del manifest sin emitir error ni warning (violación de ENGINEERING_PRINCIPLES §IV, P1); (3) los Ground Truths tienen node_id serializado en representación no canónica que potencialmente altera el framing de oracle_hash (consecuencia no verificada; requiere hidratación + cálculo de identidad, P1). La Coverage Declarada está limitada a native_pdf (1/7 traits). La baseline canónica de 20-30 documentos requiere adquisición externa, curaduría de traits, y decisión sobre el tratamiento de calibration_v1 y los artefactos legacy.

**Defectos dominantes confirmados:**

1. **DF-19 activo y verificado criptográficamente (E-5.1-001, GAP-5.1-01, P0):** El hash almacenado de calibration_v1/manifest.json (c64a74d7f483d9cebda323f5791b31afb450c139e5ac6d96e4c1786b227d37ea) NO coincide con el hash calculado por ManifestFingerprintCalculator.compute_hash() con el algoritmo actual de 6 dimensiones (2333205e8c3664585eebc35cb7e98be7ea4009ad9a5281eea1d0da71318841d7). calibration_v1 no es elegible para sealing bajo el contrato vigente (NADR-F17BIS-16 §5.4 R13-R16). El tratamiento del artifact (migración, regeneración, descarte, conservación como histórico) queda sujeto a decisión de ADR_F17_BIS_05. Este gap bloquea la certificación de calibration_v1 específicamente; no bloquea la Fase 5 si se adquieren documentos nuevos sin utilizar calibration_v1. **Trazabilidad:** DF-19 es el carry-forward histórico (FASE_2_HANDOFF). GAP-5.1-01 es la materialización actual de ese defecto. E-5.1-001 es la evidencia concreta.

2. **Pydantic ignora campos legacy silenciosamente (E-5.1-010, GAP-5.1-06, P1):** RawCorpusManifestDTO.model_validate_json() retorna DTO_VALID para calibration_v1/manifest.json a pesar de que el JSON contiene campos ground_truth_version y ground_truth_sha256 que NO existen en RawDocumentEntryDTO. Pydantic usa extra='ignore' por defecto y descarta silenciosamente los campos desconocidos. Viola ENGINEERING_PRINCIPLES §IV (Cero Fallos Silenciosos). Requiere un mecanismo explícito que impida la pérdida silenciosa de campos no reconocidos. La estrategia concreta queda a decisión de ADR_F17_BIS_05.

3. **node_id serializado en representación no canónica (E-5.1-011, GAP-5.1-07, P1):** Los Ground Truths de calibration_v1 tienen node_id serializado como "value='p1_b0'" en lugar de "p1_b0". OracleSemanticIdentityCalculator incluye node_id en el framing del oracle_hash. Si este valor es hidratado literalmente como node_id, el framing utilizado por OracleSemanticIdentityCalculator será diferente del framing canónico. Consecuencia no verificada: requiere hidratación + cálculo de identidad para confirmar si el oracle_hash resultante diverge del esperado (HITO 5.4).

4. **Coverage Declarada limitada (E-5.1-002, GAP-5.1-02, P1):** Los 5 documentos de calibration_v1 declaran solo native_pdf en traits. Coverage Declarada: 1/7 traits (14.3%). Los nombres de archivo sugieren variedad semántica (señales nominales), pero este HITO no verifica contenido real. La Coverage Observada corresponde a HITO 5.4 / curaduría humana. La Coverage Requerida corresponde a ADR_F17_BIS_05.

**Veredicto:** El universo físico de candidatos está identificado y caracterizado. Los contratos de dominio existentes son suficientes en principio (confirmado en HITO 5.0), pero el estado físico actual no es elegible para el proceso de certificación sin tratamiento previo. El HITO 5.1 establece la elegibilidad física preliminar de los candidatos; la certificabilidad real depende de HITO 5.2 (atomicidad física de persistencia, infra/fs/), HITO 5.3 (comparabilidad algorítmica), HITO 5.4 (curaduría de Ground Truth y calibración científica), y la síntesis en ADR_F17_BIS_05.

---

## 2. LÍMITE EPISTEMOLÓGICO Y MÉTODO FORENSE

### 2.1 Límite epistemológico

Este HITO es read-only. No propone implementación. No decide diseño. No crea entidades. No modifica código. No mueve archivos. No certifica ningún artefacto.

Lo que este HITO **puede** establecer:
- El universo físico exhaustivo de artefactos candidatos.
- La identidad física determinista (SHA-256) de cada artefacto.
- Los grupos de duplicados byte-a-byte.
- El lineage PDF ↔ manifest ↔ candidate ↔ Ground Truth ↔ Sealed Oracle.
- La Coverage Declarada en traits (ExtractionChallengeTrait).
- La elegibilidad física preliminar de cada identidad de contenido para avanzar al proceso de certificación.
- Los gaps de Coverage Declarada.
- La validez del hash del manifest contra el algoritmo actual.
- El comportamiento del DTO ante campos legacy.
- La estructura de serialización de los Ground Truths.

Lo que este HITO **no puede** establecer:
- La validez científica del contenido de los Ground Truths (requiere curaduría humana — HITO 5.4).
- La Coverage Observada (fenómenos realmente presentes en el documento — HITO 5.4 / curaduría humana).
- La Coverage Requerida (fenómenos que la baseline necesita cubrir — ADR_F17_BIS_05).
- La decisión final de qué documentos forman la baseline canónica (pertenece a ADR_F17_BIS_05).
- La política de selección (greedy, weighted set cover, manual experta — ADR_F17_BIS_05).
- La provenance de los documentos (no existe en el dominio actual).
- Si los .ast.json legacy son compatibles con el formato actual de ASTNode (requiere inspección de contenido — HITO 5.4).
- La atomicidad física de la persistencia (infra/fs/ fuera de scope — HITO 5.2).
- Que el sistema pueda sellar físicamente el corpus de forma atómica.
- Que un crash a mitad de sealing sea recuperable.
- Que CorpusRepository sea idempotente.
- Que GroundTruthStore garantice Zero Partial Sealing a nivel de filesystem.
- Si un replace() o write sequence preserva el baseline anterior.
- Que None sea semánticamente equivalente a DRAFT en ground_truth_state (no se demuestra en este HITO; requiere cita normativa explícita).

### 2.2 Método forense

La auditoría siguió el método:

1. **Physical Discovery:** Enumerar todos los archivos .pdf en scope definido.
2. **Identity by Content:** Calcular SHA-256 de cada artefacto usando Get-FileHash -LiteralPath.
3. **Duplicate Detection:** Agrupar artefactos por SHA-256 idéntico.
4. **Lineage Reconstruction:** Verificar correspondencia PDF ↔ manifest ↔ candidate ↔ Ground Truth.
5. **Manifest Validation:** Validar JSON sintáctico y contra RawCorpusManifestDTO (Pydantic).
6. **Manifest Hash Verification:** Recalcular manifest_hash con ManifestFingerprintCalculator y comparar con hash almacenado.
7. **DTO Behavior Audit:** Verificar comportamiento de Pydantic ante campos legacy no reconocidos.
8. **Ground Truth Structure Inspection:** Inspeccionar estructura JSON de Ground Truths para detectar defectos de serialización.
9. **Coverage Analysis:** Extraer traits declarados en manifests y comparar con ExtractionChallengeTrait.
10. **Candidate Qualification:** Clasificar cada identidad de contenido como ADVANCE_CANDIDATE, CONDITIONAL_CANDIDATE, TO_BE_VERIFIED, EXCLUDED.
11. **Gap Identification:** Comparar estado observado contra contratos normativos vigentes.

### 2.3 Límite entre HITO 5.1 y HITO 5.4

Este HITO observa **señales nominales** (nombres de archivo, metadatos declarados). No inspecciona **contenido real** de los documentos.

- **HITO 5.1 dice:** "El manifest declara únicamente native_pdf; existe una discrepancia entre la Coverage Declarada y las señales nominales del dataset (nombres de archivo como doc_03_math, doc_04_table, doc_05_graph)."
- **HITO 5.4 dice:** "Determinar mediante inspección si el documento realmente contiene multi-column, heavy math, tables, figures, etc."

El HITO 5.1 observa. El HITO 5.4 verifica contenido.

### 2.4 Niveles ontológicos del inventario

Este HITO distingue explícitamente tres niveles ontológicos:

| Nivel | Definición | Ejemplo |
|---|---|---|
| **PhysicalArtifact** | Un archivo PDF concreto en una ruta concreta del filesystem | tests/corpus/calibration_v1/pdf/doc_03_math.pdf |
| **ContentIdentity** | Una identidad de contenido única determinada por SHA-256 | 21b9283a... |
| **CorpusDocument** | Un documento candidato con lineage potencial (document_id) | doc_03_math |

Toda clasificación en este HITO declara explícitamente a qué nivel aplica.

---

## 3. ALCANCE AUDITADO

| Superficie | Módulos / Archivos | Estado |
|---|---|---|
| tests/corpus/ | 3 PDFs legacy + .ast.json, benchmark_v1/, calibration_v1/ | Auditado |
| tests/corpus/benchmark_v1/ | manifest.json (140 bytes, documents: []) | Auditado |
| tests/corpus/calibration_v1/ | manifest.json, 5 PDFs, 5 GTs, candidates/ | Auditado |
| tests/fixtures/ | sample_3_pages.pdf, sample_3_pages.pdf_assets | Auditado |
| datasets/ | pesaran1999.pdf, pesaran1999.pdf_assets | Auditado |
| Raíz del repositorio (*.pdf) | input.pdf, MVP_traduccion.pdf, translated_*.pdf, [Amoretal_2023]_3hojas.pdf | Auditado |
| tests/output/ | translated_marchenko_pastur_1967_3hoja.pdf | Auditado |
| venv/ | Excluido | Fuera de scope |
| .git/ | Excluido | Fuera de scope |
| __pycache__/ | Excluido | Fuera de scope |
| core/benchmark/corpus/enums.py | ExtractionChallengeTrait (7 traits) | Auditado |
| core/benchmark/corpus/dtos.py | RawDocumentEntryDTO, RawCorpusManifestDTO | Auditado |
| core/benchmark/corpus/services.py | ManifestFingerprintCalculator | Auditado (verificación de hash) |
| core/benchmark/ground_truth/identity.py | OracleSemanticIdentityCalculator | Referenciado (impacto de node_id en framing) |
| core/benchmark/topology/ | No auditado | Fuera de scope (Fase 4) |
| infra/fs/ | No auditado | Fuera de scope (HITO 5.2) |

---

## 4. FUENTES DE EVIDENCIA

| Tipo | Fuente | Uso en el HITO |
|---|---|---|
| ADR Maestro | ADR_F17_BIS_MASTER.md §5, §6 | Invariantes, alcance, corpus de 20-30 documentos |
| NADR | NADR-F17BIS-12, 13, 14, 16, 17 | Reglas normativas de baseline |
| HITO previo | HITO_5.0 v1.0.2 | Estado de contratos de dominio, gaps operacionales |
| Handoff | FASE_2_HANDOFF, FASE_3_HANDOFF, FASE_4_HANDOFF | Carry-forwards (DF-18, DF-19) |
| Metodología | METHODOLOGY_FOR_FORENSIC_HITOs.md v1.2.0 | Estructura canónica del HITO |
| Principios | ENGINEERING_PRINCIPLES.md §IV | Cero Fallos Silenciosos |
| Código | core/benchmark/corpus/enums.py | ExtractionChallengeTrait |
| Código | core/benchmark/corpus/dtos.py | RawDocumentEntryDTO |
| Código | core/benchmark/corpus/services.py | ManifestFingerprintCalculator.compute_hash() |
| Disco | tests/corpus/, tests/fixtures/, datasets/, raíz | Estado físico del repositorio |
| Verificación | Get-FileHash -LiteralPath (PowerShell) | Identidad física SHA-256 |
| Verificación | Python: RawCorpusManifestDTO.model_validate_json() | Validación de manifests contra DTO |
| Verificación | Python: ManifestFingerprintCalculator.compute_hash() | Recálculo de manifest_hash |
| Verificación | Python: hydrate_ground_truth() | Intento de hidratación de GTs (fallido: TypeError) |
| Inspección | Get-Content doc_01_single.json | Estructura de Ground Truth |

---

## 5. INVENTARIO FÍSICO RECONSTRUIBLE

### 5.1 Tabla primaria de reconstrucción aritmética

| Métrica | Valor | Derivación |
|---|---|---|
| Artefactos PDF totales descubiertos | **15** | Enumeración recursiva completa |
| Artefactos excluidos (outputs/tests) | **4** | input.pdf, MVP_traduccion.pdf, translated_c17cb80d.pdf, translated_marchenko.pdf |
| Artefactos candidatos | **11** | 15 - 4 = 11 |
| Grupos de duplicados | **2** | G1 (84891f98...), G2 (21b9283a...) |
| Copias en G1 | **4** | [Amoretal] raíz, [Amoretal] corpus, doc_02_double, sample_3_pages |
| Copias en G2 | **2** | marchenko_pastur, doc_03_math |
| Exceso de duplicados | **4** | (4-1) + (2-1) = 3 + 1 = 4 |
| Identidades de contenido únicas candidatas | **7** | 11 - 4 = 7 |

**Verificación:** 15 artefactos - 4 excluidos = 11 candidatos. 11 candidatos - 4 duplicados = 7 identidades únicas. ✅

### 5.2 Inventario completo de artefactos (nivel PhysicalArtifact)

| # | Ruta relativa | SHA-256 | Bytes | Grupo | Clasificación |
|---|---|---|---|---|---|
| A01 | calibration_v1/pdf/doc_01_single.pdf | 2a1bab7f... | 531,778 | — | Candidato |
| A02 | calibration_v1/pdf/doc_02_double.pdf | 84891f98... | 2,045,076 | G1 | Candidato |
| A03 | calibration_v1/pdf/doc_03_math.pdf | 21b9283a... | 1,048,265 | G2 | Candidato |
| A04 | calibration_v1/pdf/doc_04_table.pdf | de56cd04... | 2,267,779 | — | Candidato |
| A05 | calibration_v1/pdf/doc_05_graph.pdf | 274ce908... | 100,864 | — | Candidato |
| A06 | tests/corpus/johnstone00distribution.pdf | b4f8e7a8... | 563,435 | — | Candidato |
| A07 | tests/corpus/marchenko_pastur.pdf | 21b9283a... | 1,048,265 | G2 | Candidato |
| A08 | tests/corpus/[Amoretal_2023].pdf | 84891f98... | 2,045,076 | G1 | Candidato |
| A09 | tests/fixtures/sample_3_pages.pdf | 84891f98... | 2,045,076 | G1 | Candidato |
| A10 | datasets/raw/pesaran1999.pdf | f1c80072... | 1,704,156 | — | Candidato |
| A11 | [Amoretal_2023].pdf (raíz) | 84891f98... | 2,045,076 | G1 | Candidato |
| A12 | input.pdf (raíz) | c17cb80d... | 287,835 | — | **EXCLUDED** |
| A13 | MVP_traduccion.pdf (raíz) | c4460cb9... | 4,068 | — | **EXCLUDED** |
| A14 | translated_c17cb80d...pdf (raíz) | ce2bd33e... | 4,069 | — | **EXCLUDED** |
| A15 | tests/output/translated_marchenko.pdf | 1cbeb59a... | 26,831 | — | **EXCLUDED** |

### 5.3 Tabla de deduplicación (nivel ContentIdentity)

| Grupo | SHA-256 | Copias | Exceso | Artefactos |
|---|---|---|---|---|
| **G1** | 84891f98... | 4 | 3 | [Amoretal] raíz, [Amoretal] corpus, doc_02_double, sample_3_pages |
| **G2** | 21b9283a... | 2 | 1 | marchenko_pastur, doc_03_math |
| — | 2a1bab7f... | 1 | 0 | doc_01_single |
| — | de56cd04... | 1 | 0 | doc_04_table |
| — | 274ce908... | 1 | 0 | doc_05_graph |
| — | b4f8e7a8... | 1 | 0 | johnstone00 |
| — | f1c80072... | 1 | 0 | pesaran1999 |
| **Total** | — | **11** | **4** | — |

**Verificación:** 11 candidatos - 4 exceso = 7 identidades únicas. ✅

### 5.4 Identidades de contenido únicas candidatas (nivel ContentIdentity)

| ID | SHA-256 | Artefacto canónico | Tamaño | Lineage |
|---|---|---|---|---|
| CI-01 | 2a1bab7f... | doc_01_single.pdf | 531,778 | calibration_v1 completo |
| CI-02 | 84891f98... | doc_02_double.pdf | 2,045,076 | calibration_v1 completo |
| CI-03 | 21b9283a... | doc_03_math.pdf | 1,048,265 | calibration_v1 completo |
| CI-04 | de56cd04... | doc_04_table.pdf | 2,267,779 | calibration_v1 completo |
| CI-05 | 274ce908... | doc_05_graph.pdf | 100,864 | calibration_v1 completo |
| CI-06 | b4f8e7a8... | johnstone00distribution.pdf | 563,435 | Legacy (.ast.json) |
| CI-07 | f1c80072... | pesaran1999.pdf | 1,704,156 | Sin lineage |

### 5.5 Mapa de flujos observados (lineage)

    CI-01 a CI-05 (calibration_v1):
      PDF (disco)
        -> manifest.json [FORMATO LEGACY: ground_truth_version, ground_truth_sha256]
          -> RawCorpusManifestDTO.model_validate_json()
            -> DTO_VALID [Pydantic ignora campos legacy silenciosamente]  [GAP-5.1-06]
            -> ground_truth_state = None (default, no del JSON)
            -> oracle_hash = None (default, no del JSON)
          -> ManifestFingerprintCalculator.compute_hash() [6 dimensiones]
            -> computed_hash ≠ stored_hash  [GAP-5.1-01, DF-19]
        -> ground_truth/*.json
          -> node_id: "value='p1_b0'"  [GAP-5.1-07: representación no canónica]
          -> OracleSemanticIdentityCalculator.calculate()
            -> CONSECUENCIA NO VERIFICADA: requiere hidratación + cálculo  [HITO 5.4]

    benchmark_v1:
      -> manifest.json [documents: [], hash correcto]
      -> pdf/ [directorio no existe]

    CI-06, CI-07 (legacy):
      -> .ast.json [formato Fase 16/17] o sin lineage
      -> Sin manifest entry
      -> Sin candidates
      -> Sin oracle_hash

---

## 7. MATRIZ OBSERVED / REQUIRED / DECISION

| # | Tema | Observed | Required | Decision previa | Estado | Evidencia |
|---|---|---|---|---|---|---|
| 1 | Hash de calibration_v1/manifest.json | stored_hash (c64a74d7...) ≠ computed_hash (2333205e...) | NADR-16 §5.4 R13-R16: manifest_hash debe ser recomputable determinísticamente | FASE_2_HANDOFF AD-10: formato extendido 4→6 dimensiones. DF-19 como carry-forward. | DISCREPANCY | E-5.1-001 |
| 2 | Comportamiento de Pydantic ante campos legacy | RawCorpusManifestDTO.model_validate_json() retorna DTO_VALID. Campos legacy ignorados silenciosamente. | ENGINEERING_PRINCIPLES §IV: Cero Fallos Silenciosos. | Ninguna fase previa abordó este comportamiento. | DISCREPANCY | E-5.1-010 |
| 3 | Serialización de node_id en Ground Truths | node_id: "value='p1_b0'" en doc_01_single.json. Representación no canónica. Consecuencia sobre oracle_hash: NO VERIFICADA. | OracleSemanticIdentityCalculator espera node_id como string simple. | FASE_3_HANDOFF AD-01: contratos de dominio centralizados. | DISCREPANCY (consecuencia no verificada) | E-5.1-011 |
| 4 | Coverage Declarada en calibration_v1 | Solo native_pdf para los 5 documentos. Coverage Declarada: 1/7 traits (14.3%). | ADR Maestro §6: "20-30 documentos de alta varianza" | FASE_4_HANDOFF §6.3. | DISCREPANCY | E-5.1-002 |
| 5 | benchmark_v1 manifest | documents: [], hash correcto (MATCH: True) | N/A (corpus vacío válido) | Bootstrap ejecutado sin PDFs. | COMPLIANT | E-5.1-004 |
| 6 | Lineage de calibration_v1 | 5/5 con manifest + candidates + GT. 0/5 sellados. ground_truth_state no materializado. | NADR-13 §5.2, NADR-12 §5.1. | FASE_2_HANDOFF. | COMPLIANT (parcial: sin sellado) | E-5.1-005 |
| 7 | Provenance | No existe en RawDocumentEntryDTO ni en CorpusDocumentMetadata | ADR Maestro §5: Determinismo y Reproducibilidad | Ninguna fase previa abordó provenance. | FINDING (DC-5.1-05) | E-5.1-009 |
| 8 | Duplicados físicos | G1: 4 copias, G2: 2 copias. Exceso: 4. | ENGINEERING_PRINCIPLES §I (YAGNI). | Ninguna fase previa abordó deduplicación. | FINDING (DC-5.1-01) | E-5.1-003 |
| 9 | Déficit cuantitativo de corpus | 7 identidades únicas vs 20-30 requeridos. Déficit observado: 13-23. | ADR Maestro §6. | FASE_4_HANDOFF §6.1. | FINDING (DC-5.1-03) | E-5.1-009 |
| 10 | Coverage Observada | No verificada. Señales nominales sugieren variedad no declarada. | HITO 5.4 / curaduría humana | No corresponde a este HITO. | OUT OF SCOPE (HITO 5.4) | — |
| 11 | Coverage Requerida | No definida. Requiere decisión de ADR_F17_BIS_05. | ADR_F17_BIS_05 | No corresponde a este HITO. | OUT OF SCOPE (ADR) | — |

### 7.1 Tres dimensiones de Coverage

| Dimensión | Definición | Quién la establece | HITO 5.1 establece |
|---|---|---|---|
| **A. Coverage Declarada** | Traits registrados en manifest | HITO 5.1 (observable) | SÍ |
| **B. Coverage Observada** | Fenómenos realmente presentes en el documento | HITO 5.4 / curaduría humana | NO — fuera de scope |
| **C. Coverage Requerida** | Fenómenos que la baseline necesita cubrir | ADR_F17_BIS_05 | NO — fuera de scope |

**Regla:** Declared ≠ Observed ≠ Required. El HITO 5.1 solo mide (A). La brecha entre (A) y (B) es responsabilidad de HITO 5.4. La brecha entre (B) y (C) es responsabilidad de ADR_F17_BIS_05.

---

## 10. REGISTRO DE EVIDENCIA FORENSE

IDs normalizados y estables. Severidad: P0 = bloquea certificación del artifact afectado, P1 = defecto estructural, P2 = riesgo latente. Tipo: DEFECTO = discrepancia demostrada, VERIFICACIÓN = resolución de hipótesis, LIMITACIÓN = frontera epistemológica.

| ID | Tipo | Sev | Evidencia | Hallazgo |
|---|---|---|---|---|
| **E-5.1-001** | DEFECTO | **P0** | calibration_v1/manifest.json → stored_hash vs computed_hash | **DF-19 activo y verificado.** Hash almacenado ≠ hash calculado. Bloquea certificación de calibration_v1. No bloquea Fase 5. Trazabilidad: DF-19 (carry-forward) → GAP-5.1-01 (materialización) → E-5.1-001 (evidencia). |
| **E-5.1-002** | DEFECTO | **P1** | calibration_v1/manifest.json → traits | **Coverage Declarada limitada.** 5 documentos declaran solo native_pdf. 1/7 traits (14.3%). Señales nominales sugieren variedad no declarada. |
| **E-5.1-003** | DEFECTO | **P2** | SHA-256 deduplication → G1 (4 copias), G2 (2 copias) | **Redundancia física.** Exceso: 4 copias redundantes. |
| **E-5.1-004** | VERIFICACIÓN | **P2** | benchmark_v1/manifest.json → hash MATCH: True | **benchmark_v1 es corpus vacío válido.** |
| **E-5.1-005** | VERIFICACIÓN | **P2** | Lineage reconstruction → 5/5 completos | **Lineage completo para calibration_v1.** 0/5 sellados. ground_truth_state no materializado. |
| **E-5.1-006** | VERIFICACIÓN | **P2** | doc_01_single.json → array de ASTNode | **Ground Truths son arrays de ASTNode serializados.** Ninguno sellado. |
| **E-5.1-007** | VERIFICACIÓN | **P2** | Qualification analysis | **Qualification Matrix.** 5 ADVANCE_CANDIDATE, 2 CONDITIONAL_CANDIDATE. |
| **E-5.1-008** | VERIFICACIÓN | **P2** | Legacy .ast.json → formato Fase 16/17 | **Legacy .ast.json en formato antiguo.** 3 identidades requieren tratamiento. |
| **E-5.1-009** | LIMITACIÓN | **P2** | RawDocumentEntryDTO → sin campos de provenance | **Provenance no existe en dominio.** |
| **E-5.1-010** | DEFECTO | **P1** | Python: DTO_VALID con campos legacy ignorados | **Pydantic ignora campos legacy silenciosamente.** Viola ENGINEERING_PRINCIPLES §IV. |
| **E-5.1-011** | DEFECTO | **P1** | doc_01_single.json → "node_id": "value='p1_b0'" | **node_id en representación no canónica.** Consecuencia no verificada. Requiere HITO 5.4. |

---

### Evidencia E-5.1-001: DF-19 activo y verificado criptográficamente

* **Archivo Fuente Primario:** tests/corpus/calibration_v1/manifest.json
* **Símbolo Auditado:** manifest_hash
* **Trazabilidad:** DF-19 (carry-forward histórico, FASE_2_HANDOFF) → GAP-5.1-01 (materialización actual) → E-5.1-001 (evidencia concreta).
* **Declaración Observada (JSON REAL del archivo):**

    {
      "corpus_version": "v1.0",
      "manifest_hash": "c64a74d7f483d9cebda323f5791b31afb450c139e5ac6d96e4c1786b227d37ea",
      "documents": [
        {
          "document_id": "doc_01_single",
          "sha256": "2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3",
          "traits": ["native_pdf"],
          "page_count": 3,
          "ground_truth_version": null,
          "ground_truth_sha256": null
        }
      ]
    }

* **Observed:** El archivo contiene campos ground_truth_version y ground_truth_sha256 (formato de 4 dimensiones, pre-Fase 3). Hash almacenado: c64a74d7... Hash calculado por algoritmo actual (6 dimensiones): 2333205e... Los hashes NO coinciden. benchmark_v1 (0 documentos) produce MATCH: True.
* **Required:** NADR-F17BIS-16 §5.4 R13-R16.
* **Decision:** FASE_2_HANDOFF AD-10. DF-19 como carry-forward.
* **Hallazgo Forense:** DF-19 es una discrepancia criptográfica activa y verificada. calibration_v1 no es elegible para sealing bajo el contrato vigente. El tratamiento del artifact queda sujeto a decisión de ADR_F17_BIS_05. Bloquea la certificación de calibration_v1 específicamente; no bloquea la Fase 5.
* **Estado:** OPEN — Tratamiento sujeto a decisión de ADR_F17_BIS_05.

---

### Evidencia E-5.1-010: Pydantic ignora campos legacy silenciosamente

* **Archivo Fuente Primario:** tests/corpus/calibration_v1/manifest.json + core/benchmark/corpus/dtos.py
* **Símbolo Auditado:** RawCorpusManifestDTO.model_validate_json() + RawDocumentEntryDTO
* **Observed:** El JSON contiene campos ground_truth_version y ground_truth_sha256 que NO existen en RawDocumentEntryDTO. Pydantic (extra='ignore' por defecto) los descarta silenciosamente. DTO_VALID. ground_truth_state y oracle_hash se establecen como None (defaults).
* **Required:** ENGINEERING_PRINCIPLES §IV.
* **Decision:** Ninguna fase previa abordó este comportamiento.
* **Hallazgo Forense:** El sistema acepta un manifest con campos legacy sin error, warning ni índice. Viola Cero Fallos Silenciosos.
* **Estado:** OPEN — Requiere un mecanismo explícito que impida la pérdida silenciosa de campos no reconocidos. La estrategia concreta queda a decisión de ADR_F17_BIS_05 (DC-5.1-06).

---

### Evidencia E-5.1-011: node_id serializado en representación no canónica

* **Archivo Fuente Primario:** tests/corpus/calibration_v1/ground_truth/doc_01_single.json
* **Símbolo Auditado:** node_id en ASTNode serializado
* **Observed:** node_id = "value='p1_b0'" en lugar de "p1_b0". Representación string de un objeto Pydantic.
* **Required:** NADR-F17BIS-17 §5.2 R5. FASE_3_HANDOFF AD-01.
* **Consecuencia demostrada:** Si se hidrata literalmente, el framing de OracleSemanticIdentityCalculator será diferente del canónico.
* **Consecuencia NO verificada:** Para confirmar divergencia del oracle_hash se requiere: (1) hidratación, (2) cálculo de identidad, (3) comparación contra referencia canónica. Este experimento NO se completó (hydrate_ground_truth() falló con TypeError). Corresponde a HITO 5.4.
* **Estado:** OPEN — Consecuencia no verificada. HITO 5.4.

---

## 11. OBSERVACIONES COMPLEMENTARIAS

| ID | Observación | Impacto | Estado |
|---|---|---|---|
| OBS-5.1-01 | tmptu237h6p es copia exacta de doc_01_single.json (SHA-256 idéntico). Residuo temporal. | Bajo | OPEN |
| OBS-5.1-02 | candidates/ (docling, pymupdf) son insumos de curaduría, no parte del ground truth. | Bajo | OPEN |
| OBS-5.1-03 | *_assets (1 byte) son residuos del pipeline, no PDFs. | Bajo | OPEN |
| OBS-5.1-04 | Señales nominales: doc_02_double → posible MULTI_COLUMN, doc_03_math → posible HEAVY_MATH, doc_04_table → posible NESTED_TABLES, doc_05_graph → posible FLOATING_FIGURES. No verificadas. Coverage Observada corresponde a HITO 5.4. | Medio | OPEN |
| OBS-5.1-05 | input.pdf y MVP_traduccion.pdf son artefactos operacionales, no candidatos. | Bajo | OPEN |
| OBS-5.1-06 | translated_*.pdf son outputs del pipeline, no documentos fuente. | Bajo | OPEN |
| OBS-5.1-07 | El manifest no contiene ground_truth_state materializado para calibration_v1. No se demuestra en este HITO que None sea semánticamente equivalente a DRAFT. Se requiere cita normativa explícita si se establece ese mapping. | Medio | OPEN |

---

## 13. MATRIZ DE PILARES

### Pilar 1 — Identidad Física y Deduplicación

| Elemento | Estado | Evidencia |
|---|---|---|
| SHA-256 calculado para todos los PDFs | EXISTENTE | E-5.1-004 |
| Grupos de duplicados identificados | EXISTENTE | E-5.1-003: G1 (4), G2 (2) |
| Inventario aritméticamente reconstruible | EXISTENTE | §5.1: 15 → 4 excluidos → 11 → 4 duplicados → 7 únicos |
| Política de deduplicación | FALTANTE | DC-5.1-01 |

**Veredicto del pilar:** PARCIAL. Identidad establecida. Política pendiente.

### Pilar 2 — Lineage y Ciclo de Vida

| Elemento | Estado | Evidencia |
|---|---|---|
| Lineage completo calibration_v1 | EXISTENTE | E-5.1-005 |
| Lineage legacy .ast.json | PARCIAL | E-5.1-008 |
| Sealed Oracles | FALTANTE | 0/5 |
| oracle_hash | FALTANTE | Todos None |
| ground_truth_state | FALTANTE | No materializado |

**Veredicto del pilar:** PARCIAL.

### Pilar 3 — Integridad Criptográfica del Manifest

| Elemento | Estado | Evidencia |
|---|---|---|
| benchmark_v1 hash | PASS | MATCH: True |
| calibration_v1 hash | FAIL | MATCH: False (DF-19) |
| Formato de manifest | LEGACY | 4 dimensiones en lugar de 6 |
| Mecanismo de rechazo/detección explícita de campos desconocidos | FALTANTE | extra='ignore' por defecto (GAP-5.1-06) |

**Veredicto del pilar:** FAIL.

### Pilar 4 — Cobertura Científica

| Elemento | Estado | Evidencia |
|---|---|---|
| Coverage Declarada | PARCIAL | Solo native_pdf (1/7) |
| Coverage Observada | TO BE VERIFIED | HITO 5.4 |
| Coverage Requerida | TO BE VERIFIED | ADR_F17_BIS_05 |
| Déficit cuantitativo | OBSERVADO | 7 vs 20-30 |
| Provenance | FALTANTE | No existe en dominio |

**Veredicto del pilar:** INSUFICIENTE.

### Pilar 5 — Operational Certification Tooling (superficie operacional)

| Elemento | Estado | Evidencia |
|---|---|---|
| Entry points de curaduría | EXISTENTE | bootstrap_corpus.py, freeze_ground_truth.py, generate_golden_draft.py |
| Exit codes diferenciados | FALTANTE | HITO 5.0 GAP-5.0-01 (DF-18) |
| Configurabilidad de corpus_path | FALTANTE | HITO 5.0 GAP-5.0-03 |

**Veredicto del pilar:** PARCIAL. Heredado de HITO 5.0.

---

## 14. GAPS CONSOLIDADOS

| GAP | Sev | Descripción | Evidencia | Pilar / Contrato | Fase destino | Estado |
|---|---|---|---|---|---|---|
| **GAP-5.1-01** | **P0** | DF-19 activo y verificado. calibration_v1/manifest.json: hash almacenado ≠ hash calculado. Bloquea certificación de calibration_v1 como baseline. No bloquea Fase 5. Trazabilidad: DF-19 → GAP-5.1-01 → E-5.1-001. | E-5.1-001 | NADR-F17BIS-16 §5.4 | **ADR_F17_BIS_05** | OPEN |
| **GAP-5.1-02** | **P1** | Coverage Declarada limitada a native_pdf (1/7 traits). Señales nominales sugieren variedad no declarada. Coverage Observada corresponde a HITO 5.4. | E-5.1-002 | ADR_F17_BIS_MASTER §6 | **Execution Plan Fase 5** | OPEN |
| **GAP-5.1-05** | **P2** | Legacy .ast.json en formato Fase 16/17. 3 identidades requieren tratamiento. Decisión sujeta a ADR_F17_BIS_05. | E-5.1-008 | NADR-F17BIS-12 §5.1 | **ADR_F17_BIS_05** | OPEN |
| **GAP-5.1-06** | **P1** | Pydantic ignora campos legacy silenciosamente. Viola ENGINEERING_PRINCIPLES §IV. Requiere mecanismo explícito; estrategia concreta a decisión de ADR. | E-5.1-010 | ENGINEERING_PRINCIPLES §IV | **ADR_F17_BIS_05** | OPEN |
| **GAP-5.1-07** | **P1** | node_id en representación no canónica. Consecuencia sobre oracle_hash no verificada. Requiere hidratación + cálculo de identidad (HITO 5.4). | E-5.1-011 | NADR-F17BIS-17 §5.2 R5 | **HITO 5.4** | OPEN |

**Nota sobre reclasificaciones:**
- GAP-5.1-03 (Redundancia física) → Finding / DC-5.1-01. No viola contrato normativo vigente.
- GAP-5.1-04 (Déficit cuantitativo) → Finding / DC-5.1-03. Estado natural pre-certificación.

---

## 15. ESTADO DE HIPÓTESIS

| ID | Hipótesis | Veredicto | Evidencia | Implicación |
|---|---|---|---|---|
| H-5.1-A | benchmark_v1 está vacío (sin manifest) | **RECHAZADA** | E-5.1-004 | Corpus vacío válido |
| H-5.1-B | calibration_v1/manifest.json compatible con algoritmo actual | **RECHAZADA** | E-5.1-001 | DF-19 activo |
| H-5.1-C | Traits declarados reflejan cobertura semántica real | **TO BE VERIFIED** | E-5.1-002 | HITO 5.4 / curaduría |
| H-5.1-D | Legacy .ast.json compatibles con ASTNode actual | **TO BE VERIFIED** | E-5.1-008 | HITO 5.4 |
| H-5.1-E | Pydantic rechaza campos desconocidos | **RECHAZADA** | E-5.1-010 | extra='ignore' |
| H-5.1-F | node_id compatible con OracleSemanticIdentityCalculator | **TO BE VERIFIED** | E-5.1-011 | HITO 5.4 |

**Nota:** Todas las hipótesis tienen veredicto y destino explícitos. No existen hipótesis abiertas sin destino. Las hipótesis TO BE VERIFIED están gestionadas (con destino asignado), no resueltas.

---

## 16. RESPUESTAS A PREGUNTAS DEL MANDATO

### 16.1 Q1 — ¿Cuál es el universo físico real?

**Respuesta forense (nivel PhysicalArtifact):** 15 artefactos PDF descubiertos. 4 excluidos (outputs/tests). 11 candidatos.

**Respuesta forense (nivel ContentIdentity):** 7 identidades de contenido únicas candidatas tras deduplicación (exceso: 4).

**Verificación aritmética:** 15 - 4 = 11 candidatos. 11 - 4 duplicados = 7 únicos. ✅

### 16.2 Q2 — ¿Cuáles son realmente documentos distintos?

**Respuesta forense:** 7 identidades de contenido únicas. G1: 4 copias (84891f98...), exceso 3. G2: 2 copias (21b9283a...), exceso 1. Duplicación estrictamente física (byte-a-byte), no semántica.

### 16.3 Q3 — ¿Qué artefactos ya tienen lineage?

**Respuesta forense:** 5 identidades (CI-01 a CI-05) con lineage completo en calibration_v1. 1 identidad (CI-06) con .ast.json legacy. 1 identidad (CI-07) sin lineage. 0 selladas. ground_truth_state no materializado.

### 16.4 Q4 — ¿Qué estado tienen realmente los Ground Truth?

**Respuesta forense:** 5 Ground Truths como arrays de ASTNode serializados con node_id en representación no canónica (GAP-5.1-07, consecuencia no verificada). El manifest no contiene ground_truth_state materializado. No se demuestra en este HITO que None sea semánticamente equivalente a DRAFT. Ninguno sellado. Manifest usa formato legacy (DF-19).

### 16.5 Q5 — ¿Qué cobertura científica representa el corpus?

**Respuesta forense:**

| Dimensión | Valor |
|---|---|
| A. Coverage Declarada | 1/7 traits (native_pdf). Medido por HITO 5.1. |
| B. Coverage Observada | No verificada. HITO 5.4. |
| C. Coverage Requerida | No definida. ADR_F17_BIS_05. |

### 16.6 Q6 — ¿Qué identidades de contenido son elegibles?

**Taxonomía de calificación (nivel ContentIdentity):**

| Calificación | Definición |
|---|---|
| **ADVANCE_CANDIDATE** | Físicamente apta para entrar al proceso de evaluación/certificación. NO significa apta para sealing. |
| **CONDITIONAL_CANDIDATE** | Requiere tratamiento previo (migración, clasificación, decisión de ADR). |
| **TO_BE_VERIFIED** | Evidencia insuficiente para clasificar. |
| **EXCLUDED** | No es documento fuente (output, test operacional). |

**Resultado:**

| CI | Identidad | Calificación | Justificación |
|---|---|---|---|
| CI-01 | doc_01_single (2a1bab7f...) | ADVANCE_CANDIDATE | Lineage completo en calibration_v1 |
| CI-02 | doc_02_double (84891f98...) | ADVANCE_CANDIDATE | Lineage completo. 4 copias (deduplicación pendiente) |
| CI-03 | doc_03_math (21b9283a...) | ADVANCE_CANDIDATE | Lineage completo. 2 copias (deduplicación pendiente) |
| CI-04 | doc_04_table (de56cd04...) | ADVANCE_CANDIDATE | Lineage completo |
| CI-05 | doc_05_graph (274ce908...) | ADVANCE_CANDIDATE | Lineage completo |
| CI-06 | johnstone00 (b4f8e7a8...) | CONDITIONAL_CANDIDATE | Legacy .ast.json, sin manifest |
| CI-07 | pesaran1999 (f1c80072...) | CONDITIONAL_CANDIDATE | Sin lineage, dataset externo |

**Nota:** ADVANCE_CANDIDATE no implica certificabilidad. calibration_v1 no es elegible para sealing bajo el contrato vigente (GAP-5.1-01). La calificabilidad para sealing depende de tratamiento previo y decisión de ADR_F17_BIS_05.

### 16.7 Q7 — ¿Qué sucede con los artefactos legacy?

**Respuesta forense:** 3 identidades legacy (CI-06 johnstone00, CI-03/G2 marchenko_pastur, CI-02/G1 Amoretal). 2 son duplicados de identidades gestionadas. 1 es única (johnstone00). El tratamiento queda sujeto a decisión de ADR_F17_BIS_05 (DC-5.1-04).

### 16.8 Q8 — ¿Cuál es el déficit del corpus?

**Respuesta forense:** Déficit cuantitativo observado: 7 identidades únicas vs rango nominal 20-30 (ADR Maestro §6). Déficit: 13-23 identidades. La estrategia de adquisición pertenece al ADR_F17_BIS_05 (DC-5.1-03).

---

## 18. MATRIZ DE TRAZABILIDAD DC

**Nota de herencia:** HITO 5.1 referencia DCs heredados de HITO 5.0 (DC-5.0-01, DC-5.0-04) sin reasignar su identidad. DCs generados por HITO 5.1 usan prefijo DC-5.1-*.

| DC | Tema | Evidencia | Fase destino |
|---|---|---|---|
| **DC-5.0-01** (heredado) | Estructura física del corpus | E-5.1-004, E-5.1-005 | ADR_F17_BIS_05 |
| **DC-5.0-04** (heredado) | Clasificación de PDFs sueltos | E-5.1-008 | ADR_F17_BIS_05 |
| **DC-5.1-01** | Política de deduplicación física | E-5.1-003 | ADR_F17_BIS_05 |
| **DC-5.1-02** | Curaduría de traits (Declared → Observed) | E-5.1-002 | ADR_F17_BIS_05 |
| **DC-5.1-03** | Política de adquisición (13-23 déficit) | E-5.1-009 | ADR_F17_BIS_05 |
| **DC-5.1-04** | Tratamiento de legacy .ast.json | E-5.1-008 | ADR_F17_BIS_05 |
| **DC-5.1-05** | Provenance | E-5.1-009 | ADR_F17_BIS_05 |
| **DC-5.1-06** | Mecanismo explícito contra pérdida silenciosa de campos | E-5.1-010 | ADR_F17_BIS_05 |
| **DC-5.1-07** | Corrección de serialización de node_id | E-5.1-011 | HITO 5.4 / Execution Plan |

---

## 19. APÉNDICE NO NORMATIVO — RIESGOS

| Riesgo | Descripción | Impacto | Evidencia |
|---|---|---|---|
| Sellado imposible de calibration_v1 sin tratamiento | No elegible bajo contrato vigente. Tratamiento sujeto a ADR. | Alto | E-5.1-001 |
| Migraciones incompletas indetectables | Pydantic ignora campos legacy. | Alto | E-5.1-010 |
| oracle_hash potencialmente incorrecto | Consecuencia no verificada. HITO 5.4. | Alto | E-5.1-011 |
| Confusión por duplicados | 4 copias del mismo documento. | Medio | E-5.1-003 |
| Cobertura insuficiente no detectada | Declared ≠ Observed ≠ Required. | Alto | E-5.1-002 |
| .ast.json legacy incompatibles | No verificado. HITO 5.4. | Medio | E-5.1-008 |
| Provenance ausente | No rastreable. | Medio | E-5.1-009 |

---

## 20. APÉNDICE NO NORMATIVO — PREGUNTAS PARA ADR

1. **DC-5.0-01:** ¿Nomenclatura canónica y estructura física del corpus?
2. **DC-5.0-04:** ¿Los 3 PDFs legacy son candidatos o residuos?
3. **DC-5.1-01:** ¿Política de deduplicación física?
4. **DC-5.1-02:** ¿Cómo se curarán traits para alinear Declared con Observed?
5. **DC-5.1-03:** ¿Política de adquisición para 13-23 identidades faltantes?
6. **DC-5.1-04:** ¿Tratamiento de legacy .ast.json?
7. **DC-5.1-05:** ¿Provenance en DTO o metadata externa?
8. **DC-5.1-06:** ¿Qué mecanismo explícito impedirá pérdida silenciosa de campos? La estrategia concreta queda a decisión de este ADR.
9. **DC-5.1-07:** ¿Cómo se corrige node_id? ¿Se requiere verificación previa (HITO 5.4)?
10. **DF-19:** ¿Tratamiento de calibration_v1/manifest.json?
11. **Coverage Requerida:** ¿Qué fenómenos debe cubrir la baseline? ¿7 traits suficientes o se requieren adicionales?

---

## 21. CIERRE DEL HITO 5.1

Este HITO confirma que el universo físico de candidatos al corpus canónico está identificado, caracterizado y aritméticamente reconstruible. Se descubrieron 15 artefactos PDF, de los cuales 4 son excluidos, 11 son candidatos, y tras deduplicación (exceso: 4) se obtienen 7 identidades de contenido únicas candidatas.

**La Fase 5 no necesita rediseñar el dominio fundamental.** Los contratos de dominio existentes son suficientes en principio (confirmado en HITO 5.0). Sin embargo, el estado físico actual presenta tres condiciones que impiden el avance directo de calibration_v1 bajo el contrato vigente:

1. **GAP-5.1-01 (P0):** DF-19 activo. Discrepancia criptográfica verificada. Bloquea certificación de calibration_v1; no bloquea Fase 5.
2. **GAP-5.1-06 (P1):** Pydantic ignora campos legacy silenciosamente. Viola ENGINEERING_PRINCIPLES §IV. Estrategia concreta a decisión de ADR.
3. **GAP-5.1-07 (P1):** node_id en representación no canónica. Consecuencia no verificada. HITO 5.4.

**El HITO 5.1 establece elegibilidad física preliminar, no certificabilidad.** La certificabilidad real depende de HITO 5.2, 5.3, 5.4 y ADR_F17_BIS_05.

**Estado del HITO:** FROZEN v1.1.2
**Condición de cierre cumplida:**
- [x] Metadata completa y consistente
- [x] Changelog actualizado
- [x] Límite epistemológico declarado
- [x] Superficies en scope inspeccionadas
- [x] Fuentes de evidencia listadas
- [x] Evidencias con ID estable, severidad y tipo
- [x] Evidencias separan Observed / Required / Decision
- [x] Gaps con evidencia vinculada y fase destino
- [x] Gaps con discrepancia demostrada contra contrato vigente
- [x] Items sin discrepancia reclasificados como Finding/DC
- [x] 8 preguntas forenses respondidas
- [x] Todas las hipótesis tienen veredicto y destino explícitos; no existen hipótesis abiertas sin destino
- [x] Cero contradicciones con HITOs previos
- [x] IDs estables y no reasignados
- [x] **Inventario físico aritméticamente reconstruible: 15 → 4 excluidos → 11 → 4 duplicados → 7 únicos**
- [x] **Niveles ontológicos separados: PhysicalArtifact / ContentIdentity / CorpusDocument**
- [x] **Taxonomía de calificación formalizada: ADVANCE_CANDIDATE / CONDITIONAL_CANDIDATE / TO_BE_VERIFIED / EXCLUDED**
- [x] **Coverage Declarada limitada (no "subrepresentada")**
- [x] **Mecanismo de rechazo/detección (no "extra='forbid'")**
- [x] **ground_truth_state no materializado (no "DRAFT implícito")**
- [x] **Estimación de adquisiciones eliminada del HITO**
- [x] **Trazabilidad DF-19 → GAP-5.1-01 → E-5.1-001 formalizada**
- [x] Matriz de Pilares presente (5 pilares)
- [x] Matriz ORD presente
- [x] Tres dimensiones de Coverage presentes
- [x] Límite 5.1 vs 5.4 reforzado
- [x] Neutralidad de gobernanza mantenida
- [x] Nota de herencia DC-5.0-* formalizada
- [x] Nota de secciones omitidas con justificación
- [x] Cadena de gobernanza verificada
- [x] Siguiente paso recomendado declarado

**Verificación de cadena de gobernanza:**
ADR_F17_BIS_MASTER → NADRs 12, 13, 14, 16, 17 → HITO 5.0 → HITO 5.1 (este) → Gaps y DCs → ADR_F17-BIS_05 → NADRs de Fase 5 → Execution Plan.

**Contradicciones con HITOs previos:** Ninguna.

**Decision Candidates generados:** DC-5.0-01 (heredado), DC-5.0-04 (heredado), DC-5.1-01 a DC-5.1-07.

**Deferred Findings:**
- DF-5.1-01: Redundancia física (G1: 4 copias, G2: 2 copias). Destino: ADR_F17_BIS_05 (DC-5.1-01).
- DF-5.1-02: Déficit cuantitativo observado (7 vs 20-30). Destino: ADR_F17_BIS_05 (DC-5.1-03).

**Siguiente paso recomendado:**
- **HITO 5.2** (CLI Tooling & Operational Integrity Audit): DF-18, semántica de fallo, atomicidad física de save_manifest_dto.
- **HITO 5.3** (Algorithmic Comparability Audit): DF-04 (ZhangShasha vs APTED).
- **HITO 5.4** (GT Curation & Scientific Calibration Infrastructure Audit): H-5.1-C, H-5.1-D, H-5.1-F. Verificación de node_id mediante hidratación + cálculo de identidad.
- **SYNTHESIS**: ADR_F17_BIS_05 con insumos de HITO 5.0, 5.1, 5.2, 5.3, 5.4.

**Elementos TO BE VERIFIED pendientes:**

| Elemento | Razón | Destino |
|---|---|---|
| H-5.1-C: Coverage Observada | Inspección de contenido | HITO 5.4 |
| H-5.1-D: Compatibilidad .ast.json | Inspección de contenido | HITO 5.4 |
| H-5.1-F: Consecuencia de node_id | Hidratación + cálculo | HITO 5.4 |
| Clasificación CI-06, CI-07 | Decisión humana | ADR_F17_BIS_05 |
| Coverage Requerida | Definición de ADR | ADR_F17_BIS_05 |
| Atomicidad física | infra/fs/ fuera de scope | HITO 5.2 |