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
 def test_missing_individual_keys_and_null_are_never_zero(self):
  a=self.doc(); b=self.doc(); a['metrics'].update(toggle=.9,webContent=None); b['metrics'].update(stepper=.8,webContent=None)
  result=compare(a,b)
  self.assertEqual(result['metricAvailability'],'partial')
  self.assertEqual(result['deltas'],{'map50':0})
  self.assertEqual(result['unavailableMetrics'],{'stepper':['left'],'toggle':['right'],'webContent':['left','right']})
  self.assertEqual(compare(b,a)['deltas'],{'map50':0})
 def test_empty_or_disjoint_metrics_are_unavailable(self):
  a=self.doc(); b=self.doc(); a['metrics']={}; b['metrics']={}
  self.assertEqual(compare(a,b)['metricAvailability'],'unavailable')
  a['metrics']={'first':.5}; b['metrics']={'second':.6}
  self.assertEqual(compare(a,b)['deltas'],{})
  self.assertEqual(compare(a,b)['metricAvailability'],'unavailable')
 def test_invalid_values_fail_even_when_other_side_missing(self):
  for value in [True,False,float('nan'),float('inf'),-float('inf'),'0.5',[],{},10**1000]:
   a=self.doc(); b=self.doc(); a['metrics']={'bad':value}; b['metrics']=None
   with self.subTest(value=type(value).__name__), self.assertRaises(ComparisonError): compare(a,b)
  a=self.doc(); b=self.doc(); a['metrics']={'x':-1e308}; b['metrics']={'x':1e308}
  with self.assertRaisesRegex(ComparisonError,'nonfinite_delta'): compare(a,b)
 def test_truthy_completion_and_duplicate_requests_rejected(self):
  a=self.doc(); a['completeness']['complete']='yes'
  with self.assertRaises(ComparisonError): compare(a,self.doc())
  a=self.doc(); a['completeness']['requestedImageIDs']=['x','x']
  with self.assertRaises(ComparisonError): compare(a,self.doc())
if __name__=='__main__': unittest.main()
