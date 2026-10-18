"""Native detector preparation checks. Retained captures remain unchanged."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import detector_native_inputs as inputs
import detector_native_inference as inference
from template_inputs398 import pin


def config(platform):
    return dict(version=inputs.VERSION,role='development',platform=platform,sources=[],
        excludedFamilies=['ChromeCoverage','MapOverlays','TabViewNavigation'],
        families=['button','row','tab'],profile='standard')


class InputTests(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(inputs.bounds([0,0,10,20],10,20),[0,0,10,20])
        for box in ([0,0,0,1],[-1,0,1,1],[0,0,11,1],[0,0,float('nan'),1]):
            with self.assertRaisesRegex(ValueError,'detector_bounds'):inputs.bounds(box,10,20)

    def test_retained_ios(self):
        root=q.QUEUE/'jobs/b417-032r-pro-a/attempts/1/out'
        c=config('iOS');c['sources']=[dict(manifest=pin(root/'manifest.json'),bodies=pin(root/'bodies.json'))]
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            result=inputs.prepare(c,Path(folder))
            self.assertGreater(len(inference.validate(result)),0)
            self.assertFalse(result['trainingEligible'])
            self.assertNotIn('ChromeCoverage',{r['screen'] for r in result['frames']})
            for role in ('train','audit','calibration'):
                with self.assertRaisesRegex(ValueError,'detector_configuration'):
                    inputs.prepare(dict(c,role=role),Path(folder))
            changed=copy.deepcopy(c);changed['sources'][0]['manifest']['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'input_changed'):inputs.prepare(changed,Path(folder))

    def test_native_development_only(self):
        c=config('tvOS');c['sources']=[dict(admission=pin(q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json'))]
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            result=inputs.prepare(c,Path(folder))
            self.assertEqual(len(inference.validate(result)),24)
            self.assertEqual(len({r['group'] for r in result['frames']}),6)
            self.assertEqual({c['class'] for r in result['frames'] for c in r['controls']},{'primaryButton','listRow','menuButton'})

    def test_two_descriptions_through_queue(self):
        import hcf_templates395 as templates
        import research_approval as approval
        source=q.QUEUE/'jobs/nctrl417-admission/attempts/1/out/admission.json'
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='detector-native-') as folder:
            root=Path(folder);queue=root/'queue'
            contract=({'configuration'},set(),'detector_native_inputs.run','artifact','diagnostic')
            with patch.dict(templates.CONTRACTS,T55=contract):
                for family in ('button','row'):
                    c=config('tvOS');c['families']=[family];c['sources']=[dict(admission=pin(source))]
                    path=root/(family+'.json');q.save(path,c)
                    doc=dict(version='hcf-template-description-v1',id='native-'+family,owner='test-NUIAK',template='T55',
                        question='Can retained development frames produce verified detector inputs?',
                        decision='Require exact hashes, geometry, groups, and development roles.',
                        inputs=dict(configuration=pin(path)),parameters={},dependencies=[])
                    templates.register(doc,queue);approval.approve(queue,doc['id'],'test','Retained input preparation only.')
                    self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
                    actual=q.load(queue/'jobs'/doc['id']/'attempts/1/out/labels.json')
                    self.assertEqual(len(actual['frames']),8)
                    self.assertEqual({r['screen'] for r in actual['frames']},{family})


if __name__=='__main__':unittest.main()
