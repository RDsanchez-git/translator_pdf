# NADR-F17BIS-04: Validation Wiring & Legacy Retirement

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-04`
* **Título:** Validation Wiring & Legacy Retirement
* **Clase de Decisión:** `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — pendiente de refactor editorial para `FROZEN`
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Validation Domain
* **Capacidad Arquitectónica:** CAP-008 (Unified Execution Plane) — etapa de validación oficial
* **Evidencia Forense:** `P5-H02`, `P5-H06`, `P2-07`, `GAP-P5-01`, `GAP-P5-04`, `GAP-P2-04`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-11` (exclusividad e inmutabilidad de la Composition Root).
  * **Influencia:** `NADR-F17BIS-07` (la iteración de curación consume los fallos emitidos por la validación).
  * **Conflictúa con:** Toda coexistencia de mecanismos de validación paralelos o heredados dentro del pipeline oficial.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Operacional:** 4 — Nodos estructuralmente corruptos progresan hacia el despacho sin validación previa, generando consumo de tokens en inferencias destinadas a fallar.
* **Mantenibilidad:** 3 — La coexistencia de mecanismos de validación heredados opaca la taxonomía de errores y dificulta el diagnóstico.
* **Recuperabilidad:** 2
* **Seguridad:** 2
* **Financiero:** 3 — Inferencias sobre nodos inválidos constituyen gasto sin retorno de valor.
* **Total Score: 14/25**

---

## 3. CONTEXTO Y EVIDENCIA FORENSE

### 3.1 Problema arquitectónico

El sistema de validación del pipeline de producción sufre una triple desconexión que rompe la garantía de calidad previa al despacho:

1. **Ausencia de validación estructural pre-inferencia.** El mecanismo canónico de validación del AST antes del despacho no forma parte del flujo de producción, por lo que las unidades alcanzan el motor de inferencia sin haber sido verificadas.
2. **Omisión de la validación de maquetación física.** La barrera defensiva que certifica la integridad geométrica del documento extraído no es invocada durante la ingesta, permitiendo que geometrías corruptas se propaguen aguas abajo.
3. **Persistencia de deuda técnica de validación.** Un mecanismo heredado de adaptación de validación, correspondiente a fases anteriores del proyecto, continúa activo en la raíz de composición, opacando la taxonomía de errores moderna.

### 3.2 Manifestación concreta identificada por la auditoría

La auditoría forense identificó que, en el estado actual del repositorio, esta desconexión se manifiesta mediante los siguientes componentes:

* **`P5-H02` / `GAP-P5-01` (P0):** El mecanismo canónico de validación estructural pre-inferencia corresponde actualmente a `PolymorphicValidationEngine` (`core/validation/ast/engine.py`), el cual no es importado ni instanciado en ninguna parte del pipeline activo. Es un componente 100% inalcanzable en producción.
* **`P2-07` / `GAP-P2-04` (P1):** El mecanismo de validación de maquetación física corresponde actualmente a `DocumentLayoutValidator` (`core/layout/validator.py`), el cual no es invocado por la raíz de composición. BoundingBoxes nulos o páginas corruptas ingresan sin filtrado *fail-fast*.
* **`P5-H06` / `GAP-P5-04` (P1):** El mecanismo heredado de adaptación corresponde actualmente a `LegacyValidatorAdapter`, el cual es inyectado y ejecutado explícitamente por la raíz de composición, manteniendo activas reglas de validación de las Fases 11 y 12.

---

## 4. DECISIÓN EJECUTIVA

**Existe un único pipeline oficial de validación, obligatorio y previo al despacho, compuesto por validación de maquetación física y validación estructural del AST, cuya integración es responsabilidad exclusiva de la Composition Root.**

En consecuencia:
* Ninguna unidad puede alcanzar el motor de inferencia sin haber atravesado la validación estructural oficial.
* Ninguna maquetación física puede ser transformada en AST sin haber atravesado la validación física oficial.
* Todo mecanismo heredado o paralelo de validación queda retirado del pipeline oficial.
* La inyección de los pipelines de validación se realiza de forma inmutable, por constructor, y exclusivamente desde la Composition Root.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Pipeline único oficial de validación
1. **MUST** existir un único pipeline oficial de validación, obligatorio y previo al despacho.
2. El pipeline oficial **MUST** estar compuesto por la validación de maquetación física y la validación estructural del AST.
3. La integración del pipeline oficial en el flujo de producción **MUST** ser responsabilidad exclusiva de la Composition Root.
4. **MUST NOT** coexistir mecanismos de validación paralelos o heredados dentro del pipeline oficial.

### 5.2 Validación estructural pre-inferencia
5. El mecanismo canónico de validación estructural **MUST** estar activo en el pipeline oficial antes del despacho hacia el motor de inferencia.
6. **MUST NOT** existir nodos del AST que progresen hacia el despacho sin haber atravesado la validación estructural oficial.
7. La validación estructural pre-inferencia **MUST** ser inyectada por constructor desde la Composition Root.

### 5.3 Validación de maquetación física
8. El mecanismo de validación de maquetación física **MUST** ser invocado en el flujo de producción entre la extracción física y la construcción del AST.
9. Toda maquetación con geometrías nulas, páginas corruptas o invariantes físicas violadas **MUST** ser rechazada de forma *fail-fast* antes de la construcción del AST.

### 5.4 Retiro de deuda técnica de validación
10. Todo mecanismo heredado de adaptación de validación **MUST NOT** coexistir con el mecanismo canónico en la Composition Root.
11. La eliminación de los mecanismos heredados **MUST** ser completa: no se aceptan adaptadores parciales, envoltorios intermedios ni banderas de desactivación.
12. La validación estructural posterior a la inferencia **MUST** integrarse exclusivamente mediante el pipeline oficial de validación definido por la arquitectura.

### 5.5 Inyección inmutable
13. Los pipelines de validación **MUST** ser inyectados por constructor en el punto de composición y en el despachador.
14. **MUST NOT** existir asignación de pipelines de validación mediante mutación de atributos post-construcción.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Los nodos estructuralmente corruptos dejarán de consumir presupuesto de inferencia, reduciendo el gasto sin retorno de valor.
* La taxonomía de errores de validación se simplifica al eliminar la capa de adaptación heredada, facilitando el diagnóstico forense.
* La barrera de maquetación física en la ingesta previene la propagación de geometrías corruptas hacia etapas posteriores del pipeline.
* La Composition Root se simplifica al consolidar la validación en el pipeline oficial y retirar los mecanismos heredados.
* La inmutabilidad de la inyección de validación garantiza que no existan despachadores parcialmente configurados en puntos de entrada alternativos.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el mecanismo canónico de validación estructural pre-inferencia forma parte del pipeline oficial y es alcanzable en el flujo de producción.
  * Verificación de la ausencia total de mecanismos heredados de adaptación de validación en la Composition Root.
  * Verificación de que el mecanismo de validación de maquetación física es invocado en el flujo de ingesta.
  * Verificación de la ausencia de mutación post-construcción en la inyección de los pipelines de validación.

* **Validation (dinámica/comportamental):**
  * Un nodo del AST con payload corrupto **MUST** ser rechazado por la validación estructural antes del despacho.
  * Una maquetación con geometría nula **MUST** ser rechazada por la validación física antes de la construcción del AST.
  * El pipeline **MUST** operar correctamente sin la presencia de los mecanismos heredados de validación.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio de Hexagonal Boundary Enforcement aplicado a la etapa de validación. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-11` | **Dependencia directa:** la exclusividad e inmutabilidad de la Composition Root son gobernadas por NADR-11. |
| `NADR-F17BIS-07` | **Influencia:** la iteración de curación consume los fallos emitidos por la validación oficial. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `2.1.2` y `2.1.3` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la implementación interna del mecanismo canónico de validación estructural pre-inferencia.
* **No gobierna** la implementación interna del mecanismo de validación de maquetación física.
* **No gobierna** las estrategias de curación posteriores a la validación (responsabilidad de `NADR-F17BIS-07`).
* **No gobierna** la Composition Root ni el mecanismo de inyección de dependencias en sí mismo (responsabilidad de `NADR-F17BIS-11`).
* **No gobierna** la ontología del AST V2 ni los payloads (Fase 16, congelada).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias sobre capacidades arquitectónicas. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.