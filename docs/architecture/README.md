# Guía de Documentación de Arquitectura

**Versión:** 1.0.0 | **Estado:** FROZEN | **Alcance:** `docs/architecture/`

---

## 1. Propósito
Define la **metodología oficial de documentación arquitectónica** del proyecto. Su objetivo es establecer un modelo de gobernanza único, consistente y escalable para todas las fases (Fase 16, 17, 17-BIS, 18, etc.), evitando la sobreingeniería y la duplicación de información.

---

## 2. Espacio de Trabajo (Architecture Workspace)

```text
docs/
└── architecture/
    ├── roadmap/
    │   └── ROADMAP_ARQUITECTONICO.md
    └── adr/
        ├── phase-16/
        ├── phase-17/
        ├── phase-17-bis/
        │   ├── README.md                 (Índice y mapa de gobernanza de la fase)
        │   ├── ADR/                      (Constitución y Capacidades)
        │   │   ├── ADR_F17_BIS_MASTER.md
        │   │   └── ADR_F17_BIS_01_...
        │   ├── NADR/                     (Normativa Técnica Inmutable)
        │   │   └── NADR_17_BIS_01_...
        │   ├── 00-foundation/            (Evidencia Forense y Auditoría - Fase 0)
        │   ├── plans/                    (Secuencia Operativa y Táctica)
        │   │   └── PHASE_17BIS_EXECUTION_PLAN.md
        │   ├── reports/                  (Métricas, CI, Benchmarks)
        |   ├── reviews/  
        │   |   ├── FASE_{X}_DEFERRED_FINDINGS_REGISTER.md   ← Registro de decisiones + batches
        │       ├── FASE_{X}_EXIT_REVIEW_EVIDENCE_LOG.md     ← Evidencia forense (este documento)
        │       └── DF-{XX}_{NOMBRE}.md                      ← Opcional, para hallazgos muy com
        │   └── handoff/                  (Documentación de transición a Fase 18)
        └── phase-18/
```
*Cada directorio bajo `adr/` funciona como un micro-proyecto independiente, gobernado por la misma metodología.*

---

## 3. Jerarquía y Trazabilidad de Gobernanza

La autoridad fluye estrictamente de arriba hacia abajo. Cada nivel implementa o refina al superior, pero **nunca** lo redefine. Cada tarea de código debe ser trazable hasta su origen arquitectónico.

`ROADMAP` ➔ `ADR MAESTRO` ➔ `ADR DE FASE` ➔ `NADR` ➔ `EXECUTION PLAN` ➔ `IMPLEMENTACIÓN` ➔ `TESTS / CI`

### Responsabilidad de cada Artefacto:
* **Roadmap:** Visión a largo plazo (¿Hacia dónde vamos?). Evolución y grandes hitos.
* **ADR Maestro:** La "constitución" de la fase (¿Por qué existe?). Define capacidades, invariantes y límites. *No contiene tareas*.
* **ADR de Fase:** Evolución de la fase (Auditorías, decisiones). Explica qué llegó a ser la arquitectura, no cómo codificarla.
* **NADR (Normative ADR):** Reglas técnicas obligatorias y restricciones (RFC-2119). *No contiene planificación*.
* **Execution Plan:** Plan táctico (¿Cómo se implementará?). Traduce los NADRs en *Phase Gates*, *Waves* y tareas. Puede evolucionar.
* **Implementación:** Código de producción que materializa el Execution Plan sin contradecir los NADRs.
* **Tests y CI:** Verificación del cumplimiento arquitectónico, normativo y funcional.

---

## 4. Estructura Interna de una Fase

Toda fase respeta la misma organización de directorios para separar responsabilidades:
* **`ADR/`**: Visión y decisiones arquitectónicas. 
* **`NADR/`**: Decisiones técnicas normativas e inmutables. 
* **`00-foundation/`**: Auditorías, evidencia forense y descubrimiento.
* **`plans/`**: Secuenciación operativa (Execution Plans).
* **`reports/`**: Métricas, reportes de benchmark y evidencia de CI.
* **`handoff/`**: Documentos de entrega para transicionar a la siguiente fase.

*💡 **Orden de Lectura Obligatorio:** Roadmap ➔ ADR Master ➔ NADR ➔ Execution Plan ➔ Implementación.*

---

## 5. Principios y Reglas Inquebrantables

La documentación sigue los mismos principios de ingeniería que el código: Fuente Única de Verdad (SSOT), Separación de Responsabilidades y YAGNI.

* **Regla 1:** Un ADR **nunca** define tareas de implementación.
* **Regla 2:** Un NADR **nunca** define planificación operativa.
* **Regla 3:** Un Execution Plan **nunca** altera ni redefine decisiones arquitectónicas.
* **Regla 4:** Los Reportes solo documentan resultados, **no** redefinen arquitectura.
* **Regla 5:** Los Tests verifican el cumplimiento, **no** reemplazan decisiones.
* **Regla 6:** **Cero burocracia.** No se crea un documento de gobernanza a menos que resuelva una ambigüedad real que bloquee la implementación.

---

## 6. Filosofía de Documentación

La documentación arquitectónica existe para habilitar y respaldar la implementación de código robusto, no para maximizar la cantidad de texto. Debe mantenerse:
* Mínima
* Explícita
* Sin duplicación
* Trazable
* Accionable

**Cuando una decisión arquitectónica ha sido implementada y verificada mediante tests, la arquitectura ha cumplido su propósito.**

## 7. Metodología Obligatoria para la escritura de la documentación necesaria a cada gobernanza

- `docs\architecture\1_METHODOLOGY_FOR_ORDERED_PIPELINE_CHANGES.md` ➔ Metodología General para cambios ordenados en el pipeline del Traductor
- `` 
- `docs\architecture\3_METH_ADR_PHASES.md` ➔ Metodología General para la construcción de las Fases en cuestión definida en el ADR_Master.
- `docs\architecture\4_METH_NADR.md` ➔ Plantilla Canónica para el armado de los NADRs de las Fases.
- `docs\architecture\5_METH_EXECUTION_PLAN.md` ➔ Metodología General para la construcción del Plan de Ejecución de una Fase en específico.
- `docs\architecture\6_METH_DEFERRED_FINDINGS_REGISTER_FASE_{X}.md` ➔ Metodología General para el regristro de la auditoría técnica de los DFs/GFs obtenido en la Fase.
- `docs\architecture\6_METH_EXIT_REVIEW_EVIDENCE_LOG_FASE_{X}.md` ➔ Metodología General para la construcción de la evidencia y resultado de los DFs/Gfs obtenidos en la Fase.
- `docs\architecture\7_METH_HANDOFF_FASE_{X}md` ➔ Metodología General para la construcción de los handoff una vez finalizada la implementación de una Fase en particular.