import copy
import unittest
from unittest.mock import patch
from pathlib import Path
from role_detector567 import assess,matched_cases

class RoleTests(unittest.TestCase):
    def test_matching_rejects_wrong_class_and_duplicate_use(self):
        frames=[dict(id='f',group='g',dataset='d',image={'path':'x'},truth=[dict(id='a',cls='button',box=[0,0,10,10]),dict(id='b',cls='button',box=[0,0,10,10])])]
        predictions={Path('x'):[dict(cls='button',box=[0,0,10,10],score=.9),dict(cls='text',box=[0,0,10,10],score=.9)]}
        with patch('role_detector567.checked',return_value=Path('x')):rows=matched_cases(frames,predictions)
        self.assertEqual([r['correct'] for r in rows],[True,False])
        predictions[Path('x')]=[]
        with patch('role_detector567.checked',return_value=Path('x')):self.assertFalse(any(r['correct'] for r in matched_cases(frames,predictions)))

    def test_prior_success_and_identity(self):
        a=dict(manifest={'sha256':'a'},settings={},cases=[dict(id='a',group='g',correct=True)])
        b=copy.deepcopy(a);b['cases'][0]['correct']=False
        self.assertEqual(assess(a,b)['lostPriorSuccesses'],['a'])
        b['manifest']={'sha256':'b'}
        with self.assertRaisesRegex(ValueError,'unmatched'):assess(a,b)

    def test_comparison_runs_through_queue(self):
        import tempfile
        import research_queue as q
        import experiment_batch402 as batches
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='role567-') as temp:
            root=Path(temp);a=dict(manifest={'sha256':'fixed'},settings={},cases=[dict(id='x',group='g',correct=False)])
            b=copy.deepcopy(a);b['cases'][0]['correct']=True
            q.save(root/'a.json',a);q.save(root/'b.json',b)
            doc=dict(version='hcf-template-description-v1',id='role567-test',owner='test-NUIAK',template='T106',
                question='Does the queue preserve matched reference identities?',decision='Reject any lost previous success.',
                inputs=dict(baseline={'file':q.relative(root/'a.json')},candidate={'file':q.relative(root/'b.json')}),parameters={},dependencies=[])
            queue=root/'queue';batches.register_batch(dict(version='experiment-batch-v1',jobs=[doc]),queue,[doc['id']])
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[doc['id']]),[(doc['id'],'complete')])
            result=q.load(queue/'jobs'/doc['id']/'attempts/1/out/benchmark_summary.json')
            self.assertEqual(result['gains'],['x']);self.assertEqual(result['metricsStatus'],'provisional')

    def test_ap_gain_cannot_hide_role_regression(self):
        a=dict(manifest={'sha256':'a'},settings={},cases=[dict(id='x',correct=False)],metrics={'set':dict(AP50=.5,perRoleAP50={'button':.5})})
        b=copy.deepcopy(a);b['cases'][0]['correct']=True;b['metrics']['set']=dict(AP50=.6,perRoleAP50={'button':.47})
        self.assertEqual(assess(a,b)['outcome'],'contradicted')
        b['metrics']['set']['perRoleAP50']['button']=.6
        self.assertEqual(assess(a,b)['outcome'],'supported')
