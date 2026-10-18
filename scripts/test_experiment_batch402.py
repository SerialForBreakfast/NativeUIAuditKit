"""Qualify batch registration without touching the active queue."""
import copy
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batch


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='batch402-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.queue = self.root/'queue'
        rows = [dict(id='case', sha256='a'*64, group='group', role='development', profile='standard',
                     family='card', outcome='correct')]
        self.input = self.root/'input.json'; q.save(self.input, dict(rows=rows))
        self.doc = dict(version='hcf-template-description-v1', id='batch402-test', owner='test-NUIAK', template='T15',
            question='Does registration preserve the same comparison?', decision='Require identical cases and no lost successes.',
            inputs={k:dict(file=q.relative(self.input)) for k in ('baseline','candidate')},
            parameters=dict(comparison='same'), dependencies=[])

    def value(self, *docs):
        return dict(version='experiment-batch-v1', jobs=list(docs or [self.doc]))

    def test_register_resume_and_execute(self):
        result = batch.register_batch(self.value(), self.queue, [self.doc['id']])
        self.assertFalse(result['executionStarted'])
        self.assertEqual(batch.register_batch(self.value(), self.queue)['jobs'][0]['id'], self.doc['id'])
        self.assertFalse((self.queue/'jobs'/self.doc['id']/'attempts/1').exists())
        self.assertEqual(q.run(self.queue, max_jobs=1, lock=self.root/'lock', job_ids=[self.doc['id']]),
                         [(self.doc['id'],'complete')])

    def test_invalid_batch_has_no_partial_registration(self):
        bad = copy.deepcopy(self.doc); bad['id']='bad';bad['template']='unknown'
        with self.assertRaisesRegex(ValueError,'template_unknown'):
            batch.register_batch(self.value(self.doc,bad),self.queue)
        self.assertFalse(self.queue.exists())
        report=batch.inspect_batch(self.value(self.doc,bad),self.queue)
        self.assertEqual([r['state'] for r in report['jobs']],['definition-valid','blocked'])
        self.assertFalse(self.queue.exists())

    def test_duplicate_cycle_and_paths(self):
        with self.assertRaisesRegex(ValueError,'duplicate_job'):batch.compile_batch(self.value(self.doc,self.doc),self.queue)
        bad=copy.deepcopy(self.doc);bad['inputs']['baseline']=dict(job=bad['id'],output='comparison.json')
        with self.assertRaisesRegex(ValueError,'dependency_cycle'):batch.compile_batch(self.value(bad),self.queue)
        bad=copy.deepcopy(self.doc);bad['inputs']['baseline']=dict(file='../outside.json')
        with self.assertRaisesRegex(ValueError,'unsafe_path'):batch.compile_batch(self.value(bad),self.queue)

    def test_changed_input_and_unknown_approval(self):
        batch.register_batch(self.value(),self.queue)
        q.save(self.input,dict(rows=[]),replace=True)
        with self.assertRaisesRegex(ValueError,'immutable_job_conflict'):batch.register_batch(self.value(),self.queue)
        with self.assertRaisesRegex(ValueError,'approval_outside_batch'):
            batch.register_batch(self.value(),self.root/'another',['not-present'])

    def test_dependency_order_and_failed_receipt(self):
        child=copy.deepcopy(self.doc); child['id']='child'
        child['inputs']['candidate']=dict(job=self.doc['id'],output='comparison.json')
        docs=batch.compile_batch(self.value(child,self.doc),self.queue)
        self.assertEqual([d['id'] for d in docs],[self.doc['id'],'child'])
        folder=self.queue/'jobs'/'failed'/'attempts/1';folder.mkdir(parents=True)
        q.save(folder/'result.json',dict(status='failed'))
        child['inputs']['candidate']=dict(job='failed',attempt=1,output='comparison.json')
        with self.assertRaisesRegex(ValueError,'producer_incomplete'):batch.compile_batch(self.value(child),self.queue)

    def test_approval_proceeds_while_dispatch_is_busy(self):
        # ACTIONS417: approval no longer waits for the dispatch lock; the runner rechecks it at dispatch.
        import research_approval
        with q.host_lock(self.queue/'batch-dispatch.lock'):
            batch.register_batch(self.value(),self.queue,[self.doc['id']])
        self.assertTrue((self.queue/'jobs'/self.doc['id']/'spec.json').exists())
        self.assertIn(self.doc['id'],research_approval.approved_map(self.queue))
        # Repeating the same registration and approval is a no-op.
        batch.register_batch(self.value(),self.queue,[self.doc['id']])
        self.assertIn(self.doc['id'],research_approval.approved_map(self.queue))


