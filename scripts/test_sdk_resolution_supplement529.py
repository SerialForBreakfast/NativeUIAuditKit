import copy
import unittest
from unittest.mock import patch
import research_queue as q
import sdk_endpoint_focus520 as m

class SupplementTests(unittest.TestCase):
    def setUp(self):
        self.path=q.ROOT/'reports/work/SDK529/supplement/sdk529-resolution-supplement-03-request.json'
        self.request=q.load(self.path)
    def test_baseline_order_and_duplicate_boxes_preserved(self):
        old=[[0,0,10,10],[0,0,10,10]]
        boxes,count=m.supplement_boxes(old,[[1,1,10,10],[40,40,10,10]])
        self.assertEqual(boxes,old+[[40,40,10,10]]);self.assertEqual(count,1)
    def test_matched_inputs_and_declared_reads(self):
        frames=m.prepare(self.request);arms=m.proposal_inputs(self.request,frames)
        for old,new in zip(arms['baseline'],arms['candidate']):
            self.assertEqual(new['boxes'][:len(old['boxes'])],old['boxes'])
        spec=m.build(self.path);q.validate(spec);q.verify_pins(spec)
        self.assertEqual(spec['authority'],'diagnostic')
    def test_changed_model_rejected(self):
        load=q.load
        def altered(path):
            d=load(path)
            if '/scoped/' in str(path):d['runtime']['detector']['weightsSHA256']='0'*64
            return d
        with patch.object(q,'load',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'detector_changed'):m.prepare(self.request)
    def test_changed_resolution_rejected(self):
        load=q.load
        def altered(path):
            d=load(path)
            if '/scoped/' in str(path):d['configuration']['imageSize']=1280
            return d
        with patch.object(q,'load',side_effect=altered):
            with self.assertRaisesRegex(ValueError,'proposal_settings'):m.prepare(self.request)
    def test_changed_confidence_rejected(self):
        r=copy.deepcopy(self.request);r['proposals']['candidate']['confidence']=.1
        with self.assertRaisesRegex(ValueError,'proposal_threshold'):m.prepare(r)
    def test_unknown_mode_rejected(self):
        r=copy.deepcopy(self.request);r['proposalMode']='arbitrary'
        with self.assertRaisesRegex(ValueError,'proposal_mode'):m.prepare(r)

if __name__=='__main__':unittest.main()
