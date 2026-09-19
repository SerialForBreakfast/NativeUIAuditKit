"""P2-A strict comparison of completed prediction-artifact-v1 documents."""
from __future__ import annotations
import hashlib, json

class ComparisonError(ValueError): pass

def _identity(document:dict)->dict:
 if document.get('formatVersion')!='prediction-artifact-v1': raise ComparisonError('unsupported_artifact')
 corpus=document.get('corpus'); category=document.get('categoryMap'); complete=document.get('completeness')
 results=document.get('results')
 if not isinstance(corpus,dict) or not isinstance(category,dict) or not isinstance(complete,dict) or not complete.get('complete') or not isinstance(results,list): raise ComparisonError('incomplete_artifact')
 ids=[]; labels=[]; images=[]
 for row in results:
  if not isinstance(row,dict) or not isinstance(row.get('imageID'),str) or not isinstance(row.get('imageSHA256'),str) or not isinstance(row.get('labelSHA256'),str): raise ComparisonError('invalid_result')
  if row.get('status') not in ('ok','empty'): raise ComparisonError('failed_or_invalid_prediction')
  ids.append(row['imageID']); images.append((row['imageID'],row['imageSHA256'])); labels.append((row['imageID'],row['labelSHA256']))
 if len(set(ids))!=len(ids) or set(ids)!=set(complete.get('requestedImageIDs',[])): raise ComparisonError('incompatible_members')
 metrics=document.get('metrics')
 if metrics is not None and not isinstance(metrics,dict): raise ComparisonError('invalid_metrics')
 return {'corpusSHA256':corpus.get('contentSHA256'),'labelsSHA256':hashlib.sha256(json.dumps(sorted(labels),separators=(',',':')).encode()).hexdigest(),'imagesSHA256':hashlib.sha256(json.dumps(sorted(images),separators=(',',':')).encode()).hexdigest(),'categoryMapSHA256':category.get('sha256'),'settingsSHA256':document.get('settingsSHA256'),'ids':set(ids),'metrics':metrics}

def compare(left:dict,right:dict)->dict:
 a,b=_identity(left),_identity(right)
 required=('corpusSHA256','labelsSHA256','imagesSHA256','categoryMapSHA256','settingsSHA256')
 if any(not a[k] or a[k]!=b[k] for k in required): raise ComparisonError('incompatible_inputs')
 if a['ids']!=b['ids']: raise ComparisonError('incompatible_members')
 if a['metrics'] is None or b['metrics'] is None:
  stable={k:a[k] for k in required}
  return {'formatVersion':'reference-comparison-v1','compatible':True,'metricAvailability':'unavailable','deltas':{},'sampleCount':len(a['ids']),'stableInputSHA256':hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
 keys=sorted(set(a['metrics'])|set(b['metrics']))
 if any(not isinstance(a['metrics'].get(k,0),(int,float)) or not isinstance(b['metrics'].get(k,0),(int,float)) for k in keys): raise ComparisonError('invalid_metrics')
 stable={k:a[k] for k in required}
 return {'formatVersion':'reference-comparison-v1','compatible':True,'metricAvailability':'available','deltas':{k:b['metrics'].get(k,0)-a['metrics'].get(k,0) for k in keys},'sampleCount':len(a['ids']),'stableInputSHA256':hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
