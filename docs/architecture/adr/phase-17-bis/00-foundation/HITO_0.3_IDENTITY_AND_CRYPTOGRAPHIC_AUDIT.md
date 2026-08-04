# HITO_0.3_IDENTITY_AND_CRYPTOGRAPHIC_AUDIT.md
## Identity, Hashing & Canonicalization Forensic Audit — Reporte Consolidado Final

* **Estado:** FROZEN / CONGELADO
* **Fecha de Emisión:** 2026-07-26
* **Fase Parent:** Fase 17-BIS (Canonical Scientific Baseline)
* **Fase Activa:** Fase 0 (Architecture & Baseline Audit Gate)
* **ADR de Gobernanza:** `ADR_F17-BIS_0`
* **Límite Epistemológico:** Solo lectura / Auditoría analítica de firmas, serialización y taxonomía de identidad. Cero mutaciones en código productivo. Disposición arquitectónica diferida al Hito 0.5 (`UNASSESSED`).

---

## 1. PROPÓSITO Y RESUMEN EJECUTIVO

El **Hito 0.3 (Identity, Hashing & Canonicalization Audit)** tiene como objetivo auditar los algoritmos de firma criptográfica, los generadores de identificadores y las políticas de serialización determinista en todo el pipeline (`core/ast`, `core/layout`, `core/segmenter`, `core/benchmark` y `tools/evaluation`).

A través del análisis de código primario en `core/layout/identity.py`, `core/ast/builder.py`, `core/segmenter/segmenters.py`, `protocols.py` y `policies.py`, esta auditoría establece la genealogía real de la identidad en el repositorio y la causa raíz de la volatilidad en la firma criptográfica del AST.

---

## 2. REGISTRO DE EVIDENCIA FORENSE COMPLETO (E-0.3-001 a E-0.3-007)

### Evidencia E-0.3-001: Inclusión de `node_id` en la Firma del AST (`compute_ast_hash`)
* **Archivo Fuente Primario:** `core/ast/hashing.py`
* **Símbolo Auditado:** `compute_ast_hash(ast: List[ASTNode]) -> str`
* **Declaración Observada:**
  ```python
  def compute_ast_hash(ast: List[ASTNode]) -> str:
      def serialize_node(n: ASTNode) -> dict:
          type_str = n.node_type.value if hasattr(n.node_type, "value") else str(n.node_type)
          return {
              "node_id": n.node_id,
              "type": type_str,
              "content": n.text_content,
              "latex": getattr(n, "latex", None),
              "children": [serialize_node(c) for c in getattr(n, "children", [])] if getattr(n, "children", None) else []
          }
      raw = json.dumps([serialize_node(n) for n in ast], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
      return hashlib.sha256(raw.encode("utf-8")).hexdigest()
  ```
* **Análisis Forense:** La firma criptográfica SHA-256 acopla directamente el identificador técnico `node_id`. Si una transformación posterior altera el `node_id` sin modificar el contenido semántico ni la jerarquía, la firma resultante diverge por completo.

---

### Evidencia E-0.3-002: Origen Determinista de Identidad Inicial (`BlockIdentityGenerator`)
* **Archivos Fuente Primarios:** `core/layout/identity.py`, `core/ast/builder.py`
* **Símbolos Auditados:** `BlockIdentityGenerator._build_seed()`, `FlatASTBuilder._map_physical_to_logical()`
* **Declaración Observada:**
  ```python
  # core/layout/identity.py
  def _build_seed(self, provider: str, page: int, block_id: str, bbox: BoundingBox, content: str, precision: int) -> str:
      dx0 = round(bbox.x0, precision)
      dy0 = round(bbox.y0, precision)
      dx1 = round(bbox.x1, precision)
      dy1 = round(bbox.y1, precision)
      return f"{provider}_p{page}_{block_id}_[{dx0:.{precision}f},{dy0:.{precision}f},{dx1:.{precision}f},{dy1:.{precision}f}]_{content}"

  # core/ast/builder.py
  return ASTNode(
      node_id=str(block.block_id) if block.block_id else f"ast_node_{index}",
      ...
  )
  ```
* **Análisis Forense:** Se demuestra que la identidad física inicial de un `ASTNode` **sí es determinista** y deriva de la firma SHA-256 de las coordenadas, página, proveedor y contenido del bloque. El AST recién extraído posee identificadores reproducibles.

