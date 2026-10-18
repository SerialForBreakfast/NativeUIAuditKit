"""Qualification checks for scoped native detector labels."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
from template_inputs398 import pin
import focusable_detector_labels422 as labels
import detector_training419 as trainer


class LabelTests(unittest.TestCase):
    def setUp(self):
        self.source=q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json'
        self.groups=set()
        self.frames=[pin(q.QUEUE/f'jobs/proposal419-{f}-prepare/attempts/1/out/training-frames.json') for f in ('button','row','tab')]

    def test_retained_preparation_and_resident_consumer(self):
        data=labels.prepare(pin(self.source),self.groups,self.frames)
        self.assertEqual(len(data['rows']),40)
        self.assertFalse(data['generalUILabelsComplete'])
        self.assertEqual({r['group'] for r in data['rows'] if r['role']=='calibration'},self.groups)
        self.assertTrue(all(r['sourceRole']=='train' for r in data['rows']))
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='labels422-') as folder:
            path,counts=trainer.prepare(data,Path(folder))
            self.assertTrue(path.exists());self.assertEqual(counts,{'train':21,'calibration':0})
            import yaml
            data=yaml.safe_load(path.read_text());self.assertEqual(data['train'],data['val'])

    def test_invalid_calibration(self):
        for groups in ({'nctrl417-dev-button-0'},):
            with self.assertRaisesRegex(ValueError,'labels_calibration_groups'):
                labels.prepare(pin(self.source),groups,self.frames)
        with self.assertRaisesRegex(ValueError,'labels_ancestry_leak'):
            labels.prepare(pin(self.source),{'b405-027-tab-group-2'},self.frames)

    def test_missing_unknown_and_changed_labels(self):
        admission=q.load(self.source);row=admission['rows'][0]
        artifact=q.load(q.ROOT/admission['sources'][0]['path'])
        scene=q.load(artifact['path'])['frames'][0]['before']['scene']
        self.assertEqual(len(labels.controls(scene,row)),4)
        mutations=[('missing',lambda s:s['elements'].pop()),
            ('unknown',lambda s:s['recipe']['appearance']['composition']['definitions']['button'].update(kind='custom')),
            ('taxonomy',lambda s:s['elements'][0].update(taxonomy_class='text')),
            ('geometry',lambda s:s['elements'][0]['rendered_body_geometry'].update(full_pixel_bounds=[0,0,1,1])),
            ('focus',lambda s:s['focus_observation'].update(verified=False))]
        for name,change in mutations:
            with self.subTest(name=name):
                bad=copy.deepcopy(scene);change(bad)
                with self.assertRaises(ValueError):labels.controls(bad,row)


if __name__=='__main__':unittest.main()
