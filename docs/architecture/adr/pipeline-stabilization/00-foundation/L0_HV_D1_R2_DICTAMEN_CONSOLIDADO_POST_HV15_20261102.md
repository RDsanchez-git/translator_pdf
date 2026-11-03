# L0/HV — Dictamen de reconciliación tras HV-15 (D1/R2)

**Corte de evidencias:** 2026-11-02 (hora local del owner, America/Argentina/Cordoba).  
**Tipo:** acta de reconciliación de resultados informados por el owner; no es aprobación del Board, certificación del producto, cambio del Charter/Atlas ni autorización para ejecutar L1.  
**Sujeto:** **B — Harness Verification** D1/R2, proyecto Docker `i0hv49cde367de`, distinto del histórico D2-12 y de una futura variante C/L1.

## 1. Identidad y hechos dinámicos observados

- HEAD de código designado: `d4cda2c379c0efd93a70e795d31c37a0ede7a192`; árbol `f2a635ef8822780698066a288e46607c8b671938`.
- Imagen local comprobada por etiqueta↔ID: `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`.
- Compose D1 `sha256:e3f8cbee35c5cdabd6b27609346e23a804b75706bfe7bac284ce50acfa555156`; overlay swap-off `sha256:b22378b9c2f98e7f5cf7b2ab130448da259845f59258f9bc9bc13534226f9e95`; fake G3-C `sha256:6d003daf9a44a36b8c12e2b7ad4f33edd3a8470221e42c38bae4e97fdc0b53a5`.
- `D1_PACKAGE_INTEGRITY`, `D1_COMPOSE_CONFIG_STATIC`, `D1_PHASED_CONFIG_STATIC`: **PASS** según consola local.
- `C_HV_CREATE_VERDICT`: **PASS_NOT_STARTED**: 5 contenedores en `created`, 0 `running`, 6 volúmenes nuevos etiquetados, una red interna. `C_HV_OBJECT_INSPECTION`: **PASS** para los campos inspeccionados; rootfs R/W en 4 servicios y R/O en fake.
- `D1_HV07_HV10_PROBE`: **PASS_LIMITED** en una sonda temporal de la red D1: denegación de TCP público IPv4/IPv6 y escritura a bind R/O; hash del archivo anfitrión sin cambios.
- `HV03_NAME_RECONCILIATION`: **PASS** tras corregir dos errores del instrumento, y comprobación anterior de hash del token ficticio en worker/fake. No se detectaron otros nombres sensibles por la expresión revisada. No equivale a revisar secretos en todas las capas de la imagen.
- `HV02_TECTONIC_EXECUTABLE`: **PASS_LIMITED**, versión 0.15.0, binario `/usr/local/bin/tectonic` SHA-256 `f0b36e78c13dd75b821984830533f872c9a12c62957e51357bc16e65cdb71013`; no se compiló PDF ni se reprodujo un build.
- **Nuevo:** `HV15_BACKUP_METHOD`: **PASS_LIMITED**: SQLite sintético con WAL existente, backup mediante API, lectura desde conexión independiente, `integrity_check=ok` y eliminación de temporales. No se capturaron DBs reales de R2 ni una instantánea global de varios SQLite.
- Recursos vistos por owner antes de esta acta: Windows **31,83 GiB RAM total** y **16,25 GiB disponibles**; Docker **11,68 GiB**; unidad C: ~**29,34 GiB libres**. Son mediciones puntuales, no consumos durante OCR. No se ejecutaron builds, pulls ni E2E-0.

## 2. Estado por control HV-01…HV-16

