"""tools/evaluation/view_gt_html.py

Genera un HTML legible del Ground Truth de un documento para facilitar la curación manual.

Uso:
    python -m tools.evaluation.view_gt_html --doc-id doc_08_bilingual_cs --corpus-dir tests/corpus/canonical
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def render_gt_html(nodes: list[dict], doc_id: str) -> str:
    """Genera HTML legible del GT."""
    rows = []
    for i, node in enumerate(nodes):
        node_id = node.get('node_id', '?')
        node_type = node.get('node_type', '?')
        strategy = node.get('strategy', '?')
        payload = node.get('payload', {})
        content = ''
        if isinstance(payload, dict):
            content = payload.get('content', '') or payload.get('text_content', '')
        elif isinstance(payload, str):
            content = payload

        # Colorear por tipo de nodo
        type_color = {
            'heading': '#e3f2fd',
            'paragraph': '#ffffff',
            'math': '#fff3e0',
            'code': '#f3e5f5',
            'table': '#e8f5e9',
            'image': '#fce4ec',
            'list': '#f1f8e9',
        }.get(node_type, '#ffffff')

        # Resaltar code-switching (palabras en español)
        spanish_words = ['los', 'las', 'que', 'una', 'para', 'con', 'esta', 'este', 'todos',
                        'muy', 'pero', 'como', 'todo', 'tiene', 'puede', 'mejor', 'aquí',
                        'está', 'eso', 'ese', 'ella', 'él', 'sí', 'no', 'casaron', 'solteros',
                        'puedo', 'hacer', 'estar', 'necesita', 'dolieron', 'remedios',
                        'damn', 'damm', 'forever', 'alone', 'lol', 'we', 'still', 'single',
                        'todos', 'nosotras', 'estamos', 'solitarias', 'siguen', 'casó',
                        'mundo', 'todo', 'se', 'fueron', 'a', 'casarse', 'y', 'nosotros',
                        'seguimos', 'solteros', 'me', 'siento', 'tan', 'pendejo', 'right', 'now',
                        'best', 'i', 'can', 'do', 'is', 'be', 'here', 'for', 'him', 'if', 'needs',
                        'lo', 'mejor', 'puedo', 'hacer', 'es', 'estar', 'aquí', 'para', 'él',
                        'si', 'necesita', 'wasnt', 'happy', 'because', 'they', 'got', 'hurt',
                        'wasnt', 'happy', 'because', 'me', 'dolieron', 'old', 'mexican', 'remedies',
                        'old', 'school', 'remedios', 'mexicanos']
        words = content.split()
        highlighted = []
        for w in words:
            clean_w = w.strip('.,!?;:')
            if clean_w.lower() in spanish_words:
                highlighted.append(f'<span style="color:red;font-weight:bold;">{html.escape(w)}</span>')
            else:
                highlighted.append(html.escape(w))
        content_highlighted = ' '.join(highlighted)

        rows.append(f"""
        <tr style="background-color:{type_color};">
            <td style="padding:8px;border:1px solid #ddd;">{i}</td>
            <td style="padding:8px;border:1px solid #ddd;font-family:monospace;">{html.escape(node_id)}</td>
            <td style="padding:8px;border:1px solid #ddd;">{html.escape(node_type)}</td>
            <td style="padding:8px;border:1px solid #ddd;">{html.escape(strategy)}</td>
            <td style="padding:8px;border:1px solid #ddd;white-space:pre-wrap;">{content_highlighted}</td>
        </tr>""")

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ground Truth: {html.escape(doc_id)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th {{ background-color: #4CAF50; color: white; padding: 10px; border: 1px solid #ddd; }}
        .legend {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        .legend span {{ display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; }}
    </style>
</head>
<body>
    <h1>Ground Truth: {html.escape(doc_id)}</h1>
    <p>Total nodos: {len(nodes)}</p>
    <div class="legend">
        <strong>Leyenda:</strong>
        <span style="background:#e3f2fd;"></span> heading
        <span style="background:#ffffff;border:1px solid #ddd;"></span> paragraph
        <span style="background:#fff3e0;"></span> math
        <span style="background:#f3e5f5;"></span> code
        <span style="background:#e8f5e9;"></span> table
        <span style="background:#fce4ec;"></span> image
        <span style="background:#f1f8e9;"></span> list
        <br>
        <strong>Code-switching:</strong> palabras en español resaltadas en <span style="color:red;font-weight:bold;">rojo</span>
    </div>
    <table>
        <tr>
            <th>#</th>
            <th>node_id</th>
            <th>node_type</th>
            <th>strategy</th>
            <th>content</th>
        </tr>
        {''.join(rows)}
    </table>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description='Genera HTML legible del Ground Truth de un documento.')
    parser.add_argument('--doc-id', required=True, help='ID del documento (ej. doc_08_bilingual_cs)')
    parser.add_argument('--corpus-dir', type=Path, default=Path('tests/corpus/canonical'),
                        help='Directorio raíz del corpus canónico')
    args = parser.parse_args()

    gt_path = args.corpus_dir / 'ground_truth' / f'{args.doc_id}.json'
    if not gt_path.exists():
        print(f'ERROR: GT no encontrado: {gt_path}')
        return

    nodes = json.loads(gt_path.read_text(encoding='utf-8'))
    html_content = render_gt_html(nodes, args.doc_id)

    output_path = gt_path.with_suffix('.html')
    output_path.write_text(html_content, encoding='utf-8')
    print(f'HTML generado: {output_path}')


if __name__ == '__main__':
    main()
