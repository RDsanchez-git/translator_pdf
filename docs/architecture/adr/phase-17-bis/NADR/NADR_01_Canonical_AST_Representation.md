# NADR-F17BIS-01: Canonical AST Representation

## 1. METADATA
* **Decision ID:** `NADR-F17BIS-01`
* **Title:** Canonical AST Representation
* **Decision Class:** `DATA` / `STRUCTURAL`
* **Compliance Level:** `MANDATORY`
* **Decision Version:** 1.0.0
* **Lifecycle:** `APPROVED` — FROZEN
* **Effective Since:** Phase 17-BIS
* **Decision Authority:** Architecture Board
* **Technical Owner:** Core Arch / Foundation Domain
* **Related Capability:** CAP-001 (Atomic Persistence & Serialization)
* **Forensic Evidence:** E-0.4-373, GAP-P6-06, E-0.1-014, E-0.2-007
* **Cross References:**
  * **Depends On:** Ninguna (fundacional).
  * **Influences:** `NADR-F17BIS-03` (el hashing semántico consume la representación hidratada), `NADR-F17BIS-10` (los oráculos de regresión se cargan mediante el contrato canónico).
  * **Conflicts With:** Toda ruta paralela de representación, hidratación o interpretación.
  * **Supersedes:** N/A

---

## 2. CONTEXTO

La Fase 16 estabilizó el AST V2 como contrato estructural fundamental del sistema: una secuencia plana, inmutable y tipada de nodos con payloads polimórficos discriminados por ontología. Toda operación downstream —normalización, segmentación, chunking, dispatching, validación, healing, ensamblado, compilación, hashing criptográfico y evaluación topológica— consume esta representación como única fuente de verdad estructural.

La auditoría forense de la Fase 0 (Hitos 0.1, 0.2 y 0.4.4-C4) demostró que el repositorio alberga múltiples rutas de materialización del AST desde representaciones serializadas, cada una con garantías distintas de validación, atomicidad y determinismo. Esta divergencia constituye una violación directa de los principios de inmutabilidad, determinismo y única fuente de verdad establecidos en `ENGINEERING_PRINCIPLES.md`.

---

## 3. PROBLEMA

Se identifican cinco defectos estructurales que invalidan la confiabilidad de la representación del AST:

### 3.1 Deserialización paralela sin validación de dominio
Existe al menos un deserializador que reconstruye nodos mediante desempaquetado manual de diccionarios no tipados, eludiendo la discriminación de payloads y las validaciones de integridad del modelo. Los nodos resultantes pueden poseer payloads incorrectos, campos ausentes o invariantes violadas sin que el sistema lo detecte.

### 3.2 Ausencia de unicidad contractual
No existe un contrato único y obligatorio que gobierne la transformación bidireccional entre la representación en memoria del AST y su forma serializada. Cada consumidor potencial puede implementar su propia ruta de hidratación, generando divergencias silenciosas.

### 3.3 Construcción directa desde datos no tipados
Es posible instanciar nodos del AST directamente a partir de diccionarios crudos sin pasar por el sistema de validación del modelo, permitiendo la inyección de estados inconsistentes que solo se manifiestan como fallos en etapas posteriores del pipeline.

### 3.4 Interpretación directa de la representación serializada
Es posible cargar la representación serializada como datos genéricos y recorrer sus campos sin hidratar el modelo de dominio, eludiendo la totalidad de sus invariantes y produciendo lógica que opera sobre una estructura no verificada.

### 3.5 Riesgo de no-determinismo en la representación serializada
Sin un contrato canónico, dos serializaciones del mismo AST pueden producir bytes diferentes (orden de campos, formato de números, codificación de caracteres), lo que invalida cualquier mecanismo de verificación criptográfica o comparación de snapshots.

---

## 4. DECISIÓN NORMATIVA

Se establece la **unicidad canónica de la representación del AST V2** como invariante arquitectónica del sistema.

Toda transformación entre la representación en memoria del AST y cualquier forma serializada (disco, red, caché, artefacto de benchmark, oráculo de ground truth) **debe** estar gobernada por un único contrato canónico que cubre serialización, deserialización, hidratación, persistencia y verificación de round-trip. No existe excepción.

Esta decisión convierte la representación del AST en una **capacidad arquitectónica protegida**: cualquier modificación incompatible del formato, del mecanismo de validación o de las garantías de atomicidad requiere un nuevo ADR y un mecanismo explícito de migración.

---

## 5. REGLAS OBLIGATORIAS (RFC 2119)

### 5.1 Unicidad canónica
- **MUST** existir exactamente un contrato de representación del AST en todo el repositorio.
- **MUST** toda lectura de AST desde cualquier fuente serializada utilizar exclusivamente dicho contrato.
- **MUST** toda escritura de AST hacia cualquier destino serializado utilizar exclusivamente dicho contrato.
- **MUST NOT** existir implementaciones paralelas, alternativas o auxiliares que produzcan o consuman representaciones serializadas del AST fuera del contrato canónico.

### 5.2 Validación de dominio
- **MUST** toda deserialización pasar por el mecanismo completo de validación del modelo de dominio, incluyendo discriminación de payloads, verificación de invariantes y tipado estricto.
- **MUST NOT** reconstruir nodos del AST mediante desempaquetado de diccionarios no tipados ni mediante construcción directa que eluda las validaciones del modelo.
- **MUST** toda deserialización fallar de forma explícita e inmediata (*fail-fast*) si los datos de entrada no satisfacen las invariantes del modelo.

