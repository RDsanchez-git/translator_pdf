import logging
from pylatexenc.latexwalker import LatexWalker, LatexWalkerParseError
from markdown_it import MarkdownIt
from core.benchmark.models import PreparedBenchmarkDataset, StructuralQualityMetrics
from core.benchmark.ports import RunnerExecutionResult

logger = logging.getLogger(__name__)

class FormalLatexSyntaxParser:
    """SOTA: Parseo real de AST para LaTeX."""
    
    @staticmethod
    def validate_syntax(text: str) -> bool:
        if not text:
            return False
        try:
            walker = LatexWalker(text)
            walker.get_latex_nodes()
            return True
        except LatexWalkerParseError as e:
            logger.debug(f"LaTeX AST Parse Error: {e}")
            return False
        except Exception:
            return False

class FormalMarkdownTableParser:
    """SOTA: Parseo real de AST para GitHub Flavored Markdown (GFM)."""
    
    @staticmethod
    def validate_syntax(text: str) -> bool:
        if not text:
            return False
        md = MarkdownIt("gfm-like")
        tokens = md.parse(text)
        
        # SOTA FIX: Reversión manual contra el Blast Radius del Migration Engine.
        # Los tokens de la librería externa 'markdown_it' exponen '.type', no '.node_type'.
        open_tables = sum(1 for t in tokens if t.type == "table_open")
        close_tables = sum(1 for t in tokens if t.type == "table_close")
        
        # Una tabla válida debe estar cerrada y existir al menos una
        return (open_tables == close_tables) and (open_tables > 0)

class StructuralQualityEvaluator:
    """SOTA: Evaluador formal de topología estructural. Cero acoplamiento con hilos externos."""
    
    @staticmethod
    def evaluate(
        dataset: PreparedBenchmarkDataset, 
        execution_result: RunnerExecutionResult
    ) -> StructuralQualityMetrics:
        
        if not execution_result.raw_records:
            return StructuralQualityMetrics(0.0, 0.0, 0.0, 0.0)

        total_chunks = len(execution_result.raw_records)
        operational_successes = sum(1 for r in execution_result.raw_records if r.success)
        
        latex_valid = 0
        md_valid = 0
        density_ratios = []
        
        original_nodes_map = {unit.chunk_id: unit.node_count for unit in dataset.prepared_units}

        for record in execution_result.raw_records:
            artifact = record.artifact_metadata
            
            # 1. Inspección de los booleanos generados por los parsers formales en el Runner
            if record.success and artifact:
                if artifact.is_latex_valid: 
                    latex_valid += 1
                if artifact.is_markdown_valid: 
                    md_valid += 1
            
            # 2. Proxy de densidad estructural (Mide mutaciones de volumen)
            orig_nodes = original_nodes_map.get(record.chunk_id, 0)
            if orig_nodes > 0 and record.output_tokens > 0:
                proxy = record.output_tokens / (record.input_tokens / orig_nodes)
                ratio = min(orig_nodes, proxy) / max(orig_nodes, proxy)
                density_ratios.append(ratio)
            else:
                density_ratios.append(1.0 if orig_nodes == 0 else 0.0)

        return StructuralQualityMetrics(
            operational_reliability=round(operational_successes / total_chunks, 4) if total_chunks > 0 else 0.0,
            token_structure_proxy=round(sum(density_ratios) / len(density_ratios), 4) if density_ratios else 0.0,
            latex_syntax_score=round(latex_valid / total_chunks, 4) if total_chunks > 0 else 0.0,
            markdown_syntax_score=round(md_valid / total_chunks, 4) if total_chunks > 0 else 0.0
        )