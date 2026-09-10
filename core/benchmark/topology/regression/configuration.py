"""Configuracion canonica del motor de evaluacion topologica.

NADR-22 §5.6 R19: Identificador criptografico de configuracion.
NADR-22 §5.6 R20: Congelamiento de la configuracion.
NADR-22 §5.6 R21: Toda modificacion invalida certificacion vigente.

Diseno:
- CanonicalEngineConfiguration: dataclass frozen que captura todos los
  parametros que afectan el resultado de la evaluacion.
- ConfigurationFingerprintCalculator: servicio stateless que calcula el
  SHA-256 determinista de la configuracion.

Las estrategias se identifican por el qualified name completo del tipo
concreto (module + qualname), no por strings libres. Esto garantiza que
el identificador sea sensible a cualquier cambio de clase sin permitir
typos ni strings inventados (ENGINEERING_PRINCIPLES §III).
"""
from __future__ import annotations

from dataclasses import dataclass

from core.shared.crypto import compute_sha256


@dataclass(frozen=True)
class CanonicalEngineConfiguration:
    """Configuracion canonica del motor de evaluacion topologica.

    Inmutable por diseno (frozen=True). Captura todos los parametros
    que afectan el resultado de la evaluacion de forma determinista.

    Los campos de estrategia contienen el qualified name completo
    (module.qualname) del tipo concreto, garantizando unicidad absoluta.
    """

    engine_type: str
    cost_weights: tuple[float, float, float]
    partition_strategy: str
    alignment_strategy: str
    normalization_policy: str
    overflow_strategy: str
    matching_policy: str
    nss_hard_fail: float
    nss_warning: float
    warning_threshold: int

    @staticmethod
    def from_components(
        *,
        engine: object,
        cost_weights: tuple[float, float, float],
        partitioner: object,
        aligner: object,
        normalizer: object,
        overflow: object,
        matching_policy: object,
        nss_hard_fail: float,
        nss_warning: float,
        warning_threshold: int,
    ) -> "CanonicalEngineConfiguration":
        """Construye la configuracion a partir de los componentes concretos.

        Extrae el qualified name completo (module.qualname) de cada
        componente de forma determinista. Esto garantiza que el
        fingerprint sea sensible a cambios de clase y unico entre
        modulos diferentes.
        """
        def _type_identity(obj: object) -> str:
            t = type(obj)
            return f"{t.__module__}.{t.__qualname__}"

        return CanonicalEngineConfiguration(
            engine_type=_type_identity(engine),
            cost_weights=cost_weights,
            partition_strategy=_type_identity(partitioner),
            alignment_strategy=_type_identity(aligner),
            normalization_policy=_type_identity(normalizer),
            overflow_strategy=_type_identity(overflow),
            matching_policy=_type_identity(matching_policy),
            nss_hard_fail=nss_hard_fail,
            nss_warning=nss_warning,
            warning_threshold=warning_threshold,
        )


class ConfigurationFingerprintCalculator:
    """Servicio de dominio para calcular el fingerprint de configuracion.

    Stateless, determinista, sin I/O (ENGINEERING_PRINCIPLES §II).
    Reutiliza compute_sha256 de core.shared.crypto (ADR §5).
    """

    @staticmethod
    def calculate(config: CanonicalEngineConfiguration) -> str:
        """Calcula el SHA-256 determinista de la configuracion.

        El payload es una cadena canonica con todos los campos en orden
        fijo, separados por pipes. Mismo config -> mismo hash, siempre.
        """
        payload = (
            f"{config.engine_type}|"
            f"{config.cost_weights[0]},{config.cost_weights[1]},{config.cost_weights[2]}|"
            f"{config.partition_strategy}|"
            f"{config.alignment_strategy}|"
            f"{config.normalization_policy}|"
            f"{config.overflow_strategy}|"
            f"{config.matching_policy}|"
            f"{config.nss_hard_fail}|"
            f"{config.nss_warning}|"
            f"{config.warning_threshold}"
        )
        return compute_sha256(payload.encode("utf-8"))
