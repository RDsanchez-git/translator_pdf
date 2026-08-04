# NADR-F17BIS-05: Real Context Resolution

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-05`
* **Título:** Real Context Resolution
* **Clase de Decisión:** `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Runtime Team
* **Capacidad Arquitectónica:** CAP-008 (Unified Execution Plane)
* **Evidencia Forense:** `OBS-P1-04`, `P4-05`
* **Referencias Cruzadas:**
  * **Depende de:** `NADR-F17BIS-11` (exclusividad e inmutabilidad de la Composition Root).
  * **Influencia:** `NADR-F17BIS-08` (el plano de ejecución distribuido debe operar la resolución de contexto en ambos modos).
  * **Conflictúa con:** Toda inyección de resolución de contexto nula o provisional en el pipeline de producción.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Operacional:** 4 — Traducciones desprovistas de contexto jerárquico degradan la fidelidad estructural del documento final.
* **Mantenibilidad:** 3 — Conectores provisionales generan deuda técnica oculta y dificultan el diagnóstico.
* **Recuperabilidad:** 3 — Entradas de materialización contaminadas requieren intervención para restaurar su confiabilidad.
* **Seguridad:** 1
* **Financiero:** 3 — La invalidación de la materialización fuerza re-inferencias, incrementando el costo FinOps.
* **Total Score: 14/25**

---

## 3. DECISIÓN EJECUTIVA

**El contexto forma parte de la identidad arquitectónica de una traducción.**

Existe un único mecanismo canónico de resolución de contexto jerárquico, obligatorio para toda ejecución productiva.

Toda materialización derivada de dicho contexto deberá preservar esa identidad durante su persistencia y reutilización.

---

## 4. CONTEXTO Y EVIDENCIA FORENSE

### 4.1 Problema arquitectónico

El pipeline de producción presenta una brecha estructural en la capacidad de resolución de contexto jerárquico. Los prompts de inferencia requieren contexto jerárquico (títulos de sección, posición espacial, migas documentales) para producir traducciones que respeten la estructura del documento. No obstante, el cableado de producción inyecta una resolución de contexto nula que retorna información contextual vacía, de modo que las traducciones se generan sin contexto y —críticamente— se persisten en la materialización con claves que no reflejan la ausencia de contexto.

Esto produce dos fallos que se retroalimentan:
1. Las traducciones carecen del contexto jerárquico necesario para la fidelidad estructural.
2. La materialización se contamina: entradas descontextualizadas se almacenan y se sirven en ejecuciones posteriores, incluso si se inyecta un mecanismo real más adelante.

### 4.2 Manifestación concreta identificada por la auditoría

* **`OBS-P1-04` / `P4-05`:** El CLI de producción inyecta un mecanismo de resolución de contexto nulo (etiquetado como TODO provisional) que retorna información contextual vacía en todas las llamadas de resolución. Este componente provisional está cableado en la ruta de ejecución productiva.
* **Impacto:** Si se procesa un documento con la materialización habilitada utilizando el mecanismo nulo, la respuesta del LLM traducida sin contexto jerárquico se persiste. En ejecuciones posteriores con un mecanismo real, el sistema devuelve un acierto de materialización que contiene una traducción degradada por falta de contexto.

### 4.3 Capacidad canónica existente

El dominio ya define una capacidad canónica de resolución de contexto: un contrato de resolución con soporte de resolución individual y por lotes, junto a un proveedor de mapeos contextuales y una implementación en memoria, además de un enriquecedor de contexto jerárquico. Estos componentes existen y están cubiertos por pruebas, pero no están cableados en la ruta productiva. El mecanismo nulo los bypassea.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Resolución de contexto real
1. La resolución de contexto jerárquico **MUST** ser una capacidad real en todo punto de inyección del pipeline de producción.
2. **MUST NOT** inyectarse resolución de contexto nula, provisional o de marcador de posición en la ruta de ejecución productiva.
3. Si el mecanismo de resolución de contexto falla o no está disponible, el sistema **MUST** fallar de forma explícita (*fail-fast*) en lugar de degradar silenciosamente a una traducción descontextualizada.

### 5.2 Identidad contextual en la materialización
4. Toda entrada persistida derivada de una resolución de contexto **MUST** estar vinculada de forma determinista a la identidad del contexto bajo el cual se generó.
5. Las claves de materialización **MUST** incorporar la identidad del contexto, de modo que las entradas generadas bajo contextos distintos sean distinguibles y no puedan colisionar.
6. **MUST NOT** persistirse entradas generadas sin información contextual consistente con la jerarquía documental.

### 5.3 Inyección y composición
7. El mecanismo canónico de resolución de contexto **MUST** ser inyectado exclusivamente por la Composition Root.
8. La resolución de contexto **MUST** operar de forma idéntica en todos los modos de ejecución.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* Las traducciones recuperan la información contextual consistente con la jerarquía documental, mejorando la fidelidad estructural del documento final.
* La materialización deviene confiable: las entradas quedan vinculadas a identidad contextual real, eliminando la contaminación.
* Los conectores provisionales se retiran de la ruta productiva, reduciendo la deuda técnica oculta.
* La capacidad canónica de resolución de contexto existente se activa en producción.
* Las entradas persistidas bajo la estrategia anterior dejan de ser compatibles con el nuevo modelo de identidad contextual.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):**
  * Verificación de que el cableado productivo inyecta un mecanismo real de resolución de contexto, no nulo ni provisional.
  * Verificación de que las claves de materialización incorporan la identidad del contexto.
* **Validation (dinámica/comportamental):**
  * Una unidad de traducción **MUST** generarse con información contextual consistente con la jerarquía documental.
  * Una entrada generada bajo un contexto A **MUST** ser distinguible en la materialización de una entrada generada bajo un contexto B.
  * Si el contexto no puede resolverse, el sistema **MUST** fallar de forma explícita.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio de cero fallos silenciosos y determinismo aplicado a la resolución de contexto. |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-11` | **Dependencia directa:** la inyección del mecanismo real de resolución de contexto es responsabilidad de la Composition Root. |
| `NADR-F17BIS-08` | **Influencia:** la resolución de contexto debe operar en ambos modos de ejecución (CLI y daemon). |
| `PHASE_17BIS_EXECUTION_PLAN` | La tarea `3.1.1` materializa estas reglas. La operación de saneamiento de las entradas incompatibles se rige por el Runbook de despliegue. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** la implementación interna del mecanismo de resolución de contexto (en memoria, respaldado por base de datos, etc.).
* **No gobierna** el algoritmo del enriquecedor jerárquico para el cálculo de la información contextual.
* **No gobierna** el mecanismo físico de almacenamiento de la materialización.
* **No gobierna** la Composition Root ni el mecanismo de inyección inmutable en sí mismo (responsabilidad de `NADR-F17BIS-11`).
* **No gobierna** la ontología del AST V2 ni los payloads (Fase 16, congelada).
* **No prescribe** tareas de implementación, procedimientos de saneamiento ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.