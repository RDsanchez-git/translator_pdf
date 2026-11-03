# Nota de trabajo — observación E2E-0 R2 escalonado, no cierre del Atlas

**Corte:** 2026-11-03 · **Estado:** `OBSERVED-DYNAMIC` acotado / investigación `IN_PROGRESS`.  
**RUN-ID:** `9cf15cac6b12` · **Proyecto:** `i0l19cf15cac6b12`.  
**Commit del código:** `d4cda2c379c0efd93a70e795d31c37a0ede7a192` · **imagen:** `sha256:abe5b5dbbc65e8920e0948b189bd9bd090eb395e99420918190128a2ec12b4bd`.  
**Modalidad:** P0–P5 secuencial e instrumentada, no prueba del despliegue concurrente R2 AS-IS. Fake Groq interno y determinista; no inferencia de proveedor real.  
**Autoridad:** autorizaciones expresas del owner para P0–P5 y aceptación de la variante escalonada registradas en conversación. Esto **no cambia** Charter `DRAFT`, decisión D-1…D-7 ni ID oficial de la unidad.

## 1. Insumos y custodia

| Objeto | Identidad / evidencia |
|---|---|
| PDF canónico | `tests/corpus/canonical/pdf/doc_01_single.pdf`; SHA-256 `2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3`; 531.778 bytes y 3 páginas. |
| AST de OCR | 61 nodos; `ast_hash=e93eaf287ee442e1f3fbc8ee6f7b4a68acf7bcbdc53c80d76e49ab6b58b341e2`. |
| Manifiesto | 5 unidades: 3 `translate`, 2 `preserve`; SHA-256 canónico `3b63913de12ab4580b491e66e8efeb5df2d99509a154d7ef5d345b01616b42ce`. |
| Salida física | `translated_2a1bab7fb7093146f62c6155c802abe6a56addab8937d45c8145560391c9fcd3.pdf`; 20.900 bytes, 4 páginas; SHA-256 `8c9f81dfcc2cfc200211894bad65a46bdd82fa45c36a9bfee1a1d454ce2d6c47`. |
| ZIP probatorio P5 | `P5_C_L1_R2_9cf15cac6b12_EVIDENCE_RO.zip`; 596.525 bytes; SHA-256 `b1fe0603732493cdacc749c116c9694be53061eef5d40fa9d1315cfafd1bb65f`; ZIP íntegro, 14 miembros y 13/13 hashes verificados. **No anexado a Git por política de custodia.** |
| Snapshots SQLite | 5/5 `integrity_check=ok`; `documents`: 1 perfil; `fsm`: 1 documento terminal; `queue`: 5 recibos, 6 tareas; `materialized`: 61 proyecciones, 1 publicación; `event.chunk_events_log`: **0 filas**. |

La revisión independiente se efectuó sobre el ZIP P5 exportado, sin nuevas ejecuciones de producto ni modificaciones a los volúmenes.

## 2. Secuencia P0–P5

| Fase | Evidencia realizada | Resultado instrumental |
|---|---|---|
| P0 | Recursos exclusivos, seed offline, hashes/permisos y red privada | `PASS_SEEDED_NO_PRODUCT_START`. |
| P1 | Bootstrap de cuatro bases SQLite, sin otros servicios | `PASS_BOOTSTRAP_ONLY`. |
| P2 | OCR canónico: PDF archivado, AST real, perfil, 5 unidades, FSM `PROCESSING` | `PASS_OCR_ONLY`; P2 V1 detenido en precheck antes de arrancar; P2 V2 fue el primer OCR real. |
| P3 | Engine + fake: cinco tareas y recibos durables, 61 proyecciones, FSM `READY_FOR_ASSEMBLY` | `PASS_ENGINE_FAKE_ONLY`. |
| P4 | Assembler real/Tectonic, PDF publicado, FSM `COMPLETED` | `PASS_ASSEMBLER_ONLY`. |
| P5 | Exportación read-only y snapshots verificables, sin reinicio de producto | `PASS_EXPORT_ONLY`; P5 V1 y V2 fallaron en instrumentos; V3 completó. |

Las tres unidades `translate` devolvieron 59/59 miembros idénticos al texto OCR fuente. Esto **no** demuestra traducción lingüística efectiva; sí ejercita contrato del fake, conexiones y persistencia.

## 3. Checkpoints del Atlas §9.2.2

Los estados se aplican **solo a este RUN-ID y a esta variante**. `REACHED` exige la evidencia indicada; `UNKNOWN` deja un alcance sin acreditar, aunque la ruta haya llegado al PDF. La secuencia P0–P5 no demuestra todo el orden concurrente AS-IS.

