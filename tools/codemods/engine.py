import os
import sys
import shutil
from typing import List, Dict, Set, Optional, Union
import libcst as cst

class MigrationRegistry:
    """Contenedor declarativo de reglas de transformación de AST."""
    def __init__(self) -> None:
        self.attributes: Dict[str, str] = {}
        self.keywords: Dict[str, str] = {}
        self.constructor_keywords: Dict[str, Dict[str, str]] = {}

    def rename_attribute(self, old: str, new: str) -> None:
        self.attributes[old] = new

    def rename_global_keyword(self, old: str, new: str) -> None:
        self.keywords[old] = new

    def rename_constructor_keyword(self, class_name: str, old: str, new: str) -> None:
        if class_name not in self.constructor_keywords:
            self.constructor_keywords[class_name] = {}
        self.constructor_keywords[class_name][old] = new

class MasterMigrationTransformer(cst.CSTTransformer):
    """
    SOTA: Transformador unificado y guiado por contexto.
    Rastrea el stack de llamadas para aplicar transformaciones quirúrgicas.
    """
    def __init__(self, registry: MigrationRegistry) -> None:
        self.registry = registry
        self.call_stack: List[str] = []
        self.attr_replacements = 0
        self.kw_replacements = 0

    def visit_Call(self, node: cst.Call) -> Optional[bool]:
        # SOTA FIX: Importación de Optional añadida arriba para este método
        if isinstance(node.func, cst.Name):
            self.call_stack.append(node.func.value)
        elif isinstance(node.func, cst.Attribute):
            self.call_stack.append(node.func.attr.value)
        else:
            self.call_stack.append("")
        return True

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        # SOTA FIX: Retorno cambiado de cst.CSTNode a cst.BaseExpression para cumplir la covarianza
        if self.call_stack:
            self.call_stack.pop()
        return updated_node

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute) -> cst.BaseExpression:
        # SOTA FIX: Retorno cambiado de cst.CSTNode a cst.BaseExpression para cumplir la covarianza
        old_attr = original_node.attr.value
        if old_attr in self.registry.attributes:
            if isinstance(original_node.value, cst.Name) and original_node.value.value in ["mime", "response", "event", "json"]:
                return updated_node
            
            self.attr_replacements += 1
            return updated_node.with_changes(attr=cst.Name(self.registry.attributes[old_attr]))
        return updated_node

    def leave_Arg(self, original_node: cst.Arg, updated_node: cst.Arg) -> Union[cst.Arg, cst.FlattenSentinel[cst.Arg], cst.RemovalSentinel]:
        # SOTA FIX: Firma de retorno extendida con los tipos exactos de la interfaz de LibCST
        if not original_node.keyword:
            return updated_node
            
        old_kw = original_node.keyword.value
        current_class = self.call_stack[-1] if self.call_stack else ""

        if current_class in self.registry.constructor_keywords:
            class_rules = self.registry.constructor_keywords[current_class]
            if old_kw in class_rules:
                self.kw_replacements += 1
                return updated_node.with_changes(keyword=cst.Name(class_rules[old_kw]))

        if old_kw in self.registry.keywords:
            self.kw_replacements += 1
            return updated_node.with_changes(keyword=cst.Name(self.registry.keywords[old_kw]))

        return updated_node

class MigrationEngine:
    """Orquestador físico del pipeline de codemods con soporte SRE."""
    def __init__(self, registry: MigrationRegistry, includes: List[str], extensions: Set[str], dry_run: bool, report_only: bool, backup: bool) -> None:
        self.registry = registry
        self.includes = includes
        self.extensions = extensions
        self.dry_run = dry_run
        self.report_only = report_only
        self.backup = backup
        
        self.files_scanned = 0
        self.files_modified = 0
        self.total_attr_changes = 0
        self.total_kw_changes = 0

    def execute(self) -> None:
        for target in self.includes:
            if not os.path.exists(target):
                continue
            if os.path.isfile(target):
                self._process_file(target)
            else:
                for root, _, files in os.walk(target):
                    if any(ex in root for exclude in [".venv", "venv", "__pycache__", ".git", "graveyard"] for ex in [exclude, "/" + exclude]):
                        continue
                    for file in files:
                        if any(file.endswith(ext) for ext in self.extensions):
                            self._process_file(os.path.join(root, file))
        self._print_summary()

    def _process_file(self, filepath: str) -> None:
        self.files_scanned += 1
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = cst.parse_module(source)
            transformer = MasterMigrationTransformer(self.registry)
            modified_tree = tree.visit(transformer)
            
            if modified_tree.code != source:
                self.files_modified += 1
                self.total_attr_changes += transformer.attr_replacements
                self.total_kw_changes += transformer.kw_replacements
                
                if not self.report_only:
                    mode_prefix = "[DRY-RUN]" if self.dry_run else "[MIGRADO]"
                    print(f"{mode_prefix} {filepath} (+{transformer.attr_replacements} attr, +{transformer.kw_replacements} kw)")
                
                if not self.dry_run:
                    if self.backup:
                        shutil.copyfile(filepath, filepath + ".bak")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(modified_tree.code)
        except Exception as e:
            print(f"[ERROR] Crash de análisis en {filepath}: {e}", file=sys.stderr)

    def _print_summary(self) -> None:
        print("\n" + "="*45)
        print("📊 METRICAS CONSOLIDADAS DEL MIGRATION ENGINE")
        print("="*45)
        print(f"Archivos escaneados:       {self.files_scanned}")
        print(f"Archivos modificados:      {self.files_modified}")
        print(f"Reemplazos de atributos:   {self.total_attr_changes}")
        print(f"Reemplazos de keywords:    {self.total_kw_changes}")
        print("-" * 45)
        print(f"Total de mutaciones AST:   {self.total_attr_changes + self.total_kw_changes}")
        print("="*45 + "\n")