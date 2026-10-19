import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import research_approval as approval
from experiment_templates import pin, checked
import proposal_agreement445 as worker
import test_model_decision434 as fixtures


def arm(scores,boxes=None):
    return dict(candidates=[dict(box=b) for b in (boxes or [[0,0,10,10] for _ in scores])],
                models={m:dict(scores=scores) for m in ('baseline','candidate')})


class AgreementTests(unittest.TestCase):
    complete=fixtures.DecisionTests.complete
    reinventory=fixtures.DecisionTests.reinventory
    def test_location_agreement_and_disagreement(self):
        self.assertTrue(worker.agreement(arm([.8]),arm([.95]),'baseline')[0])
        self.assertFalse(worker.agreement(arm([.8]),arm([.95],[[20,20,10,10]]),'baseline')[0])

    def test_preserves_single_selection_and_abstains_on_ties(self):
        for a,b in [(arm([.9]),arm([.99])),(arm([]),arm([.9])),(arm([.8,.8]),arm([.9])),(arm([.8]),arm([.9,.95]))]:
            self.assertFalse(worker.agreement(a,b,'baseline')[0])

    def test_invalid_scores_and_boxes_fail(self):
        for a in [arm([float('nan')]),arm([.8],[[0,0,-1,2]])]:
            with self.assertRaises(ValueError):worker.agreement(a,arm([.9]),'baseline')

    def test_hcf_unchanged_and_truth_not_used_for_choice(self):
        old=arm([.8]);new=arm([.95]);new['models']['baseline']['outcome']='wrong'
        row=dict(id='one',sha256='hash',group='g',profile='hcf',noFocus=False,arms={'detector':old})
        other=dict(row,arms={'detector':new})
        reference=dict(id='one',group='g',profile='hcf',noFocus=False,arm='detector',model='baseline',reference='miss',outcome='wrong',gain=False,newWrong=True)
        with patch.object(worker.supplemental,'evaluate',return_value=dict(rows=[reference])):
            r=worker.evaluate(dict(rows=[row],inputs={'baseline':{},'candidate':{}}),dict(rows=[other]))
        self.assertEqual(r['rows'][0]['outcome'],'miss');self.assertFalse(r['rows'][0]['usedSupplemental'])

    def test_false_nofocus_selection_remains_a_regression(self):
        old=arm([.8]);new=arm([.95]);new['models']['baseline']['outcome']='false-selection'
        row=dict(id='one',sha256='hash',group='g',profile='standard',noFocus=True,arms={'detector':old})
        other=dict(row,arms={'detector':new})
        reference=dict(id='one',group='g',profile='standard',noFocus=True,arm='detector',model='baseline',reference='correct-abstention',outcome='false-selection',gain=False,newWrong=True)
        with patch.object(worker.supplemental,'evaluate',return_value=dict(rows=[reference])):
            r=worker.evaluate(dict(rows=[row],inputs={'baseline':{},'candidate':{}}),dict(rows=[other]))
        self.assertTrue(r['rows'][0]['loss']);self.assertTrue(r['rows'][0]['newWrong'])

    def test_real_request_in_queue_and_invalid_source(self):
        root_source=q.ROOT/'reports/work/SELECTION444/compiled'
        bundles=sorted(root_source.glob('supplemental-*-bundle.json'))
        if len(bundles)!=8:self.skipTest('Retained SELECTION444 inputs unavailable')
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='agreement445-test-') as folder:
            self.root=Path(folder);self.queue=self.root/'queue';self.queue.mkdir()
            parent=dict(id='source',adapter=dict(steps=['bounded_selection444.finish']),selectionBranch='supplemental')
            source=dict(version='bounded-selection-followup-v1',branch='supplemental',modelAccepted=False,
                standard=dict(baseline=dict(gains=2,newWrong=1,noFocus=3,groups=13)),preservation=dict(losses=['retained'],newWrongSelections=[]))
            self.complete(parent,{'decision.json':source})
            for name,valid in [('valid',True),('invalid',False)]:
                request=self.root/(name+'.json')
                q.save(request,dict(version='proposal-agreement-request-v1',id='test-agreement-'+name,decision='source',bundles=[pin(p) for p in bundles]))
                manifest=worker.compile_request(request,self.root/name,self.queue)
                if not valid:
                    self.complete(parent,{'decision.json':dict(source,version='unsupported')})
                ids=[]
                for r in manifest['jobs']:
                    q.submit(checked(r['spec']),self.queue);approval.approve(self.queue,r['job'],'test','Verify bounded cached agreement without inference.');ids.append(r['job'])
                for _ in range(2):q.run(self.queue,job_ids=ids,lock=self.root/'runner.lock',max_jobs=10)
                if valid:
                    self.assertTrue(all(q.state(self.queue/'jobs'/i)[0]=='complete' for i in ids),[(i,q.state(self.queue/'jobs'/i)[0]) for i in ids])
                    result=q.load(self.queue/'jobs'/ids[-1]/'attempts/1/out/decision.json')
                    self.assertFalse(result['modelAccepted']);self.assertTrue(result['preservation']['losses'])
                    before=[len(q.attempts_of(self.queue/'jobs'/i)) for i in ids]
                    q.run(self.queue,job_ids=ids,lock=self.root/'runner.lock',max_jobs=10)
                    self.assertEqual(before,[len(q.attempts_of(self.queue/'jobs'/i)) for i in ids])
                else:
                    self.assertEqual(q.state(self.queue/'jobs'/ids[0])[0],'exhausted')
                    self.assertTrue(all(not q.attempts_of(self.queue/'jobs'/i) for i in ids[1:]))


if __name__=='__main__':unittest.main()