---

### Evidencia E-0.3-003: Inyección de Identidad de Runtime en Segmentación Multi-Oracional (`ParagraphSegmenter`)
* **Archivos Fuente Primarios:** `core/segmenter/segmenters.py`, `core/segmenter/service.py`
* **Símbolos Auditados:** `ParagraphSegmenter.segment()`, `UUIDIdentityGenerator`
* **Declaración Observada:**
  ```python
  # core/segmenter/segmenters.py (Para casos multi-oracionales N > 1)
  yield node.spawn_fragment(
      new_id=self._id_generator.generate(),
      new_payload=new_payload,
      segment_index=current_segment
  )

  # core/segmenter/service.py
  class UUIDIdentityGenerator:
      def generate(self) -> str:
          return str(uuid.uuid4())
  ```
* **Análisis Forense:**
  1. Cuando un párrafo contiene múltiples oraciones ($N > 1$), `ParagraphSegmenter` invoca `self._id_generator.generate()` para asignar un `node_id` a cada nuevo fragmento.
  2. La implementación inyectada en runtime es `UUIDIdentityGenerator` (`uuid.uuid4()`), emitiendo UUIDs aleatorios.
  3. `spawn_fragment()` conserva el linaje asignando `parent_node_id = self.node_id`.
  4. **Consecuencia:** La identidad de los fragmentos es de naturaleza operacional/runtime. Si un AST segmentado se pasa por `compute_ast_hash()`, el hash SHA-256 varía en cada corrida debido a los UUIDs efímeros de los fragmentos.

---

### Evidencia E-0.3-004: *Contract Drift* entre `BoundaryPolicy` y `ScientificBoundaryPolicy`
* **Archivos Fuente Primarios:** `core/segmenter/protocols.py`, `core/segmenter/policies.py`, `core/segmenter/segmenters.py`
* **Símbolos Auditados:** `BoundaryPolicy.find_boundaries()`, `ScientificBoundaryPolicy.find_boundaries()`
* **Declaración Observada:**
  ```python
  # core/segmenter/protocols.py (Docstring del contrato):
  # Retorna tupla de offsets absolutos [inicio_oración, ... , longitud_total].
  # Ejemplo documentado: (0, 45, 100)

  # core/segmenter/policies.py (Implementación real):
  for match in self._PUNCTUATION_SCANNER.finditer(text):
      ...
      boundaries.append(candidate.punct_end)
  if not boundaries or boundaries[-1] != text_length:
      boundaries.append(text_length)
  return tuple(boundaries)  # Para 1 oración devuelve (L,) -> len == 1
  ```
* **Hallazgo Forense:**
  1. Existe un *Contract Drift* entre el docstring de `BoundaryPolicy` (que describe incluir el offset inicial `0`) y la implementación de `ScientificBoundaryPolicy` (que retorna únicamente los puntos de corte finales `[end_1, end_2, ..., end_n]`).
  2. `ParagraphSegmenter` opera correctamente con la implementación real: para un párrafo de 1 sola oración de longitud $L$, `find_boundaries()` retorna `(L,)` (`len == 1`). La condición `if len(boundaries) <= 1:` evalúa `True` y **se conserva el nodo original con su `node_id` determinista**.
  3. Se retracta la hipótesis previa de fragmentación en párrafos de una sola oración.

---

### Evidencia E-0.3-005: Desfase de Metadatos en `spawn_fragment()`
* **Archivos Fuente Primarios:** `core/ast/models.py`, `core/segmenter/segmenters.py`
* **Símbolos Auditados:** `ASTNode.spawn_fragment()`
* **Declaración Observada:**
  ```python
  def spawn_fragment(self, new_id: str, new_payload: 'ASTPayload', segment_index: int) -> 'ASTNode':
      return self.model_copy(update={
          "node_id": new_id,
          "payload": new_payload,
          "parent_node_id": self.node_id,
          "segment_index": segment_index
      })
  ```
* **Hallazgo Forense:** `spawn_fragment()` actualiza `segment_index`, pero no actualiza `segment_count`. Los fragmentos emitidos reportan `segment_index > 1` mientras `segment_count` permanece congelado en `1`. (Pendiente de verificación en Hito 0.5 si `segment_count` fue deprecado en el DTO oficial de Fase 16.3).

