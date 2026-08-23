# FASE_{X}_EXIT_REVIEW_EVIDENCE_LOG.md

**Documento:** `docs/architecture/adr/phase-{fase}/reviews/FASE_{X}_EXIT_REVIEW_EVIDENCE_LOG.md`
**Versión:** {X.Y.Z}
**Estado:** {IN_PROGRESS | FROZEN}
**Fecha:** {YYYY-MM-DD}
**Última actualización:** {YYYY-MM-DD}
**Derivado de:** `PHASE_{FASE}_EXECUTION_PLAN.md` v{versión} — Gate {N} Exit Review
**Propósito:** Registro auditable de la evidencia forense que fundamenta cada decisión
tomada durante el Exit Review. Cada finding incluye los archivos auditados, el análisis,
los gaps confirmados, la justificación normativa y la clasificación final.

> **Este documento NO es:**
> - El Findings Register (registro de decisiones y resultados de implementación)
> - El Execution Plan (secuencia de tareas)
> - Un documento de gobernanza normativa (NADRs/ADRs)
>
> **Este documento SÍ es:**
> - La evidencia forense que justifica cada clasificación del Findings Register
> - El registro auditable de qué se auditó y por qué se decidió lo que se decidió
> - Un documento de consulta futura para no re-derivar conclusiones

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| {X.Y.Z} | {YYYY-MM-DD} | {Descripción del cambio} |

---

## 0. MARCO NORMATIVO Y PRINCIPIOS RECTORES

### 0.1 Jerarquía normativa aplicada

```text
{ADR_PADRE_MASTER}  >  {ADR_FASE_XX}  >  {NADR-XX..YY}  >  {PHASE_FASE_EXECUTION_PLAN}
```

> *"No lower governance level is authorized to redefine or contradict
> decisions established by an upper level."*

### 0.2 Principio rector del Exit Review

> *"{Pregunta rectora específica de la fase.
> Ejemplo: ¿La existencia de este finding impide que el objetivo de la fase
> sea una representación determinista, reproducible y arquitectónicamente
> fiel del pipeline productivo que vamos a certificar?}"*

### 0.3 Reglas transversales aplicables

> {Citar reglas transversales que aplican al análisis de hallazgos.
> Ejemplo: Regla de separación Benchmark/Producción,
> Corolario forense P2, Separación de identidades, etc.}

---

## 1. CONVENCIONES DEL REGISTRO

### 1.1 Identificadores

| Prefijo | Significado | Origen |
|---------|-------------|--------|
| `DF-{XX}` | Deferred Finding | Hallazgo técnico identificado durante implementación |
| `GF-{XX}` | Governance Finding | Conflicto normativo entre niveles de gobernanza |
| `H-{XX}-{X}` | Hallazgo derivado | Hallazgo descubierto durante la auditoría de otro DF |

### 1.2 Estados de clasificación

| Estado | Significado |
|--------|-------------|
| `RESOLVED` | Implementado y cerrado |
| `RESOLVED — DELETE` | Código muerto eliminado |
| `RESOLVED — MOVE` | Código reubicado en capa correcta |
| `RESOLVED — REFACTORED` | Código refactorizado sin cambio funcional |
| `RESOLVED — FACTORY EXTRACTION` | Lógica extraída a factory canónica |
| `CLOSED (NAR)` | No Action Required — falso positivo o correcto por diseño |
| `ACCEPTED_LIMITATION` | Limitación conocida y documentada |
| `RECLASSIFIED_FUTURE_PHASE` | Movido a fase posterior con justificación |
| `IMPLEMENTATION_REQUIRED` | Requiere implementación (scope por definir o acotado) |
| `REVIEW_REQUIRED` | Requiere análisis adicional antes de decidir |
| `PENDING_REVIEW` | Pendiente de análisis en Exit Review |

### 1.3 Reglas de evidencia

- Cada finding **DEBE** incluir la lista de archivos/documentos auditados con evidencia concreta.
- Cada finding **DEBE** distinguir entre: (a) gap objetivo confirmado, (b) hipótesis pendiente de demostración, (c) no-gap (comportamiento correcto por diseño).
- No se implementa código durante el Exit Review. La implementación se agrupa en un batch posterior.
- Ningún DF se cierra sin evidencia de código o documental que fundamente la decisión.

