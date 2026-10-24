"""Check additive producer metadata using retained captures, without device calls."""
import copy
import unittest
import research_queue as q
from harvest_artwork_geometry import validate
from harvest_sidecar_v2 import require, scene_check
from ttr_campaign_queue493 import export_labels


class ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=q.QUEUE/'jobs/adr493-session-1-r4/attempts/1/out/corpus'
        cls.scene=q.load(next(cls.folder.rglob('after.json')))['capture_endpoint']['after_scene']
        cls.element=next(e for e in cls.scene['elements'] if (e.get('artwork_geometry') or {}).get('presentation'))
        cls.size=(cls.scene['scene_width'],cls.scene['scene_height'])
        cls.generation=cls.scene['focus_observation']['generation']

    def check(self,value):
        validate(value,self.size,require,element_id=self.element['element_id'],generation=self.generation)

    def test_current_and_legacy_geometry(self):
        value=copy.deepcopy(self.element['artwork_geometry']);self.check(value)
        value.pop('presentation');self.check(value)
        value['presentation']=None;self.check(value)

    def test_identity_and_geometry_fail_closed(self):
        for key,value in [('element_id','wrong'),('generation',-1),('version',2),('source','unknown'),
                          ('visible_pixel_bounds',[0,0,-1,10]),('visible_normalized_bounds',[0,0,1,1])]:
            doc=copy.deepcopy(self.element['artwork_geometry']);doc['presentation'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(doc)

    def test_unknown_metadata_is_rejected(self):
        value=copy.deepcopy(self.element['artwork_geometry']);value['presentation']['guess']=True
        with self.assertRaises(ValueError):self.check(value)

    def test_retained_four_cases_validate(self):
        old=q.load(q.QUEUE/'jobs/adr493-session-1-r4/spec.json')
        config=q.load(q.ROOT/old['capture']['plan']['path'])
        images,labels=export_labels(self.folder,config['manifest'])
        self.assertEqual(len(images),8);self.assertEqual(len(labels),8)
        self.assertTrue(all(not row['trainingEligible'] for row in labels))

    def test_navigation_does_not_bypass_observed_focus(self):
        for mutation in ('unverified','wrong-generation','unknown-mode'):
            scene=copy.deepcopy(self.scene)
            if mutation=='unverified':scene['focus_observation']['verified']=False
            elif mutation=='wrong-generation':scene['focus_observation']['generation']+=1
            else:scene['focus_observation']['verificationMode']='unknown'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                scene_check(scene,self.size,scene['focused_element_id'],transition_visibility=True)
