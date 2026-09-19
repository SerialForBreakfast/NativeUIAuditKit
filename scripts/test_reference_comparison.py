import unittest
from reference_comparison import ComparisonError,compare
class T(unittest.TestCase):
 def doc(self): return {'formatVersion':'prediction-artifact-v1','complete':True,'corpusSHA256':'c','labelsSHA256':'l','categoryMapSHA256':'m','settingsSHA256':'s','results':[{'imageID':'x'}],'metrics':{'map50':.5}}
 def test_zero_and_delta(self):
  a=self.doc(); self.assertEqual(compare(a,a)['deltas']['map50'],0); b=self.doc(); b['metrics']['map50']=.6; self.assertAlmostEqual(compare(a,b)['deltas']['map50'],.1)
 def test_rejects_incompatible(self):
  a=self.doc(); b=self.doc(); b['labelsSHA256']='bad'
  with self.assertRaisesRegex(ComparisonError,'incompatible'): compare(a,b)
if __name__=='__main__': unittest.main()
