class AlignmentQualityPolicy:
    """Gobierna las reglas de negocio para evaluar la densidad y cobertura del alineamiento físico."""
    
    @staticmethod
    def calculate_coverage(
        aligned_count: int, 
        unmatched_candidate_count: int, 
        unmatched_ground_truth_count: int
    ) -> float:
        """Calcula el ratio de cobertura de anclajes emparejados sobre el espacio muestral total."""
        total = aligned_count + unmatched_candidate_count + unmatched_ground_truth_count
        return aligned_count / total if total > 0 else 1.0