---

### Evidencia E-0.3-006: Aislamiento Semántico en Evaluación Topológica (`ASTFingerprintPolicy`)
* **Archivo Fuente Primario:** `tools/evaluation/topology/fingerprint.py`
* **Símbolos Auditados:** `ASTFingerprintPolicy.semantic_fingerprint()`, `ASTFingerprintPolicy.identity_fingerprint()`
* **Declaración Observada:**
  ```python
  @staticmethod
  def semantic_fingerprint(node: ASTNode) -> tuple[str, str]:
      node_type_str = node.node_type.value if hasattr(node.node_type, "value") else str(node.node_type)
      content_str = node.text_content.strip()
      return (node_type_str, content_str)
  ```
* **Análisis Forense:** El subsistema de benchmarking en `tools/` desacopla explícitamente la comparación semántica de la identidad física de los nodos. Coexisten en la misma clase `semantic_fingerprint` (utilizado por el benchmark, inmune a `node_id`) e `identity_fingerprint` (que exige estabilidad en `node_id`).

---

### Evidencia E-0.3-007: Trazabilidad Física en Compilador TeX (`TexBuilder` / `RenderUnit`)
* **Archivos Fuente Primarios:** `core/compiler/rendering/models.py`, `apps/compiler/tex_builder.py`
* **Análisis Forense:** `node_id` cumple un rol legítimo dentro de la compilación TeX para inyectar trazabilidad en comentarios de depuración (`% [NODE_ID: ...]`). Se confirma que `node_id` es un identificador de *Runtime Lineage*, no de *Firma Criptográfica Canónica*.

---

## 3. TAXONOMÍA FORMAL DE IDENTIDAD EN EL SISTEMA

Basado en la evidencia primaria recopilada, se formaliza la estructura tridimensional de la identidad en la arquitectura del proyecto:

```text
                                  TAXONOMÍA DE IDENTIDAD DEL AST
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
1. IDENTIDAD SEMÁNTICA                 2. IDENTIDAD FÍSICA / RUNTIME            3. IDENTIDAD DE BASELINE
   ($H_{semantic}$)                       ($H_{runtime}$)                          ($H_{baseline}$)
   - `node_type`                          - `node_id` (SHA256 layout / UUID)       - `corpus_version`
   - `text_content` (normalizado)          - `parent_node_id`                       - Hash del PDF físico
   - Orden secuencial relativo             - `bboxes` / `pages`                     - $H_{semantic}$ del Oráculo
   - Nivel de jerarquía (`depth`)          - Metadatos de confianza                 - Total páginas / Traits
         │                                      │                                      │
         ▼                                      ▼                                      ▼
   Inmune a volatilidad.                 Requerido para TeX comentarios         Firma Inmutable de la
   Usado por Benchmark.                   y trazabilidad de renderizado.         Baseline Científica (Fase 2).
```

---

## 4. MATRIZ DE GAPS Y CANDIDATOS A DECISIÓN

| ID Gap | Componente | Defecto Observado | Impacto en Baseline | Candidato a Decisión (Hito 0.5) |
| :--- | :--- | :--- | :---: | :--- |
| **GAP-0.3-01** | `compute_ast_hash` | Incluye `node_id` en la serialización JSON de firma (`E-0.3-001`). | **P0 (Bloqueante)** | **DC-01:** Rediseñar `compute_ast_hash` para calcular la firma sobre la identidad semántica $H_{semantic}$ pura (agnóstica a `node_id`). |
| **GAP-0.3-02** | `UUIDIdentityGenerator` | Genera UUIDs v4 aleatorios durante la segmentación multi-oracional (`E-0.3-003`). | **P1 (Runtime)** | **DC-08:** Determinar si la identidad de fragmentos debe ser determinista (hash) o si basta con desacoplar `node_id` de $H_{semantic}$. |
| **GAP-0.3-03** | `ManifestFingerprintCalculator` | No incorpora $H_{semantic}$ en la firma global del manifiesto (`E-0.2-003`). | **P0 (Bloqueante)** | **DC-03:** Definir la fórmula de encadenamiento global $H_{baseline} = \text{SHA256}(V_{corpus} \parallel \sum H_{pdf} \parallel \sum H_{semantic})$. |
| **GAP-0.3-04** | `BoundaryPolicy` | Discrepancia entre docstring `(0, end_1, ...)` e implementación `(end_1, ...)` (`E-0.3-004`). | **P1 (Contrato)** | **DC-09:** Armonizar el contrato de `BoundaryPolicy` actualizando el docstring o formalizando la tupla de cortes. |
| **GAP-0.3-05** | `ASTNode.spawn_fragment` | No actualiza `segment_count` (`E-0.3-005`). | **P2 (Deuda)** | Verificar si `segment_count` debe ser eliminado del DTO o actualizado por un normalizador. |

