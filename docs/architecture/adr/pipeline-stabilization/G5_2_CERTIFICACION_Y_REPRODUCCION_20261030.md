# G5/2 — Certificación de recuperación y reproducción histórica

**Fecha del gate:** 2026-10-30
**Estado:** PASS en el laboratorio sintético aislado; no constituye habilitación de producción.
**Rama de integración:** `fix/pdf-pdf-pipeline-integration` → PR #26 (Draft, base `pipeline_stabilization`).
**Cierre local del código:** `8d45b4ebd452aabd77902554ea4ac006f46a8f3e` (G5/1), `a45b10a812967583ef0398538d420e8cca8719c1` (tests), `c680d4b6c56a646aaa5dfc1b40f8a5ce73709548` (G5/2).

## Alcance efectivamente certificado

- Preflight: imagen histórica exacta, cinco módulos G5/2 montados en solo lectura, red Docker `internal`, sin puertos publicados, volúmenes dedicados y Tectonic disponible.
- Dos contenedores efímeros ejecutaron el worker real y terminaron mediante `SIGKILL` en dos puntos controlados de `ASSEMBLING` y `COMPILING`. Se acreditó estado durable SQLite/WAL, exit 137 y ausencia de PDF final prematuro.
- `ReconcilerDaemon._sweep_tasks()` recuperó ambas tareas con liderazgo/epoch válidos, invalidó el propietario obsoleto y retornó las FSM a `READY_FOR_ASSEMBLY`; comprobaciones de fencing e idempotencia PASS.
- El assembler real, con `HostTectonicRunner` y caché offline, produjo dos PDF parseables; FSM y tareas finales en `COMPLETED`; preservación del alcance histórico G4 PASS.
- No se utilizaron proveedores LLM reales. G5/2 ejercitó entradas sintéticas; no repitió el recorrido OCR/LLM completo de G4.

La secuencia funcional quedó acreditada en el host con `G5_2_FULL_FOUR_STEP_GATE: PASS`. Su resultado no debe extrapolarse a todos los mecanismos de fallo ni a configuración productiva.

## Evidencia inmutable: conservar fuera de Git

| Archivo (en archivo privado de evidencias) | SHA-256 | Alcance |
|---|---|---|
| `G5_2_HISTORICAL_EVIDENCE_20261030_R4.zip` | `e683c7182c0e7c76c1a82cfcc68d4f3af7cec5781b2739575135890b28ace21e` | 69 entradas: recibos encadenados, cuatro contenedores/logs, SQLite/WAL, PDF, código, caché, scripts, manifiestos y verificación offline |
| `G5_2_RUNTIME_IMAGE_G4_FBF166B.tar` | `ab828d049916cbfc05c6d926d1e6a58be6b13b0a6414fce70ccee578f329a886` | Imagen histórica completa, 7 040 132 608 bytes |

Imagen OCI/Docker identificada por `sha256:b476a8ceedb67a6843bb8673ba9defd87d939d18d09066b0b428882960a0e302` antes de `docker save`. Los hashes anteriores se obtuvieron y verificaron en el Windows del operador. **No se han reabierto estos dos artefactos privados en la revisión de integración.** No añadir TAR, ZIP privados, bases ni PDF de prueba al repositorio ni a artifacts públicos sin sanitización y control de acceso.

## Procedimiento para reproducción futura (no ejecución directa de one-shots históricos)

1. **Custodia e identidad:** obtener copias autorizadas de los dos archivos; calcular SHA-256 y comparar con los valores anteriores **antes** de extraer o cargar. Restringir acceso por posibles secretos o metadatos privados.
2. **Host nuevo:** usar Linux Docker Engine/Compose compatibles; importar el TAR con `docker load`, verificar el ID resultante y la plataforma. Conservar la imagen original sin reconstrucción silenciosa.
3. **Código reproducible:** partir del commit `c680d4b…` o del código exacto/manifest incluido en el ZIP; verificar hashes de los cinco módulos de producción. Nunca utilizar el código G4 de la imagen sin los overlays G5/2: la imagen por sí sola **no incluye** estos fixes.
4. **Namespace nuevo:** crear identificadores nuevos de red `internal`, volúmenes y contenedores; sin puertos publicados, sin egress ni credenciales reales. No reutilizar `g5asm20261030r01` ni nombres de archivos de recibos existentes.
5. **Preparación Tectonic:** copiar los 294 archivos de caché offline, verificando el árbol SHA-256. La inicialización de caché requiere permisos de propietario adecuados; la variante futura para caché vacía del kit pasó pruebas locales, **pero no ha sido certificada en Docker Desktop**. Revisarla y validarla previamente, no ejecutarla automáticamente como si fuera el procedimiento histórico certificado.
6. **Reproducción controlada:** usar `03_REPRODUCCION_FUTURA.md` y `03_CONFIGURACION_EJECUTADA/G5_2_RUNTIME_CONFIG.json` del kit. Revisar, parametrizar para el nuevo namespace y auditar los ejecutores **antes** de lanzar procesos o enviar SIGKILL. No relanzar los scripts históricos one-shot sobre evidencias originales.
7. **Criterios PASS:** dos interrupciones 137 en fases verificadas, dos WAL durables, dos recuperaciones reconciler/epoch/fencing, dos PDF Tectonic válidos, tareas/FSM `COMPLETED`, logs y hashes íntegros, aislamiento y no contaminación de evidencias previas. Capturar recibos y verificar offline un ZIP nuevo con SHA-256 propio.

El ZIP histórico R4 conserva también las revisiones de los ejecutores y las incidencias del congelamiento R1–R4, relevantes para no repetir los defectos de instrumentación.

## Límites y contrato operativo pendiente

- **Error normal de compilación:** `fail_authorized()` coloca la FSM en `FAILED_RETRYABLE` y la tarea en `FAILED`. La ruta automática de ensamblado actualmente reclama `READY_FOR_ASSEMBLY`, mientras que el sweep reconciliador busca tareas `PROCESSING`. Por ello no está demostrado un reintento automático posterior a esa combinación. Tratarla como **intervención operativa requerida** hasta diseñar y verificar una transición explícita; no declarar autoreintento universal.
- **SQLite / filesystem:** `os.replace` ocurre antes del commit de estado. Existe una ventana de crash en la que puede observarse un PDF completo aun sin FSM `COMPLETED`; la reparación puede regenerarlo. El filesystem y las bases WAL no forman una transacción atómica global.
- **Alcance de herramientas:** Ruff `tests` PASS; Pyright `tests` sin errores de tipado, con seis imports no resueltos en el entorno local; no equivale a Pyright de producción PASS. El CI de la rama de integración requiere ejecución propia.
- **Gobernanza:** el PASS de G5/2 es un gate de resiliencia bajo entradas sintéticas. No autoriza despliegue, proveedores reales, promoción de R2 como ruta canónica, limpieza del laboratorio histórico ni merge de PR #26 sin revisión expresa.

## Trazabilidad

G5/0 (reconciler/leases) y G5/1 (Engine real SIGKILL) mantienen sus recibos históricos previos; G4 acredita el PDF→PDF autónomo con proveedor sintético. Este documento añade G5/2, no reemplaza los expedientes G3/G4/G5 anteriores ni altera el Atlas AS-IS. La evidencia definitiva está en los archivos privados con hashes de esta sección, no en este texto narrativo.
