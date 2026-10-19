import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import research_approval as approval
from experiment_templates import pin, checked
import cached_model_cascade as worker
import test_model_decision434 as fixtures
from test_proposal_agreement445 import arm


class CascadeTests(unittest.TestCase):
    complete = fixtures.DecisionTests.complete
    reinventory = fixtures.DecisionTests.reinventory

    def example(self, profile='standard', scores=None, no_focus=False):
        a = arm(scores or [.2]); b = arm([.95])
        a['models']['candidate']['scores'] = [.2]
        b['models']['candidate']['outcome'] = 'false-selection' if no_focus else 'correct'
        raw = dict(id='one', sha256='hash', group='group', profile=profile, noFocus=no_focus, arms={'detector':a})
        other = dict(raw, arms={'detector':b})
        row = dict(id='one', profile=profile, arm='detector', model='baseline', reference='correct-abstention' if no_focus else 'miss', unrestricted='wrong')
        with patch.object(worker.agreement, 'evaluate', return_value=dict(rows=[row])):
            return worker.evaluate(dict(rows=[raw]),dict(rows=[other]))['rows'][0]

    def test_fallback_and_preservation(self):
        self.assertTrue(self.example()['gain'])
        self.assertFalse(self.example(scores=[.95])['usedSupplemental'])
        self.assertFalse(self.example(profile='hcf')['usedSupplemental'])
        row = self.example(no_focus=True)
        self.assertTrue(row['loss']);self.assertTrue(row['newWrong'])

    def test_real_queue_reuse_failure_and_restart(self):
        bundles = sorted((q.ROOT/'reports/work/SELECTION444/compiled').glob('supplemental-*-bundle.json'))
        self.assertEqual(len(bundles),8)
        review = q.load(q.QUEUE/'jobs/agreement445-decision/attempts/1/out/decision.json')
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='cascade-test-') as folder:
            self.root=Path(folder);self.queue=self.root/'queue';self.queue.mkdir()
            original=dict(id='selection-source',adapter=dict(steps=['bounded_selection444.finish']),selectionBranch='supplemental')
            parent=dict(id='review',adapter=dict(steps=['proposal_agreement445.finish']))
            self.complete(original,{'decision.json':{}})
            for name in ('positive','negative'):
                content=copy.deepcopy(review)
                if name=='negative':content['version']='unsupported'
                self.complete(parent,{'decision.json':content})
                request=self.root/(name+'.json')
                q.save(request,dict(version='cached-cascade-request-v1',id='cascade-'+name,decision=original['id'],review=parent['id'],bundles=[pin(p) for p in bundles]))
                manifest=worker.compile_request(request,self.root/name,self.queue)
                ids=[]
                for row in manifest['jobs']:
                    q.submit(checked(row['spec']),self.queue)
                    approval.approve(self.queue,row['job'],'test','Verify cached cascade execution and rejection.')
                    ids.append(row['job'])
                for _ in range(2):
                    q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
                if name=='positive':
                    q.dependency_inputs(q.load(self.queue/'jobs'/ids[1]/'spec.json'),self.queue)
                    self.assertTrue(all(q.state(self.queue/'jobs'/i)[0]=='complete' for i in ids),[(i,q.state(self.queue/'jobs'/i)) for i in ids])
                    result=q.load(self.queue/'jobs'/ids[-1]/'attempts/1/out/decision.json')
                    self.assertFalse(result['modelAccepted'])
                    self.assertEqual(result['slices']['hcf/baseline']['gain'],0)
                    counts=[len(q.attempts_of(self.queue/'jobs'/i)) for i in ids]
                    q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
                    self.assertEqual(counts,[len(q.attempts_of(self.queue/'jobs'/i)) for i in ids])
                else:
                    self.assertEqual(q.state(self.queue/'jobs'/ids[0])[0],'exhausted')
                    self.assertTrue(all(not q.attempts_of(self.queue/'jobs'/i) for i in ids[1:]))


if __name__=='__main__':unittest.main()
