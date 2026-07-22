import json
from pathlib import Path

VALID_AST_NODE_TYPES = {
    "composite_block",
    "heading",
    "paragraph",
    "display_equation",
    "inline_equation",
    "table_simple",
    "table_complex",
    "image",
    "caption",
    "code",
    "list"
}

TYPE_MAPPING = {
    "title": "heading",
    "author": "paragraph",
    "abstract": "paragraph",
    "header": "paragraph",
    "footer": "paragraph",
    "footnote": "paragraph",
    "page_number": "paragraph"
}

def main() -> None:
    gt_dir = Path("tests/corpus/calibration_v1/ground_truth")
    if not gt_dir.exists():
        print(f"[ERROR] No existe el directorio '{gt_dir}'.")
        return

    for json_file in gt_dir.glob("*.json"):
        content = json.loads(json_file.read_text(encoding="utf-8"))
        modified = False

        for node in content:
            current_type = node.get("node_type")
            if current_type not in VALID_AST_NODE_TYPES:
                new_type = TYPE_MAPPING.get(current_type, "paragraph")
                node["node_type"] = new_type
                modified = True

        if modified:
            json_file.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[OK] Ground Truth normalizado: '{json_file.name}'")

if __name__ == "__main__":
    main()