---

## 5. DISPOSICIÓN ARQUITECTÓNICA Y RECOMENDACIÓN DE ACCIÓN

### 5.1 Regla de No-Remediación durante la Fase 0
Los defectos y riesgos identificados en esta auditoría quedan expresamente sin modificación en código productivo durante el Hito 0.3, en cumplimiento estricto del marco *Production Read-Only*. Esta auditoría separa formalmente:
1. **Descubrimiento:** Identificación y demostración del comportamiento actual.
2. **Diagnóstico:** Determinación de causa raíz e impacto.
3. **Disposición:** Recomendación de tratamiento futuro.
4. **Remediación:** Modificación del sistema, reservada exclusivamente para la Fase de Implementación tras la aprobación de los ADRs en el Hito 0.5.

### 5.2 Disposición de la Identidad Canónica
Se recomienda **NO utilizar `node_id` como componente normativo de la identidad criptográfica científica del AST** hasta que el Hito 0.5 determine formalmente su semántica. Se propone formalizar la separación entre Identidad Física/Runtime, Identidad Semántica e Identidad Criptográfica de Baseline.

### 5.3 Acción Recomendada para Hito 0.5
Abrir decisiones arquitectónicas explícitas para resolver:
* **DC-01 (Canonical AST Identity & Hashing Contract):** Definir la fórmula exacta de $H_{semantic}$ excluyendo atributos de runtime efímeros.
* **DC-03 (Baseline Manifest Cryptographic Commitment):** Definir el encadenamiento criptográfico global de la baseline.
* **DC-08 (Determinism of Fragment IDs):** Evaluar el paso a hashes deterministas para fragmentos o la conservación de UUIDs acotados a runtime.

### 5.4 Disposición de `UUIDIdentityGenerator` y Contract Drift
* `UUIDIdentityGenerator` se mantiene en estado **OBSERVED / NOT REMEDIATED**. Su existencia no es un defecto en sí misma; la falla radica en que `compute_ast_hash()` consuma identificadores de runtime.
* La discrepancia en `BoundaryPolicy` se registra como **CONTRACT DRIFT / DOCUMENTATION MISALIGNMENT**, recomendando la actualización del docstring del protocolo en la fase de remediación.

---

## 6. LÍMITE EPISTEMOLÓGICO Y DECLARACIÓN DE CIERRE DEL HITO 0.3

El **Hito 0.3 (Identity, Hashing & Canonicalization Audit)** queda oficialmente **COMPLETADO Y CONGELADO (`FROZEN`)**.

**Garantías del Entregable:**
1. **Genealogía de Identidad Mapeada:** Se identificó que la identidad original nace determinista en `BlockIdentityGenerator` y que la fragilidad criptográfica se limita a `compute_ast_hash` cuando procesa fragmentos de runtime.
2. **Corrección Forense Aplicada:** Se desmintió la fragmentación espuria en oraciones únicas y se reclasificó el hallazgo de `BoundaryPolicy` como *Contract Drift*.
3. **Taxonomía Tridimensional Establecida:** Se delimitó la separación conceptual entre Identidad Semántica ($H_{semantic}$), Identidad de Runtime ($H_{runtime}$) e Identidad de Baseline ($H_{baseline}$).

## 6. DISPOSICIÓN ARQUITECTÓNICA Y RECOMENDACIÓN DE ACCIÓN

### 6.1 Regla de No-Remediación durante el Hito 0.3

Los defectos y riesgos identificados en esta auditoría quedan expresamente **sin modificación en código productivo** durante el Hito 0.3.

Esta restricción no implica aceptación del comportamiento observado. Significa que la auditoría separa formalmente:

