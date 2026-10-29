"""Exercise bounded recovery using the real queue in isolated directories."""
import copy
import unittest
from unittest import mock
import research_queue as q
import research_graph as g
import research_dashboard_states as display
from test_research_queue import QueueTests

class RecoveryGraphTests(unittest.TestCase):
    def setUp(self):
        self.f=QueueTests();self.f.setUp();self.addCleanup(self.f.tearDown)
        p=self.f.modules/'rq_fixture.py'
        p.write_text(p.read_text()+'''
def repair():
    import hashlib
    deps=json.loads((OUT/'dependencies.json').read_text())
    failure=json.loads((ROOT/deps[0]['result']['path']).read_text())
    assert failure['status']=='failed'
    produce()
    p=OUT/'result.json'
    (OUT/'artifact-receipt.json').write_text(json.dumps(dict(version='research-artifact-v1',outputs=[dict(path='result.json',sha256=hashlib.sha256(p.read_bytes()).hexdigest())])))
def uncertain():
    import hashlib
    source=ROOT/'INPUT'
    (OUT/'gate.json').write_text(json.dumps(dict(version='research-condition-v1',outcome='inconclusive',reason='Insufficient independent support.',evidence=[dict(path='INPUT',sha256=hashlib.sha256(source.read_bytes()).hexdigest())])))
'''.replace('INPUT',q.relative(self.f.input)))
    def producer(self,ident='a-failed',cont=True):
        return self.f.spec_v2(id=ident,jobKind='artifact',continueIndependentOnFailure=cont,
            evidence=dict(reads=[q.relative(self.f.input)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['rq_fixture.fail'],outputAttributes=['rq_fixture.OUT']),
            limits=dict(timeoutSeconds=20,maxOutputBytes=100000,maxAttempts=1))
    def recovery(self,p,ident='b-repair',reason='process_failed'):
        return self.f.spec_v2(id=ident,jobKind='artifact',evidence=dict(reads=[q.relative(self.f.input)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['rq_fixture.repair'],outputAttributes=['rq_fixture.OUT']),
            dependencies=[dict(job=p['id'],specSHA256=q.text_digest(p),outputs=[],failure=dict(attempt=1,reason=reason))],
            limits=dict(timeoutSeconds=20,maxOutputBytes=100000,maxAttempts=1))
    def test_two_campaigns_repair_then_continue_without_retry(self):
        for prefix in ('first','second'):
            p=self.producer(prefix+'-a');r=self.recovery(p,prefix+'-b')
            self.f.submit(p);self.f.submit(r)
            self.f.submit(self.f.spec(id=prefix+'-c'))
            self.f.submit(self.f.spec(id=prefix+'-d',dependencies=[dict(job=r['id'],specSHA256=q.text_digest(r),outputs=['result.json'])]))
        results=self.f.run_queue(max_jobs=10)
        self.assertEqual(len(results),8)
        for prefix in ('first','second'):
            self.assertEqual(q.state(self.f.queue/'jobs'/ (prefix+'-a'))[0],'exhausted')
            for suffix in ('b','c','d'):self.assertEqual(q.state(self.f.queue/'jobs'/(prefix+'-'+suffix))[0],'complete')
        self.assertEqual(self.f.run_queue(max_jobs=10),[])
        self.assertTrue((self.f.attempt(job='first-a')/'stderr.log').exists())
    def test_unapproved_repair_does_not_stop_independent_work(self):
        p=self.producer();self.f.submit(p);self.f.submit(self.recovery(p),approve=False);self.f.submit(self.f.spec(id='c-independent'))
        result=dict(self.f.run_queue());self.assertEqual(result['b-repair'],'not_approved');self.assertEqual(result['c-independent'],'complete')
    def test_default_failure_still_stops_cycle(self):
        self.f.submit(self.producer(cont=False));self.f.submit(self.f.spec(id='c-independent'))
        self.assertEqual(self.f.run_queue(),[('a-failed','failed')])
    def test_unmatched_failure_does_not_release_repair(self):
        p=self.producer();self.f.submit(p);self.f.submit(self.recovery(p,reason='timeout'));self.f.submit(self.f.spec(id='c-independent'))
        self.f.run_queue();self.assertEqual(q.state(self.f.queue/'jobs/b-repair')[0],'blocked')
        self.assertEqual(q.state(self.f.queue/'jobs/c-independent')[0],'complete')
    def test_failure_artifacts_and_unbounded_retries_rejected(self):
        p=self.producer();r=self.recovery(p)
        for change,error in [('output','failure_outputs_forbidden'),('attempts','failure_recovery_attempt_limit'),('cancel','failure_dependency_reason')]:
            bad=copy.deepcopy(r)
            if change=='output':bad['dependencies'][0]['outputs']=['checkpoint.pt']
            elif change=='attempts':bad['limits']['maxAttempts']=2
            else:bad['dependencies'][0]['failure']['reason']='cancelled'
            with self.assertRaisesRegex(ValueError,error):q.validate(bad,self.f.modules)
    def test_cancelled_and_later_attempts_do_not_release_repair(self):
        p=self.producer();r=self.recovery(p);self.f.submit(p);self.f.submit(r,approve=False);self.f.run_queue()
        path=self.f.attempt(job=p['id'])/'result.json';result=q.load(path);result['status']='cancelled';q.save(path,result,replace=True)
        with self.assertRaisesRegex(ValueError,'recovery_not_selected'):q.dependency_inputs(r,self.f.queue)
        result['status']='failed';q.save(path,result,replace=True)
        (self.f.queue/'jobs'/p['id']/'attempts/2').mkdir()
        with self.assertRaisesRegex(ValueError,'recovery_attempt_unavailable'):q.dependency_inputs(r,self.f.queue)
    def test_changed_result_identity_rejected(self):
        p=self.producer();r=self.recovery(p);self.f.submit(p);self.f.run_queue()
        path=self.f.attempt(job=p['id'])/'result.json';doc=q.load(path);doc['specSHA256']='0'*64;q.save(path,doc,replace=True)
        with self.assertRaisesRegex(ValueError,'recovery_result_identity'):q.dependency_inputs(r,self.f.queue)
    def test_inconclusive_selects_only_approved_branch(self):
        p=self.f.spec(id='a-uncertain',adapter=dict(type='python-callable',steps=['rq_fixture.uncertain'],outputAttributes=['rq_fixture.OUT']))
        self.f.submit(p)
        for ident,outcome in [('b-followup','inconclusive'),('c-success','supported')]:
            s=self.f.spec(id=ident,dependencies=[dict(job=p['id'],specSHA256=q.text_digest(p),outputs=['gate.json'])],conditions=[dict(job=p['id'],output='gate.json',outcome=outcome)])
            self.f.submit(s)
        self.f.run_queue()
        self.assertEqual(q.state(self.f.queue/'jobs/b-followup')[0],'complete')
        self.assertEqual(q.state(self.f.queue/'jobs/c-success')[0],'blocked')
        self.assertEqual(display.classify(dict(state='blocked',attempts=0,requirements=['condition_not_met:a-uncertain:inconclusive:Insufficient support.']))[0],'unselected')
    def test_failed_repair_does_not_loop_or_block_independent_work(self):
        p=self.producer();r=self.recovery(p);r['adapter']['steps']=['rq_fixture.fail'];r['continueIndependentOnFailure']=True
        self.f.submit(p);self.f.submit(r);self.f.submit(self.f.spec(id='c-independent'))
        result=dict(self.f.run_queue());self.assertEqual(result['b-repair'],'failed');self.assertEqual(result['c-independent'],'complete')
        self.assertEqual(self.f.run_queue(),[])
        self.assertEqual(len(q.attempts_of(self.f.queue/'jobs/b-repair')),1)
    def test_successful_producer_does_not_select_recovery(self):
        p=self.f.spec(id='a-success');r=self.recovery(p)
        self.f.submit(p);self.f.submit(r);self.f.run_queue()
        with self.assertRaisesRegex(ValueError,'recovery_not_needed'):q.dependency_inputs(r,self.f.queue)
        row=dict(state='blocked',attempts=0,requirements=['recovery_not_needed:a-success:complete'])
        self.assertEqual(display.classify(row)[0],'unselected')
    def test_existing_batch_compiler_reuses_recovery_without_a_new_script(self):
        from test_experiment_batch402 import BatchTests
        import experiment_batch402 as batch
        f=BatchTests();f.setUp()
        try:
            for prefix in ('one','two'):
                bad=f.root/(prefix+'-bad.json');q.save(bad,dict(rows=[dict(id='other',sha256='a'*64,group='group',role='development',profile='standard',family='card',outcome='correct')]))
                producer=copy.deepcopy(f.doc);producer.update(id=prefix+'-a',continueIndependentOnFailure=True)
                producer['inputs']['candidate']=dict(file=q.relative(bad))
                repair=copy.deepcopy(f.doc);repair['id']=prefix+'-b'
                repair['dependencies']=[dict(job=producer['id'],outputs=[],failure=dict(attempt=1,reason='process_failed'))]
                independent=copy.deepcopy(f.doc);independent['id']=prefix+'-c'
                docs=[repair,independent,producer]
                batch.register_batch(dict(version='experiment-batch-v1',jobs=docs),f.queue,[d['id'] for d in docs])
            q.run(f.queue,max_jobs=10,python=__import__('sys').executable,lock=f.root/'lock')
            for prefix in ('one','two'):
                self.assertEqual(q.state(f.queue/'jobs'/(prefix+'-a'))[0],'exhausted')
                for suffix in ('b','c'):self.assertEqual(q.state(f.queue/'jobs'/(prefix+'-'+suffix))[0],'complete')
        finally:f.doCleanups()

    def test_failure_cannot_directly_release_training(self):
        r=self.recovery(self.producer());r['authority']='training'
        with self.assertRaisesRegex(ValueError,'failure_recovery_diagnostic'):q.validate(r,self.f.modules)

    def test_capture_cannot_opt_into_continue_on_failure(self):
        p=self.producer();p['authority']='training'
        with self.assertRaisesRegex(ValueError,'failure_continuation_scope'):q.validate(p,self.f.modules)

if __name__=='__main__':unittest.main()
