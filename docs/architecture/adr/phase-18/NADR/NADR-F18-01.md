# NADR-F18-01: Execution Identity & Scientific Isolation

## 1. METADATA

* **Decision ID:** `NADR-F18-01`
* **Título:** Execution Identity & Scientific Isolation
* **Clase de Decisión:** `GOVERNANCE / DATA`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.3
* **Ciclo de Vida:** `FROZEN`
* **Vigente Desde:** Fase 18, Subfase 18.1
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Staff Engineering
* **Capacidad Arquitectónica:** CAP-SCI-IDENTITY (Scientific Identity Boundary) — define qué propiedades constituyen la identidad científica de un documento y las aísla constitucionalmente del mecanismo de ejecución y del estado operacional.
* **Evidencia Forense:** `GAP-0.4-03`, `DC-02`, `INV-SCI-1`, `INV-OPS-1`, `INV-EXEC-IDENTIFIABILITY`, `HITO_0.12 v1.0.1`, `HITO_0.4 v1.3.0`, `E-0.4-001`, `E-0.4-002`, `E-0.4-003`, `E-0.4-004`
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F18_MASTER.md` FROZEN, `ADR_F18.1` v1.0.2 FROZEN, `ADR_F17_BIS_MASTER.md` FROZEN
  * **Influencia:** `NADR-F18-02` (la ejecución concurrente debe respetar esta frontera), `DC-12` / Subfase 18.5 (el guard diferencial usa esta frontera como contrato de comparación), `ADR_F18.5` (pendiente)
  * **Conflictúa con:** cualquier modificación del mecanismo de ejecución que altere la identidad científica o falsifique la evidencia científica
  * **Reemplaza a:** N/A

### Changelog

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | 2026-10-04 | Emisión inicial |
| 1.0.1 | 2026-10-04 | Corrección (8 cambios): (1) Risk Score Financiero ajustado de 3 a 4 con justificación de bloqueo de DC-12 y fases posteriores. (2) Capacidad Arquitectónica reformulada como identificador CAP-SCI-IDENTITY conforme al formato CAP-XXX del template canónico. (3) Referencia a ADR_F17_BIS_MASTER añadida en §8 como dependencia de autoridad. (4) Exclusión de la demostración integrada de C8/C9/C13 añadida en §9. (5) §5.5 Trazabilidad de Identidad separado como dominio propio (reglas 19-20). (6) Cláusula de invalidación con referencia explícita a Subfase 18.5 (§5.4 R17). (7) Manifestación concreta con nombres de archivo como evidencia en §4.2. (8) Test de invalidación añadido en §7. |
| 1.0.2 | 2026-10-04 | Corrección de observaciones menores: (1) Changelog v1.0.1 completado para reflejar los 8 cambios aplicados. (2) Regla 2 (§5.1) aclarada como piso constitucional mínimo; se explicita que DC-02 es el refinamiento de la composición, no una composición cerrada. |
| 1.0.3 | 2026-10-04 | Corrección editorial-normativa pre-FROZEN (4 cambios): (1) Regla 1 (§5.1) aclarada: la determinación exhaustiva de las propiedades de identidad científica es resultado de DC-02, no una exhaustividad ya demostrada por este NADR. (2) §6 reformulado como establecimiento normativo, no como cumplimiento demostrado. (3) §7 reformulado como propiedades verificables, evitando prescribir implementación concreta. (4) §3: "inmutable" sustituido por "estable durante la vigencia de esta decisión". |

---

## 2. ARCHITECTURE RISK SCORE

* **Operacional:** 5 — Si la frontera entre scientific identity y execution identity no está explícitamente definida, el sistema puede producir resultados científicos distintos bajo distintas condiciones operacionales, violando INV-SCI-1. Esto constituye un fallo operacional crítico que corrompe la verdad del resultado.
* **Mantenibilidad:** 4 — Sin una frontera de identidad clara, toda evolución del mecanismo de ejecución requiere análisis de impacto sobre la identidad científica, incrementando el costo de cambio y el riesgo de regresión silenciosa.
* **Recuperabilidad:** 3 — La identidad científica en sí no es recuperable si se corrompe (no existe rollback a una identidad correcta). Sin embargo, el sistema puede recuperarse de fallos operacionales que no afectan la identidad. Score medio por asimetría.
* **Seguridad:** 2 — No es directamente una superficie de ataque externo. La integridad de la identidad tiene implicaciones de confianza y trazabilidad, pero no expone vulnerabilidades explotables. Score bajo.
* **Financiero:** 4 — Si la identidad científica se corrompe, los resultados son inválidos y requieren reprocesamiento completo. Además, si la frontera de identidad no está definida, el guard diferencial (DC-12) no puede operar, lo cual retrasa la certificación de neutralidad científica y bloquea la Subfase 18.5 y, por extensión, las fases posteriores que dependen de dicha certificación. El costo financiero incluye tanto el reprocesamiento como el retraso en cascada.

* **Total Score: 18/25**

**Severidad:** `S1` (crítico)

---

## 3. DECISIÓN EJECUTIVA

**La identidad científica de un documento y su evidencia asociada constituyen una frontera constitucional estable durante la vigencia de esta decisión, que ningún mecanismo de ejecución, política de scheduling, variación de concurrencia, asignación de recursos o estado operacional puede alterar, y toda propiedad del sistema debe clasificarse explícitamente como scientific identity, execution identity u operational state.**

En consecuencia:

* Ninguna variación del mecanismo de ejecución puede constituir una nueva interpretación científica del documento ni falsificar la evidencia científica canónica.
* Las diferencias operacionales entre ejecuciones viven en evidencia operacional separada y no contaminan la identidad científica.
* El modo o política de ejecución es identificable y reproducible, habilita testing diferencial, y queda excluido de la identidad científica.
* Cualquier modificación posterior que afecte las dimensiones utilizadas para comparación diferencial invalida la evidencia dependiente y requiere reevaluación conforme a la gobernanza de la subfase correspondiente.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

La capacidad de distinguir constitucionalmente entre identidad científica, identidad de ejecución y estado operacional está ausente. Sin esta frontera, el sistema no puede garantizar que la modificación del mecanismo de ejecución preserve la verdad científica, ni puede operar el guard diferencial que certifica dicha preservación.

ADR_F17_BIS_MASTER §3 estableció tres dimensiones ortogonales (Integridad, Identidad, Regresión) y declaró que "Identidad no reemplaza la Regresión". Sin embargo, esa separación opera a nivel de baseline y corpus canónico. La frontera entre identidad científica e identidad de ejecución a nivel de runtime —es decir, qué propiedades del mecanismo de ejecución pertenecen a cada dominio— no ha sido normada.

Clases de defectos identificados:

1. **Ausencia de clasificación normativa de propiedades:** No existe definición congelada de qué parámetros pertenecen a la identidad científica y cuáles pertenecen al mecanismo de ejecución o al estado operacional. Esto impide establecer un contrato de comparación estable.
2. **Ambigüedad entre evidencia científica y evidencia operacional:** Sin frontera explícita, las diferencias operacionales entre ejecuciones pueden contaminar la evidencia científica o ser interpretadas erróneamente como regresión científica.
3. **Indeterminación del modo de ejecución:** El modo o política bajo la cual se ejecuta un documento no es sistemáticamente identificable ni reproducible, lo que impide el testing diferencial y la trazabilidad de resultados.

### 4.2 Manifestación concreta identificada por la auditoría

* **`GAP-0.4-03` (P0 — Crítico):** No existe definición congelada que determine qué parámetros pertenecen a scientific identity y cuáles a operational metadata. Esta ambigüedad impide definir el contrato de comparación del guard diferencial (DC-12, Subfase 18.5).
* **`DC-02` (DEFERRED — destino 18.1):** Parámetros de runtime en identity científica vs metadata operacional. Su resolución es prerrequisito para la frontera de identidad y para el guard diferencial.
* **`E-0.4-001` (prerrequisito verificado):** El mecanismo de hashing de AST (`compute_ast_hash` en `core/ast/hashing.py`) es determinista e insensible al orden de procesamiento. Constituye la base técnica de la identidad científica a nivel de nodo.
* **`E-0.4-002` (prerrequisito verificado):** El ensamblado (`DocumentAssembler.assemble` en `core/compiler/assembler.py`) es determinista bajo mismas entradas; la invariancia bajo orden de completitud no está demostrada.
* **`E-0.4-003` (prerrequisito verificado):** Las métricas científicas (`DoubleProtectionMechanism.evaluate` en `core/benchmark/topology/regression/mechanism.py`) son deterministas bajo mismo AST.
* **`E-0.4-004` (boundary verificado):** Los exit codes operacionales (`outcome_to_exit_code` en `core/benchmark/verification/outcome.py`) están bien definidos y separados de los verdicts científicos.
* **`INV-SCI-1`, `INV-OPS-1`, `INV-EXEC-IDENTIFIABILITY` (ADR_F18_MASTER §5.1):** Invariantes constitucionales que declaran qué debe ser verdadero, pero que requieren reglas normativas concretas para su materialización.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Scientific Identity Boundary

1. Toda propiedad del sistema que determine el resultado científico de un documento **MUST** pertenecer a scientific identity; la determinación exhaustiva de dichas propiedades **MUST** ser establecida mediante DC-02.
2. La scientific identity **MUST** incluir, como mínimo, la baseline sellada, los parámetros científicos congelados y la representación estructural canónica del documento.
3. La scientific identity **MUST NOT** incluir propiedades del mecanismo de ejecución, del scheduling, de la concurrencia, de la asignación de recursos, ni del estado operacional.
4. Ninguna modificación del mecanismo de ejecución **MUST** alterar la scientific identity de un documento ni la evidencia científica canónica asociada.
5. Toda variación en la scientific identity **MUST** constituir una nueva versión científica del documento, gobernada por el proceso de re-baseline correspondiente, y **MUST NOT** ser introducida como efecto lateral de un cambio operacional.

> **Nota sobre la Regla 2:** La composición aquí establecida es un **piso constitucional mínimo**, no una composición cerrada. La resolución de `DC-02` (Subfase 18.1) constituye el refinamiento de esta frontera y puede precisar o ampliar las dimensiones de identidad, siempre sin violar el piso mínimo ni incorporar propiedades del mecanismo de ejecución conforme a la Regla 3. Toda modificación resultante de DC-02 que afecte dimensiones utilizadas por el guard diferencial queda sujeta a la cláusula de invalidación de la Regla 17.

### 5.2 Execution Identity

6. Toda propiedad que determine el modo o la política bajo la cual se ejecuta un documento **MUST** ser clasificada como execution identity.
7. La execution identity **MUST** ser identificable unívocamente y reproducible, de modo que habilite testing diferencial entre modos de ejecución.
8. La execution identity **MUST NOT** formar parte de la scientific identity ni alterar la evidencia científica canónica.
9. La execution identity **MUST** ser registrable como evidencia operacional separada de la evidencia científica.

### 5.3 Operational State

10. Toda propiedad que varíe durante la ejecución sin afectar el resultado científico **MUST** ser clasificada como operational state.
11. El operational state **MUST NOT** alterar la scientific identity ni la execution identity.
12. Las diferencias en operational state entre ejecuciones con la misma scientific identity **MUST NOT** falsificar la evidencia científica ni ser interpretadas como regresión científica.
13. El operational state **MUST** ser registrable como evidencia operacional separada de la evidencia científica.

### 5.4 Comparability & Stability

14. Toda ejecución **MUST** poder ser identificada unívocamente por su execution identity.
15. Dos ejecuciones con la misma scientific identity y distinta execution identity **MUST** producir la misma evidencia científica canónica.
16. La frontera entre scientific identity, execution identity y operational state **MUST** estar explícitamente documentada, versionada y gobernada.
17. Cualquier modificación posterior que afecte las dimensiones de identidad utilizadas para comparación diferencial **MUST** invalidar la evidencia dependiente y **MUST** requerir reevaluación conforme a la gobernanza de la Subfase 18.5.
18. La clasificación de una propiedad como scientific identity, execution identity u operational state **MUST** ser estable durante la vigencia de una comparación diferencial, salvo invalidación explícita conforme a la regla 17.

### 5.5 Trazabilidad de Identidad

19. Todo artefacto producido por el pipeline **MUST** llevar asociada su identidad científica y su identidad de ejecución de forma distinguible.
20. La evidencia operacional **MUST** ser trazable a la ejecución que la produjo sin contaminar la identidad científica del artefacto.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* La frontera constitucional entre scientific identity, execution identity y operational state queda establecida normativamente, eliminando la ambigüedad identificada en `GAP-0.4-03`. Su cumplimiento efectivo deberá ser demostrado por la implementación y la validación correspondientes.
* El guard diferencial (`DC-12`, Subfase 18.5) dispondrá de una frontera de comparación normativamente definida, cuya suficiencia deberá ser demostrada en DC-12.
* Las variaciones del mecanismo de ejecución gobernadas por `NADR-F18-02` no pueden corromper la verdad científica, al estar sujetas a la frontera de identidad aquí establecida.
* La evidencia científica queda aislada de la evidencia operacional, permitiendo certificación de neutralidad científica bajo variación operacional.
* El modo de ejecución queda identificado y es reproducible, habilitando testing diferencial y trazabilidad de resultados.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Property test que verifica que la scientific identity de un documento no cambia ante variaciones del mecanismo de ejecución, scheduling o concurrencia.
  * Type check o validación estructural que verifica que toda propiedad relevante está clasificada como scientific identity, execution identity u operational state.
  * Verificación de que la frontera de identidad está documentada y versionada.
  * Verificación de que la evidencia operacional y la evidencia científica están registradas en dominios separados.
  * Propiedad exigible: todo artefacto lleva asociadas una identidad científica y una identidad de ejecución distinguibles. El mecanismo concreto de asociación corresponde al Execution Plan, no a este NADR.

* **Validation (dinámica/comportamental):**
  * Golden corpus: ejecutar el mismo documento con la misma scientific identity y distinta execution identity, y verificar que la evidencia científica canónica es idéntica.
  * Differential testing: comparar la evidencia científica producida bajo distintos modos de ejecución y verificar invariancia.
  * Mutation testing: introducir variaciones operacionales deliberadas y verificar que no alteran la scientific identity ni la evidencia científica.
  * Test de invalidación: modificar la frontera de identidad y verificar que la evidencia dependiente del guard diferencial es invalidada.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F18_MASTER.md` FROZEN | Materializa las invariantes constitucionales INV-SCI-1, INV-OPS-1 e INV-EXEC-IDENTIFIABILITY declaradas en §5.1 del ADR Maestro. |