| Control | Dictamen de esta reconciliación | Alcance / precondición restante |
|---|---|---|
| **HV-01** Código y procedencia | **PARCIAL** | HEAD/imagen identificados; falta reconciliación final del fingerprint de una variante C/L1 y del snapshot de código si procede. |
| **HV-02** Build y Tectonic | **PASS_LIMITED** | Tectonic ejecutable acreditado; build bitwise/reproducible y compilación con recursos offline **no** acreditados. |
| **HV-03** Secretos | **PASS_LIMITED** | Entorno efectivo de contenedores creados y token ficticio; no escaneo exhaustivo de capas ni credenciales fuera de los campos inspeccionados. |
| **HV-04** Mounts | **PASS_LIMITED** | Montajes reales de 5 objetos creados sin binds inesperados; confirmar montaje final C antes de escribir. |
| **HV-05** DB, estado y rutas | **PENDIENTE — DEFECTO CONOCIDO DE DISEÑO D1** | Los 6 volúmenes del B actual tienen nombres globales fijos sin RUN-ID. No reutilizar el Compose para crear un segundo proyecto; futuro C con volúmenes propios y estado vacío. |
| **HV-06** Red y puertos | **PASS_LIMITED** | Única red interna, IPv6 deshabilitado, 0 puertos publicados, inspección de objetos detenidos. |
| **HV-07** Egress | **PASS_LIMITED** | TCP público IPv4/IPv6 denegado desde sonda en red D1; no equivale a auditoría completa de protocolos/procesos. |
| **HV-08** SDK/endpoints | **PASS_LIMITED** | SDK Groq 1.4.0 y URL root fake previamente probados; worker D1 aún no ejecutado. |
| **HV-09** Contrato fake | **PASS_LIMITED** | Contrato temporal SDK→fake 2/2 y script G3-C por hash; no fake integrado del stack completo. |
| **HV-10** Inmutabilidad | **PASS_LIMITED** | Bind R/O de referencia en sonda, sin prueba sobre checkout original (que no se monta). 4 rootfs funcionales son R/W. |
| **HV-11** Reversibilidad | **PENDIENTE** | Inventario y etiquetas observados, procedimiento selectivo definido; retiro no ejecutado ni autorizado. |
| **HV-12** Procedencia | **PARCIAL** | Hashes/config/transcripciones conocidos; el expediente de L1 requerirá RUN-ID, UTC, comandos, resultados y hashes de evidencia, sin secretos. |
| **HV-13** Cobertura | **PARCIAL JUSTIFICADO** | 5 servicios para R2 nominal; reconciler/sweeper no incluidos: recuperación/faults/concurrencia fuera de cobertura. |
| **HV-14** Comparabilidad | **PARCIAL** | Deltas históricos→D1 documentados; C/L1 escalonado necesita fingerprint específico. Phased ≠ AS-IS concurrente. |
| **HV-15** Snapshots | **PASS_LIMITED** | Método SQLite WAL verificado en base sintética; respaldos reales por DB y coherencia inter-DB pendientes de ejecución controlada. |
| **HV-16** Autoridad | **PARCIAL — DECISIÓN PENDIENTE** | Owner validó **propuesta técnica** PDF/R2 phased, no aprobó automáticamente Charter DRAFT, Board D1–D7 ni inicio de L1. |

`PASS_LIMITED` **no** significa cierre integral del control; el alcance descrito es parte obligatoria del veredicto.

## 3. Dictamen L0/etapas y bloqueo operativo

**Variante B/D1 actual: `L0_ELEGIBILITY = UNKNOWN / HOLD_PRECONDITIONS` respecto de habilitar L1.** No existe base para declarar `ELIGIBLE` integral y tampoco corresponde atribuir fallo de producto. La composición B es una instancia de HV ya creada, no el sujeto C autorizado para ejecutar E2E-0. Los cinco contenedores siguen **detenidos** y deben permanecer así. Para una eventual corrida C, el D1 B tal como está tiene precondiciones conocidas no satisfechas (nombres fijos, falta de seed, falta de autoridad de lanzamiento). 

