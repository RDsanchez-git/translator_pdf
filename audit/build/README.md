# I0-1 — Audit Sandbox build inputs (instrumentación, DRAFT)

**Estado:** `I0-1 SOURCE PREPARATION IMPLEMENTED; ARTIFACT ACQUISITION / BUILD / HV / L1 NOT RUN`.
**Fuentes:** D1 publicado en el commit `8d3aa568ba5ce01202280cd93adca564a966038a`; código del sujeto a congelar por SHA completo antes de cualquier ejecución. El paquete es **solo para revisión**; no está incorporado al repositorio del owner.

## Archivos

- `prepare_source.py`: crea una exportación de origen desde un **commit completo** mediante Git objects, independiente del working tree, con lista positiva y manifiesto de hashes. No descarga ni compila.
- `source_policy.json`: política explícita de rutas y extensiones. Deliberadamente no admite PDFs, corpus, documentos del usuario, SQLite, resultados JSON ni `.env`.
- `verify_materials.py`: valida `requirements.lock`, **todos los wheels**, Tectonic y una base Docker `@sha256:` frente al manifiesto; bloquea entradas faltantes o extrañas. Después compone un contexto local nuevo sin ejecutar Docker.
- `.dockerignore`: segunda frontera de lista positiva en el contexto de Docker (excluye cualquier archivo añadido por accidente). Nunca sustituye al generador/validador de hashes.
- `Dockerfile.audit`: instala **solo ruedas verificadas** sin acceso de red; no invoca `apt-get` ni `curl`; copia únicamente código autorizado y Tectonic verificado. Requiere una base Linux preparada y aprobada con librerías nativas de Tectonic, identificada por digest; **no se proporciona todavía**.
- `materials-manifest.template.json`: es plantilla deliberadamente inutilizable, no reemplazar campos con valores ficticios.
- `tests/test_i0_1.py`: tests con repositorios sintéticos temporales, sin acceso a red ni corpus.

## Primer control local, sin cambios de producto

Desde una copia de estos archivos y usando el SHA del sujeto confirmado para la siguiente adquisición:

```powershell
python -m unittest discover -s audit/build/tests -v
python audit/build/prepare_source.py `
  --repo . `
  --commit <SHA_COMMIT_COMPLETO_DE_CODIGO> `
  --out <CARPETA_NUEVA_FUERA_DEL_REPOSITORIO>
```

El segundo comando **solo crea una copia de código versionado** en una carpeta nueva fuera del repositorio. No ejecutarlo con rutas de salida existentes, dentro del repo, o sin decidir el SHA del sujeto. No se necesita Docker Desktop.

## Materiales: adquisición futura separada y autorizada

`verify_materials.py` requiere, en una carpeta **externa** que se rellena solo tras obtener artefactos reales y aprobar su origen:

```
materials/
  materials-manifest.json
  requirements.lock
  tectonic
  wheels/
    <wheels-linux-cp311-con-hash>.whl
```

El `materials-manifest.json` debe contener:

```json
{
  "schema_version": "1.0",
  "status": "APPROVED_MATERIALS",
  "target_platform": "linux/amd64",
  "python_version": "3.11",
  "groq_version": "1.4.0",
  "base_image": "<NOMBRE_DE_IMAGEN>@sha256:<DIGEST_REAL_DE_64_HEX>",
  "files": {
    "requirements.lock": "<SHA256_REAL>",
    "tectonic": "<SHA256_REAL>",
    "wheels/<NOMBRE_REAL>.whl": "<SHA256_REAL>"
  }
}
```

La plantilla es explicativa: **no debe usarse tal cual**. Cada wheel del lock debe estar representado, en la plataforma correcta y vinculado por hash al lock. Dependencias no fijadas, URLs directas, `-e`, listas transitivas incompletas, binarios fuera del manifiesto o un digest de imagen faltante producen rechazo.

Aún pendiente: seleccionar y preregistrar un resolver Python, índice/procedencia y mecanismo de descarga aprobados; generar lock completo y wheelhouse para Linux/amd64 Python 3.11; comprobar reproducibilidad en dos adquisiciones independientes si la política lo exige; y disponer de base de imagen con runtime nativo de Tectonic, referenciada por digest. No se inventan estos insumos.

Una vez adquiridos los artefactos, exclusivamente después de autorización documental:

```powershell
python audit/build/verify_materials.py `
  --source-context <CARPETA_SOURCE_PREPARADA> `
  --materials <CARPETA_MATERIALES_APROBADOS> `
  --out <CARPETA_NUEVA_CONTEXT_BUILD>
```

Este comando verifica materiales y arma un directorio: **no construye imagen**. Para una construcción posterior se exige revisión y autorización independiente, usando `docker build --network=none` con `--build-arg BASE_IMAGE=<digest aprobado>`, plataforma Linux amd64, caché controlada, hashes y evidencia. El Dockerfile requiere esa base preinstalada en el daemon; no presupone que esté disponible.

## Límites importantes

1. **No tiene lock real**, ni Tectonic real verificado, ni base Docker aprobada; por diseño no puede superar I0-1 completo ni iniciar build.
2. **La allowlist es restrictiva**: si faltan plantillas, otros recursos o imports, no se amplía a ciegas para que los tests pasen. Cualquier excepción requiere revisión y un nuevo hash de política. `configs` YAML y código Python no acreditan completitud de runtime.
3. **No hay certificación automática de ausencia de secretos en el contenido del código.** El generador rechaza archivos/raíces sensibles por política, pero una clave hardcodeada dentro de un `.py` requeriría escaneo adicional, manual y automatizado, antes de cualquier build. El manifiesto con estado `APPROVED_MATERIALS` es una afirmación del operador; las firmas/procedencia y aprobación humana deben verificarse en un gate independiente.
4. **El Dockerfile es estructural**, no un build verificado. Linux, dependencias compartidas y compatibilidad con Tectonic se verifican en HV. El control de no egress runtime pertenece a I0-3/HV, no a este paquete.
5. **No reutilizar el Compose productivo** ni hacer `docker compose up` hasta I0-3 y autorización HV. El fake Groq y el Compose aislado se implementarán en I0-2/I0-3.
6. **El SDK Groq 1.4.0 fue verificado en Windows local** respecto de `GROQ_BASE_URL`; requiere nueva verificación en imagen Linux, no inferirla.
7. **Los tests sintéticos son pruebas del generador, no del pipeline**; cualquier fallo de la instrumentación se registra como `HARNESS_FAILURE`, nunca como resultado A/B/C de E2E-0.
8. `PYTHONPATH=/app` y paquetes instalados con wheels no validan permisos SQLite o flujo de datos. La futura composición revisará lectura/escritura, redes y persistencia.

## Criterio de salida de I0-1

- Diff instrumental revisado; test de lista positiva sin contaminación ni secretos del working tree.
- Commit/tree del sujeto explicitados y manifiestos de blobs calculados.
- Lock cerrado con SHA reales, wheelhouse completo y Tectonic/base aprobados.
- Build **offline** reproducible y smoke test dentro de imagen (posteriores a autorización).
- Captura de entradas y salidas de los controles HV pertinentes.

**Hasta completar todo ello: `I0-1 PARTIAL; PF-06 NO ACREDITADO; HV NOT_RUN; L1 NO_EJECUTADO; outcome=null`.**
