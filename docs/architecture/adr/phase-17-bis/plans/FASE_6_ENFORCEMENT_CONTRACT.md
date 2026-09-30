# FASE 6 ENFORCEMENT CONTRACT
## Continuous Verification — Merge Enforcement Declaration (NADR-F17BIS-30)

**Documento:** `docs/architecture/adr/phase-17-bis/plans/FASE_6_ENFORCEMENT_CONTRACT.md`
**Versión:** 1.0.0
**Estado:** ACTIVE (transicional)
**Fecha:** 2026-09-30
**Derivado de:** NADR-F17BIS-30 (FROZEN), PHASE_17BIS_FASE6_EXECUTION_PLAN.md v1.0.10 (Task 4.1.1, MIG-01, MIG-04)
**Autoridad:** Architecture Board. Este documento declara el enforcement contract operativo; NO redefine reglas de NADR-30.
**Ubicación:** `plans/` según Guía de Documentación de Arquitectura v1.0.0 §4 (secuenciación operativa). La evidencia binaria de CI vive en `reports/evidence/` (§4: "evidencia de CI"); los documentos de hallazgos viven en `reviews/`.

---

## 1. Propósito

Declarar en lenguaje plano y auditable: qué checks de Continuous Verification
bloquean integración, cuáles son informativos, bajo qué condiciones se activan
los bloqueantes, y qué huecos de enforcement existen hoy.

---

## 2. Estado server-side al momento de emisión

| Hecho | Evidencia |
|---|---|
| Branch protection NO configurada en `main` | Screenshot Settings → Branches: "Classic branch protections have not been configured" (2026-09-30) |
| `gh` CLI no disponible en el entorno | `CommandNotFoundException` al ejecutar `gh --version` |
| Flujo de integración actual del maintainer: push directo a `main` | Historial git (`fbd8bb4..8734e8b main -> main`) |
| Estado basal CV: HARD_FAIL en FULL y SMOKE | Ejecución empírica 2026-09-30: exit code 2 en ambos perfiles (NSS 0.7208 < 0.80, 163 Critical FN) |

---

## 3. Decisión de enforcement (Opción B transicional)

| Check | Workflow | Perfil CV | Estado | Bloquea merge de PR | Bloquea push directo |
|---|---|---|---|:---:|:---:|
| `static-analysis` | ci.yml | — | **REQUIRED** | Sí | No |
| `unit-tests` | ci.yml | — | informativo | No | No |
| `integration-tests` | ci.yml | — | informativo | No | No |
| `regression-gates` | ci.yml | SMOKE | informativo | No | No |
| `cv-full-profile` | continuous-verification.yml | FULL | informativo | No | No |

**Mecanismo:** classic branch protection rule sobre `main` con `static-analysis`
como único required status check. Se elige classic (no ruleset) en la fase
transicional porque un ruleset con required checks rechaza el push directo por
chicken-and-egg (el commit nuevo aún no tiene checks al momento del push), lo que
rompería el flujo actual del maintainer sin aportar enforcement real.

**Por qué `static-analysis` sí es required hoy:** su estado basal es verde
(pyright 0 errors, import-linter 4/4 KEPT), es determinista y rápido. Bloquea
merges con errores de tipo o violaciones de contratos de arquitectura.

**Nota de nombres:** GitHub reporta los checks por el campo `name:` del job, no
por su ID: `static-analysis` ⇒ "Static Analysis (pyright + import-linter)";
`regression-gates` ⇒ "Regression Gates (Continuous Verification — Smoke Profile)";
`cv-full-profile` ⇒ "Continuous Verification — Full Profile". La branch protection
se configura con los nombres reportados.

**Nota de nombres:** GitHub reporta los checks por el campo `name:` del job, no por
su ID: `static-analysis` ⇒ "Static Analysis (pyright + import-linter)";
`regression-gates` ⇒ "Regression Gates (Continuous Verification — Smoke Profile)";
`cv-full-profile` ⇒ "Continuous Verification — Full Profile". La branch protection
se configura con los nombres reportados.

---

## 4. Trade-off honesto (sin eufemismos)

1. **Con esta configuración, una regresión estructural real introducida por un
   cambio NO bloquea integración hoy.** Continuous Verification como control de
   merge está *diferido condicionalmente*, no activo. El único control de merge
   activo es `static-analysis`.

2. **Con required status checks activos, ningún commit nuevo entra a `main` sin
   haber pasado `Static Analysis` en alguna rama o PR:** el push directo de un
   commit sin checks pasados es rechazado. El flujo operativo resultante es
   rama → PR (o push a develop) → merge/push del mismo SHA con checks verdes.
   Lo que permanece diferido no es el bloqueo de entrada, sino que **los checks
   de Continuous Verification (`regression-gates`, `cv-full-profile`) aún no son
   required**: una regresión estructural que no rompa static-analysis no bloquea
   integración hoy (cláusula 6.1).

3. **Estado basal esperado de los checks CV: ROJO** (exit 2, HARD_FAIL) tanto para
   `regression-gates` (SMOKE) como `cv-full-profile` (FULL), por el estado basal del
   extractor. Este rojo es conocido y documentado; no indica regresión nueva.
   Distinguir una regresión nueva del rojo basal requiere inspección del artifact
   de evidencia (NSS y verdict en el JSON persistido), no el color del check.

---

## 5. Semántica de exit codes → estado de check

