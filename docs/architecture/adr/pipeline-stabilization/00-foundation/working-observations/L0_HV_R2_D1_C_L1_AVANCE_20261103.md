# Nota de trabajo — avance L0/HV R2 (D1 y C/L1)

**Corte:** 2026-11-03 · **Estado:** `IN_PROGRESS` · **Naturaleza:** evidencia dinámica complementaria, **no** certificación integral L0 ni sustitución del Atlas/Charter. No hay folio `E-*` oficial asignado.  
**Código de ejecución:** `d4cda2c379c0efd93a70e795d31c37a0ede7a192` · **Imagen local:** `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`.

## 1. Sujetos distintos, sin herencia automática

- **D1/HV (observación instrumental inicial):** proyecto `i0hv49cde367de`, cinco contenedores `created`, seis volúmenes con nombres globales fijos, red interna, sonda pública TCP IPv4/IPv6 y bind de referencia RO. Se documentaron límites y defectos en `L0_HV_D1_R2_MATRIZ_RECONCILIACION_HV01_HV16_20261102.md` (expediente local del owner). No hubo ejecución PDF→PDF de D1.
- **C/L1 R2 (testigo escalonado):** proyecto `i0l19cf15cac6b12`, RUN-ID `9cf15cac6b12`, seis volúmenes por RUN-ID, red privada `i0l19cf15cac6b12_internal`; P0 creó/sembró recursos, P1 inicializó SQLite, P2 ejecutó OCR, P3 Engine y fake, P4 Assembler y P5 exportó evidencia. Es una **variante instrumentada por fases**, distinta de D1 y del despliegue concurrente AS-IS.
- **No evaluado aquí:** rutas R1 y R3, concurrencia R2 AS-IS, uso de proveedor real, recuperación ante fallos y testigos L2 de garantía FROZEN.

## 2. Reconciliación HV-01…HV-16 — alcance honesto

`ACOTADO` = control avalado solo por la modalidad concreta; `PARCIAL` = prueba o requisito no satisfecho íntegramente; `PENDIENTE` = no ejercitado; `AVANCE` = evidencia posterior adicional sin redefinir resultados históricos.

| HV | Control del borrador L0 | Evidencia D1 y delta de C/L1 | Estado de la garantía integral |
|---|---|---|---|
| HV-01 | Código e imagen | HEAD de ejecución, ID de imagen y Compose C/L1 verificados en preflights; el Atlas mantiene baseline histórica distinta. | ACOTADO a R2/HEAD `d4cda2`. |
| HV-02 | Build/ejecutables | Imagen R2 local reutilizada sin build/pull; Tectonic se ejecutó efectivamente en P4. Cold builds y reproducibilidad de suministro no probados. | PARCIAL. |
| HV-03 | Secretos | Variables efectivas de cinco contenedores inspeccionadas sin revelar valores; `GROQ_API_KEY` dummy en worker/fake, endpoint interno y sin proxy declarado. | ACOTADO; no auditoría exhaustiva del host/imagen. |
| HV-04 | Montajes | Cinco servicios y seis volúmenes comprobados; fake con bind RO, sin binds inesperados. Cuatro rootfs de servicios no son RO. | ACOTADO. |
| HV-05 | Rutas y estado fresco | D1 tenía nombres globales fijos; C/L1 introdujo nombres por RUN-ID, 45.563.084 bytes de seeds verificados y bases nuevas sin estado histórico. | AVANCE C/L1; no valida limpieza/repetibilidad universal. |
| HV-06 | Red y puertos | Red interna sin publicación de puertos; C/L1 validó identidad `internal` e IPv6 desactivado. Fake y Engine se comunicaron internamente durante P3. | ACOTADO. |
| HV-07 | Egress | Sondas públicas TCP IPv4/IPv6 denegadas en D1 **y de nuevo en la red C/L1**. | ACOTADO; no certifica todos los protocolos/procesos. |
| HV-08 | SDK/endpoint | SDK Groq 1.4.0 ensayado en D1; C/L1 acreditó `GROQ_BASE_URL` del worker y comunicación efectiva con fake. | ACOTADO. |
| HV-09 | Contrato fake | D1 probó solicitudes de sonda; C/L1 verificó fixture/identidad de manifiesto y persistió 3 respuestas `translate` de fake. | ACOTADO a ese fixture/manifiesto. |
| HV-10 | Inmutabilidad de referencia | Bind RO de referencia D1 rechazó escritura; en C/L1 no se montó checkout original para escritura. | ACOTADO; no se ensayó inmutabilidad general. |
| HV-11 | Reversibilidad | Recursos C/L1 identificables por RUN-ID; no se ejecutó desmontaje ni limpieza de los laboratorios. | PENDIENTE. |
| HV-12 | Procedencia | Recibos enlazados P0–P5, hashes de entrada/salida, cinco backups SQLite consistentes, ZIP P5 verificable. | AVANCE sustancial; registro formal con ID no emitido. |
| HV-13 | Cobertura de servicios | Cinco servicios del R2 instrumentado; `reconciler` no integrado en esta corrida. | PARCIAL respecto de cobertura AS-IS. |
| HV-14 | Comparabilidad | Overlay sin swap, fake interno, recursos por RUN-ID y secuencia P0–P5 documentados; no equivalente a concurrencia de producción. | PARCIAL. |
| HV-15 | Snapshot SQLite | P5 exportó 5 snapshots; los 5 pasaron `PRAGMA integrity_check` independiente. | ACOTADO al estado final detenido. |
| HV-16 | Autoridad/límites | Owner autorizó fases/sondas y variante escalonada en conversación; disco ≥~28 GiB durante la serie, Docker RAM 11,68 GiB, sin proveedor real. Charter sigue `DRAFT`, D-1…D-7 pendientes. | PARCIAL en gobernanza formal. |