* **Descubrimiento:** identificación y demostración del comportamiento actual.
* **Diagnóstico:** determinación de causa raíz e impacto.
* **Disposición:** recomendación de tratamiento futuro.
* **Remediación:** modificación del sistema, reservada para un Hito posterior con ADR aprobado.

El Hito 0.3 queda, por tanto, limitado a evidencia, clasificación y recomendación.

### 6.2 Disposición de la Identidad Canónica

Se recomienda **NO utilizar `node_id` como componente normativo de la identidad criptográfica científica del AST** hasta que el Hito 0.5 determine formalmente su semántica.

La evidencia actual demuestra que `node_id` posee naturaleza híbrida:

1. Inicialmente puede derivar de una identidad física determinista producida por `BlockIdentityGenerator`.
2. Durante transformaciones estructurales posteriores puede ser reemplazado por una identidad generada por `NodeIdentityGenerator`.
3. El benchmark ya dispone de una representación semántica independiente de `node_id` mediante `ASTFingerprintPolicy.semantic_fingerprint()`.

Por tanto, se recomienda separar explícitamente:

```text
IDENTIDAD FÍSICA / RUNTIME
    node_id
    parent_node_id
    metadata espacial
    segmentación / linaje

IDENTIDAD SEMÁNTICA
    node_type
    contenido normalizado
    orden topológico canónico
    estructura semántica

IDENTIDAD CRIPTOGRÁFICA DE BASELINE
    hash canónico derivado exclusivamente
    de la representación científica definida
    por el contrato de Ground Truth
```

### 6.3 Acción recomendada para Hito 0.5

Abrir una decisión arquitectónica específica para resolver:

**DC-01 — Canonical AST Identity & Hashing Contract**

La decisión deberá determinar formalmente:

1. Qué atributos constituyen la identidad científica canónica del AST.
2. Qué atributos son exclusivamente de runtime/linaje.
3. Si `node_id` debe excluirse de la firma canónica.
4. Qué normalización de contenido y ordenamiento debe aplicarse antes del hashing.
5. Si debe existir una representación canónica independiente de la entidad `ASTNode`.
6. Cómo debe encadenarse dicha firma con `H_physical`, `SchemaVersion` y `CorpusVersion`.
7. Qué invariantes de reproducibilidad deberán convertirse posteriormente en Regression Gates.

### 6.4 Disposición de `UUIDIdentityGenerator`

No se recomienda sustituir inmediatamente `UUIDIdentityGenerator`.

La existencia de un generador UUID no constituye por sí sola un defecto: puede ser válida para identidad operacional de fragmentos.

La decisión pendiente es determinar si esa identidad operacional está siendo incorrectamente utilizada como componente de una firma científica.

Por tanto:

```text
UUIDIdentityGenerator
        │
        └── Estado: OBSERVED / NOT YET REMEDIATED

compute_ast_hash
        │
        └── Estado: ARCHITECTURALLY BLOCKING / DECISION REQUIRED

canonical semantic identity
        │
        └── Estado: TO BE FORMALLY DEFINED IN HITO 0.5
```

### 6.5 Disposición de la discrepancia contractual de `BoundaryPolicy`

La divergencia observada entre la documentación del contrato de `BoundaryPolicy.find_boundaries()` y la semántica efectiva consumida por `ParagraphSegmenter` deberá registrarse como **contract drift**.

No se recomienda modificarla durante Hito 0.3.

La resolución deberá determinar primero cuál de las dos semánticas es la canónica:

```text
A) (0, end_1, end_2, ..., end_n)

o

B) (end_1, end_2, ..., end_n)
```

La implementación actual parece consumir la alternativa **B**, mientras que la documentación del protocolo describe la alternativa **A**.

Esta discrepancia debe resolverse mediante contrato explícito antes de introducir cambios en la implementación.

### 6.6 Criterio de salida

El Hito 0.3 no se considerará bloqueado por la existencia de estos defectos.

Se considera correcto que finalice con:

```text
DISCOVERED
    ↓
EVIDENCED
    ↓
CLASSIFIED
    ↓
DISPOSITION ASSIGNED
    ↓
DEFERRED TO ARCHITECTURAL DECISION
```

y no con una modificación inmediata del código productivo.
