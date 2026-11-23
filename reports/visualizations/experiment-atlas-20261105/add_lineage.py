"""Add verified pinned-output reuse. Reuse edges never become dispatch dependencies."""
from pathlib import Path
import json,re,sys,gzip,base64,hashlib
from collections import defaultdict
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import research_queue as q
x=json.loads((HERE/'data.json').read_text());ids={n['id']:i for i,n in enumerate(x['jobs'])}
pattern=re.compile(r'^reports/work/research-queue/jobs/([^/]+)/attempts/(\d+)/out/(.+)$')
cache={};receipts={};pairs={(a,b)for a,b,*_ in x['edges']};added=[];checked=0

def pins(value):
 if isinstance(value,dict):
  if isinstance(value.get('path'),str)and isinstance(value.get('sha256'),str):yield value
  for child in value.values():yield from pins(child)
 elif isinstance(value,list):
  for child in value:yield from pins(child)

def source_of(pin):
 m=pattern.fullmatch(pin.get('path',''))
 if not m or m[1] not in ids:return
 key=(m[1],m[2]);path=ROOT/'reports/work/research-queue/jobs'/m[1]/'attempts'/m[2]/'result.json'
 if key not in receipts:
  try:receipts[key]={r['path']:r['sha256']for r in json.loads(path.read_text()).get('outputs',[])}
  except(OSError,ValueError):receipts[key]={}
 if receipts[key].get(m[3])==pin['sha256']:return ids[m[1]]

for index,n in enumerate(x['jobs']):
 spec=json.loads((ROOT/n['spec']).read_text());refs=list(spec.get('inputs',[]))
 refs.extend(s['from']for s in spec.get('stage',[]))
 for ref in list(refs):
  rel=ref.get('path','');path=ROOT/rel
  if path.suffix!='.json' or not path.is_file()or path.stat().st_size>500000:continue
  key=(rel,ref.get('sha256'))
  if key not in cache:
   try:cache[key]=list(pins(json.loads(path.read_text())))if q.digest(path)==ref.get('sha256')else[]
   except(OSError,ValueError):cache[key]=[]
  refs.extend(cache[key])
 for ref in refs:
  parent=source_of(ref)
  if parent is not None and parent!=index and (parent,index)not in pairs:
   pairs.add((parent,index));added.append([parent,index,'reuse'])
x['edges'].extend(added)
owner={j:i for i,e in enumerate(x['experiments'])for j in e['owned']};epairs={(a,b)for a,b,*_ in x['experimentEdges']}
for a,b,t in added:
 aa,bb=owner[a],owner[b]
 if aa!=bb and(aa,bb)not in epairs:epairs.add((aa,bb));x['experimentEdges'].append([aa,bb,'reuse'])
x['limitations'].append('Dotted reuse links bind pinned artifact hashes to terminal output receipts. They are not runner prerequisites.')
raw=json.dumps(x,separators=(',',':'),ensure_ascii=False).encode();(HERE/'data.json').write_bytes(raw)
m=json.loads((HERE/'manifest.json').read_text());m['sourceCounts']['pinnedReuseLinks']=len(added);m['sourceCounts']['allLinks']=len(x['edges']);(HERE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('Verified pinned artifact reuse links:',len(added))