### 1.4 Árbol de decisión del Gate Exit Review

```text
1. ¿Sigue siendo válido el hallazgo?
   → NO: CLOSED (NAR)
   → SÍ: continuar

2. ¿Puede resolverse dentro del Gate actual?
   → SÍ: RESOLVED
   → NO: continuar

3. ¿Es un problema técnico?
   → SÍ: RECLASIFICADO a Gate futuro
   → NO: continuar

4. ¿Es un conflicto normativo?
   → SÍ: CONVERTIDO EN GF
   → NO: ACCEPTED_LIMITATION o RECLASSIFIED_FUTURE_PHASE
```

---

## 2. ESTRUCTURA POR FINDING

{Repetir esta estructura por cada DF/GF analizado.}

### {N} {DF/GF}-{XX} — {Título corto del hallazgo}

| Campo | Valor |
|-------|-------|
| **ID** | {DF/GF}-{XX} |
| **Tipo** | {Deferred Finding / Governance Finding / Hallazgo derivado} |
| **Estado** | `{Clasificación final}` |
| **Origen** | {Wave/Task/Gate donde se identificó} |
| **Gate destino original** | {Gate original} |
| **Estado previo** | {Estado anterior si fue reclasificado} |
| **Prioridad** | {Baja / Media / Alta / Critical / N/A} |
| **¿Requiere implementación?** | {Sí/No — con alcance si aplica} |
| **¿Bloquea {objetivo de la fase}?** | {Sí/No/Condicional} |

#### {N}.1 Texto original del DF

> *"{Texto exacto del hallazgo tal como fue registrado originalmente
> en el Execution Plan}"*

#### {N}.2 Reformulación corregida (si aplica)

{Si el texto original era ambiguo, incorrecto o desactualizado,
reformular con precisión. Si no aplica, indicar
"No requiere reformulación" y omitir esta sección.}

**Formulación correcta:**

> *"{Reformulación precisa del hallazgo}"*

#### {N}.3 Archivos y documentos auditados

| # | Archivo / Documento | Evidencia extraída |
|---|---------------------|-------------------|
| 1 | `{ruta/al/archivo.py}` | {Descripción de la evidencia concreta encontrada} |
| 2 | `{ruta/al/documento.md}` §{N} | {Cita o descripción de la evidencia} |
| 3 | Grep: `{patrón}` en `{directorios}` | {Resultado del grep: N resultados / 0 resultados} |
| ... | ... | ... |

#### {N}.4 Análisis

{Análisis detallado del hallazgo. Debe responder:}
- ¿La condición original existe?
- ¿Es una violación normativa o un comportamiento correcto por diseño?
- ¿Qué NADRs/ADRs aplican?
- ¿Cuál es el impacto funcional real?

#### {N}.5 Gaps objetivos confirmados (si aplica)

| # | Gap | Evidencia | Severidad |
|---|-----|-----------|-----------|
| G1 | {Descripción del gap} | {Archivo/línea que lo demuestra} | {Baja/Media/Alta} |
| G2 | {Descripción del gap} | {Evidencia} | {Severidad} |

#### {N}.6 Lo que NO es un gap

| Aspecto | Veredicto | Justificación |
|---------|-----------|---------------|
| {Aspecto que podría parecer gap pero no lo es} | ✅ Correcto por diseño | {Justificación con referencia normativa} |
| {Otro aspecto} | ❌ No relacionado | {Justificación} |

#### {N}.7 Impacto en {objetivo de la fase}

| Dimensión | ¿Afecta? | Justificación |
|-----------|----------|---------------|
| Determinismo | {✅/❌/⚠️} | {Justificación} |
| Reproducibilidad | {✅/❌/⚠️} | {Justificación} |
| Corrección funcional | {✅/❌/⚠️} | {Justificación} |
| Bloquea {siguiente fase} | {✅/❌/⚠️} | {Justificación} |

#### {N}.8 Sub-acciones identificadas (si aplica)

| Sub-acción | Descripción | Estado | Scope |
|------------|-------------|--------|-------|
| {DF}-{XX}-A | {Descripción} | {Demostrado/Pendiente} | {Producción/Benchmark/Tooling} |
| {DF}-{XX}-B | {Descripción} | {Estado} | {Scope} |

#### {N}.9 Clasificación consolidada

