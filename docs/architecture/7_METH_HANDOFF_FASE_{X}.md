# FASE_{X}_HANDOFF.md — PLANTILLA CANÓNICA

**Documento:** `docs/architecture/adr/phase-{fase}/handoff/FASE_{X}_HANDOFF.md`
**Versión:** 1.0.0
**Estado:** FROZEN
**Fecha:** {YYYY-MM-DD}
**Fase completada:** {Nombre completo de la fase}
**Siguiente fase:** {Nombre de la siguiente fase según ROADMAP}
**Derivado de:** `PHASE_{FASE}_EXECUTION_PLAN.md` v{versión} + `FASE_{X}_DEFERRED_FINDINGS_REGISTER.md` v{versión}

### Changelog
| Versión | Fecha | Cambio |
|---|---|---|
| 1.0.0 | {YYYY-MM-DD} | Emisión inicial al cierre de {Fase} |

---

## 1. EXECUTIVE SUMMARY

{2-3 párrafos máximos. Responder exactamente tres preguntas:}

1. **¿Qué se logró?** — Objetivo de la fase y estado final (COMPLETED / PARTIAL / FAILED)
2. **¿Cuál es el estado actual?** — Métricas de validación, hallazgos resueltos vs diferidos
3. **¿Qué necesita la siguiente fase?** — Prerequisitos críticos y restricciones carry-forward

> **Regla:** Este bloque es lo único que un humano necesita leer para entender dónde está
> el proyecto. Si alguien solo lee esta sección, debe poder decidir si continuar o no.

---

## 2. STATE SNAPSHOT

### 2.1 Repository State

| Campo | Valor |
|-------|-------|
| Rama principal | `{branch}` |
| Commit hash de cierre | `{SHA}` |
| Estado del árbol | {Limpio / Con cambios pendientes} |
| Baseline de tests | **{X} passed, {Y} skipped** (no debe degradarse sin justificación) |
| Pyright / Type checker | **{N} errors, {N} warnings** |
| Imports huérfanos | {N detectados} |
| {Otra validación específica} | {Resultado} |

### 2.2 Validation Results

```bash
# Comandos ejecutados al cierre de la fase
{comando_1}    # {resultado esperado} ✅
{comando_2}    # {resultado esperado} ✅
{comando_3}    # {resultado esperado} ✅
```

### 2.3 Governance Document State

| Documento | Estado | Versión |
|-----------|--------|---------|
| ADR Maestro | {FROZEN/DRAFT} | {v} |
| ADR de Fase | {FROZEN/DRAFT} | {v} |
| NADRs ({N} documentos) | {FROZEN/DRAFT} | {v} |
| Execution Plan | {FROZEN/DRAFT} | {v} |
| Evidence Log | {FROZEN/DRAFT} | {v} |
| Findings Register | {ARCHIVED/DRAFT} | {v} |
| Methodology | {FROZEN} | {v} |

### 2.4 Phase Metrics

| Métrica | Valor |
|---------|-------|
| Hallazgos analizados | {N} |
| Hallazgos resueltos | {N} |
| Hallazgos cerrados sin acción (NAR) | {N} |
| Hallazgos diferidos a fase futura | {N} |
| Batches ejecutados | {N} |
| Archivos eliminados | {N} |
| Archivos movidos | {N} |
| Archivos creados | {N} |
| Archivos modificados | {N} |

---

## 3. ARCHITECTURAL DECISIONS MADE

{Lista de decisiones arquitectónicas significativas tomadas durante la fase.
Cada una debe ser trazable a un NADR, ADR o principio de ingeniería.}

| # | Decisión | Contexto | Justificación | Evidencia |
|---|----------|----------|---------------|-----------|
| AD-01 | {Qué se decidió} | {Qué problema lo motivó} | {NADR/ADR/Principio que lo respalda} | {Archivo/commit que lo demuestra} |
| AD-02 | {Decisión} | {Contexto} | {Justificación} | {Evidencia} |
| AD-NN | {Decisión} | {Contexto} | {Justificación} | {Evidencia} |

---

## 4. SCOPE DELIVERED

### 4.1 Capacidades arquitectónicas habilitadas

{Lista de capacidades que la fase habilitó, mapeadas a NADRs específicos.}

| Capacidad | NADR | Estado |
|-----------|------|--------|
| {Descripción de la capacidad} | NADR-{XX} | {✅ DONE / ⚠️ PARTIAL} |

### 4.2 Archivos clave creados/modificados

**Creados:**
- `{ruta}` — {propósito}

**Modificados significativamente:**
- `{ruta}` — {qué cambió}

**Eliminados (zombies y deuda):**
- `{ruta}` — {por qué se eliminó}

---

## 5. CARRY-FORWARD

### 5.1 Active Constraints (restricciones que la siguiente fase DEBE respetar)

{No listar todas las reglas de todos los NADRs. Solo las que son
relevantes y restrictivas para la siguiente fase específica.}

| Restricción | Fuente | Relevancia para siguiente fase |
|-------------|--------|-------------------------------|
| {Restricción concreta} | {NADR/ADR/Principio §N} | {Por qué importa para lo que viene} |

### 5.2 Deferred Findings (hallazgos diferidos a fases futuras)

{Todos los DFs/GFs que NO se resolvieron en esta fase y se arrastran.
Cada uno DEBE tener destino explícito y justificación.}

| ID | Descripción | Destino | Bloquea |
|----|-------------|---------|---------|
| {DF-XX} | {Descripción breve} | {Fase destino} | {Qué bloquea, o "Nada"} |

### 5.3 Known Risks & Caveats

