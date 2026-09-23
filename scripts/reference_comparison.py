"""P2-A strict comparison of completed prediction-artifact-v1 documents."""
from __future__ import annotations
import hashlib, json, math

class ComparisonError(ValueError): pass

def _identity(document:dict)->dict:
 if document.get('formatVersion')!='prediction-artifact-v1': raise ComparisonError('unsupported_artifact')
 corpus=document.get('corpus'); category=document.get('categoryMap'); complete=document.get('completeness')
 results=document.get('results')
 if not isinstance(corpus,dict) or not isinstance(category,dict) or not isinstance(complete,dict) or complete.get('complete') is not True or not isinstance(results,list): raise ComparisonError('incomplete_artifact')
 ids=[]; labels=[]; images=[]
 for row in results:
  if not isinstance(row,dict) or not isinstance(row.get('imageID'),str) or not isinstance(row.get('imageSHA256'),str) or not isinstance(row.get('labelSHA256'),str): raise ComparisonError('invalid_result')
  if row.get('status') not in ('ok','empty'): raise ComparisonError('failed_or_invalid_prediction')
  ids.append(row['imageID']); images.append((row['imageID'],row['imageSHA256'])); labels.append((row['imageID'],row['labelSHA256']))
 requested=complete.get('requestedImageIDs')
 if not isinstance(requested,list) or not requested or any(not isinstance(i,str) or not i for i in requested): raise ComparisonError('incompatible_members')
 if len(set(requested))!=len(requested) or len(set(ids))!=len(ids) or set(ids)!=set(requested): raise ComparisonError('incompatible_members')
 metrics=document.get('metrics')
 if metrics is not None and not isinstance(metrics,dict): raise ComparisonError('invalid_metrics')
 if metrics is not None:
  for key,value in metrics.items():
   if not isinstance(key,str) or not key: raise ComparisonError('invalid_metrics')
   if value is not None:
    try: valid=type(value) in (int,float) and math.isfinite(value)
    except OverflowError: valid=False
    if not valid: raise ComparisonError('invalid_metrics')
 return {'corpusSHA256':corpus.get('contentSHA256'),'labelsSHA256':hashlib.sha256(json.dumps(sorted(labels),separators=(',',':')).encode()).hexdigest(),'imagesSHA256':hashlib.sha256(json.dumps(sorted(images),separators=(',',':')).encode()).hexdigest(),'categoryMapSHA256':category.get('sha256'),'settingsSHA256':document.get('settingsSHA256'),'ids':set(ids),'metrics':metrics}

def compare(left:dict,right:dict)->dict:
 a,b=_identity(left),_identity(right)
 required=('corpusSHA256','labelsSHA256','imagesSHA256','categoryMapSHA256','settingsSHA256')
 if any(not a[k] or a[k]!=b[k] for k in required): raise ComparisonError('incompatible_inputs')
 if a['ids']!=b['ids']: raise ComparisonError('incompatible_members')
 left_metrics=a['metrics'] or {}; right_metrics=b['metrics'] or {}
 keys=sorted(set(left_metrics)|set(right_metrics))
 deltas={}; unavailable={}
 for key in keys:
  missing=[side for side,metrics in (('left',left_metrics),('right',right_metrics)) if metrics.get(key) is None]
  if missing:
   unavailable[key]=missing
  else:
   delta=right_metrics[key]-left_metrics[key]
   try: finite=math.isfinite(delta)
   except OverflowError: finite=False
   if not finite: raise ComparisonError('nonfinite_delta')
   deltas[key]=delta
 availability='partial' if deltas and unavailable else ('available' if deltas else 'unavailable')
 stable={k:a[k] for k in required}
 return {'formatVersion':'reference-comparison-v1','compatible':True,'metricAvailability':availability,'deltas':deltas,'unavailableMetrics':unavailable,'sampleCount':len(a['ids']),'stableInputSHA256':hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
