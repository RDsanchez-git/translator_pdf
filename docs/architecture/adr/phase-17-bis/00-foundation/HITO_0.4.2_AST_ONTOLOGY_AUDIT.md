# HITO_0.4.2_AST_ONTOLOGY_AUDIT.md
## AST Ontology, Payload Discrimination & Criticality Forensic Audit — Reporte Consolidado Final

* **Estado:** FROZEN / CONGELADO (Sub-Hito 0.4.2)
* **Fecha de Emisión:** 2026-07-27
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate) — Hito 0.4
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Solo lectura / Auditoría analítica de la ontología de nodos `ContentNodeType`, discriminación de payloads `ASTPayload` y contratos de validación. Cero mutaciones en código productivo. Disposición diferida al Hito 0.5 (`UNASSESSED`).

---

## 1. PROPÓSITO Y ALCANCE DEL SUB-HITO 0.4.2

El **Sub-hito 0.4.2** audita la expresividad semántica, la suficiencia, las fronteras de representación física vs. lógica, la discriminación de payloads y la presencia/ausencia de reglas de validación especializadas en la ontología del AST V2 (`ContentNodeType`).

A través del análisis de código primario en `core/ast/enums.py`, `core/ast/models.py`, `core/ast/protocols.py`, `core/layout/models.py` y `core/validation/ast/protocols.py`, se evalúa cómo la ontología gobierna la construcción, traducción y validación de entidades en el dominio.

---

## 2. REGISTRO DE EVIDENCIA FORENSE Y FORTALEZAS (E-0.4-101 a E-0.4-107)

### Evidencia E-0.4-101: Ortogonalidad Estricta de Dimensiones de Dominio
* **Archivos Fuente Primarios:** `core/ast/enums.py`, `core/ast/models.py`
* **Símbolos Auditados:** `ContentNodeType`, `TranslationStrategy`, `SemanticOrigin`, `HeadingLevel`
* **Análisis Forense:** El modelo aísla la naturaleza semántica de un nodo (`ContentNodeType`) de su comportamiento de procesamiento (`TranslationStrategy`), su origen de extracción (`SemanticOrigin`) y su jerarquía (`HeadingLevel`). Se evita la contaminación de "Nodos Dios" donde el tipo decide la lógica de ejecución.

---

### Evidencia E-0.4-102: Payloads Específicos por Composición sin Herencia Artificial
* **Archivo Fuente Primario:** `core/ast/models.py`
* **Símbolos Auditados:** `HeadingPayload`, `ParagraphPayload`, `MathPayload`, `CodePayload`, `ImagePayload`, `ListPayload`
* **Análisis Forense:** Cada categoría de contenido posee un DTO inmutable e independiente. El modelo favorece la composición pura sobre jerarquías de herencia complejas, manteniendo bajo el acoplamiento y garantizando inmutabilidad mediante `ConfigDict(frozen=True)`.

---

### Evidencia E-0.4-103: Aislamiento Absoluto entre Representación Física (Layout) y Lógica (AST)
* **Archivos Fuente Primarios:** `core/layout/models.py`, `core/ast/models.py`
* **Símbolos Auditados:** `LayoutBlockDraft` vs. `ASTNode`
* **Análisis Forense:** Existe una frontera clara entre la maquetación física (`LayoutBlockDraft`: `bbox`, `column_index`, `provider_native_id`) y la representación del árbol sintáctico (`ASTNode`: `node_type`, `payload`, `strategy`, `depth`). La transformación es unidireccional ($\text{Layout} \longrightarrow \text{AST}$) y evita la contaminación de conceptos físicos en el dominio abstracto.

---

### Evidencia E-0.4-104: Representación Plana Secuencial y Reconstrucción Dinámica
* **Archivo Fuente Primario:** `core/ast/models.py`
* **Símbolo Auditado:** `ASTNode`
* **Análisis Forense:** El AST V2 se modela como una lista plana y secuencial de nodos. La jerarquía y el orden de lectura se expresan explícitamente mediante `parent_node_id`, `depth` y `sequence_id`, facilitando la indexación post-orden y el particionado por ventanas en los motores topológicos.

---

