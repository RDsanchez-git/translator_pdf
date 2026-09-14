import json
import re
import sys
from pathlib import Path

doc = sys.argv[1]
p = Path(f'tests/corpus/canonical/ground_truth/{doc}.json')
nodes = json.loads(p.read_text(encoding='utf-8'))
pat = re.compile(r"^value='([^']+)'$")
lineage, ids = [], []
for n in nodes:
    m = pat.match(n['node_id'])
    if m:
        n['node_id'] = m.group(1)
        lineage.append({'old_id': m.group(0), 'new_id': m.group(1)})
    ids.append(n['node_id'])
    md = n.get('metadata')
    if isinstance(md, dict) and md.get('parent_node_id'):
        m2 = pat.match(md['parent_node_id'])
        if m2:
            md['parent_node_id'] = m2.group(1)
if len(ids) != len(set(ids)):
    raise SystemExit(f'COLISION post-canonicalizacion en {doc}')
p.write_text(json.dumps(nodes, indent=2, ensure_ascii=False), encoding='utf-8')
Path(f'tests/corpus/canonical/{doc}_canonicalization_lineage.json').write_text(json.dumps(lineage, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'{doc}: {len(lineage)}/{len(nodes)} canonicalizados, 0 colisiones')
