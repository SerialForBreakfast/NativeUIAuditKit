"""Exercise campaign contracts through the real isolated queue with synthetic evidence."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import research_approval as approval
import research_campaign451 as worker
from experiment_templates import pin, checked
from model_decision_batch434 import register


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='campaign451-')
        self.root=Path(self.temp.name);self.queue=self.root/'queue';self.queue.mkdir()
        refs={}
        for key in ('baseline','candidate','candidateSelection','baselineSelection','capture','mapping','tool','scorecard','ringProposals'):
            p=self.root/(key+'.json')
            q.save(p,dict(plan=dict(trainingEligible=False,cases=[dict(role='development')])) if key=='capture' else {'softwareOnly':key})
            refs[key]=pin(p)
        self.rows=[]; raw=[]
        for i in range(4):
            no=i==3
            self.rows.append(dict(id=str(i),sha256=str(i)*64,case='case',group='group-'+str(i),profile='standard',condition='one'))
            models={m:dict(scores=[.1 if no or m=='baseline' else .95],outcome='correct-abstention' if no else 'miss' if m=='baseline' else 'correct') for m in ('baseline','candidate')}
            known=copy.deepcopy(models);known['baseline']=dict(scores=[.1 if no else .95],outcome='correct-abstention' if no else 'correct')
            raw.append(dict(id=str(i),sha256=str(i)*64,group='case',profile='standard',noFocus=no,
                arms={'known-box':dict(candidates=[dict(box=[0,0,10,10])],models=known),
                      'detector':dict(candidates=[dict(box=[0,0,10,10])],models=models,focusedProposalPresent=None if no else True)}))
        self.report=dict(version='detector-focus-pilot-v1',modelAccepted=False,threshold=.85,matchingIoU=.5,duplicateIoU=.5,inputs=refs,rows=raw)
        self.specs={}
        for name in ('base','correction'):
            spec=dict(id=name,template=dict(id='T57',inputs=refs,parameters={}),dependencies=[])
            self.specs[name]=spec;self.complete(spec,self.report)
        self.membership=self.root/'membership.json';q.save(self.membership,dict(version='coverage-membership-v1',rows=self.rows))

    def tearDown(self):self.temp.cleanup()

    def complete(self,spec,report,status='complete'):
        job=self.queue/'jobs'/spec['id'];out=job/'attempts/1/out';out.mkdir(parents=True,exist_ok=True)
        q.save(job/'spec.json',spec,replace=True);q.save(out/'benchmark_summary.json',report,replace=True)
        q.save(out.parent/'result.json',dict(status=status,specSHA256=q.text_digest(spec),
            outputs=[dict(path='benchmark_summary.json',sha256=q.digest(out/'benchmark_summary.json'))]),replace=True)

    def request(self,name='campaign',**changes):
        doc=dict(version='research-campaign-v1',id=name,question='Does the fixed correction preserve Standard selections?',
            membership=pin(self.membership),pairs=[dict(condition='one',baseline='base',correction='correction')],
            retainedFailures=[],budget=dict(maxJobs=4,maxSeconds=3200,maxOutputBytes=400_000_000))
        doc.update(changes);p=self.root/(name+'.json');q.save(p,doc,replace=True)
        return worker.compile_request(p,self.root/name,self.queue)

    def execute(self,manifest):
        register(manifest,self.queue,approve=True)
        ids=[r['job'] for r in manifest['jobs']]
        for _ in range(3):q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
        states={i:q.state(self.queue/'jobs'/i)[0] for i in ids}
        self.assertTrue(all(s=='complete' for s in states.values()),states)
        return q.load(self.queue/'jobs'/ids[-1]/'attempts/1/out/decision.json')

    def test_two_campaigns_and_restart_do_not_duplicate(self):
        for name in ('first','second'):
            m=self.request(name);r=self.execute(m)
            self.assertEqual(r['outcome'],'supported');self.assertFalse(r['modelAccepted'])
            self.assertEqual(r['slices']['standard/detector']['gains'],3)
            self.assertEqual(worker.compile_request(self.root/(name+'.json'),self.root/name,self.queue),m)
            self.assertEqual(q.run(self.queue,job_ids=[r['job'] for r in m['jobs']],lock=self.root/'lock'),[])

    def test_known_failure_blocks_acceptance(self):
        r=self.execute(self.request(retainedFailures=[dict(reason='Retained consumer positive lost.',evidence=pin(self.membership))]))
        self.assertEqual(r['outcome'],'contradicted')

    def test_no_focus_regression(self):
        report=copy.deepcopy(self.report)
        report['rows'][-1]['arms']['detector']['models']['candidate']=dict(scores=[.95],outcome='false-selection')
        self.complete(self.specs['correction'],report)
        r=self.execute(self.request());self.assertEqual(r['outcome'],'contradicted')
        self.assertEqual(r['slices']['standard/detector']['newWrong'],1)

    def test_inconclusive_without_gains(self):
        report=copy.deepcopy(self.report)
        for row in report['rows']:
            row['arms']['detector']['models']['candidate']=copy.deepcopy(row['arms']['detector']['models']['baseline'])
        self.complete(self.specs['correction'],report)
        self.assertEqual(self.execute(self.request())['outcome'],'inconclusive')

    def test_missing_producer_and_changed_hash_block_without_acceptance(self):
        m=self.request();register(m,self.queue,approve=True)
        p=self.queue/'jobs/correction/attempts/1/out/benchmark_summary.json'
        q.save(p,{},replace=True)
        q.run(self.queue,job_ids=[r['job'] for r in m['jobs']],lock=self.root/'lock',max_jobs=10)
        self.assertEqual(q.state(self.queue/'jobs/campaign-diagnose-01')[0],'complete')
        self.assertEqual(q.state(self.queue/'jobs/campaign-compare-01')[0],'blocked')
        self.assertFalse(q.attempts_of(self.queue/'jobs/campaign-decision'))

    def test_invalid_labels_fail_predictably(self):
        report=copy.deepcopy(self.report);report['rows'][0]['noFocus']=True
        self.complete(self.specs['base'],report)
        m=self.request();register(m,self.queue,approve=True)
        q.run(self.queue,job_ids=[r['job'] for r in m['jobs']],lock=self.root/'lock',max_jobs=10)
        self.assertEqual(q.state(self.queue/'jobs/campaign-diagnose-01')[0],'exhausted')
        self.assertFalse(q.attempts_of(self.queue/'jobs/campaign-decision'))

    def test_unknown_proposal_on_focused_frame_is_rejected(self):
        report=copy.deepcopy(self.report)
        report['rows'][0]['arms']['detector']['focusedProposalPresent']=None
        with self.assertRaisesRegex(ValueError,'campaign_proposal_unknown'):
            worker.validate_report(report,self.rows)

    def test_budget_duplicate_and_unmatched_inputs_rejected(self):
        with self.assertRaisesRegex(ValueError,'campaign_budget_exceeded'):
            self.request(budget=dict(maxJobs=1,maxSeconds=800,maxOutputBytes=100_000_000))
        with self.assertRaisesRegex(ValueError,'campaign_pairs'):
            self.request(pairs=[dict(condition='one',baseline='base',correction='correction')]*2)
        report=copy.deepcopy(self.report);report['rows']*=2
        with self.assertRaises(ValueError):worker.validate_report(report,self.rows)
        spec=copy.deepcopy(self.specs['correction']);spec['template']['inputs']['scorecard']=spec['template']['inputs']['capture']
        self.complete(spec,self.report)
        with self.assertRaisesRegex(ValueError,'campaign_unmatched_inputs'):self.request()

    def test_embedded_score_uses_existing_template_after_diagnosis(self):
        refs=self.specs['correction']['template']['inputs']
        doc=dict(version='hcf-template-description-v1',id='new-score',owner='Maximum-mini-NUIAK',template='T57',
            task='campaign',question='Can a pending scoring job follow the diagnosis?',decision='Require matched regression evidence.',
            inputs=refs,parameters={},dependencies=[])
        m=self.request(pairs=[dict(condition='one',baseline='base',correction=doc)])
        specs={r['job']:q.load(checked(r['spec'])) for r in m['jobs']}
        self.assertEqual(specs['new-score']['template']['id'],'T57')
        self.assertEqual(specs['new-score']['dependencies'][-1]['specSHA256'],q.text_digest(specs['campaign-diagnose-01']))
        # This is compile qualification, not a claim that software-only model bytes can run inference.
        self.assertFalse((self.queue/'jobs/new-score').exists())

    def test_output_budget_exhaustion_preserves_attempt_and_blocks_report(self):
        m=self.request()
        first=q.load(checked(m['jobs'][0]['spec']))
        first['limits']['maxOutputBytes']=1
        p=self.root/'bounded.json';q.save(p,first)
        q.submit(p,self.queue)
        approval.approve(self.queue,first['id'],'test','Test output budget preservation in isolation.')
        q.run(self.queue,job_ids=[first['id']],lock=self.root/'lock')
        attempt=self.queue/'jobs'/first['id']/'attempts/1'
        self.assertEqual(q.state(attempt.parent.parent)[0],'exhausted')
        self.assertTrue((attempt/'result.json').exists())
        self.assertEqual(q.run(self.queue,job_ids=[first['id']],lock=self.root/'lock'),[])

    def test_missing_receipt_releases_after_completion(self):
        self.complete(self.specs['correction'],self.report,status='failed')
        m=self.request();register(m,self.queue,approve=True)
        ids=[r['job'] for r in m['jobs']]
        q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
        self.assertFalse(q.attempts_of(self.queue/'jobs/campaign-compare-01'))
        self.complete(self.specs['correction'],self.report)
        self.assertEqual(self.execute(m)['outcome'],'supported')


if __name__=='__main__':unittest.main()