- **Etapa A:** COMPLETADA (preflight de lectura y reconciliación).
- **Etapa B:** pruebas focalizadas completadas con `PASS_LIMITED`; garantías de configuración C requieren nueva revisión.
- **Etapa C:** Compose D1 validado, objetos Docker creados e inspeccionados **sin arranque**; verificación multiservicio funcional no ejecutada.
- **Etapa D:** dictamen provisional de HOLD/UNKNOWN consignado; `ELIGIBLE` **no adjudicado**.
- **L1/E2E-0:** **NO EJECUTADO**, `execution_outcome=null`, CP-00…CP-12 `NOT_OBSERVED`; ninguna clase A/B/C.

## 4. Decisiones ya tomadas y próximos pasos mínimos

**Decisión técnica ya validada por el owner:** candidato de preregistro `tests/corpus/canonical/pdf/doc_01_single.pdf` (v3.9, 3 páginas, `heavy_math`, SHA-256 `2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3`), ruta R2 OCR→Engine→Assembler **escalonada**, proveedor determinista G3-C, sin proveedor real, sin build/pull, separación de veredicto físico/científico. **No pedir otra vez validar esta misma propuesta.**

1. **Formalizar autoridad del ensayo** según Charter/Board, incluyendo aceptar que `phased` es variante instrumental y no equivalencia de concurrencia AS-IS. La aceptación técnica del PDF ya consta, pero no sustituye la decisión formal aplicable.
2. **Diseñar la composición C/L1 separada** mediante curaduría estática: sin los seis `volumes.*.name` fijos de B, RUN-ID, fresh DB/AST/output, montaje y UID/GID consistentes con G4, `pull_policy: never` y red interna. **No** crear ni iniciar objetos C todavía; verificar que no referencia ni escribe los seis volúmenes B/históricos.
3. **Planificar el seed offline mínimo autorizado:** solo copia del PDF seleccionado y cachés tiktoken/Tectonic (~45,6 MB entre ambos recursos y PDF) verificados por hash; jamás AST/SQLite/PDF final históricos. El bootstrap G4 no acepta volúmenes vacíos.
4. **Cerrar presupuesto operacional antes de escribir:** medir RAM Docker y C: justo antes de C; conservar STOP preventivo de 20 GiB libres, plan de observación de RAM, disponibilidad de espacio y stop quiescente por checkpoint. El umbral no es cuota dura de Docker. No sustituir RAM real con swap. No copiar gigabytes ni reconstruir imagen.
5. **Solo con autorización específica de arranque y L0 satisfecho para C:** preparar P0/P1…P5 y capturar CP-00…CP-12, snapshots SQLite por backup API y hashes de salida, sin cambios del criterio post hoc.

**Acción inmediata sin costo de Docker:** registrar este dictamen y preparar únicamente el **diseño estático C** para revisión de autoridad y presupuesto. No ejecutar más sondas genéricas, `compose create`, `up`, `run`, limpiezas ni scripts G4 sobre el proyecto B existente.

## 5. Trazabilidad

- Salidas proporcionadas por el owner durante el diálogo hasta `HV15_BACKUP_METHOD: PASS_LIMITED` (2026-11-02).
- `L0_HV_D1_R2_MATRIZ_RECONCILIACION_HV01_HV16_20261102.md` y `L0_HV_D1_R2_DECISION_GATE_ESTATICO_Y_PREREGISTRO_CANDIDATO_20261102.md`; `E2E0_R2_PREREGISTRO_OPERATIVO_PROPUESTA_TECNICA_VALIDADA_20261102.md`.
- Repositorio `RDsanchez-git/translator_pdf` commit `d4cda2c…`: `PIPELINE_STABILIZATION_AUDIT_CHARTER.md` v0.1.0 DRAFT, `PRODUCTION_PIPELINE_EXECUTION_ATLAS.md` v0.2.15 §9, `L0_AUDIT_SANDBOX_DESIGN_AND_VERIFICATION_SPEC_DRAFT.md` HV-01…HV-16.
