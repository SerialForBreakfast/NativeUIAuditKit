"""Build and verify the standalone inline fragment from the frozen data snapshot."""
from pathlib import Path
import base64,gzip,hashlib,json,re,ast
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
data=json.loads((ROOT/'data.json').read_text())
notes_node=next(n for n in ast.walk(ast.parse((ROOT/'export_snapshot.py').read_text())) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='notes'for t in n.targets))
notes=ast.literal_eval(notes_node.value)
for experiment in data['experiments']:
 if experiment['id']in notes:experiment['outcome'],experiment['reason']=notes[experiment['id']]
(ROOT/'data.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False))
assert len({n['id']for n in data['jobs']})==len(data['jobs'])
assert len({n['id']for n in data['experiments']})==len(data['experiments'])
for a,b,*_ in data['edges']:assert 0<=a<len(data['jobs']) and 0<=b<len(data['jobs']) and a!=b
owners=[j for e in data['experiments']for j in e['owned']]
assert len(owners)==len(set(owners))==len(data['jobs'])
for e in data['experiments']:
 assert e['owned']or e['start'] is None
 assert e['state']!='complete'or e['owned']
 assert set(e['owned'])<=set(e['members'])
for ident in ['B405-271','B405-272','B405-273','B405-276','HCF574','IOS573']:
 assert next(e for e in data['experiments']if e['id']==ident)['outcome']=='contradicted'
assert next(e for e in data['experiments']if e['id']=='B405-277')['outcome']=='not-assessed'
raw=(ROOT/'data.json').read_bytes();payload=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
assert json.loads(gzip.decompress(base64.b64decode(payload)))==data
vendor=(PROJECT/'scripts/vendor/cytoscape-3.33.1/cytoscape.min.js').read_bytes()
assert hashlib.sha256(vendor).hexdigest()=='f55947f3daa3bae53209d4b885c195c157f595c225e508a6b382598d9452d6e2'
template=(ROOT/'atlas-fragment.html').read_text()
assert not re.search(r'\b(fetch|XMLHttpRequest|WebSocket)\s*\(',template)
assert not any(s in template.lower()for s in ('<!doctype','<html>','<head>','<body>'))
fragment=template.replace('__ATLAS_PAYLOAD__',payload).replace('__ATLAS_VENDOR__',base64.b64encode(gzip.compress(vendor,mtime=0)).decode())
assert len(fragment.encode())<1000000
(ROOT/'experiment-atlas.html').write_text(fragment)
manifest=json.loads((ROOT/'manifest.json').read_text());manifest.update(snapshotSHA256=hashlib.sha256(raw).hexdigest(),fragmentSHA256=hashlib.sha256(fragment.encode()).hexdigest(),fragmentBytes=len(fragment.encode()),jsonBytes=len(raw),compressedBytes=len(payload),dataChecks='passed: identifiers, edges, ownership, non-execution, known rejections, native non-acceptance, compression, vendor integrity, no network data calls')
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