class NoFocusTests(unittest.TestCase):
    def test_explicit_native_empty_state_only(self):
        from native343 import signature
        scene=dict(recipe={},is_settled=True,focus_observation=dict(verified=True,source='uikit_focus_system',
            observedID=None,generation=1,plannedFocusIDs=[]),focused_element_id=None,observation_generation=1,
            observation_diagnostics=dict(sampledGeneration=1,sampleAgeMilliseconds=1,stableMilliseconds=200,
                nativeFocusResolved=True,reason='ready',nativeProbe=dict(referenceFocused=True)),
            timestamp=1,scene_width=1920,scene_height=1080,elements=[])
        value=dict(device=dict(simulator_udid='s',fixture_instance_id='i',fixture_run_id='r'),scene=scene,startedAt=1,finishedAt=1)
        self.assertIsNone(signature(value,value,None)[1])
        scene['elements']=[dict(element_id='decoy',is_focused=False)]
        with self.assertRaisesRegex(ValueError,'missing_controls'):signature(value,value,None)
        scene['recipe']=dict(appearance=dict(composition=dict(definitions={'label':dict(kind='text')},
            regions=[dict(items=[dict(id='decoy',component='label')])])))
        self.assertIsNone(signature(value,value,None)[1])
        scene['focus_observation']['verified']=False
        with self.assertRaisesRegex(ValueError,'unverified_focus'):signature(value,value,None)

    def test_native_recipe_contract(self):
        from native_coverage402 import validate
        import native343
        composition=dict(styles={'image':dict(focus=dict(kind='native_image'),fontSize=24)},
            definitions={'poster':dict(kind='poster')},regions=[dict(frame=[0,0,100,100],items=[{}]) for _ in range(4)])
        plan=dict(version='native-hcf402-v1',binding=dict(simulatorUDID=native343.TARGET,endpoint='http://127.0.0.1:8080'),
            role='study-pending',trainingEligible=False,profiles=['standard','hcf'],repeats=1,expectedFrames=2,
            captureBudgetBytes=100_000_000,qualification=dict(complete=True,restoration='verified'),
            cases=[dict(id='test',role='development',condition='no-focus',targets=[None],
                        recipe=dict(element_count=4,appearance=dict(composition=composition)))])
        validate(plan)
        bad=copy.deepcopy(plan);bad['cases'][-1]['targets']=['item-0']
        with self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(plan);bad['captureBudgetBytes']+=1
        with self.assertRaisesRegex(ValueError,'coverage_budget'):validate(bad)
        bad=copy.deepcopy(plan);bad['cases'][0]['recipe']['appearance']['composition']['styles']['image']['fontSize']=180
        with self.assertRaisesRegex(ValueError,'native_font_size'):validate(bad)
        bad=copy.deepcopy(plan);bad['cases'][0]['recipe']['element_count']=5
        with self.assertRaisesRegex(ValueError,'native_item_count'):validate(bad)


class RetainedReportTests(unittest.TestCase):
    setUp=BatchTests.setUp
    value=BatchTests.value
    def test_class_report_queue_success_and_failure(self):
        metric=dict(support=10,ap50=.5,precision=.5,recall=.5,tp=5,fp=5,fn=5)
        path=self.root/'evaluation.json'
        q.save(path,dict(baseline=dict(perClass=[dict(metric,**{'class':'button'})]),
                         populations=dict(withheld=dict(perClass=[dict(metric,**{'class':'button'})]))))
        for name in ('button','missing'):
            doc=copy.deepcopy(self.doc);doc.update(id='class-'+name,template='T33',
                inputs=dict(evaluation=dict(file=q.relative(path))),parameters=dict(className=name))
            batch.register_batch(self.value(doc),self.queue,[doc['id']])
            expected='complete' if name=='button' else 'failed'
            self.assertEqual(q.run(self.queue,max_jobs=1,lock=self.root/'lock',job_ids=[doc['id']]),[(doc['id'],expected)])


if __name__=='__main__':unittest.main()
