import argparse
from tools.codemods.engine import MigrationRegistry, MigrationEngine

def main() -> None:
    parser = argparse.ArgumentParser(description="SOTA Platform Migration Client")
    parser.add_argument("--include", nargs="+", required=True, help="Rutas o Bounded Contexts a procesar.")
    parser.add_argument("--extensions", nargs="+", default=[".py"], help="Extensiones de archivo objetivo.")
    parser.add_argument("--report-only", action="store_true", help="Oculta el detalle por archivo, muestra solo el resumen.")
    parser.add_argument("--backup", action="store_true", help="Genera archivos .bak físicos antes de escribir.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Modo simulación analítica.")
    group.add_argument("--apply", action="store_true", help="Escritura destructiva en disco.")
    
    args = parser.parse_args()

    # =====================================================================
    # ESPECIFICACIÓN DECLARATIVA DE LA MIGRACIÓN (FASE 16.10)
    # =====================================================================
    registry = MigrationRegistry()
    
    # Reglas para el Hito 1: ASTNode.type -> node_type
    registry.rename_attribute(old="type", new="node_type")
    registry.rename_constructor_keyword(class_name="ASTNode", old="type", new="node_type")
    registry.rename_constructor_keyword(class_name="TranslationUnit", old="chunk_type", new="chunk_type") # Ej. de persistencia
    
    # Reglas futuras listas para activar des-comentando:
    # registry.rename_attribute(old="content", new="payload")
    # registry.rename_constructor_keyword(class_name="ASTNode", old="content", new="payload")

    engine = MigrationEngine(
        registry=registry,
        includes=args.include,
        extensions=set(args.extensions),
        dry_run=args.dry_run,
        report_only=args.report_only,
        backup=args.backup
    )
    engine.execute()

if __name__ == "__main__":
    main()