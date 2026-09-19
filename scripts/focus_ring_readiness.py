"""Offline FR-A quota, pair-integrity, and seed-split validator."""
from collections import Counter
class ReadinessError(ValueError): pass
MIN={'gridMatrix':2000,'mediaShelf':1500,'settingsList':1000,'actionDialog':500,'heroCarousel':500,'focusMaze':500}
def validate(rows):
 seen=set(); scene=Counter(); theme=Counter(); hard=Counter()
 for r in rows:
  if not r.get('focused') or not r.get('unfocused') or r.get('labelSource')=='modelPrediction': raise ReadinessError('invalid_pair')
  if r['seed'] in seen: raise ReadinessError('seed_leakage')
  seen.add(r['seed']); scene[r['scene']]+=1; theme[(r['scene'],r['theme'])]+=1
  if r.get('hardNegative'): hard[(r['theme'],r['class'])]+=1
 if any(scene[x]<n for x,n in MIN.items()) or any(theme[(s,t)]<.2*MIN[s] for s in ('gridMatrix','mediaShelf') for t in ('light','highContrast')): raise ReadinessError('underfilled_quota')
 if sum(hard.values())<100 or any(not hard[(t,c)] for t in ('light','highContrast') for c in ('imageView','collectionItem')): raise ReadinessError('empty_hard_negative_stratum')
 return {'pairs':len(rows),'sceneCounts':dict(scene),'hardNegativeCounts':dict(hard)}