| CP | Estado | Evidencia y límite |
|---|---|---|
| CP-00 | REACHED (variante) | Imagen/HEAD, Compose instrumentado, fake interno, recursos y rutas verificados; no cold build. |
| CP-01 | REACHED | Bootstrap SQLite P1 y validación independiente posterior. |
| CP-02 | REACHED | PDF con hash canónico archivado tras OCR P2. |
| CP-03 | REACHED | AST OCR real persistido, 61 nodos y hash. |
| CP-04 | REACHED | Perfil persistido, 5 unidades con miembros vinculados. |
| CP-05 | REACHED | FSM/cola coherentes en P2 y finales; `PROCESSING` no tomado como éxito de inferencia. |
| CP-06 | REACHED acotado | Engine reclamó/finalizó tareas con `execution_id` y lease registrados; no ensayo aislado del doble-ATTACH/recovery. |
| CP-07 | REACHED acotado | Fake atendió las 3 unidades `translate`; no demostración integral de autoridad pre-I/O o proveedor real. |
| CP-08 | **UNKNOWN para journal definido** | **`event.chunk_events_log = 0`**, aunque `queue.chunk_result_receipts = 5` durables y verificados. Los recibos del mecanismo G3 no deben rebautizarse como eventos del plano `event.db`. Revisar contrato antes de certificar este CP. |
| CP-09 | REACHED | 61 proyecciones versionadas/hasheadas, una publicación, cinco tareas LLM completadas. |
| CP-10 | REACHED | Barrera `READY_FOR_ASSEMBLY`, perfil y proyecciones recibidos por Assembler. |
| CP-11 | REACHED | Compilación real con Tectonic; existencia de PDF publicado y log de promoción. |
| CP-12 | REACHED | PDF válido y verificable, hash, FSM `COMPLETED` terminal, tarea Assembler completada y ZIP P5. |

**Observación CP-08:** la tabla `chunk_events_log` vacía es un hecho probado sobre el snapshot. Determinar si el journal durable de esta ruta se instrumenta **deliberadamente** en `queue.chunk_result_receipts` o falta una obligación contractual precisa es trabajo pendiente; no se deduce de este documento un incumplimiento FROZEN específico.

## 4. Tres dictámenes separados

| Dimensión | Dictamen | Lectura correcta |
|---|---|---|
| `execution_outcome` | **A** | PDF físicamente válido, atribuible al run, conforme al criterio estrecho de E2E-0/Atlas §9.2.3. |
| `scientific_verdict` | **FAIL** | Fórmulas, símbolos griegos, exponentes, desigualdades y fracciones se perdieron o degradaron en el PDF final. |
| `contract_verdict` | **PRESERVACIÓN MATEMÁTICA FALLIDA; cobertura global UNKNOWN** | No equivale a certificar ni denegar integralmente todos los contratos FROZEN. |
| `linguistic_translation_verdict` | **NOT_EVALUABLE_FAKE_ECHO** | El fake devuelve texto de entrada; no mide traducción lingüística. |
| `product_readiness` | **NOT_DEMONSTRATED** | Sin R1/R3 comparable, concurrencia, proveedor real y pruebas de recuperación/fencing. |

**Evidencia visual:** sobre original p. 2, `D = β⁻¹ − (1−δ)` pierde `β`, `δ` y exponente en salida p. 2. La desigualdad de Bellman del original p. 3 pierde relación `≥` y `β` en salida p. 3. El AST de 61 nodos clasifica 59 `paragraph` y 2 `heading`, **0** ecuaciones; las dos unidades `preserve` son encabezados y no fórmulas. Las 61 proyecciones reproducen el texto OCR, lo que localiza representación dañada **antes** del fake, además de pérdidas visibles en render final. No está aislada la función causal exacta: extracción/clasificación/TeX/Tectonic requieren testigos L2 separados. **No reabrir E2-02 automáticamente ni crear GAP nuevo por reflejo.**

## 5. Pendientes explícitos; no hay cierre global

- **R1/R3**: aún sin testigos comparables de L0/L1; no inferir resultados A/B/C.
- **R2 AS-IS concurrente**: no ensayado; P0–P5 es una variante de ejecución, no selección de ruta canónica.
- **L2**: investigar preservación matemática y CP-08; evaluar autoridad, replay/idempotencia, recovery, parser y render de fórmulas de forma focal.
- **Suministro**: cold builds, SBOM completo y portabilidad siguen pendientes cuando sean pertinentes.
- **Gobernanza**: Charter `DRAFT`, Atlas `IN_PROGRESS`, unidad/HITO/folios por aprobar; no modificar NADR FROZEN, declarar readiness ni tocar registros históricos.

**Fuente primaria externa al repo:** ZIP P5 y recibos P0–P5 conservados por el owner, salidas PowerShell y revisión científica offline del 2026-11-03. Esta nota es una adenda probatoria de trabajo **sin trasladar artefactos binarios al repositorio**.