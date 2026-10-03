import copy
import unittest
import tempfile
from pathlib import Path
from PIL import Image
import human_annotation_review as h
from family_transfer48 import assess,select_review,candidates,draw_review
from harvest_sidecar_v2 import recipe_hash


class FamilyTests(unittest.TestCase):
    def frame(self,complete=False):
        return dict(complete=complete,controls=[dict(bounds=[0,0,10,10],state='focused'),
            dict(bounds=[20,0,10,10],state='unfocused')])

    def test_known_wrong_and_partial_unknown(self):
        d=assess(self.frame(),[dict(box=[20,0,30,10],score=.5),dict(box=[50,0,60,10],score=.8)])
        self.assertEqual((d['knownWrong'],d['unreviewed'],d['targetLocated']),(1,1,False))

    def test_complete_unmatched_is_not_unknown(self):
        d=assess(self.frame(True),[dict(box=[50,0,60,10],score=.8)])
        self.assertEqual(d['detections'][0]['kind'],'unmatched_complete');self.assertEqual(d['unreviewed'],0)

    def test_threshold_and_invalid_predictions(self):
        self.assertFalse(assess(self.frame(),[dict(box=[0,0,10,10],score=.249)])['targetLocated'])
        self.assertTrue(assess(self.frame(),[dict(box=[0,0,10,10],score=.25)])['targetLocated'])
        with self.assertRaises(ValueError):assess(self.frame(),[dict(box=[0,0,10,10],score=float('nan'))])

    def test_manifest_all_targets_hashes_ancestry(self):
        m=candidates({'kind':'test'});self.assertEqual(len(m['cases']),18)
        self.assertEqual(sum(len(c['target_element_ids']) for c in m['cases']),66)
        self.assertEqual(len({c['case_id'] for c in m['cases']}),18)
        for c in m['cases']:
            self.assertEqual(c['recipe']['recipe_hash'],recipe_hash(c['recipe']))
            self.assertEqual(c['split_group'],'validation')
            self.assertEqual(c['independence_group'],'fixture_procedural_renderer_v1')
            self.assertEqual(len(c['target_element_ids']),c['recipe']['element_count'])

    def test_selection_deduplicates_and_covers_roles(self):
        rows=[]
        for i in range(20):
            rows.append(dict(role='button' if i<18 else 'row',image={'sha256':str(i)},
                translation=dict(knownWrong=0,targetLocated=False),
                **{'translation-scale':dict(knownWrong=i,targetLocated=False)}))
        rows.append(copy.deepcopy(rows[-1]));chosen=select_review(rows,4)
        self.assertEqual(len(chosen),4);self.assertEqual(len({r['image']['sha256'] for r in chosen}),4)
        self.assertEqual({r['role'] for r in chosen},{'row','button'})

    def test_real_render_keeps_two_panels_and_target_outline(self):
        parent=h.ROOT/'.build/debug-output/family48-tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as directory:
            root=Path(directory);source=root/'input.png';Image.new('RGB',(100,60),'black').save(source)
            frame=dict(self.frame(),image=h.ref(source));a=assess(frame,[])
            target=root/'review.jpg';draw_review(frame,{'translation':a,'translation-scale':a},target)
            with Image.open(target) as image:
                self.assertEqual(image.size,(200,105))
                self.assertGreater(image.getpixel((1,46))[1],100)


if __name__=='__main__':unittest.main()