| `ADR_F18.1` v1.0.2 FROZEN | Particulariza la decisión DC-02 (identity científica vs operacional) asignada a la Subfase 18.1. |
| `ADR_F17_BIS_MASTER.md` FROZEN | **Dependencia de autoridad:** la baseline sellada y la identidad científica canónica son establecidas por F17-BIS; este NADR no las redefine. La separación Integridad/Identidad/Regresión de ADR_F17_BIS §3 permanece como fundamento. |
| `NADR-F18-02` (pendiente) | **Influencia directa:** El mecanismo de ejecución concurrente gobernado por NADR-F18-02 debe respetar la frontera de identidad aquí establecida. NADR-F18-02 depende de este NADR. |
| `DC-12` / `ADR_F18.5` (pendiente) | **Influencia directa:** El guard diferencial de la Subfase 18.5 depende de la frontera de identidad definida aquí. Cualquier modificación posterior que afecte las dimensiones de comparación invalida la evidencia de DC-12 conforme a la regla 17. |
| `PHASE_18.1_EXECUTION_PLAN.md` (pendiente) | Materializa las tareas que implementan estas reglas normativas y define el DoD operativo. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** el mecanismo de ejecución concurrente, bounded execution, backpressure, cancellation, concurrency safety ni estructura de contextos (responsabilidad de `NADR-F18-02`).
* **No gobierna** el guard diferencial propiamente dicho ni su promoción a CI (responsabilidad de la Subfase 18.5, `DC-12`).
* **No gobierna** la composición de la baseline científica ni los parámetros científicos congelados (responsabilidad de la Fase 17-BIS y su proceso de recalibración).
* **No gobierna** la demostración integrada de C8 Scientific Neutrality, C9 Scientific Determinism ni C13 Verification-Path Determinism (responsabilidad de la Subfase 18.5; este NADR establece únicamente la dimensión de identidad que las habilita).
* **No gobierna** resource budgets, admission policy, fairness, batching ni adaptive scheduling (responsabilidad de la Subfase 18.3).
* **No gobierna** journal semantics, durable recovery ni persistencia de estado (responsabilidad de la Subfase 18.2).
* **No gobierna** provider characterization ni cache semantics (responsabilidad de la Subfase 18.4).
* **No gobierna** observabilidad profunda (responsabilidad de Fase 20).
* **No prescribe** tareas de implementación, Definition of Done ni secuencia operativa (responsabilidad del `PHASE_18.1_EXECUTION_PLAN.md`).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias que materializan la frontera constitucional entre scientific identity, execution identity y operational state. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.