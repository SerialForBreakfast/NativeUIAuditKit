"""R-A offline inventory and capture-matrix validation; no device operations."""
from collections import Counter
class MatrixError(ValueError): pass
def validate(rows, matrix):
 ids=set(); hashes=set(); counts=Counter(); labeled=0; screenshots=0
 for r in rows:
  required=('id','contentSHA256','app','surface','os','device','provenance','annotationStatus')
  if not all(r.get(k) for k in required): raise MatrixError('missing_provenance')
  if r['id'] in ids or r['contentSHA256'] in hashes: raise MatrixError('duplicate_content')
  if r['annotationStatus']=='prediction': raise MatrixError('prediction_not_ground_truth')
  ids.add(r['id']); hashes.add(r['contentSHA256']); counts[(r['app'],r['surface'])]+=1; screenshots+=1
  labeled += r['annotationStatus']=='groundTruth'
 for cell,target in matrix.items():
  if target<1: raise MatrixError('invalid_target')
  if counts[cell]>target: raise MatrixError('matrix_overflow')
 if sum(matrix.values())<500: raise MatrixError('insufficient_matrix_target')
 return {'uniqueScreenshots':screenshots,'labeledMAPExamples':labeled,'unlabeledScreenshots':screenshots-labeled,'cellCounts':{f'{a}/{s}':n for (a,s),n in counts.items()},'remaining':{f'{a}/{s}':n-counts[(a,s)] for (a,s),n in matrix.items()}}