### Evidencia E-0.4-105: Discriminación Tipada Inmutable de Payloads
* **Archivo Fuente Primario:** `core/ast/models.py`
* **Símbolo Auditado:** `ASTNode._discriminate_payload()`
* **Análisis Forense:** Mediante el decorador `@model_validator(mode="before")`, Pydantic actúa como una factoría interna que instanciará automáticamente el DTO correspondiente (`HeadingPayload`, `MathPayload`, etc.) basándose exclusivamente en `node_type`. Esto elimina cadenas manuales de `isinstance` a lo largo del codebase.

---

### Evidencia E-0.4-106: Ontología Minimalista y Compacta
* **Archivo Fuente Primario:** `core/ast/enums.py`
* **Símbolo Auditado:** `ContentNodeType` (11 miembros)
* **Análisis Forense:** La ontología se mantiene deliberadamente minimalista. Elementos periféricos de documentos académicos (autores, bibliografía, notas al pie, anexos) no poseen tipos dedicados en el enum y son absorbidos dentro de `PARAGRAPH` o `LIST`. Esto simplifica la interfaz del parser y estabiliza el modelo de dominio.

---

### Evidencia E-0.4-107: Desacoplamiento de las Reglas de Validación Específicas
* **Archivo Fuente Primario:** `core/validation/ast/protocols.py`
* **Símbolo Auditado:** `NodeValidator(Protocol)`
* **Análisis Forense:** El dominio define el puerto `NodeValidator` (`can_validate`, `validate`), pero la evidencia del código inspeccionado confirma que la ontología gobierna actualmente la representación, el payload y la estrategia de traducción, pero **todavía no gobierna directamente validadores especializados por tipo de nodo** (`HeadingValidator`, `TableValidator`, etc.). El marco soporta esta extensión por polimorfismo, pero la lógica de validación por tipo no está ligada al enum en el núcleo actual.

---

## 3. REGISTRO DE OBSERVACIONES Y ASIMETRÍAS (OBS-0.4.2-01 a OBS-0.4.2-05)

| ID Observación | Componente | Comportamiento Observado | Impacto Arquitectónico / Riesgo |
| :--- | :--- | :--- | :--- |
| **OBS-0.4.2-01** | `models.py` | `TABLE_SIMPLE` y `TABLE_COMPLEX` comparten exactamente el mismo DTO `TablePayload(content: str)`. Igualmente, `DISPLAY_EQUATION` e `INLINE_EQUATION` comparten `MathPayload`. | **Redundancia de Schema:** Coexisten tipos semánticos distintos sin diferenciación en sus modelos de datos subyacentes. |
| **OBS-0.4.2-02** | `builder.py` | `FlatASTBuilder._TYPE_MAPPING` asigna `"TABLE"` $\rightarrow$ `TABLE_SIMPLE` y `"EQUATION"` $\rightarrow$ `DISPLAY_EQUATION`. | **Tipos Inalcanzables por Defecto:** `TABLE_COMPLEX` e `INLINE_EQUATION` nunca son producidos por la ingesta estándar; requieren inyección manual. |
| **OBS-0.4.2-03** | `models.py` | `COMPOSITE_BLOCK` está declarado en `ContentNodeType`, pero no figura en el diccionario `type_mapping` de `_discriminate_payload()`. | **Asimetría de Hidratación:** Si se pasa un diccionario crudo con `node_type: "composite_block"`, el discriminador no posee un mapeo explícito en su tabla de dispatch. |
| **OBS-0.4.2-04** | `enums.py` | `ContentNodeType` carece de métodos o clasificadores de criticidad semántica (`DC-06`). | **Carencia para Benchmarking:** El dominio no informa si perder un `HEADING` o una `DISPLAY_EQUATION` debe penalizar más que perder un `PARAGRAPH`. |
| **OBS-0.4.2-05** | `models.py` | `CAPTION` no posee un payload propio y reutiliza `ParagraphPayload`. | **Pérdida de Enlace Semántico:** El caption no almacena una referencia explícita al ID de la imagen o tabla a la que describe. |

---

## 4. AST ONTOLOGY & PAYLOAD CAPABILITY MATRIX

