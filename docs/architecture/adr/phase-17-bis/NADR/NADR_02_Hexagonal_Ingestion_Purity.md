# NADR-F17BIS-02: Hexagonal Ingestion Purity

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-02`
* **Título:** Hexagonal Ingestion Purity
* **Clase de Decisión:** `STRUCTURAL`
* **Nivel de Cumplimiento:** `MANDATORY`
* **Versión:** 1.0.0
* **Ciclo de Vida:** `APPROVED` — FROZEN
* **Vigente Desde:** Phase 17-BIS
* **Autoridad:** Architecture Board
* **Responsable Técnico:** Layout Team
* **Capacidad Arquitectónica:** CAP-005 (Hexagonal Physical Abstraction)
* **Evidencia Forense:** `P2-08`, `P2-09`, `E-0.4-326`, `C2-R02`
* **Referencias Cruzadas:**
  * **Depende de:** `ADR_F17_BIS_MASTER` (principio constitucional 7, *Hexagonal Boundary Enforcement*).
  * **Influencia:** `NADR-F17BIS-11` (el enforcement global de fronteras aplica esta frontera concreta), evaluación empírica de motores de extracción (Fase 17).
  * **Conflictúa con:** Toda dependencia concreta del dominio de ingesta respecto a librerías de infraestructura.
  * **Reemplaza a:** N/A

---

## 2. ARCHITECTURE RISK SCORE (Severity: S2)
* **Operacional:** 3 — Portabilidad limitada y acoplamiento operativo a un único motor de extracción.
* **Mantenibilidad:** 5 — Violación hexagonal: el dominio depende físicamente de una librería C/Python de terceros, impidiendo evaluar, testear o sustituir la ingesta de forma aislada.
* **Recuperabilidad:** 2
* **Seguridad:** 2 — Apertura de descriptores de archivo fuera de gestores de contexto en el dominio.
* **Financiero:** 2 — Reduce la capacidad de optimizar costos mediante la selección del proveedor más adecuado al perfil documental.
* **Total Score: 14/25**

---

## 3. CONTEXTO Y EVIDENCIA FORENSE

La auditoría de la Fase 0 (Bloques C2 y P2) identificó que la frontera de ingesta física —el punto donde el documento binario se convierte en representación de dominio— está comprometida por dependencias concretas de infraestructura dentro del espacio de nombres del dominio:

* **`P2-09` / `E-0.4-326` (P1):** `PDFRouter.detect_pdf_type()` importa e invoca directamente la librería C/Python `fitz` (PyMuPDF) desde `core/ast/router.py`, violando la regla de inversión de dependencias de la Arquitectura Hexagonal. Adicionalmente, la clasificación reimplementa la inspección física mediante heurísticas no contractualizadas.
* **`P2-08` (P1):** `apps/bootstrap/pipeline_factory.py` instancia imperativamente un proveedor de extracción concreto (`PyMuPDFProvider`), ignorando la configuración de proveedor predeterminado (`DEFAULT_EXTRACTION_PROVIDER`). Los proveedores alternativos (`DoclingProvider`, `TesseractProvider`) quedan inalcanzables en runtime.

---

## 4. DECISIÓN EJECUTIVA

La organización establece que **la ingesta física de documentos constituye una frontera hexagonal estricta**: ninguna dependencia concreta de infraestructura puede residir en el dominio, y la inspección, clasificación y extracción de documentos **deben** estar gobernadas exclusivamente por abstracciones del dominio, de forma agnóstica al proveedor.

Esta decisión materializa el principio constitucional **Hexagonal Boundary Enforcement** y el principio de ingeniería **Arquitectura Hexagonal (Ports and Adapters)**.

---

## 5. REGLAS NORMATIVAS (RFC 2119)

### 5.1 Pureza del dominio en la ingesta
1. **MUST NOT** existir importaciones ni invocaciones de librerías concretas de infraestructura (lectura física de binarios, motores de terceros) dentro del espacio de nombres del dominio.
2. Toda inspección física del documento **MUST** realizarse a través de puertos definidos por el dominio, implementados exclusivamente en adaptadores de infraestructura.
3. Las decisiones de clasificación y enrutamiento del documento **MUST** depender únicamente de abstracciones del dominio, provistas por los puertos del dominio, nunca del acceso directo al binario del documento.

### 5.2 Ingesta agnóstica de proveedor
4. La selección del proveedor de extracción **MUST** estar gobernada por una política explícita del sistema.
5. **MUST NOT** fijarse imperativamente la selección de un proveedor concreto en el dominio ni en la orquestación.
6. El puerto de extracción **MUST** exponer las capacidades declaradas del proveedor de forma declarativa, de modo que las decisiones del dominio puedan resolverse sin inspección directa del binario.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

* El dominio deviene evaluable y portable de forma aislada, sin dependencias binarias concretas.
* Los proveedores de extracción devienen efectivamente intercambiables, habilitando la evaluación empírica multimodular (Fase 17) y las futuras políticas de selección por perfil documental.
* Las heurísticas de inspección física se trasladan a los adaptadores, donde pueden evolucionar sin afectar al dominio.
* La sustitución o incorporación de nuevos proveedores deja de requerir modificaciones en el dominio.

---

## 7. VERIFICACIÓN Y VALIDACIÓN

* **Verification (estática/mecánica):** Verificación del cumplimiento de la frontera hexagonal definida por este NADR.
* **Validation (dinámica/comportamental):**
  * La selección de proveedor mediante política produce un pipeline operativo con cualquier proveedor compatible.
  * La clasificación del documento se resuelve mediante las capacidades declaradas por el puerto, sin carga del binario en el dominio.

---

## 8. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
| :--- | :--- |
| `ADR_F17_BIS_MASTER` | Materializa el principio constitucional 7 (*Hexagonal Boundary Enforcement*). |
| `ADR_F17_BIS_01` | Este NADR gobierna una de las invariantes cuya remediación exige la Fase 1. |
| `NADR-F17BIS-11` | NADR-11 gobierna el Composition Root y el enforcement global de fronteras; este NADR gobierna específicamente la pureza de la frontera de ingesta. |
| Fase 17 (completada) | La ingesta agnóstica de proveedor es la condición que hace válida la evaluación empírica de motores de extracción. |
| `PHASE_17BIS_EXECUTION_PLAN` | Las tareas `2.2.1` y `2.2.2` materializan estas reglas. |

---

## 9. FRONTERA NORMATIVA (qué NO gobierna este NADR)

* **No gobierna** el Composition Root, el mecanismo de inyección de dependencias ni la inmutabilidad del wiring (responsabilidad de `NADR-F17BIS-11`).
* **No gobierna** el enforcement global de fronteras mediante contratos estáticos sobre la totalidad del repositorio (responsabilidad de `NADR-F17BIS-11`).
* **No gobierna** el tipado estricto de las fronteras de datos entre capas (responsabilidad de `NADR-F17BIS-11`).
* **No gobierna** el cableado de las etapas de maquetación física al pipeline (responsabilidad de `NADR-F17BIS-11`) ni la validación de la maquetación (responsabilidad de `NADR-F17BIS-04`).
* **No gobierna** el contrato de mapeo físico-lógico ni la ontología del AST V2 (Fase 16, congelada).
* **No gobierna** la evaluación de proveedores de extracción ni la selección del motor por defecto (Fase 17, completada y congelada).
* **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---
**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.