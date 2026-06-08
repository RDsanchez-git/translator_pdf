"""
core/validation/preservation.py
Validador de preservación de entidades literales e integridad referencial (PI-01 a PI-05).
Sólido y acotado para el alcance de la Fase 11E.

Limitaciones identificadas para Backlog (Fase 11E.5 / Refactor de Escalabilidad):
- No valida identificadores académicos extendidos (arXiv, PMID, PMC).
- Las URLs mantienen comparación literal sin normalización de paths.
"""

import re
from typing import List, Set
from core.validation.models import ValidationContext, ValidationResult, Severity, Scope

class PreservationValidator:
    """
    SOTA: Guardián de integridad referencial y dependencias estructurales.
    Aplica operaciones asimétricas de conjuntos protegiendo la semántica documental.
    """

    DOI_REGEX = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.IGNORECASE)
    URL_REGEX = re.compile(r'https?://[^\s{}]+')
    ORCID_REGEX = re.compile(r'\b\d{4}-\d{4}-\d{4}-\d{3}[0-9X]\b', re.IGNORECASE)
    ISBN_REGEX = re.compile(r'\b(?:97[89])?[- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,6}[- ]?\d{1}\b')
    
    # PI-04: Punteros de lectura cruzada (Ampliación de comandos de LaTeX moderno)
    REF_REGEX = re.compile(r'\\(?:cite|ref|eqref|autoref|cref|Cref|pageref|nameref|vref|Vref|cpageref)\s*\{([^}]+)\}')
    # PI-04b: Anclas topológicas independientes
    LABEL_REGEX = re.compile(r'\\label\s*\{([^}]+)\}')
    # PI-05: Dependencias con tolerancia a argumentos opcionales entre corchetes
    DEP_REGEX = re.compile(r'\\(?:input|include|bibliography|addbibresource)(?:\[[^\]]*\])?\s*\{([^}]+)\}')

    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        results: List[ValidationResult] = []

        if context.scope == Scope.CHUNK:
            results.extend(self._check_doi(context))
            results.extend(self._check_url(context))
            results.extend(self._check_isbn_orcid(context))

        elif context.scope == Scope.DOCUMENT:
            results.extend(self._check_cross_references(context))
            results.extend(self._check_labels(context))
            results.extend(self._check_dependencies(context))

        return results

    def _check_doi(self, context: ValidationContext) -> List[ValidationResult]:
        # Corrección: Normalización a minúsculas para neutralizar la aserción de strings en el set
        source = {d.lower() for d in self.DOI_REGEX.findall(context.source_text)}
        target = {d.lower() for d in self.DOI_REGEX.findall(context.target_text)}
        missing = source - target
        if missing:
            return [ValidationResult("PI-01", False, Severity.HARD_FAIL, f"DOI perdido o alterado: {missing}", context)]
        return []

    def _check_url(self, context: ValidationContext) -> List[ValidationResult]:
        # Las URLs mantienen comparación estricta de case por semántica de paths de servidores remotos
        source = set(self.URL_REGEX.findall(context.source_text))
        target = set(self.URL_REGEX.findall(context.target_text))
        missing = source - target
        if missing:
            return [ValidationResult("PI-02", False, Severity.HARD_FAIL, f"URL literal perdida o modificada: {missing}", context)]
        return []

    def _check_isbn_orcid(self, context: ValidationContext) -> List[ValidationResult]:
        results = []
        # ORCID (Normalizado por consistencia de case)
        source_orc = {o.lower() for o in self.ORCID_REGEX.findall(context.source_text)}
        target_orc = {o.lower() for o in self.ORCID_REGEX.findall(context.target_text)}
        if missing_orc := source_orc - target_orc:
            results.append(ValidationResult("PI-03", False, Severity.HARD_FAIL, f"ORCID perdido/alterado: {missing_orc}", context))

        # ISBN
        source_isbn = set(self.ISBN_REGEX.findall(context.source_text))
        target_isbn = set(self.ISBN_REGEX.findall(context.target_text))
        if missing_isbn := source_isbn - target_isbn:
            results.append(ValidationResult("PI-03", False, Severity.HARD_FAIL, f"ISBN perdido/alterado: {missing_isbn}", context))
        return results

    def _check_cross_references(self, context: ValidationContext) -> List[ValidationResult]:
        source_keys = self._extract_sub_keys(self.REF_REGEX.findall(context.source_text))
        target_keys = self._extract_sub_keys(self.REF_REGEX.findall(context.target_text))
        
        missing = source_keys - target_keys
        unexpected = target_keys - source_keys
        if missing or unexpected:
            return [ValidationResult("PI-04", False, Severity.HARD_FAIL, f"Punteros rotos. Faltan: {missing}, Sobran: {unexpected}", context)]
        return []

    def _check_labels(self, context: ValidationContext) -> List[ValidationResult]:
        source_labels = self._extract_sub_keys(self.LABEL_REGEX.findall(context.source_text))
        target_labels = self._extract_sub_keys(self.LABEL_REGEX.findall(context.target_text))
        
        missing = source_labels - target_labels
        unexpected = target_labels - source_labels
        if missing or unexpected:
            return [ValidationResult("PI-04b", False, Severity.HARD_FAIL, f"Anclas rotas. Faltan: {missing}, Sobran: {unexpected}", context)]
        return []

    def _check_dependencies(self, context: ValidationContext) -> List[ValidationResult]:
        source_deps = self._extract_sub_keys(self.DEP_REGEX.findall(context.source_text))
        target_deps = self._extract_sub_keys(self.DEP_REGEX.findall(context.target_text))
        
        missing = source_deps - target_deps
        unexpected = target_deps - source_deps
        if missing or unexpected:
            return [ValidationResult("PI-05", False, Severity.HARD_FAIL, f"Dependencias estructurales rotas. Faltan: {missing}, Sobran: {unexpected}", context)]
        return []

    @staticmethod
    def _extract_sub_keys(raw_matches: List[str]) -> Set[str]:
        keys = set()
        for match in raw_matches:
            for part in match.split(','):
                clean = part.strip()
                if clean:
                    keys.add(clean)
        return keys