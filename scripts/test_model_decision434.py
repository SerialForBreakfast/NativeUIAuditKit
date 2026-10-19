"""Qualify reusable decisions with synthetic evidence, never model training."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import model_decision434 as worker
import model_decision_batch434 as compiler
from experiment_templates import pin
from consumer_crop_comparison import summarize


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='decision434-test-')
        self.root=Path(self.temp.name);self.queue=self.root/'queue';self.queue.mkdir()
        self.inputs={}
        for key in ('capture','proposals','geometry','mapping','tool','oldmodel'):
            path=self.root/(key+'.json')
            q.save(path,dict(plan=dict(trainingEligible=False,cases=[dict(role='development')])) if key=='capture' else dict(softwareOnly=key))
            self.inputs[key]=pin(path)
        self.train=dict(id='training',authority='training',template=dict(id='T06'),training=dict(epochs=30))
        self.complete(self.train,{'fit.json':dict(epochs=30,selection='fixed-last',earlyStopped=False,boundaryStopped=False),
                                  'final.pt':dict(softwareOnly='not-a-model')})
        self.pairs=[]
        self.add_pair('native',False)
        self.add_pair('consumer',True)
        self.plan=dict(version='model-decision-batch-v1',id='experiment-a',question='Does the candidate preserve previous successes?',
            controlledComparison='Same fixed software evidence, only model scores change.',executionBatch=None,training='training',pairs=self.pairs)

    def tearDown(self):self.temp.cleanup()

    def complete(self,spec,outputs):
        job=self.queue/'jobs'/spec['id'];out=job/'attempts/1/out';out.mkdir(parents=True,exist_ok=True)
        q.save(job/'spec.json',spec,replace=True)
        if spec.get('dependencies'):
            q.save(out/'dependencies.json',q.dependency_inputs(spec,self.queue),replace=True)
        for name,doc in outputs.items():q.save(out/name,doc,replace=True)
        self.reinventory(spec['id'])

    def reinventory(self,ident,status='complete'):
        job=self.queue/'jobs'/ident;attempt=job/'attempts/1'
        q.save(attempt/'result.json',dict(status=status,specSHA256=q.text_digest(q.load(job/'spec.json')),
            outputs=[dict(path=str(p.relative_to(attempt/'out')),sha256=q.digest(p)) for p in (attempt/'out').rglob('*') if p.is_file()]),replace=True)

    def add_pair(self,name,consumer):
        if consumer:
            membership=self.root/'membership.json'
            rows=[dict(id=f'crop-{i}',frame='consumer-frame',group='consumer-group',role='development',profile='standard',
                family='button',label=int(i==0),bounds=[0,0,10,10],image=self.inputs['capture']) for i in range(2)]
            q.save(membership,dict(version='consumer-crops-v1',trainingEligible=False,rows=rows))
            common=dict(membership=pin(membership),tool=self.inputs['tool'])
        else:common={k:self.inputs[k] for k in ('capture','proposals','geometry','mapping','tool')}
        for side in ('baseline','candidate'):
            inputs=dict(common,model=self.inputs['oldmodel'] if side=='baseline' else dict(job='training',output='final.pt'))
            spec=dict(id=name+'-'+side,template=dict(id='T63' if consumer else 'T37',inputs=inputs,
                parameters=dict(backend='pytorch') if consumer else {}),dependencies=[])
            if side=='candidate':spec['dependencies']=[dict(job='training',specSHA256=q.text_digest(self.train),outputs=['final.pt'])]
            if consumer:
                report=summarize(rows,[.95,.1]);report['backend']='pytorch'
                outputs={'benchmark_summary.json':report}
            else:
                arm=dict(boxes=[[0,0,10,10]],scores=[.1 if side=='baseline' else .95],outcome='miss' if side=='baseline' else 'correct')
                report=dict(threshold=.85,rows=[dict(id=name,group='native-group',profile='standard',noFocus=False,
                    arms={a:copy.deepcopy(arm) for a in ('known-box','raw-proposal','mapped-proposal')})])
                outputs={'selection.json':report}
            self.complete(spec,outputs)
        self.pairs.append(dict(id=name,baseline=name+'-baseline',candidate=name+'-candidate'))

    def compile(self,plan=None):
        plan=plan or self.plan;path=self.root/(plan['id']+'.json');q.save(path,plan,replace=True)
        return compiler.compile_plan(path,self.root/plan['id'],self.queue)

    def execute(self,manifest):
        compiler.register(manifest,self.queue,approve=True)
        ids=[row['job'] for row in manifest['jobs']]
        for unused in range(5):
            q.run(self.queue,job_ids=ids,lock=self.root/'runner.lock',max_jobs=10)
            states={i:q.state(self.queue/'jobs'/i)[0] for i in ids}
            if all(s=='complete' for s in states.values()):break
            if any(s in ('failed','exhausted','invalid') for s in states.values()):
                detail=[]
                for i,s in states.items():
                    if s not in ('failed','exhausted','invalid'):continue
                    a=q.attempts_of(self.queue/'jobs'/i)[-1]
                    detail.append((i,(a/'result.json').read_text(),(a/'stderr.log').read_text()))
                self.fail(str(detail))
        self.assertTrue(all(s=='complete' for s in states.values()),states)
        return ids

    def test_two_descriptions_use_same_worker_through_queue(self):
        a=self.compile();self.execute(a)
        b=copy.deepcopy(self.plan);b['id']='experiment-b';b['question']='Does a second description reuse the same workflow?'
        self.execute(self.compile(b))
        for ident in ('experiment-a','experiment-b'):
            decision=q.load(self.queue/f'jobs/{ident}-decision/attempts/1/out/decision.json')
            self.assertEqual(decision['outcome'],'supported');self.assertFalse(decision['modelAccepted'])
            follow=q.load(self.queue/f'jobs/{ident}-followup/attempts/1/out/followup.json')
            self.assertFalse(follow['newTrainingAuthorized'])
        self.assertEqual(q.run(self.queue,job_ids=[r['job'] for r in a['jobs']],lock=self.root/'runner.lock'),[])

    def test_regression_selects_diagnosis_through_queue(self):
        path=self.queue/'jobs/consumer-candidate/attempts/1/out/benchmark_summary.json'
        report=q.load(path);report=summarize([ {k:v for k,v in r.items() if k not in ('score','category')} for r in report['crops']],[.1,.1])
        report['backend']='pytorch';q.save(path,report,replace=True);self.reinventory('consumer-candidate')
        self.execute(self.compile())
        report=q.load(self.queue/'jobs/experiment-a-decision/attempts/1/out/decision.json')
        self.assertEqual(report['outcome'],'contradicted');self.assertTrue(report['losses'])
        follow=q.load(self.queue/'jobs/experiment-a-followup/attempts/1/out/followup.json')
        self.assertTrue(follow['failureGroups']);self.assertFalse(follow['newTrainingAuthorized'])

    def test_missing_completed_score_blocks_only_dependents(self):
        self.reinventory('native-candidate','failed')
        manifest=self.compile();compiler.register(manifest,self.queue,approve=True)
        spec=q.load(self.queue/'jobs/experiment-a-compare-01/spec.json')
        with self.assertRaisesRegex(ValueError,'dependency_incomplete'):q.dependency_inputs(spec,self.queue)

    def test_changed_output_is_rejected(self):
        manifest=self.compile();compiler.register(manifest,self.queue)
        path=self.queue/'jobs/native-candidate/attempts/1/out/selection.json';q.save(path,{},replace=True)
        with self.assertRaisesRegex(ValueError,'dependency_output_changed'):
            q.dependency_inputs(q.load(self.queue/'jobs/experiment-a-compare-01/spec.json'),self.queue)

    def test_changed_settings_and_wrong_training_are_rejected(self):
        path=self.queue/'jobs/native-candidate/spec.json';spec=q.load(path)
        spec['template']['inputs']['mapping']=self.inputs['geometry'];q.save(path,spec,replace=True)
        with self.assertRaisesRegex(ValueError,'decision_unmatched_inputs'):self.compile()
        spec['template']['inputs']['mapping']=self.inputs['mapping'];spec['template']['inputs']['model']['job']='other'
        q.save(path,spec,replace=True)
        with self.assertRaisesRegex(ValueError,'decision_score_model'):self.compile()

    def test_duplicate_pairs_rejected(self):
        self.plan['pairs']*=2
        with self.assertRaisesRegex(ValueError,'decision_duplicate_pair'):self.compile()

    def test_completed_output_reference_matches_its_exact_pin(self):
        producer=dict(id='capture-producer');self.complete(producer,{'capture.json':q.load(q.ROOT/self.inputs['capture']['path'])})
        concrete=pin(self.queue/'jobs/capture-producer/attempts/1/out/capture.json')
        for side in ('baseline','candidate'):
            path=self.queue/f'jobs/native-{side}/spec.json';spec=q.load(path)
            spec['template']['inputs']['capture']=concrete if side=='candidate' else dict(job='capture-producer',output='capture.json')
            if side=='baseline':spec['dependencies']=[dict(job='capture-producer',specSHA256=q.text_digest(producer),outputs=['capture.json'])]
            q.save(path,spec,replace=True)
        self.assertTrue(self.compile()['jobs'])

    def test_new_train_and_score_descriptions_compile_with_existing_templates(self):
        initialization=self.inputs['oldmodel']
        config=self.root/'train-config.json';q.save(config,dict(initialization=initialization))
        membership=self.root/'membership-plan.json';q.save(membership,dict(rows=[dict(id='software-row')]))
        preparation=dict(id='prepare');self.complete(preparation,{'crops.json':q.load(membership)})
        common=dict(version='hcf-template-description-v1',owner='Maximum-mini-NUIAK',parameters={},
            question='Does a reusable batch compile existing training and scoring templates?',
            decision='Compare matched evidence before accepting any candidate.')
        train=dict(common,id='new-training',template='T06',inputs=dict(configuration=pin(config),initialization=initialization,membership=pin(membership)),
            dependencies=[dict(job='prepare',specSHA256=q.text_digest(preparation),outputs=['crops.json'])],
            training=dict(initialization=initialization,membership=[pin(membership)],epochs=30,resume='restart',
                storageBudgetBytes=2<<30,experimentLogRunId='TEST434',acceptanceEvidence='Preserve previous successes in matched development comparisons.'))
        inputs={k:self.inputs[k] for k in ('capture','proposals','geometry','mapping','tool')}
        score=dict(common,id='new-score',template='T37',inputs=dict(inputs,model=dict(job='new-training',output='final.pt')),dependencies=[])
        batch=self.root/'execution.json';q.save(batch,dict(version='experiment-batch-v1',jobs=[train,score]))
        plan=copy.deepcopy(self.plan);plan.update(id='new-experiment',executionBatch=pin(batch),training='new-training',
            pairs=[dict(id='native',baseline='native-baseline',candidate='new-score')])
        manifest=self.compile(plan)
        ids={r['job'] for r in manifest['jobs']}
        self.assertTrue({'new-training','new-score','new-experiment-decision','new-experiment-followup'}<=ids)
        self.assertFalse((self.queue/'jobs/new-training').exists())

    def test_incomplete_and_duplicate_evidence_never_pass(self):
        row=dict(id='case',group='group',profile='standard',arm='raw-proposal',noFocus=False,
            baseline='miss',candidate='miss',gain=False,loss=False,newWrong=False)
        pair=dict(pair='one',models=dict(baseline=dict(sha256='a'*64),candidate=dict(sha256='b'*64)),rows=[row])
        self.assertEqual(worker.assess([pair],['one'])['outcome'],'inconclusive')
        with self.assertRaisesRegex(ValueError,'decision_incomplete_suite'):worker.assess([pair],['one','two'])
        pair['rows']*=2
        with self.assertRaisesRegex(ValueError,'decision_duplicate_case'):worker.assess([pair],['one'])

    def pending_preparation(self, mutate=None):
        import hcf_templates395 as templates
        initialization=self.inputs['oldmodel']
        config=self.root/'frozen-train.json';q.save(config,dict(initialization=initialization))
        crop_config=self.root/'frozen-crops.json';q.save(crop_config,dict(destination='software-only',roles=['train','development']))
        rows=[dict(id=role,role=role,profile='standard',group=role,label=1) for role in ('train','development')]
        if mutate:mutate(rows)
        membership=self.root/'frozen-membership.json';q.save(membership,dict(version='crop-membership-plan-v1',rows=rows))
        admission=dict(id='admission');self.complete(admission,{'admission.json':dict(softwareOnly=True)})
        common=dict(version='hcf-template-description-v1',owner='Maximum-mini-NUIAK',parameters={},
            question='Can frozen membership connect pending preparation to existing training?',
            decision='Stop before training if produced membership differs from the frozen plan.')
        prepare=dict(common,id='pending-prepare',template='T05',inputs=dict(configuration=pin(crop_config)),
            dependencies=[dict(job='admission',specSHA256=q.text_digest(admission),outputs=['admission.json'])])
        train=dict(common,id='pending-training',template='T06',inputs=dict(configuration=pin(config),initialization=initialization,membership=pin(membership)),
            dependencies=[dict(job=prepare['id'],specSHA256=q.text_digest(templates.build(prepare)),outputs=['crops.json'])],
            training=dict(initialization=initialization,membership=[pin(membership)],epochs=30,resume='restart',
                storageBudgetBytes=2<<30,experimentLogRunId='TEST439',acceptanceEvidence='Preserve previous successes with fixed evaluation groups.'))
        inputs={k:self.inputs[k] for k in ('capture','proposals','geometry','mapping','tool')}
        score=dict(common,id='pending-score',template='T37',inputs=dict(inputs,model=dict(job=train['id'],output='final.pt')),dependencies=[])
        batch=self.root/'pending-batch.json';q.save(batch,dict(version='experiment-batch-v1',jobs=[score,train,prepare]))
        plan=copy.deepcopy(self.plan);plan.update(id='pending-experiment',executionBatch=pin(batch),training=train['id'],
            pairs=[dict(id='native',baseline='native-baseline',candidate=score['id'])])
        return self.compile(plan)

    def test_pending_preparation_compiles_without_crop_bytes_or_training(self):
        manifest=self.pending_preparation()
        specs={r['job']:q.load(q.ROOT/r['spec']['path']) for r in manifest['jobs']}
        self.assertTrue({'pending-prepare','pending-training','pending-score'}<=set(specs))
        self.assertFalse((self.queue/'jobs/pending-prepare').exists())
        from unittest.mock import patch
        log=self.root/'software-log.json';q.save(log,dict(run='TEST439',purpose='Registration only. No model execution.'))
        with patch.object(q,'EXPERIMENT_LOG',log):
            q.submit(q.ROOT/next(r['spec']['path'] for r in manifest['jobs'] if r['job']=='pending-training'),self.queue)
        with self.assertRaises(ValueError):q.dependency_inputs(specs['pending-training'],self.queue)
        self.assertFalse(q.attempts_of(self.queue/'jobs/pending-training'))

    def test_pending_preparation_rejects_group_leakage(self):
        with self.assertRaisesRegex(ValueError,'decision_membership_leak'):
            self.pending_preparation(lambda rows:rows[1].update(group=rows[0]['group']))

    def test_pending_preparation_rejects_duplicate_membership(self):
        with self.assertRaisesRegex(ValueError,'decision_membership_duplicate'):
            self.pending_preparation(lambda rows:rows[1].update(id=rows[0]['id']))

    def test_no_focus_and_new_wrong_override_gains(self):
        rows=[dict(id='gain',group='group',profile='standard',arm='raw-proposal',noFocus=False,
                baseline='miss',candidate='correct',gain=True,loss=False,newWrong=False),
              dict(id='none',group='other',profile='standard',arm='raw-proposal',noFocus=True,
                baseline='correct-abstention',candidate='false-selection',gain=False,loss=True,newWrong=True)]
        pair=dict(pair='one',models=dict(baseline=dict(sha256='a'*64),candidate=dict(sha256='b'*64)),rows=rows)
        self.assertEqual(worker.assess([pair],['one'])['outcome'],'contradicted')


if __name__=='__main__':unittest.main()
