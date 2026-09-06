# NADR-F17-BIS-21: Ground Truth Eligibility, Migration & Sealing

## 1. METADATA

* **Decision ID:** `NADR-F17-BIS-21`
* **Título:** Ground Truth Eligibility, Migration & Sealing
* **Clase de Decisión:** `DATA / OPERATIONAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.2.1
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 17-BIS — Fase 5 (Baseline Certification)
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Baseline Certification Team
* **Capacidad Arquitectónica:** CAP-F5-02 (Ground Truth Eligibility, Migration & Sealing) — Establece las reglas normativas para el ciclo de vida del Ground Truth desde su generación hasta su sellado como oráculo canónico, incluyendo la elegibilidad, canonicalización de identidad, validez estructural, migración de artefactos legacy, protección de oráculos sellados, y el sellado criptográfico bajo Zero Partial Sealing.
* **Evidencia Forense:** `E-5.4-001` (manifest legacy DF-19), `E-5.4-004` (node_ids legacy), `E-5.4-008` (.ast.json legacy incompatibles), `E-5.4-012` (OracleSemanticIdentityCalculator incluye node_id), Verificación forense H-5.1-F (hash legacy ≠ hash canónico), Verificación forense H-5.1-D (.ast.json incompatibles), `GAP-5.4-001`, `GAP-5.4-002`, `GAP-5.4-004`, `GAP-5.2-05` (Certification Boundary Integrity violation)
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (FROZEN), `ADR_F17_BIS_05` (FROZEN), `NADR-F17-BIS-20` (Canonical Corpus Qualification), `NADR-F17BIS-12` (Ontología GT), `NADR-F17BIS-13` (Validez y Completitud), `NADR-F17BIS-14` (Autoridad de Sellado), `NADR-F17BIS-16` (Semántica de Identidad), `NADR-F17BIS-17` (Contratos de Dominio)
  * **Influencia:** `NADR-F17-BIS-22` (Canonical Evaluation Configuration), `NADR-F17-BIS-23` (Scientific Calibration), `NADR-F17-BIS-24` (Certification Tooling Integrity), `PHASE_17BIS_FASE5_EXECUTION_PLAN`
  * **Conflictúa con:** Sellado parcial de corpus, modificación de oráculos sellados, sellado de artefactos legacy sin migración, canonicalización no determinista de node_ids, sobrescritura de oráculos sellados sin verificación de estado.
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-09-05 | Emisión inicial DRAFT. 31 reglas normativas en 8 dominios. |
| 1.1.0 | 2026-09-05 | Versión combinada: (1) Agregado dominio de Validez Estructural; (2) Agregado dominio de Protección de Oráculos Sellados; (3) Agregada hidratación canónica explícita; (4) Agregadas restricciones del contrato de dominio para node_ids; (5) Clase de Decisión actualizada a DATA / OPERATIONAL. Total: 43 reglas normativas en 9 dominios. |
| 1.2.0 | 2026-09-05 | Correcciones: (1) Changelog corregido: "36 reglas" → "43 reglas"; (2) GAP-5.4-003 eliminado de evidencia forense (responsabilidad de NADR-20, no de NADR-21); (3) R40: referencia explícita a GAP-5.2-05 (mecanismos de migración de tipos); (4) R29: referencia explícita a H-5.1-F (node_id es parte de la identidad); (5) R35: referencia explícita a H-5.1-D (artefactos legacy incompatibles). |
| 1.2.1 | 2026-09-05 | **FROZEN.** Corrección de consistencia normativa: (1) R39 reformulada para eliminar la excepción de "autorización explícita" que contradecía R19 y NADR-24 R25; (2) Decisión Ejecutiva (bullet 5) alineada con la inmutabilidad absoluta de Sealed. No cambia la decisión arquitectónica; elimina una ambigüedad de redacción que contradecía la inmutabilidad ya establecida en R19. Total: 43 reglas en 9 dominios (sin cambio de conteo). |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Sin Ground Truths elegibles y sellados, la certificación de la baseline no puede ejecutarse. Toda modificación del runtime queda sin red de seguridad.
* **Mantenibilidad:** 4 — Sin identidad canónica del oráculo verificable, la evolución del Ground Truth es ambigua y propensa a mutaciones silenciosas.
* **Recuperabilidad:** 4 — Sin oracle_hash verificable y recomputable, la recuperación ante corrupción o sustitución de oráculos es imposible.
* **Seguridad:** 3 — Sin sellado criptográfico, los Ground Truths pueden ser modificados silenciosamente, comprometiendo la validez de toda evaluación posterior.
* **Financiero:** 3 — Sin sellado, la certificación de la baseline queda bloqueada, generando costo de oportunidad significativo para las fases posteriores (18-21).
* **Total Score: 19/25**

**Severidad:** `S1` (Crítico)

---

## 3. DECISIÓN EJECUTIVA

**Todo Ground Truth debe ser elegible bajo un contrato de dominio verificable, curado mediante inspección humana experta, canónico en su identidad, válido estructuralmente, y sellado criptográficamente bajo Zero Partial Sealing estricto, antes de poder constituirse en oráculo de autoridad científica.**

En consecuencia:
* Ningún Ground Truth puede ser sellado si no puede hidratarse bajo el contrato vigente del dominio.
* Ningún Ground Truth puede ser sellado si sus node_ids no están en representación canónica.
* Ningún Ground Truth puede ser sellado si no satisface el contrato de validez estructural.
* Ningún artefacto legacy puede ser sellado directamente sin migración validada o re-extracción.
* Ningún oráculo sellado puede ser sobrescrito, modificado o eliminado. Toda corrección posterior al sellado debe producir un nuevo artefacto/versionado y atravesar nuevamente  el lifecycle de elegibilidad, validación y sellado.
* El sellado de la baseline es una operación atómica gobernada por una única autoridad; no existe sellado parcial.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La arquitectura de certificación de la baseline requiere que los Ground Truths sean oráculos canónicos sellados criptográficamente. Sin embargo, la auditoría forense demostró que el estado actual del repositorio presenta cuatro clases de deficiencias que impiden el sellado:

1. **Node_ids en representación no canónica:** Los Ground Truths del corpus actual tienen node_ids en representación legacy que producen identidad criptográfica distinta bajo el algoritmo vigente. Esto impide la verificación de integridad del oráculo.

2. **Artefactos legacy incompatibles:** Los archivos .ast.json legacy utilizan un formato incompatible con el contrato AST vigente, lo que impide su hidratación bajo el contrato actual.

3. **Manifest en formato legacy:** El manifest del corpus actual está en formato legacy (4 dimensiones), incompatible con el algoritmo de hashing vigente (6 dimensiones).

4. **Certification Boundary Integrity violation:** Existe un mecanismo de migración de tipos que puede sobrescribir Ground Truths sellados sin verificar el estado de sellado, comprometiendo la inmutabilidad de los oráculos.

**Nota sobre curaduría humana experta:** La curaduría humana experta es un requisito de elegibilidad de Ground Truth (R5). La cobertura de traits del corpus es responsabilidad de NADR-F17BIS-20 (Canonical Corpus Qualification), no de este NADR.

### 4.2 Manifestación concreta identificada por la auditoría

* **`E-5.4-004` (P1 — Alto):** Los Ground Truths del corpus tienen node_ids en representación no canónica (`"value='p1_b0'"` en lugar de `"p1_b0"`). Verificación forense H-5.1-F (2026-09-05) confirmó que el hash legacy (`085cf4a8...`) difiere del hash canónico (`fe0f8409...`), cerrando la hipótesis como RECHAZADA.

* **`E-5.4-008` (P1 — Alto):** Los archivos .ast.json legacy utilizan un formato incompatible con el contrato AST vigente: `"type"` en lugar de `"node_type"`, `"content"` en lugar de `"payload.content"`, ausencia de `"sequence_id"`, `"strategy"`, `"depth"`, `"parent_node_id"`. Verificación forense H-5.1-D confirmó que los artefactos no son directamente compatibles y requieren migración o re-extracción.

* **`E-5.4-001` (P0 — Crítico):** El manifest de calibration_v1 está en formato legacy (DF-19), con campos `ground_truth_version` y `ground_truth_sha256` en lugar de `oracle_hash` y `ground_truth_state`. El hash almacenado (`c64a74d7...`) no coincide con el hash calculado por el algoritmo vigente (`2333205e...`).

* **`E-5.4-012` (VERIF):** La identidad semántica del oráculo incluye node_id, node_type, strategy y payload_hash. La identidad NO incluye sequence_id, depth, parent_id, ni metadata.

* **`GAP-5.2-05` (P1 — Alto):** El mecanismo de migración de tipos (`sanitize_ground_truth_types.py`) puede sobrescribir Ground Truths sellados sin verificar el estado de sellado, constituyendo una violación de Certification Boundary Integrity.

* **`GAP-5.4-001` (P1):** Manifest legacy incompatible. Justifica R38 (manifest canónico).
* **`GAP-5.4-002` (P1):** Node_ids legacy. Justifica R8-R12 (canonicalización).
* **`GAP-5.4-004` (P1):** .ast.json legacy incompatibles. Justifica R35-R37 (migración).

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Elegibilidad de Ground Truth

1. Todo Ground Truth **MUST** poder hidratarse bajo el contrato vigente del dominio antes de ser elegible para sellado.
2. La hidratación de un Ground Truth **MUST** realizarse exclusivamente a través del mecanismo canónico de hidratación definido por la arquitectura. La construcción directa de oráculos a partir de artefactos serializados sin hidratación **MUST NOT** ser permitida.
3. El proceso de hidratación **MUST** requerir el estado del ciclo de vida como parámetro explícito. La inferencia del estado a partir del artefacto serializado **MUST NOT** ser permitida.
4. Todo Ground Truth **MUST** tener sus node_ids en representación canónica antes de ser elegible para sellado.
5. Todo Ground Truth **MUST** haber sido curado mediante inspección humana experta antes de ser elegible para sellado.
6. Todo Ground Truth **MUST** tener su identidad semántica recomputada bajo el contrato vigente antes de ser elegible para sellado.
7. Un Ground Truth que no cumpla los requisitos de elegibilidad **MUST NOT** ser sellado.

### 5.2 Canonicalización de NodeId

8. Todo node_id **MUST** estar en representación canónica conforme al contrato de dominio vigente.
9. La representación legacy de un node_id **MUST** ser migrada a representación canónica antes del sellado del Ground Truth.
10. La canonicalización **MUST** ser determinista: el mismo node_id en representación legacy **MUST** producir el mismo node_id en representación canónica en cualquier ejecución.
11. La canonicalización **MUST** preservar la trazabilidad del node_id original como referencia de lineage.
12. Todo node_id canónico **MUST** satisfacer las restricciones del contrato de dominio de identificadores vigente: prohibición del carácter separador de framing, no vaciedad, y longitud mínima.

### 5.3 Validez Estructural

13. Un Ground Truth elegible para sellado **MUST** satisfacer el contrato de validez estructural definido por la arquitectura.
14. El contrato de validez estructural **MUST** verificar, como mínimo: no vaciedad del Ground Truth, ausencia de node_ids duplicados, integridad de contenido, y consistencia de tipos de nodo.
15. La violación del contrato de validez estructural **MUST** producir un error explícito con identificación de la violación. La degradación silenciosa de un Ground Truth inválido **MUST NOT** ser permitida.
16. El proceso de sellado **MUST** verificar la validez estructural de cada Ground Truth antes del sellado. El sellado de un Ground Truth inválido **MUST** abortar la operación.

### 5.4 Ciclo de Vida del Ground Truth

17. Todo Ground Truth **MUST** seguir el ciclo de vida definido por el contrato de dominio vigente: Draft → Audited → Validated → Sealed.
18. Las transiciones de estado **MUST** ser gobernadas por la autoridad de lifecycle definida por el contrato de dominio vigente.
19. Un Ground Truth en estado Sealed **MUST NOT** ser modificado, sobrescrito ni eliminado por ninguna operación de curaduría o certificación.
20. Las transiciones de estado **MUST** ser inmutables: toda transición **MUST** retornar una nueva instancia del objeto, no mutar la instancia existente.
21. Un Ground Truth en estado Sealed **MUST NOT** ser revertido a ningún estado anterior.

### 5.5 Sellado (Sealing) y Zero Partial Sealing

22. El sellado de la baseline **MUST** ser una operación atómica: el corpus completo **MUST** ser sellado como una única unidad, no documento por documento de forma independiente.
23. El sellado **MUST** verificar la completitud biyectiva entre los documentos del corpus y los oráculos de Ground Truth antes de ejecutar el sellado. Si la correspondencia biyectiva no se cumple, el sellado **MUST** abortar.
24. El sellado **MUST** verificar la validez de cada oráculo de Ground Truth conforme al contrato de validez vigente antes de ejecutar el sellado.
25. El sellado **MUST** ser gobernado por una única autoridad. No existe sellado parcial ni autoridad de sellado distribuida.
26. El sellado **MUST** producir una identidad semántica determinista para cada oráculo sellado.
27. La verificación de completitud **MUST** ser ejecutada antes del sellado, no después. El sellado sin verificación de completitud previa **MUST NOT** ser permitido.

### 5.6 Identidad del Oráculo

28. La identidad semántica de un oráculo **MUST** ser calculada conforme al contrato de identidad vigente del dominio.
29. La identidad semántica de un oráculo **MUST** incluir: node_id, node_type, strategy, y contenido del payload. La verificación forense H-5.1-F confirmó empíricamente que el node_id es parte constitutiva de la identidad semántica: un node_id en representación legacy produce una identidad criptográfica distinta a la producida por el mismo node_id en representación canónica.
30. La identidad semántica de un oráculo **MUST NOT** incluir: sequence_id, depth, parent_id, ni metadata incidental.
31. La identidad semántica de un oráculo **MUST** ser determinista: el mismo oráculo **MUST** producir la misma identidad en cualquier ejecución.

### 5.7 Identidad de Baseline

32. La identidad de la baseline **MUST** ser derivada determinísticamente de los oráculos sellados que la componen.
33. La identidad de la baseline **MUST** ser encadenada: la identidad global **MUST** ser un hash compuesto que incluya las identidades de todos los oráculos sellados, la identidad del manifest, y la versión del esquema del dominio.
34. La identidad de la baseline **MUST** ser recomputable determinísticamente a partir de los artefactos sellados. La misma colección de oráculos sellados **MUST** producir la misma identidad de baseline en cualquier ejecución.

### 5.8 Migración de Artefactos Legacy

35. Los artefactos legacy **MUST NOT** ser sellados directamente bajo el contrato vigente. La verificación forense H-5.1-D confirmó empíricamente que los artefactos .ast.json legacy son incompatibles con el contrato AST vigente y no pueden hidratarse bajo el contrato actual.
36. Los artefactos legacy **MUST** ser migrados al formato vigente o re-extraídos bajo el pipeline de producción actual antes de poder participar en el proceso de certificación.
37. La migración **MUST** preservar la trazabilidad de lineage: el artefacto migrado **MUST** conservar una referencia al artefacto original y a la operación de migración que lo produjo.
38. Un manifest en formato legacy **MUST** ser migrado al formato vigente antes de cualquier operación de certificación. La certificación con manifest en formato legacy **MUST NOT** ser permitida.

### 5.9 Protección de Oráculos Sellados y Autoridad Única

39. Un oráculo sellado MUST NOT ser sobrescrito, modificado o eliminado. La inmutabilidad de un oráculo sellado es absoluta. Cualquier corrección, migración o remediación posterior al sellado MUST producir un nuevo artefacto/versionado y atravesar nuevamente el lifecycle completo de elegibilidad, validación y sellado definido por este NADR. No existe autorización, explícita o implícita, que permita mutar un oráculo sellado in-place.
40. Todo mecanismo que pueda modificar Ground Truths (incluyendo mecanismos de migración de tipos y sanitización) **MUST** verificar el estado de sellado antes de cualquier modificación. La modificación de un oráculo sellado sin verificación de estado **MUST NOT** ser permitida. Esta regla materializa la resolución de GAP-5.2-05 (Certification Boundary Integrity violation).
41. La sobrescritura no autorizada de un oráculo sellado **MUST** producir un error explícito con identificación de la violación. La degradación silenciosa **MUST NOT** ser permitida.
42. La certificación de la baseline **MUST** ser gobernada por una única autoridad. No existe certificación parcial ni autoridad de certificación distribuida.
43. Toda operación de sellado **MUST** ser ejecutada exclusivamente por la autoridad de sellado definida por el contrato de dominio vigente. Ningún otro componente **MUST** poder ejecutar el sellado.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* **Ground Truths elegibles bajo contrato verificable:** Los Ground Truths solo pueden ser sellados si cumplen los requisitos de elegibilidad definidos por el contrato de dominio vigente. Esto elimina el riesgo de sellar artefactos corruptos, incompletos o en formato legacy.
* **Node_ids canónicos verificables:** Los node_ids quedan en representación canónica conforme al contrato de dominio, eliminando el riesgo de identidad criptográfica inconsistente y habilitando la verificación de integridad del oráculo.
* **Validez estructural garantizada:** Los Ground Truths solo pueden ser sellados si satisfacen el contrato de validez estructural. Esto elimina el riesgo de sellar Ground Truths estructuralmente inválidos.
* **Sellado atómico bajo Zero Partial Sealing:** El sellado se ejecuta como una única operación atómica que verifica completitud biyectiva y validez de cada oráculo antes de ejecutar. Esto elimina el riesgo de sellado parcial.
* **Oráculos sellados inmutables y protegidos:** Un oráculo sellado no puede ser modificado, sobrescrito ni eliminado. Todo mecanismo de modificación debe verificar el estado de sellado. Esto garantiza que la baseline sea un oráculo determinista e inmutable.
* **Artefactos legacy migrados o re-extraídos:** Los artefactos legacy no pueden ser sellados directamente. Deben ser migrados al formato vigente o re-extraídos bajo el pipeline de producción actual. Esto elimina el riesgo de sellar artefactos incompatibles.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que todo node_id del Ground Truth está en representación canónica conforme al contrato de dominio.
  * Verificación de que todo Ground Truth puede hidratarse bajo el contrato vigente del dominio.
  * Verificación de que todo Ground Truth satisface el contrato de validez estructural.
  * Verificación de que la identidad semántica de cada oráculo es calculable bajo el contrato de identidad vigente.
  * Verificación de que el manifest está en el formato vigente (6 dimensiones).
  * Verificación de que no existen artefactos legacy sin migración en el corpus canónico.
  * Verificación de que no existen mecanismos de modificación de Ground Truths que no verifiquen el estado de sellado.

* **Validation (dinámica/comportamental):**
  * Ejecución del sellado sobre el corpus canónico, verificando que el sellado se ejecuta correctamente con todos los Ground Truths elegibles.
  * Verificación de la completitud biyectiva: el sellado aborta si la correspondencia entre documentos y oráculos no se cumple.
  * Verificación de la atomicidad del sellado: una interrupción durante el sellado no produce un sellado parcial.
  * Verificación de la inmutabilidad del oráculo sellado: toda tentativa de modificación de un oráculo sellado produce un error explícito.
  * Verificación de la protección de oráculos sellados: todo mecanismo de modificación verifica el estado de sellado antes de modificar.
  * Verificación del determinismo de la identidad semántica: el mismo oráculo produce la misma identidad en múltiples ejecuciones.
  * Verificación de la recomputabilidad de la identidad de baseline: la misma colección de oráculos sellados produce la misma identidad de baseline en múltiples ejecuciones.
  * Verificación de la migración de artefactos legacy: un artefacto legacy migrado produce un Ground Truth elegible bajo el contrato vigente.
  * Verificación de que el corpus cualificado puede ser consumido por el proceso de certificación definido por NADR-24 sin violar las invariantes de este NADR.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Este NADR materializa la visión del ADR Maestro §5 (Invariante de Sellado Estricto: Zero Partial Sealing) y DC-05 (Ciclo de Vida del Ground Truth). |
| `ADR_F17_BIS_05` | Este NADR implementa D2 (Ground Truth Curation & Eligibility) y D3 (Identidad, Sealing y Autoridad Única) del ADR de Fase 5. |
| `NADR-F17BIS-20` | **Dependencia directa:** Este NADR depende de la cualificación del corpus establecida por NADR-20. Un Ground Truth no puede ser elegible si el documento del corpus no está cualificado. |
| `NADR-F17BIS-12` | **Dependencia directa:** Este NADR extiende la ontología del Ground Truth definida por NADR-12 (GroundTruthDraft, SealedOracle, hydrate_ground_truth). |
| `NADR-F17BIS-13` | **Dependencia directa:** Este NADR extiende las reglas de validez y completitud definidas por NADR-13 (OracleValidityContract, Zero Partial Sealing). |
| `NADR-F17BIS-14` | **Dependencia directa:** Este NADR extiende las reglas de autoridad de sellado definidas por NADR-14 (Asimetría de Puertos y Autoridad de Sellado). |
| `NADR-F17BIS-16` | **Dependencia directa:** Este NADR extiende la semántica de identidad definida por NADR-16 (OracleSemanticIdentityCalculator, ManifestFingerprintCalculator). |
| `NADR-F17BIS-17` | **Dependencia directa:** Este NADR extiende los contratos de dominio definidos por NADR-17 (DocumentId, NodeId). |
| `NADR-F17-BIS-22` | **Influencia:** NADR-22 (Canonical Evaluation Configuration) depende de los oráculos sellados establecidos por este NADR para evaluar el motor topológico. |
| `NADR-F17-BIS-23` | **Influencia:** NADR-23 (Scientific Calibration) depende de los oráculos sellados establecidos por este NADR para la calibración empírica. |
| `NADR-F17-BIS-24` | **Influencia:** NADR-24 (Certification Tooling Integrity) depende de los oráculos sellados establecidos por este NADR para la certificación. |
| `PHASE_17BIS_FASE5_EXECUTION_PLAN` | Materializa las reglas de este NADR mediante tareas de canonicalización, migración, curaduría y sellado. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la cualificación del corpus ni la cobertura de traits de los documentos (responsabilidad de `NADR-F17BIS-20`).
* **No gobierna** la configuración del motor de evaluación topológica ni el modelo de costo (responsabilidad de `NADR-F17-BIS-22`).
* **No gobierna** la calibración empírica de parámetros ni la independencia de datasets (responsabilidad de `NADR-F17-BIS-23`).
* **No gobierna** la integridad operacional del tooling de certificación ni la semántica de fallo (responsabilidad de `NADR-F17-BIS-24`).
* **No gobierna** la integración en CI/CD de los Regression Gates (responsabilidad de Fase 6).
* **No gobierna** la infraestructura de persistencia ni la atomicidad de escrituras (responsabilidad de `NADR-F17BIS-16` y el Execution Plan).
* **No prescribe** el protocolo de curaduría humana experta ni los criterios específicos de curaduría (responsabilidad del Execution Plan).
* **No prescribe** el algoritmo específico de canonicalización de node_ids (responsabilidad del Execution Plan).
* **No prescribe** la implementación específica del sellado ni la serialización de oráculos (responsabilidad del Execution Plan).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del `PHASE_17BIS_FASE5_EXECUTION_PLAN`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.