## 3. Hechos instrumentales y límites

- P0: cinco contenedores detenidos, seis volúmenes exclusivos y semillas G4 verificadas; **sin** copiar AST, SQLite o PDF de salida históricos. P1: cuatro planos SQLite inicializados. P2: OCR produjo 61 nodos y cinco unidades (tres `translate`, dos `preserve`). P3: cinco tareas `COMPLETED`, 61 proyecciones y `READY_FOR_ASSEMBLY`. P4: PDF físico de 20.900 bytes y cuatro páginas con FSM `COMPLETED`. P5 V3: ZIP de 596.525 bytes, cinco snapshots SQLite y no reinicio de servicios.
- Sondas del perímetro C/L1: red interna, TCP público IPv4 e IPv6 denegados, credenciales ficticias y ausencia de proxies activos declarados. Estas observaciones no agotan la superficie de seguridad.
- Los errores instrumentales P2 V1 (precheck RO) y P5 V1/V2 (verificación SQLite/Windows) se documentan como incidencias del arnés, **no** defectos R2 del procesamiento; P2 V2 y P5 V3 pasaron. No se autoriza repetir una fase por su éxito ni borrar estado.
- Política de recursos mantenida: imagen existente, sin builds/pulls/export TAR, sin `prune`/`down -v`, STOP operativo ante C: <20 GiB o presión de recursos; estos umbrales no proceden del Charter. Última medición P5: **28,83 GiB libres** en C:. La imagen no tiene cuota global de crecimiento garantizada para volúmenes.

## 4. Estado y continuaciones

**L0/HV:** suficiente evidencia focal de infraestructura para **este testigo R2 escalonado ya ejecutado**, pero **no** 16 PASS integrales ni declaración normativa de elegibilidad para R1/R3 o AS-IS concurrente. El cierre metodológico del Atlas continúa `IN_PROGRESS`.

**Siguiente:** comparar R1 y R3 con baseline/criterios explícitos; conservar `UNKNOWN` en controles no probados; retomar L2 para localizar causas científicas y garantías de recuperación/fencing. No seleccionar ruta canónica ni modificar Charter/Atlas histórico por inferencia.