| Exit code | Veredicto (NADR-27) | Estado del check CV |
|:---:|---|---|
| 0 | PASS | verde |
| 1 | WARNING | rojo |
| 2 | HARD_FAIL (REGRESSION) | rojo |
| 3 | BASELINE_INTEGRITY_FAILURE | rojo |
| 4 | EXECUTION_FAILURE | rojo |

GitHub trata cualquier exit ≠ 0 como failure del check; no hay granularidad
nativa por exit code. Un check CV en rojo con exit 3 o 4 indica problema
operacional o de baseline, no divergencia científica; el contrato de evidencia
(NADR-28) permite distinguirlo en el artifact persistido.

---

## 6. Cláusulas de activación

**6.1 Promoción de `regression-gates` y `cv-full-profile` a REQUIRED** cuando:
- (a) el estado basal del corpus canónico sea PASS (exit 0) en ejecución FULL, o
- (b) exista recalibración gobernada de thresholds (DC-6.6, decisión de gobernanza
  post-Fase 6) que lleve el estado basal a PASS.

Hasta entonces, promoverlos a required congelaría `main` con un rojo permanente
que no distingue regresiones nuevas del estado basal: teatro de enforcement.

**Comportamiento al promocionar (declarado para que no sorprenda):** GitHub trata
cualquier exit ≠ 0 como failure en required checks; no hay granularidad nativa por
exit code. Al promocionar, WARNING (exit 1) también bloqueará merges. Esto es
coherente con 6.1(a): el estado basal PASS implica exit 0, entonces cualquier
desviación del basal (warning o fail) es señal de regresión y debe bloquear.
Un wrapper que traduzca WARNING a exit 0 para evitar el bloqueo está **prohibido**:
violaría NADR-F17BIS-27 §5.6 R32 (sys.exit propaga el exit code sin reinterpretar).

**6.2 Evidencia server-side (MIG-04):** al configurar la classic rule, registrar
screenshot o respuesta de API como evidencia en
`docs/architecture/adr/phase-17-bis/reports/evidence/` (directorio de evidencia de
CI según la Guía de Documentación de Arquitectura §4; se crea al guardar el primer
artefacto, no antes, por YAGNI) y referenciarla en Task 4.1.3. El Evidence Log
(`reviews/FASE_6_EXIT_REVIEW_EVIDENCE_LOG.md`) documenta en texto la evidencia
forense y apunta a esta ruta.

**6.3 Cierre del hueco restante:** promover `regression-gates` y `cv-full-profile`
a required (cláusula 6.1) y, opcionalmente, activar "Require a pull request before
merging" o migrar a ruleset para exigir revisión vía PR. El hueco de entrada sin
checks quedó cerrado con la activación de required status checks (2026-09-30).

---

## 7. Alternativas rechazadas

| Alternativa | Razón de rechazo |
|---|---|
| **A:** `regression-gates` REQUIRED hoy | Congela `main` permanentemente (estado basal HARD_FAIL); produce teatro de enforcement que se termina bypasseando por frustración, peor que no tener gate |
| **C:** sin branch protection | Hueco total de enforcement; viola el espíritu de NADR-30 §5.4 R11-R13 |
| **D:** gate relativo (required check que falla solo si el veredicto empeora vs estado basal) | Cambia la semántica de veredicto de NADR-19/NADR-27 sin gobernanza que lo autorice (cláusula de jerarquía normativa del ADR Maestro); introduce comparación entre ejecuciones que complica reproducibilidad (NADR-28) |
| **Ruleset** con required checks en fase transicional | Rechaza push directo por chicken-and-egg; rompe el flujo actual sin aportar enforcement real al maintainer |

---

## 8. Procedimiento MIG-01 (configuración server-side)

1. GitHub → Settings → Branches → **Add classic branch protection rule**
2. Branch name pattern: `main`
3. Activar **Require status checks to pass before merging**
4. Buscar y seleccionar: `static-analysis`
5. **NO** seleccionar `regression-gates` ni `cv-full-profile` (informativos según §3)
6. Decidir "Include administrators": si se desactiva, existe override de emergencia
   (§9); si se activa, no existe override y §9 se marca N/A
7. **Create**
8. Evidencia: screenshot de la regla creada →
   `docs/architecture/adr/phase-17-bis/reports/evidence/branch-protection-main.png`,
   referenciado en Task 4.1.3 y en el Evidence Log

---

## 9. Override de emergencia

Si "Include administrators" queda desactivado, el maintainer puede mergear un PR
con checks rojos como bypass de emergencia. Todo uso de override DEBE registrarse
en el Findings Register con justificación explícita (ENGINEERING_PRINCIPLES §IV).
Si queda activado, no existe override y esta sección es N/A.

---

## 10. Referencias

- NADR-F17BIS-30 §5.1-§5.7 (reglas de enforcement y merge protection)
- PHASE_17BIS_FASE6_EXECUTION_PLAN.md v1.0.10 §5.1, §7 (MIG-01, MIG-04)
- Guía de Documentación de Arquitectura v1.0.0 (FROZEN) §2-§4: ubicación de
  artefactos por responsabilidad (contract en plans/, evidencia de CI en reports/)
- DF-09: enforcement de merge de CV diferido condicionalmente (checks CV
  informativos hasta cláusula 6.1); hueco de push directo cerrado por activación
  de required status checks (2026-09-30) (ACCEPTED_LIMITATION)
- DF-10: PASS path no demostrable con estado basal del extractor (RECLASSIFIED_FUTURE_PHASE)
- Evidencia de estado server-side: screenshot 2026-09-30 (branch protection inexistente)