| Campo | Valor |
|-------|-------|
| Condición original existe | {✅ Sí / ❌ No / ⚠️ Parcialmente} |
| Es violación arquitectónica | {✅ Sí / ❌ No} |
| Es violación de gobernanza | {✅ Sí / ❌ No} |
| Es problema técnico | {✅ Sí / ❌ No} |
| Pertenece a {Fase actual} | {✅ Sí / ❌ No} |
| Bloquea {objetivo} | {✅ Sí / ❌ No / ⚠️ Condicional} |
| Clasificación | `{ESTADO_FINAL}` |
| Prioridad | {Baja/Media/Alta/N/A} |

#### {N}.10 Regla aplicada

> **{NADR/ADR/ENGINEERING_PRINCIPLES} §{N} ({Nombre}):**
> *"{Cita textual de la regla que fundamenta la decisión}"*

{Explicación de cómo la regla aplica al caso concreto.}

---

## 3. GATE EXIT REVIEW SUMMARY

{Una sub-sección por cada Gate Exit Review ejecutado.}

### 3.{N} Gate {N} Exit Review ({YYYY-MM-DD})

**Árbol de decisión aplicado:**

| DF | ¿Válido? | ¿Resoluble? | ¿Técnico? | Decisión | Motivo |
|----|----------|-------------|-----------|----------|--------|
| DF-{XX} | {✅ Sí / ❌ No / ⚠️ Parcial} | {✅ Sí / ❌ No} | {✅ Sí / ❌ No} | {Decisión} | {Motivo} |

**Resumen:**
- RESOLVED: {N} ({DF-XX})
- RECLASIFICADO → Gate {X}: {N} ({DF-XX, DF-YY})
- CLOSED (NAR): {N} ({DF-XX})
- CONVERTIDO EN GF: {N} ({GF-XX})
- Nuevos hallazgos registrados: {N} ({DF-XX})

---

## 4. TABLA CONSOLIDADA FINAL

{Se completa al cierre del último Gate Exit Review.}

### 4.1 Resumen por clasificación

| Clasificación | Cantidad | DFs |
|--------------|----------|-----|
| `CLOSED (NAR)` | {N} | {DF-XX, DF-YY} |
| `RESOLVED — DELETE` | {N} | {DF-XX} |
| `RESOLVED` | {N} | {DF-XX} |
| `IMPLEMENTATION_REQUIRED` | {N} | {DF-XX} |
| `RECLASSIFIED_FUTURE_PHASE` | {N} | {DF-XX} |
| `REVIEW_REQUIRED` | {N} | {DF-XX} |
| `ACCEPTED_LIMITATION` | {N} | {DF-XX} |

### 4.2 Tabla consolidada

| DF | Estado | Decisión |
|----|--------|----------|
| {DF/GF-XX} | `{Estado final}` | {Descripción breve de la decisión} |

---

## 5. CRITERIOS DE CIERRE

### 5.1 Criterio de cierre del Evidence Log

El documento se considera cerrado (`FROZEN`) cuando:

- [ ] Todos los hallazgos del Execution Plan tienen evidencia forense registrada
- [ ] Ningún hallazgo está en estado `PENDING_REVIEW`
- [ ] La tabla consolidada final está completa
- [ ] Cada clasificación tiene al menos una regla normativa aplicada
- [ ] Los hallazgos `RECLASSIFIED_FUTURE_PHASE` tienen destino explícito
- [ ] Los hallazgos `REVIEW_REQUIRED` tienen plan de reevaluación

### 5.2 Relación con el Findings Register

El Evidence Log y el Findings Register son documentos complementarios:

| Documento | Propósito | Momento |
|-----------|-----------|---------|
| **Evidence Log** (este documento) | Evidencia forense de cada decisión | Al cierre del Exit Review |
| **Findings Register** | Registro de decisiones + resultados de implementación | Durante y después del Exit Review |

Cada entrada del Findings Register debe tener una referencia cruzada a la
sección correspondiente de este Evidence Log.

---

**Nota de Gobernanza:** Este documento es el registro de evidencia forense
del Exit Review. No tiene autoridad normativa. No redefine reglas de NADRs
ni ADRs. Su único propósito es documentar la evidencia que fundamenta cada
clasificación del Findings Register, para que futuras sesiones o fases no
tengan que re-derivar conclusiones.