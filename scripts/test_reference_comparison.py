import unittest
from reference_comparison import ComparisonError,compare
class T(unittest.TestCase):
 def doc(self): return {'formatVersion':'prediction-artifact-v1','corpus':{'contentSHA256':'c'},'categoryMap':{'sha256':'m'},'settingsSHA256':'s','completeness':{'complete':True,'requestedImageIDs':['x']},'results':[{'imageID':'x','imageSHA256':'i','labelSHA256':'l','status':'empty'}],'metrics':{'map50':.5}}
 def test_zero_and_delta(self):
  a=self.doc(); self.assertEqual(compare(a,a)['deltas']['map50'],0); b=self.doc(); b['metrics']['map50']=.6; self.assertAlmostEqual(compare(a,b)['deltas']['map50'],.1)
 def test_rejects_incompatible(self):
  a=self.doc(); b=self.doc(); b['results'][0]['labelSHA256']='bad'
  with self.assertRaisesRegex(ComparisonError,'incompatible'): compare(a,b)
  b=self.doc(); b['results'][0]['status']='failed'
  with self.assertRaisesRegex(ComparisonError,'failed'): compare(a,b)
 def test_missing_metrics_are_explicitly_unavailable(self):
  a=self.doc(); b=self.doc(); del a['metrics']; del b['metrics']
  result=compare(a,b); self.assertEqual(result['metricAvailability'],'unavailable'); self.assertEqual(result['deltas'],{})
if __name__=='__main__': unittest.main()
