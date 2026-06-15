from typing import Dict, List, Optional, Any
from enum import Enum

class NormalizationDomain(Enum):
    TEXT = "TEXT_DOMAIN"
    MATH = "MATH_DOMAIN"
    STRUCTURED = "STRUCTURED_DOMAIN"
    PASSTHROUGH = "PASSTHROUGH_DOMAIN"

class NormalizationPolicy:
    def __init__(self, policy_id: str):
        self.policy_id = policy_id
        self.normalizers: List[Any] = []

    def append(self, normalizer: Any) -> "NormalizationPolicy":
        self.normalizers.append(normalizer)
        return self

class NormalizationPolicyRegistry:
    """Registry Singleton que mapea claves canónicas a dominios y políticas lógicas."""
    _instance: Optional["NormalizationPolicyRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_registry()
        return cls._instance

    def _init_registry(self):
        self._domain_policies: Dict[str, NormalizationPolicy] = {}
        self._type_to_domain_map: Dict[str, str] = {}
        self._frozen: bool = False

    @property
    def is_bootstrapped(self) -> bool:
        return self._frozen

    def map_type_to_domain(self, canonical_key: str, domain: NormalizationDomain) -> None:
        if self._frozen:
            raise RuntimeError("DNL_REGISTRY_ERROR: Registry is frozen.")
        self._type_to_domain_map[canonical_key] = domain.value

    def register_policy(self, domain: NormalizationDomain, policy: NormalizationPolicy) -> None:
        if self._frozen:
            raise RuntimeError("DNL_REGISTRY_ERROR: Registry is frozen.")
        self._domain_policies[domain.value] = policy

    def get_policy_for_type(self, canonical_key: str) -> Optional[NormalizationPolicy]:
        domain_value = self._type_to_domain_map.get(canonical_key)
        if not domain_value:
            return None
        return self._domain_policies.get(domain_value)

    def freeze(self) -> None:
        """SOTA: Valida la consistencia de los tipos mapeados activamente sin exigir dominios futuros."""
        for canonical_key, domain_value in self._type_to_domain_map.items():
            if domain_value not in self._domain_policies:
                raise RuntimeError(
                    f"DNL_INTEGRITY_ERROR: The key '{canonical_key}' maps to domain '{domain_value}', "
                    f"but no policy has been registered for that domain."
                )
        self._frozen = True

    @classmethod
    def get_instance(cls) -> "NormalizationPolicyRegistry":
        return cls()