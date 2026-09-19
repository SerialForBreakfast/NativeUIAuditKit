import unittest
from focus_ring_readiness import ReadinessError, validate, MIN

def rows():
 out=[]; n=0
 for scene,count in MIN.items():
  for i in range(count):
   theme=('light','highContrast')[i%2] if scene in ('gridMatrix','mediaShelf') else 'light'
   hard=scene=='gridMatrix' and i<100
   if hard: theme=('light','highContrast')[(i//2)%2]
   out.append({'focused':f'f{n}','unfocused':f'u{n}','labelSource':'fixtureGroundTruth','seed':f'{scene}-{i}','scene':scene,'theme':theme,'class':'imageView' if i%2 else 'collectionItem','hardNegative':hard}); n+=1
 return out
class Tests(unittest.TestCase):
 def test_valid(self): self.assertEqual(validate(rows())['pairs'],6000)
 def test_pair_seed_and_quota_rejections(self):
  r=rows(); r[0]['focused']=''
  with self.assertRaisesRegex(ReadinessError,'invalid_pair'): validate(r)
  r=rows(); r[1]['seed']=r[0]['seed']
  with self.assertRaisesRegex(ReadinessError,'seed_leakage'): validate(r)
  r=rows(); r=[x for x in r if x['scene']!='focusMaze']
  with self.assertRaisesRegex(ReadinessError,'underfilled_quota'): validate(r)
 def test_hard_negative_strata_rejection(self):
  r=rows()
  for x in r: x['hardNegative']=False
  with self.assertRaisesRegex(ReadinessError,'empty_hard_negative_stratum'): validate(r)
if __name__=='__main__': unittest.main()