### 5.3 Prohibición de interpretación directa
- **MUST NOT** existir adaptadores, utilidades, scripts o herramientas que interpreten directamente la representación serializada del AST —incluyendo su carga como datos estructurados genéricos y el recorrido de sus campos— sin hidratarla previamente a través del contrato canónico.
- **MUST** todo consumidor de una representación serializada tratarla como dato opaco hasta su hidratación mediante el contrato canónico.

### 5.4 Determinismo e idempotencia
- **MUST** la serialización ser determinista: ante el mismo AST en memoria, la representación serializada resultante **debe** ser byte-idéntica en toda ejecución.
- **MUST** la deserialización ser idempotente: `deserializar(serializar(ast))` **debe** producir un AST semánticamente idéntico al original.
- **MUST NOT** la serialización depender de estado externo no determinista (reloj, identificador de proceso, orden de inicialización).

### 5.5 Inmutabilidad de la representación
- **MUST** la deserialización producir exclusivamente estructuras inmutables coherentes con el contrato `frozen=True` del AST V2.
- **MUST NOT** la serialización mutar el AST de entrada.

### 5.6 Atomicidad de persistencia
- **MUST** toda escritura de AST a disco garantizar atomicidad a nivel de sistema operativo (escritura intermedia, sincronización física, reemplazo atómico).
- **MUST NOT** existir la posibilidad de un archivo parcialmente escrito tras una interrupción del proceso.

### 5.7 Estabilidad del contrato
- **MUST NOT** modificarse el formato serializado de forma incompatible sin un ADR explícito que documente la migración.
- **SHOULD** el formato serializado incluir información suficiente para detectar incompatibilidades de versión en el momento de la deserialización.

### 5.8 Verificación estática
- **MUST** existir un mecanismo de verificación estática automatizada que detecte y bloquee tanto la construcción directa de nodos AST desde datos no tipados como la interpretación directa de representaciones serializadas fuera del contrato canónico.
- **MUST** dicho mecanismo ejecutarse como parte de la compuerta de integración continua.

### 5.9 Trazabilidad de oráculos
- **MUST** toda lectura de un oráculo serializado (ground truth, snapshot de regresión, fixture de benchmark) utilizar el mismo contrato canónico que la escritura.
- **MUST NOT** existir oráculos serializados cuyo formato no sea reproducible mediante el contrato canónico vigente.

---

## 6. CONSECUENCIAS ARQUITECTÓNICAS

### 6.1 Consecuencias directas
- **Única fuente de verdad representacional:** se elimina toda clase de defectos derivados de hidrataciones divergentes.
- **Validación garantizada:** ningún nodo inconsistente puede ingresar al pipeline desde una fuente serializada.
- **Determinismo criptográfico habilitado:** la estabilidad byte-a-byte de la representación es precondición para hashing reproducible, fingerprints de regresión y sellado de ground truth.
- **Atomicidad de persistencia:** la escritura segura protege contra corrupción en escenarios de fallo de proceso o corte de energía.
- **Verificabilidad de round-trip:** un único contrato permite pruebas exhaustivas de bidireccionalidad sobre el corpus de fixtures.

### 6.2 Implicaciones del contrato canónico
La adopción de un contrato canónico implica que:
- toda evolución incompatible requiere un proceso formal de gobernanza (nuevo ADR y mecanismo de migración);
- los consumidores existentes deberán alinearse con el contrato vigente;
- las herramientas auxiliares (evaluación, experimentos, scripts) quedan sujetas a las mismas reglas del dominio.

---

## 7. RELACIÓN CON OTROS ARTEFACTOS

| Artefacto | Relación |
|---|---|
| `ADR_F17_BIS_MASTER` (FROZEN) | Este NADR materializa la capacidad CAP-001 definida por el ADR Maestro. No lo modifica. |
| `ADR_F17_BIS_01` (Production Pipeline Alignment) | Este NADR gobierna una de las invariantes que la Fase 1 debe garantizar. |
| `NADR-F17BIS-03` (Semantic Hashing) | **Depende de este NADR:** el hashing semántico requiere una representación determinista como precondición. NADR-03 gobierna la fórmula del hash; NADR-01 gobierna la estabilidad de la representación sobre la que opera. |
| `NADR-F17BIS-10` (Regression Gates) | **Depende de este NADR:** los oráculos de regresión deben cargarse mediante el contrato canónico para que la comparación sea válida. |
| `ENGINEERING_PRINCIPLES.md` | Implementa los principios de inmutabilidad estricta, determinismo, fail-fast y única fuente de verdad. |
| `PHASE_17BIS_EXECUTION_PLAN` | La materialización operativa de este NADR se ejecuta a través de sus tareas. El plan prescribe qué consumidores migrar y qué mecanismo de verificación implementar; este NADR no prescribe esas decisiones operativas ni su Definition of Done. |

---

## 8. FRONTERA NORMATIVA (qué NO gobierna este NADR)

- **No gobierna** la fórmula de cálculo de hashes criptográficos sobre el AST (responsabilidad de NADR-03).
- **No gobierna** la ubicación física de los archivos serializados ni la estructura de directorios (responsabilidad del Execution Plan y la infraestructura).
- **No gobierna** la tecnología concreta de serialización (responsabilidad de implementación).
- **No gobierna** el contenido semántico del AST ni sus invariantes de dominio (responsabilidad del modelo AST V2 de Fase 16, congelado).
- **No prescribe** tareas de implementación ni Definition of Done (responsabilidad del Execution Plan).

---

**Nota de Gobernanza:** Este documento define exclusivamente reglas normativas obligatorias. Toda implementación que pretenda materializar esta decisión deberá demostrar trazabilidad explícita hacia este NADR mediante el Execution Plan correspondiente.