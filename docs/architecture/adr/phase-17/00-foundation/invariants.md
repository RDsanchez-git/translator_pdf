# 11E.1 Definición de Invariantes de Confiabilidad para Traducción

## Modelo de Severidades y Scope

| Severidad | Efecto |
|-----------|--------|
| HARD_FAIL | Aborta chunk o documento |
| WARNING | Telemetría, pipeline continúa |
| INFO | Observabilidad |

| Scope | Significado |
|-------|-------------|
| Chunk | Validación sobre cada unidad de traducción individual |
| Document | Validación sobre el documento final ensamblado |

---

## 11E.1.1 Structural Invariants

### SI-01 Delimiter Balance
- **Descripción**: Balance de `{}` y `[]` en cada chunk.
- **Scope**: Chunk
- **Severidad**: HARD_FAIL

### SI-02 Math Delimiter Balance
- **Descripción**: Balance de `$` (inline) y `$$` (display) en cada chunk.
- **Scope**: Chunk
- **Severidad**: HARD_FAIL

### SI-03 Environment Integrity
- **Descripción**: Los entornos `\begin{...}` y `\end{...}` deben estar correctamente anidados y balanceados en el documento final.
- **Scope**: Document
- **Severidad**: HARD_FAIL

### SI-04 Reserved Character Semantics
- **Descripción**: Los caracteres reservados de LaTeX (`% & $ _ # { }`) no deben perder su significado original. Si aparecen escapados en el origen, el destino debe preservar una representación equivalente que mantenga la misma semántica LaTeX (no necesariamente la barra literal).
- **Scope**: Chunk
- **Severidad**: HARD_FAIL

---

## 11E.1.2 Preservation Invariants

### PI-01 DOI Preservation
- **Scope**: Chunk, HARD_FAIL
### PI-02 URL Preservation
- **Scope**: Chunk, HARD_FAIL
### PI-03 ISBN/ORCID Preservation
- **Scope**: Chunk, HARD_FAIL
### PI-04 Cross-Reference Key Preservation
- **Descripción**: Claves en `\cite{}`, `\ref{}`, `\label{}`, `\autoref{}`, `\cref{}`, `\pageref{}`.
- **Scope**: Document (porque una referencia puede definirse en un chunk y usarse en otro)
- **Severidad**: HARD_FAIL

---

## 11E.1.3 Perimeter Invariants

### PeI-01 Markdown Leakage
- **Scope**: Chunk, HARD_FAIL
### PeI-02 Meta-Text Leakage
- **Scope**: Chunk, HARD_FAIL

---

## 11E.1.4 Volumetric Invariants

### VI-01 Translation Length Ratio
- **Descripción**: `len_caracteres(destino)/len_caracteres(origen)` en rango [0.7, 1.4].
- **Scope**: Chunk, **WARNING**

---

## 11E.1.5 Semantic Invariants (Fase 1)

### SeI-01 Numerical Preservation
- **Scope**: Chunk, **WARNING**
### SeI-02 Physical Unit Preservation
- **Scope**: Chunk, **WARNING**

---

## 11E.1.6 Compilation Invariants

### CI-01 Compilation Integrity
- **Descripción**: El documento final ensamblado debe compilar con `pdflatex` sin errores fatales.
- **Scope**: Document
- **Severidad**: HARD_FAIL