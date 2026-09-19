"""P4-B deterministic split-safe assembly; consumes normalized record dictionaries."""
from __future__ import annotations
import hashlib, json
class AssemblyError(ValueError): pass
def assemble(records:list[dict], blend:dict[str,int]|None=None)->dict:
 blend=blend or {}; seen={}; result={"training":[],"validation":[],"test":[],"calibration":[],"held-out":[]}; coverage={}
 for r in sorted(records,key=lambda x:x['id']):
  split=r.get('split'); ident=r.get('id'); content=r.get('contentSHA256'); family=r.get('family')
  if split not in result or not ident or not content: raise AssemblyError('invalid_record')
  key=(content,family)
  if key in seen and seen[key]!=split: raise AssemblyError('cross_split_leakage')
  seen[key]=split
  if blend and r.get('source') in blend and sum(1 for x in result[split] if x.get('source')==r['source'])>=blend[r['source']]: continue
  result[split].append(dict(r))
  if split=='training':
   for c in r.get('classes',[]): coverage[c]=coverage.get(c,0)+1
 members=[x for xs in result.values() for x in xs]
 return {'formatVersion':'assembled-corpus-v1','membership':result,'trainingClassCounts':coverage,'memberDigest':hashlib.sha256(json.dumps(members,sort_keys=True).encode()).hexdigest(),'uncoveredClasses':sorted(set(c for r in records for c in r.get('classes',[]))-set(coverage))}
