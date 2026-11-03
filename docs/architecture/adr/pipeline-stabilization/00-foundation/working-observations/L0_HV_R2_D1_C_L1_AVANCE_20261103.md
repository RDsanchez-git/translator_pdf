# L0/HV — avance documentado sobre D1 y C/L1 R2

**Fecha:** 2026-11-03. **Estado:** IN_PROGRESS. **Modalidad:** nota de observación, no acta normativa ni cierre de L0/Atlas. **Imagen R2:** sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd. **HEAD probado:** d4cda2c379c0efd93a70e795d31c37a0ede7a192.

## Sujetos que no deben confundirse

- **D1/HV:** proyecto i0hv49cde367de; cinco contenedores inicialmente creados/detenidos y seis volúmenes con nombres fijos; pruebas de configuración, fake/SDK, red pública TCP IPv4/IPv6 y bind RO de referencia. No se ejecutó PDF del corpus en D1.
- **C/L1:** proyecto i0l19cf15cac6b12, RUN-ID 9cf15cac6b12, seis volúmenes nuevos por RUN-ID y red interna propia. Preflight, siembra offline P0, bootstrap P1, OCR P2, Engine/fake P3, Assembler P4 y exportación P5 autorizados/ejecutados por fases. **No** equivale al despliegue concurrente AS-IS.
- **R1 y R3:** aún sin caracterización L0/L1 equivalente. No trasladarles resultados de D1/C/L1.

## Reconciliación de los dieciséis controles

Estados: **ACOTADO** significa evidencia positiva solo en el perímetro citado; **PARCIAL** requiere pruebas o decisiones adicionales; **PENDIENTE** no ejecutado; **AVANCE** evidencia nueva que no sustituye el corte histórico de D1.

| Control | Evidencia D1 más delta C/L1 | Estado integral |
|---|---|---|
| HV-01 Código/imagen | HEAD e imagen ID verificados; Compose C/L1 asociado al run. | ACOTADO a R2 y HEAD fijado. |
| HV-02 Build/ejecutables | Imagen reutilizada sin build ni pull; Tectonic se ejecutó en P4. Cold builds no ensayados. | PARCIAL. |
| HV-03 Secretos | Variables efectivas inspeccionadas en C/L1; key dummy worker/fake, endpoint interno, sin proxies declarados. Sin divulgar valores. | ACOTADO, no auditoría general del host. |
| HV-04 Mounts | Cinco servicios y seis volúmenes; fake con bind RO; sin bind imprevisto. Los cuatro rootfs restantes eran RW. | ACOTADO. |
| HV-05 Rutas/estado fresco | D1 conserva defecto de nombres globales fijos; C/L1 usa RUN-ID; P0 verificó semillas frescas sin importar DB/AST histórico. | AVANCE C/L1. |
| HV-06 Red/puertos | Red internal y puertos no publicados; fake y Engine se comunicaron internamente en P3. | ACOTADO. |
| HV-07 Egress | TCP público IPv4/IPv6 bloqueado por sonda tanto en D1 como en red C/L1. | ACOTADO; no todos los protocolos/servicios. |
| HV-08 SDK/endpoint | Contrato SDK-fake focal D1 y endpoint/flujo real Engine-fake C/L1 verificados. | ACOTADO. |
| HV-09 Contrato fake | Fixture y manifiesto vinculados; P3 tuvo 3 unidades translate, respuestas almacenadas. | ACOTADO. |
| HV-10 Inmutabilidad | En D1 bind RO rechazó escritura; C/L1 no montó checkout original como RW. | ACOTADO. |
| HV-11 Reversibilidad | Objetos C/L1 identificables por RUN-ID, pero no se probó desmontaje; no borrar laboratorios. | PENDIENTE. |
| HV-12 Procedencia | Recibos P0–P5, hashes input/output, cinco snapshots SQLite y ZIP P5 verificado. | AVANCE; IDs de Evidence Log pendientes del Board. |
| HV-13 Cobertura | Cinco servicios R2 de esta ruta; reconciler no desplegado en la variante. | PARCIAL frente a AS-IS general. |
| HV-14 Comparabilidad | Deltas instrumentales: red/volúmenes RUN-ID, fake interno, swap deshabilitado y fases. | PARCIAL: no concurrencia original. |
| HV-15 Backup SQLite | Exportación P5 de cinco snapshots con 5/5 integrity_check correcto. | ACOTADO al estado final detenido. |
| HV-16 Autoridad/recursos | Autorizaciones owner para P0–P5 y fases; controles de memoria/disco. Charter permanece DRAFT y decisiones D-1…D-7 pendientes. | PARCIAL en gobernanza formal. |

## Recursos y límites

- Host Windows ~31,83 GiB RAM física; Docker 11,68 GiB asignados. Última cifra comunicada de espacio libre en C: 28,83 GiB tras P5. No se hicieron builds, pulls, prune ni eliminaciones de laboratorios.
- P0 verificó 45.563.084 bytes de PDF/cachés permitidos; P1 inicializó cuatro bases SQLite. P2/P3/P4/P5 ejecutaron operaciones sobre los objetos C/L1 existentes.
- P2 V1 y P5 V1/V2 fallaron por instrumentos de verificación: no confundir esos STOP con falla del producto. P2 V2 y P5 V3 completaron sus operaciones sin reprocesamiento de pasos anteriores.
- El umbral preventivo de 20 GiB y los presupuestos incrementales proceden del protocolo operativo local, **no** del Charter.

**Dictamen de avance:** controles focales suficientes para contextualizar este testigo R2 escalonado, pero **no** 16 PASS universales, ni elegibilidad de R1/R3, ni autorización de borrar recursos. Las preguntas abiertas siguen en el Atlas IN_PROGRESS. Consultar la nota E2E-0 R2 del mismo directorio para los checkpoints.
