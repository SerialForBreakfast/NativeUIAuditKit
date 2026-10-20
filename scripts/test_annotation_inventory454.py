"""Native inventory completeness, provenance, and geometry checks."""
import copy
import unittest
import research_queue as q
from template_inputs398 import pin
import annotation_inventory454 as a


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.ref = pin(q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json')
        admission = q.load(q.ROOT/self.ref['path'])
        self.row = admission['rows'][0]
        artifact = q.load(q.ROOT/admission['sources'][0]['path'])
        self.scene = q.load(artifact['path'])['frames'][0]['before']['scene']

    def test_retained_inventory_is_not_general_label_acceptance(self):
        result = a.audit(self.ref)
        self.assertEqual(result['frames'], 40)
        self.assertEqual(result['uniqueImages'], 21)
        self.assertEqual(result['roleCounts']['label_view'], 176)
        self.assertFalse(result['generalUILabelsComplete'])
        self.assertFalse(result['modelAccepted'])

    def test_reject_incomplete_or_changed_inventory(self):
        changes = [lambda s:s.pop('semantic_inventory'),
            lambda s:s['semantic_inventory'].update(truncated=True),
            lambda s:s['semantic_inventory'].update(exclusions={'a':'unmeasured'}),
            lambda s:s['semantic_inventory'].update(generation=-1),
            lambda s:s['semantic_inventory'].update(width=1),
            lambda s:s['semantic_inventory'].update(focus_known=False),
            lambda s:s['semantic_inventory']['elements'].append(s['semantic_inventory']['elements'][0]),
            lambda s:s['semantic_inventory']['elements'][0].update(source='layout_guess'),
            lambda s:s['semantic_inventory']['elements'][0].update(visible_pixel_bounds=[-1,0,2,2]),
            lambda s:s['semantic_inventory']['elements'][0].update(parent_id='absent')]
        for change in changes:
            scene = copy.deepcopy(self.scene)
            change(scene)
            with self.assertRaises((ValueError, KeyError)):
                a.inventory(scene, self.row)


if __name__ == '__main__':
    unittest.main()
