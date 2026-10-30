"""Replay export integrity tests. These do not establish model accuracy."""
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import research_queue as q
import real_app_benchmark543 as m

class ReplayAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.root=Path(self.tmp.name)
        Image.new('RGB',(10,8)).save(self.root/'source.png')
        self.source=q.digest(self.root/'source.png')
        self.manifest={'source_sha256':self.source}
        self.result={'action_authorized':False,'receipt':{'action_authorized':False,'width':10,'height':8,'image_sha256':self.source,'provider':{'partial':True,'elements':[]}},'predictionSelection':{'id':None,'status':'partial_provider_result'},'unavailable_provenance':['preprocessing_identity']}
    def tearDown(self):self.tmp.cleanup()
    def write(self):
        for name,value in [('input-manifest.json',self.manifest),('result.json',self.result)]:
            (self.root/name).write_text(json.dumps(value))
        c={'completed':True,**{key:q.digest(self.root/name) for name,key in [('source.png','source_sha256'),('input-manifest.json','input_manifest_sha256'),('result.json','result_sha256')]}}
        (self.root/'completion.json').write_text(json.dumps(c))
    def audit(self):return m.audit_replay(self.root,self.root/'audit.json')
    def test_partial_stays_ineligible(self):
        self.write();r=self.audit();self.assertTrue(r['providerPartial']);self.assertFalse(r['accuracyEligible']);self.assertEqual(r['unavailableProvenance'],['preprocessing_identity'])
    def test_tampered_result_rejected(self):
        self.write();(self.root/'result.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'replay_hash'):self.audit()
    def test_reference_input_rejected(self):
        self.manifest['focusBox']=[0,0,1,1];self.write()
        with self.assertRaisesRegex(ValueError,'reference_leakage'):self.audit()
    def test_false_selection_rejected(self):
        self.result['predictionSelection']={'id':'missing','status':'selected'};self.write()
        with self.assertRaisesRegex(ValueError,'replay_selection'):self.audit()
    def test_geometry_mismatch_rejected(self):
        self.result['receipt']['width']=9;self.write()
        with self.assertRaisesRegex(ValueError,'replay_geometry'):self.audit()
    def test_complete_export_still_needs_labels(self):
        self.result['receipt']['provider']={'partial':False,'elements':[{'id':'a','focused':True,'ambiguous':False}],'focus_execution':{'model_scoring_complete':True}}
        self.result['predictionSelection']={'id':'a','status':'selected'};self.write();self.assertFalse(self.audit()['accuracyEligible'])
if __name__=='__main__':unittest.main()
