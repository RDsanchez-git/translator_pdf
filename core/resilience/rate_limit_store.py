"""
Puerto abstracto para persistencia de estado de cuotas.

NADR-08 §5.1 R1: Puerto abstracto desacoplado del backend de persistencia.
NADR-08 §5.1 R4: La selección del backend se realiza desde la Composition Root.

GOBERNANZA (GF-01):
Este puerto define exclusivamente el contrato de PERSISTENCIA de estado
(load/save). La interfaz operativa de coordinación (try_consume, CAS,
refill) se definirá en Gate 4 cuando se resuelva el mecanismo de
coordinación multi-proceso. Ver GF-01 en el Governance Findings Register.

El algoritmo de Token Bucket (refill, wait_time, consume) pertenece a
QuotaManager. El Store solo persiste/recupera estado.

NOTA: Este puerto es SÍNCRONO por diseño. La capa infra/db/ usa
exclusivamente sqlite3 (sync). La concurrencia intra-proceso la
garantiza asyncio.Lock() en QuotaManager, no el Store.
"""

from typing import Protocol, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class BucketState:
    """
    Snapshot inmutable del estado de un bucket de cuota.
    
    tokens: cantidad de tokens disponibles en el momento del snapshot.
    last_update: time.time() (epoch seconds) del momento del snapshot.
                 NO es time.monotonic(). El QuotaManager convierte
                 entre epoch y monotonic al cargar/guardar.
    """
    tokens: float
    last_update: float


class RateLimitStore(Protocol):
    """
    Puerto de persistencia para estado de cuotas.

    Contrato mínimo: load / save.
    
    NADR-08 §5.1 R1: Desacoplado del backend concreto.
    NADR-08 §5.1 R2: Operaciones atómicas de consulta y actualización.
    
    ESTADO: Contrato de persistencia definido. La interfaz operativa de
    coordinación (try_consume, CAS) se definirá en Gate 4 (GF-01).
    """

    def load(self, bucket_id: str) -> Optional[BucketState]:
        """
        Retorna el estado actual del bucket.
        
        Returns:
            BucketState si existe, None si el bucket no está inicializado.
        """
        ...

    def save(self, bucket_id: str, state: BucketState) -> None:
        """
        Persiste el estado del bucket (overwrite atómico).
        """
        ...