{Limitaciones conocidas de la implementación actual que la siguiente
fase debe conocer. No son bugs, son decisiones conscientes.}

| Riesgo | Descripción | Mitigación actual |
|--------|-------------|-------------------|
| {Nombre del riesgo} | {Qué puede pasar} | {Qué se hizo para mitigarlo} |

---

## 6. FORWARD CONTEXT

### 6.1 Next Phase Prerequisites

**Lo que ya está listo:**
- ✅ {Item completado que la siguiente fase puede usar directamente}

**Lo que se necesita antes de arrancar:**
- {Item que debe resolverse o crearse antes de iniciar la siguiente fase}

### 6.2 Next Phase Handoff Checklist

{Checklist accionable para quien arranca la siguiente fase.}

- [ ] {Acción concreta 1}
- [ ] {Acción concreta 2}
- [ ] {Acción concreta N}

### 6.3 ROADMAP — Objetivos de la siguiente fase

{Copiar los objetivos declarados en el ROADMAP para la siguiente fase.
Esto evita que el LLM o el humano tengan que buscar en el ROADMAP.}

1. **{Objetivo 1}** — {descripción breve}
2. **{Objetivo 2}** — {descripción breve}
3. **{Objetivo N}** — {descripción breve}

**Hito crítico:** {Qué se considera "completado" al final de la siguiente fase}

### 6.4 Documentos que la siguiente fase debe crear

| Documento | Plantilla | Propósito |
|-----------|-----------|-----------|
| {ADR de Fase} | {ruta o referencia a plantilla} | {propósito} |
| {NADRs} | {ruta o referencia} | {propósito} |
| {Execution Plan} | {ruta o referencia} | {propósito} |

---

## 7. REFERENCE MAP

### 7.1 FROZEN documents (fuentes de verdad)

| Documento | Ruta |
|-----------|------|
| {Nombre} | `{ruta completa}` |

### 7.2 ARCHIVED documents

| Documento | Ruta |
|-----------|------|
| {Nombre} | `{ruta completa}` |

### 7.3 Support documents

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| {Nombre} | `{ruta completa}` | {para qué sirve} |

---

## 8. LLM CONTEXT BLOCK

> **INSTRUCCIONES PARA LLM:** Este bloque está diseñado para ser cargado directamente
> en una nueva conversación. Contiene el contexto mínimo necesario para continuar
> el trabajo del proyecto sin cargar los 15+ documentos de gobernanza.
> Las referencias en §7 contienen el detalle completo cuando sea necesario.

### 8.1 Project Identity

```text
Proyecto: {Nombre del proyecto}
Descripción: {1-2 líneas de qué hace}
Stack: {Lenguaje, frameworks, herramientas clave}
Arquitectura: {Patrones arquitectónicos principales}
Fase actual completada: {Fase X}
Siguiente fase: {Fase Y}
```

### 8.2 Code State

```text
Tests: {X} passed, {Y} skipped (BASELINE — NO DEBE DEGRADARSE)
Pyright: {N} errors, {N} warnings
Rama: {branch} ({estado})
```

### 8.3 Active Critical Rules (carry-forward obligatorio)

```text
1. {Regla más importante para la siguiente fase}
2. {Regla 2}
3. {Regla 3}
...
N. {Regla N}
```

### 8.4 Document Priority Map (qué cargar según la tarea)

```text
Prioridad 1 (cargar SIEMPRE al iniciar sesión):
- {documento 1}
- {documento 2}
- {documento N}

Prioridad 2 (cargar para implementación):
- {documento 1}
- {documento N}

Prioridad 3 (consultar según necesidad):
- {documento 1}
- {documento N}
```

### 8.5 Pending Items (carry-forward)

```text
[{ID}] {Descripción breve}
       → Destino: {Fase}
       → Bloquea: {Qué, o "Nada"}
       → Opciones: {Si aplica}
```

### 8.6 Work Conventions

```text
- {Convención de trabajo 1}
- {Convención de trabajo 2}
- {Convención de trabajo N}
```

### 8.7 System Entry Points

```text
{ruta_entry_point_1}    → {qué hace}
{ruta_entry_point_2}    → {qué hace}
{ruta_entry_point_N}    → {qué hace}
```

{Descripción de factories centralizadas o composition roots relevantes.}

---

## 9. CLOSURE CRITERIA

Este handoff se considera cerrado (FROZEN) cuando:

- [ ] Resumen ejecutivo completo (§1)
- [ ] Estado actual validado con evidencia (§2)
- [ ] Decisiones arquitectónicas documentadas (§3)
- [ ] Scope entregado listado (§4)
- [ ] Todos los items diferidos listados con destino (§5.2)
- [ ] Restricciones carry-forward identificadas (§5.1)
- [ ] Known risks documentados (§5.3)
- [ ] Prerequisitos de siguiente fase definidos (§6)
- [ ] Mapa de referencias completo (§7)
- [ ] LLM Context Block autocontenido (§8)

**Veredicto:** {✅ CERRADO — FROZEN / 🟡 EN PROGRESO}

---

**Nota de Gobernanza:** Este documento es el punto de transición entre fases.
No tiene autoridad normativa. No redefine reglas. Su propósito es capturar el estado
exacto del proyecto al cierre de la fase y proporcionar el contexto necesario para que
cualquier agente (humano o LLM) pueda continuar el trabajo sin pérdida de información.

Para la siguiente sesión, basta con cargar este documento + los de Prioridad 1 (§8.4)
para tener contexto completo de arranque. Los detalles normativos se consultan bajo
demanda según la tarea específica.