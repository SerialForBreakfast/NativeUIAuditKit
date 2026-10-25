import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import research_approval as approval
from experiment_templates import checked,pin
from model_decision_batch434 import register
from supplemental_proposals427 import load
from proposal_tier_policy import compare
from test_proposal_tier_policy import report
import resolution_fallback514 as r

class ResolutionTests(unittest.TestCase):
    def test_policy_does_not_use_truth(self):
        self.assertFalse(compare(report(.9,'wrong'),report(),'high-first')['gains'])
        self.assertTrue(compare(report(.1,'correct-abstention',True),report(.9,'false-selection',True),'high-first')['newWrongSelections'])
        self.assertFalse(compare(report(),report(.1,'miss'),'high-first')['lostPriorSuccesses'])

    def test_two_campaigns_and_queue_failure(self):
        original=q.load(q.ROOT/'reports/work/STREAM514/plan.json')
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='resolution514-') as folder:
            root=Path(folder);queue=root/'queue'
            for i in range(2):
                plan=dict(original,id=f'resolution-test-{i}',pairs=[original['pairs'][i]])
                p=root/f'plan-{i}.json';q.save(p,plan);m=r.compile_plan(p,root/f'compiled-{i}')
                register(m,queue,approve=True);ids=[x['job'] for x in m['jobs']]
                for _ in range(2):q.run(queue,job_ids=ids,max_jobs=4,lock=root/'lock')
                self.assertEqual([q.state(queue/'jobs'/x)[0] for x in ids],['complete']*2, (queue/'jobs'/ids[0]/'attempts/1/result.json').read_text()+(queue/'jobs'/ids[0]/'attempts/1/stderr.log').read_text())
                self.assertEqual(q.run(queue,job_ids=ids,lock=root/'lock'),[])
            spec=q.load(checked(m['jobs'][0]['spec']));pair=q.load(checked(spec['comparison']))
            pair['fallback']['report']['sha256']='0'*64
            p=root/'invalid.json';q.save(p,pair);spec['id']='resolution-test-1-invalid';spec['comparison']=pin(p)
            spec['inputs']=[spec['plan'],pin(p)];sp=root/'bad-spec.json';q.save(sp,spec);q.submit(sp,queue)
            approval.approve(queue,spec['id'],'test','Bounded invalid receipt test.')
            self.assertEqual(q.run(queue,job_ids=[spec['id']],max_jobs=1,lock=root/'lock'),[(spec['id'],'failed')])

    def test_changed_weights_are_rejected(self):
        from unittest.mock import patch
        pair=q.load(q.ROOT/'reports/work/STREAM514/compiled/pair-01.json')
        a=load(pair['baseline']);b=load(pair['fallback'])
        cards=[q.load(checked(x['inputs']['scorecard'])) for x in (a,b)]
        cards[1]['identity']['detector']['weightsSHA256']='0'*64
        with patch.object(r.q,'load',side_effect=cards):
            with self.assertRaisesRegex(ValueError,'resolution514_weights'):r.evaluate(a,b)

    def test_duplicate_reports_rejected(self):
        rows=compare(report(),report(),'high-first')
        with self.assertRaisesRegex(ValueError,'resolution514_duplicate_case'):r.summarize([rows,rows])

if __name__=='__main__':unittest.main()