| Tipo de Nodo (`ContentNodeType`) | Payload (`ASTPayload`) | Ingesta Estándar | Discriminador Mapeado | Gobernanza de Validaciones | Estado Arquitectónico |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `HEADING` | `HeadingPayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Robusto:** Incluye `heading_level` (H1, H2, H3). |
| `PARAGRAPH` | `ParagraphPayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Robusto:** Tipo canónico por defecto. |
| `DISPLAY_EQUATION` | `MathPayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Robusto:** Expresiones matemáticas en bloque. |
| `INLINE_EQUATION` | `MathPayload` | **NO** | **SÍ** | Genérica (vía `NodeValidator`) | **Redundante:** Mismo payload que `DISPLAY`. Inalcanzable por defecto. |
| `TABLE_SIMPLE` | `TablePayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Solapado:** Comparte `TablePayload` con `COMPLEX`. |
| `TABLE_COMPLEX` | `TablePayload` | **NO** | **SÍ** | Genérica (vía `NodeValidator`) | **Inalcanzable:** No producido por `FlatASTBuilder`. |
| `IMAGE` | `ImagePayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Robusto:** Maneja `asset_path` y `alt_text`. |
| `CAPTION` | `ParagraphPayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Básico:** Sin anclaje a la entidad visual descrita. |
| `CODE` | `CodePayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Robusto:** Maneja especificación de `language`. |
| `LIST` | `ListPayload` | **SÍ** | **SÍ** | Genérica (vía `NodeValidator`) | **Básico:** Almacena contenido sin sub-ítems. |
| `COMPOSITE_BLOCK` | `ParagraphPayload` | **SÍ** | **NO** (`OBS-0.4.2-03`) | Genérica (vía `NodeValidator`) | **Incompleto:** Falta mapeo explícito en `type_mapping`. |

---

## 5. DISPOSICIÓN ARQUITECTÓNICA Y RECOMENDACIÓN DE ACCIÓN

### 5.1 Regla de No-Remediación (Fase 0)
Se mantiene la política de lectura estricta. Ningún enum o modelo del AST ha sido modificado en producción durante el Sub-hito 0.4.2.

### 5.2 Recomendaciones para el Hito 0.5:
1. **Racionalización de Ontología (`DC-11`):** Evaluar la unificación de `TABLE_SIMPLE` y `TABLE_COMPLEX` en un único tipo `TABLE`, salvo que se introduzca un `ComplexTablePayload` diferenciado (p. ej., estructura de celdas).
2. **Completitud en Discriminador (`OBS-0.4.2-03`):** Añadir `ContentNodeType.COMPOSITE_BLOCK: ParagraphPayload` dentro de `type_mapping` en `ASTNode._discriminate_payload()` para cerrar la asimetría de hidratación.
3. **Ponderación de Criticidad en Dominio (`DC-06`):** Extender `ContentNodeType` con una propiedad de dominio (p. ej. `criticality_weight`) para alimentar las matrices de costos del benchmark topológico.

---

## 6. RESULTADOS CONSOLIDADOS SUB-HITO 0.4.2

### Auditoría Ontológica, Materialización y Protocolos de Validación
* **Causa Raíz:** Evaluación de la expresividad y suficiencia del modelo de información `ContentNodeType`, la discriminación de payloads `ASTPayload` y la interfaz `NodeValidator`.
* **Hallazgos Clave Registrados:**
  * **Aislamiento Limpio de Capas:** Se confirmó que la representación lógica (`ASTNode`) está desacoplada de la maquetación física (`LayoutBlockDraft`) y de las estrategias de procesamiento.
  * **Demostración de Redundancia de Schemas:** Se verificó que `TABLE_SIMPLE`/`TABLE_COMPLEX` y `DISPLAY_EQUATION`/`INLINE_EQUATION` comparten los mismos DTOs de datos subyacentes (`TablePayload` y `MathPayload`).
  * **Asimetría en Discriminador:** Detección de la ausencia de `COMPOSITE_BLOCK` en la tabla `type_mapping` de `_discriminate_payload()`.
  * **Gobierno de Validación:** Se constató que la ontología gobierna la estructura y los payloads, pero el comportamiento de validación por tipo no está directamente ligado al enum en el núcleo actual.

---

## 7. DECLARACIÓN DE CIERRE DEL SUB-HITO 0.4.2

El **Sub-hito 0.4.2 (AST Ontology Audit)** queda **COMPLETADO Y CONGELADO (`FROZEN`)**.