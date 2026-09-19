"""P2-A strict comparison of completed prediction-artifact-v1 documents."""
from __future__ import annotations
import hashlib, json
class ComparisonError(ValueError): pass
def compare(left:dict,right:dict)->dict:
 for d in (left,right):
  if d.get('formatVersion')!='prediction-artifact-v1' or not d.get('complete'): raise ComparisonError('incomplete_artifact')
 required=('corpusSHA256','labelsSHA256','categoryMapSHA256','settingsSHA256')
 if any(left.get(k)!=right.get(k) for k in required): raise ComparisonError('incompatible_inputs')
 a,b=left.get('results',[]),right.get('results',[])
 if {x.get('imageID') for x in a}!={x.get('imageID') for x in b}: raise ComparisonError('incompatible_members')
 def metric(d): return d.get('metrics',{})
 keys=sorted(set(metric(left))|set(metric(right)))
 return {'formatVersion':'reference-comparison-v1','compatible':True,'deltas':{k:metric(right).get(k,0)-metric(left).get(k,0) for k in keys},'sampleCount':len(a),'stableInputSHA256':hashlib.sha256(json.dumps({k:left[k] for k in required},sort_keys=True).encode()).hexdigest()}
