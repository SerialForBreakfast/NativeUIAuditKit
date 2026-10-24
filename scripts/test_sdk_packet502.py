"""Software contract tests only. These packets are not captured SDK evidence."""
import copy
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import research_queue as q
from sdk_packet502 import review, review_request, build
from experiment_templates import pin


def sample(image):
    element=dict(identity=dict(id='button', lifetime='test-lifetime', revision=1), coordinateSpace='screenPixels',
        bounds=dict(x=0,y=0,width=1,height=1), hidden=False, enabled=True, selected=False,
        observedState=dict(source='uikit_ancestor_state',hidden=False,enabled=True,effectiveAlpha=1))
    observation=dict(appID='software-test',processID='test-process',runID='test-run',focusID='button',
        focusKnown=True,interrupted=False,sourceKind='authenticated_sdk_challenge',elements=[element])
    return dict(schemaVersion=1, admission='review_only',labelSource='sdk_reported_focus_and_registered_geometry',
        imageSHA256=q.digest(image),imageBytes=image.stat().st_size,width=1,height=1,
        captureStartNS=1,captureEndNS=2,observationEndNS=3,clockID='test-clock',captureID='test-capture',
        sourceID='software-test',issues=[],before=copy.deepcopy(observation),after=copy.deepcopy(observation))


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.addCleanup(self.tmp.cleanup)
        self.image=Path(self.tmp.name)/'frame.png';Image.new('RGB',(1,1)).save(self.image)
        self.doc=sample(self.image)

    def test_focus_states_are_distinct(self):
        self.assertEqual(review(self.doc,self.image)['focusState'],'focused')
        for side in ('before','after'):self.doc[side].pop('focusID')
        self.assertEqual(review(self.doc,self.image)['focusState'],'no_focus')
        self.doc['after']['focusKnown']=False
        r=review(self.doc,self.image)
        self.assertEqual(r['focusState'],'unknown');self.assertFalse(r['trainingEligible'])

    def test_inventory_drift_and_point_coordinates_are_not_labels(self):
        self.doc['after']['elements'][0]['identity']['revision']=2
        self.assertIn('registered_inventory_changed_during_capture',review(self.doc,self.image)['reasons'])
        self.doc=sample(self.image)
        for side in ('before','after'):self.doc[side]['elements'][0]['coordinateSpace']='windowPoints'
        r=review(self.doc,self.image);self.assertEqual(r['focusState'],'unknown')
        self.assertIsNone(r['elements'][0]['pixelBounds'])

    def test_reported_problems_and_stale_brackets_remain_unknown(self):
        for mutate in ('expired','clock','identity'):
            doc=copy.deepcopy(self.doc)
            if mutate=='expired':doc['issues']=['observation_expired']
            elif mutate=='clock':doc['observationEndNS']=2000000000
            else:doc['after']['runID']='different'
            with self.subTest(mutate=mutate):self.assertEqual(review(doc,self.image)['focusState'],'unknown')

    def test_corrupt_pixels_and_duplicate_ids_fail(self):
        self.doc['imageSHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'sdk_packet_pixels'):review(self.doc,self.image)
        self.doc=sample(self.image);self.doc['after']['elements']*=2
        with self.assertRaisesRegex(ValueError,'sdk_packet_duplicate_identity'):review(self.doc,self.image)

    def request(self):
        evidence=Path(self.tmp.name)/'evidence.json';q.save(evidence,self.doc)
        return dict(version='sdk-packet-request-v1',id='sdk503-software',evidence=pin(evidence),image=pin(self.image),
            expectedAppID='software-test',expectedSourceID='software-test',group='software-only',role='review_only')

    def test_request_preserves_group_and_compiles_existing_queue_spec(self):
        request=self.request();path=Path(self.tmp.name)/'request.json';q.save(path,request)
        spec=build(path);q.validate(spec);q.verify_pins(spec)
        result=review_request(request)
        self.assertEqual(result['group'],'software-only');self.assertFalse(result['trainingEligible'])
        self.assertEqual(spec['authority'],'diagnostic')

    def test_request_rejects_wrong_app_source_and_training_role(self):
        request=self.request()
        for key,value,reason in [('expectedAppID','other','sdk_request_app_mismatch'),
                ('expectedSourceID','other','sdk_request_source_mismatch'),('role','training','sdk_request_role')]:
            changed=copy.deepcopy(request);changed[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,reason):review_request(changed)
