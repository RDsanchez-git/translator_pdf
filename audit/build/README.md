# I0-1 + I0-1B — Instrumentación de auditoría, consolidada (no acreditada)

**Estado:** código y pruebas instrumentales preparados. La resolución real, descarga,
instalación de ruedas, Tectonic/binario ELF, build de imagen, HV y E2E-0 están
**PENDIENTES y NO EJECUTADOS**. No implica `PF-06 PASS` ni un resultado del producto.

**Sujeto congelado:** commit `c56f3e124d76ae9f1506e4b12fbf0faa4881b574`,
tree `eb7d2f6770517b72546055f4b611bac4734a3db3`.
I0-1 caracteriza 328 archivos del snapshot y 24 dependencias de ejecución.
`groq==1.4.0` es **restricción instrumental**, no versión histórica certificada.

## Única estructura instrumental dentro del repositorio

- `prepare_source.py` + `source_policy.json`: exportación del snapshot desde Git
  por allowlist (se conservan los archivos de I0-1).
- `prepare_resolution.py`: prepara **solo** `requirements.in`,
  `groq-constraint.in` y `resolution-plan.json` desde un snapshot completo
  y externamente anclado. La salida siempre permanece `INCOMPLETE_NOT_AUTHORIZED_NOT_EXECUTED`.
- `verify_materials.py`: **único** gate de lock/wheels/materiales; valida I0-1
  completo, manifiesto de origen contra hash confiable, manifiesto de materiales
  v1.1, hashes externos e internos `RECORD`, límites ZIP y cierre transitivo.
  Después ensambla en directorio nuevo y compara cada archivo del contexto
  con los hashes de los **manifiestos copiados ya validados**.
- `Dockerfile.audit`, `.dockerignore`: políticas de contexto I0-1 sin cambios.
- `materials-manifest.template.json`: plantilla **deliberadamente inutilizable**,
  v1.1; reemplaza la plantilla v1.0 cuando se adopte esta versión.
- `tests/test_i0_1.py`, `tests/test_prepare_resolution.py`: tests sintéticos;
  **no** resuelven ni instalan dependencias, ni usan el corpus.

No se requiere ni se conserva `verify_lock_wheels.py` como segunda ruta de
acreditación, ni `tests/test_i0_1b.py` de la revisión aislada: sus controles de
lock/wheels se consolidaron en el verificador y la preparación inerte quedó
cubierta por `tests/test_prepare_resolution.py`. Conservar por separado el RAR
original si se necesita trazabilidad histórica, **fuera** del árbol operativo.

## Aplicación segura

1. **No fusionar a ciegas**: respaldar la carpeta `audit/build/` local y comparar
   estos archivos con modificaciones locales que todavía no fueron adjuntadas.
2. Mantener `prepare_source.py`, `source_policy.json`, `Dockerfile.audit` y
   `.dockerignore` idénticos a la base I0-1, salvo revisión documentada.
3. Aplicar en `audit/build/` los cambios del verificador, planner, plantilla,
   tests y este README; no copiar carpetas `src/`, `materials/`, `wheels/` ni secretos.
4. Comprobar en la raíz del repo, en Python con `packaging` ya disponible:

   ```sh
   python -B -m unittest discover -s audit/build/tests -v
   ```

5. Revisar `git diff -- audit/build` y `git status --short` **antes** de decidir
   cualquier commit instrumental. No se ha hecho commit/push automáticamente.

**Comandos futuros, SOLO con aprobación independiente e insumos auténticos:**

```sh
python -B audit/build/prepare_resolution.py \
  --source-context <SNAPSHOT_I0-1> --out <NUEVO_DIRECTORIO_EXTERNO> \
  --expected-source-manifest-sha256 <SHA256_DE_EVIDENCIA_I0-1>

python -B audit/build/verify_materials.py \
  --source-context <SNAPSHOT_I0-1> --materials <MATERIALES_APROBADOS> \
  --out <NUEVO_CONTEXTO_EXTERNO> \
  --expected-source-manifest-sha256 <SHA256_DE_EVIDENCIA_I0-1>
```

El SHA del manifiesto debe venir de **evidencia I0-1 previamente aceptada**, no
calcularse de un snapshot arbitrario para fingir aprobación.

## Qué sigue pendiente para grado producción

1. Acreditar y bloquear las herramientas instrumentales (Python/`packaging`,
   resolver, pip) y el artefacto/distribución de cada binario por SHA/procedencia.
2. Resolver/adquirir en un enclave Linux/amd64 CPython 3.11 separado **solo con
   autorización**, registrar índice/corte, reproducibilidad, binarios y materiales.
3. Comprobar que el host de validación coincide **realmente** con la imagen base
   aprobada (digest + Python patch + ABI + glibc); los campos del manifiesto por
   sí solos no autentican la imagen.
4. Calibrar límites de ZIP con wheels aprobados; validar legalidad/licencias y
   seguridad del supply chain; realizar pruebas offline autorizadas y HV.
5. Revisar excepciones de recursos faltantes mediante política explícita, nunca
   ampliar el allowlist para forzar un PASS. No correr Compose productivo ni E2E-0.

La verificación de materiales **no es certificación de inmutabilidad**:
`chmod` es solamente una barrera accidental, y el contexto final debe protegerse
contra mutaciones posteriores mediante aislamiento y verificación del consumidor.

**Estado formal:** `I0-1 PASS previo; I0-1B tests sintéticos PASS; INTEGRACIÓN
LOCAL Y TOOLING LOCK PENDIENTES; PF-06 NO ACREDITADO; HV NOT_RUN; E2E-0 NOT_EXECUTED;
execution_outcome=null`.
