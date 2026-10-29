import copy,tempfile,unittest
from pathlib import Path
from PIL import Image
import research_queue as q
from experiment_templates import pin
from test_sdk_packet502 import sample
import sdk_annotations529 as m

class AnnotationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.image=self.root/'frame.png';Image.new('RGB',(1,1)).save(self.image);self.e=sample(self.image)
  for side in ('before','after'):
   self.e[side]['focusID']=None;self.e[side]['elements'][0]['className']='UIButton'
  self.policy=dict(rules=[{'id':'test','class':'primaryButton','match':{'nativeClass':'UIButton','registeredID':'button'},'reviewer':'software-test','evidence':'explicit synthetic test role'}],taxonomy=['primaryButton','secondaryButton'],coverage=dict(scope='registered_only',reviewer=None,evidence=None,expectedIDs=[]),transform=None)
 def test_partial_inventory_never_becomes_complete(self):
  r=m.annotations(self.e,self.image,self.policy);self.assertEqual(r['qualifiedIDs'],['button']);self.assertFalse(r['completeSupportedInventory'])
 def test_disabled_control_remains_detector_target(self):
  for side in ('before','after'):self.e[side]['elements'][0]['observedState']['enabled']=False
  self.assertEqual(m.annotations(self.e,self.image,self.policy)['qualifiedIDs'],['button'])
 def test_unknown_and_conflicting_class_remain_unmapped(self):
  rule=copy.deepcopy(self.policy['rules'][0]);rule['class']='secondaryButton';self.policy['rules'].append(rule)
  self.assertEqual(m.annotations(self.e,self.image,self.policy)['unresolvedIDs'],['button'])
 def test_duplicate_annotations_are_not_complete(self):
  for side in ('before','after'):
   other=copy.deepcopy(self.e[side]['elements'][0]);other['identity']['id']='other';self.e[side]['elements'].append(other)
  rule=copy.deepcopy(self.policy['rules'][0]);rule['match']['registeredID']='other';self.policy['rules'].append(rule)
  self.assertEqual(m.annotations(self.e,self.image,self.policy)['duplicates'],[['button','other']])
 def test_complete_inventory_requires_exact_review(self):
  p=self.root/'coverage.json';q.save(p,{'softwareOnly':True});self.policy['coverage'].update(scope='complete_supported_classes',reviewer='software-test',evidence=pin(p),expectedIDs=['button'])
  self.assertTrue(m.annotations(self.e,self.image,self.policy)['completeSupportedInventory'])
  self.policy['coverage']['expectedIDs'].append('missing')
  with self.assertRaisesRegex(ValueError,'inventory'):m.annotations(self.e,self.image,self.policy)
 def test_unknown_coordinates_and_explicit_transform(self):
  for side in ('before','after'):self.e[side]['elements'][0]['coordinateSpace']='windowPoints'
  self.assertEqual(m.annotations(self.e,self.image,self.policy)['unresolvedIDs'],['button'])
  p=self.root/'transform.json';q.save(p,{'softwareOnly':True});self.policy['transform']=dict(coordinateSpace='windowPoints',affine=[1,0,0,1,0,0],evidence=pin(p))
  self.assertEqual(m.annotations(self.e,self.image,self.policy)['qualifiedIDs'],['button'])
 def test_unlabelled_is_not_missed_and_predictions_are_unchanged(self):
  rows=m.annotations(self.e,self.image,self.policy)['rows'];pred=[{'box':[0,0,1,1],'class':'primaryButton'}];original=copy.deepcopy(pred)
  r=m.compare_labels(rows,pred,{})
  self.assertEqual(r['baseline']['unlabelledIDs'],['button']);self.assertEqual(r['baseline']['unmatchedIDs'],[])
  self.assertEqual(r['reviewed']['matchedIDs'],['button']);self.assertFalse(r['modelImprovement']);self.assertEqual(pred,original)

 def test_production_mapping_requires_verified_source(self):
  policy=self.root/'policy.json';q.save(policy,self.policy)
  request=dict(version='sdk-annotation-review-v1',id='review-source',frames=[{}],policy=pin(policy))
  with self.assertRaisesRegex(ValueError,'mapping_evidence_pin'):m.evaluate(request)
  source=self.root/'source.json';q.save(source,{'role':'primaryButton','softwareOnly':True})
  self.policy['rules'][0]['evidence']=pin(source);q.save(policy,self.policy,replace=True);request['policy']=pin(policy)
  source.write_text('changed')
  with self.assertRaises(ValueError):m.evaluate(request)

if __name__=='__main__':unittest.main()
