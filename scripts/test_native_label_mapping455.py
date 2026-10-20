"""Canonical mapping tests preserve native control bounds and exclusions."""
import copy
import unittest
import research_queue as q
from template_inputs398 import pin
import native_label_mapping455 as m


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.admission = pin(q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json')
        a = q.load(q.ROOT/self.admission['path'])
        self.row = a['rows'][0]
        artifact = q.load(q.ROOT/a['sources'][0]['path'])
        self.scene = q.load(artifact['path'])['frames'][0]['before']['scene']

    def test_retained_membership_preserves_all_controls_and_lost_tab(self):
        frames = [pin(q.QUEUE/f'jobs/proposal419-{f}-prepare/attempts/1/out/training-frames.json') for f in ('button','row','tab')]
        data, report = m.prepare(self.admission, frames)
        old = q.load(q.ROOT/'reports/work/DETECTOR422/labels-v2/membership.json')
        self.assertEqual(data['rows'], old['rows'])
        self.assertEqual(data['names'], old['names'])
        self.assertEqual(sum(report['classes'].values()), 160)
        self.assertIn('b405-167-tab-selected-b405-027-tab-selected-1-standard-item-1-0', [r['id'] for r in data['rows']])

    def test_standalone_and_nested_content_are_distinct(self):
        scene = copy.deepcopy(self.scene)
        element = next(e for e in scene['semantic_inventory']['elements'] if e['role']=='label_view')
        standalone = copy.deepcopy(element)
        standalone.pop('parent_id'); standalone['id']='standalone-text'
        scene['semantic_inventory']['elements'].append(standalone)
        mapped = m.map_scene(scene, self.row)
        self.assertEqual(next(x['class'] for x in mapped['targets'] if x['id']=='standalone-text'), 'label')
        self.assertTrue(any(x['id']==element['id'] for x in mapped['excluded']))
        standalone['role']='image_view'; standalone['native_class']='UIImageView'
        mapped=m.map_scene(scene,self.row)
        self.assertEqual(next(x['class'] for x in mapped['targets'] if x['id']=='standalone-text'),'imageView')

    def test_unsupported_role_class_cycle_and_declared_container_fail(self):
        for change in [lambda e:e.update(role='new_role'), lambda e:e.update(native_class='UnknownLabel'),
                       lambda e:e.update(parent_id=e['id']), lambda e:e.update(declared_taxonomy='alert')]:
            scene=copy.deepcopy(self.scene)
            element=next(e for e in scene['semantic_inventory']['elements'] if e['role']=='label_view')
            change(element)
            with self.assertRaises(ValueError):m.map_scene(scene,self.row)


if __name__ == '__main__': unittest.main()
