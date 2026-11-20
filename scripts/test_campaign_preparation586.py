"""Generated software checks. These records do not establish model quality."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import research_approval as approval
from template_inputs398 import pin
import campaign_state586 as state
import campaign_preparation586 as prep
import detector_completion586 as completion
import detector_training_batch478 as legacy


class PreparationTests(unittest.TestCase):
    def setUp(self):
        folder=q.ROOT/'.build/langgraph586';folder.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=folder);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.queue=self.root/'queue';(self.queue/'jobs').mkdir(parents=True)
        self.state=self.root/'state';self.state.mkdir()

    def campaign(self,name='ios586-example',track='iOS detection',jobs=1,missing=False,applies='training'):
        parent=self.queue/'jobs'/(name+'-source');out=parent/'attempts/1/out';out.mkdir(parents=True)
        source=dict(id=parent.name,task='GENERATED586')
        q.save(parent/'spec.json',source)
        report=dict(version='detector-case-match-v1',gains=['gain'],lostPriorSuccesses=['loss'],decisions=[],modelAccepted=False)
        q.save(out/'benchmark_summary.json',report)
        q.save(out.parent/'result.json',dict(version=q.RESULT_VERSION,status='complete',job=parent.name,
            specSHA256=q.text_digest(source),outputs=[dict(path='benchmark_summary.json',sha256=q.digest(out/'benchmark_summary.json'),bytes=(out/'benchmark_summary.json').stat().st_size)]))
        old=self.root/(name+'-source-manifest.json');q.save(old,dict(version='model-decision-compiled-v1',jobs=[dict(job=parent.name,spec=pin(parent/'spec.json'),specSHA256=q.text_digest(source))]))
        event=self.root/(name+'-source-event.json');q.save(event,dict(version='campaign-event585-v1',campaignID=name,track=track,scope='Generated software evidence.',manifest=pin(old),prerequisites=[],
            jobs=[dict(job=parent.name,specSHA256=q.text_digest(source),result=pin(out.parent/'result.json'),outputs=[pin(out/'benchmark_summary.json')])]))
        request=self.root/(name+'-request.json');q.save(request,dict(version='detector-training-batch-v1',question='Does generated evidence preserve previous detections?',baselines=['one']))
        entries=[]
        for n in range(jobs):
            ident=name+'-job-'+str(n)
            spec=dict(version='research-spec-v2',id=ident,task='GENERATED586',owner='Maximum-mini-NUIAK',kind='screen',authority='diagnostic',jobKind='artifact',
                hypothesis='Generated records test workflow behavior without model execution.',question='Does generated evidence preserve previous detections?',
                controlledComparison='Use identical generated source evidence.',decisionRule='Preserve provisional status and exact inputs.',
                nextActionByOutcome=dict(supported='Review software evidence.',contradicted='Repair the caller.'),
                inputs=[pin(request),pin(q.MODULES/'detector_completion586.py')],
                dependencies=[dict(job=parent.name,specSHA256=q.text_digest(source),outputs=['benchmark_summary.json'])],
                evidence=dict(reads=[pin(request)['path']],artifactReceipt='artifact-receipt.json'),
                adapter=dict(type='python-callable',steps=['detector_completion586.finish'],outputAttributes=['detector_completion586.OUT']),
                limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
            path=self.root/(ident+'.json');q.save(path,spec)
            entries.append(dict(job=ident,spec=pin(path),specSHA256=q.text_digest(spec)))
        manifest=self.root/(name+'-compiled.json');q.save(manifest,dict(version='model-decision-compiled-v1',plan=pin(request),existing=[dict(job=parent.name,specSHA256=q.text_digest(source))],jobs=entries,executionStarted=False))
        requirement=self.root/(name+'-eligibility.json');q.save(requirement,dict(trainingEligible=not missing))
        config=dict(version='campaign-preparation586-v1',id=name,track=track,scope='Generated software records only.',source=pin(event),manifest=pin(manifest),
            selection=dict(evidence=pin(out/'benchmark_summary.json'),field=['modelAccepted'],equals=False),
            requirements=[dict(id='generated-eligibility',owner='Maximum-mini-NUIAK',requirement='Generated prerequisite remains missing.',resumeWhen='Provide verified eligible evidence.',
                appliesTo=applies,evidence=pin(requirement),field=['trainingEligible'],equals=True)])
        path=self.root/(name+'-config.json');q.save(path,config)
        return pin(path),entries

    def controller(self,event,output,*extra):
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LANGSMITH_TRACING='false',LANGCHAIN_TRACING_V2='false')
        return subprocess.run([str(q.ROOT/'.venv-langgraph585/bin/python'),'-B',str(q.MODULES/'campaign_state586.py'),
            '--event',str(q.ROOT/event['path']),'--database',str(self.state/'state.sqlite'),'--output',str(output),*extra],
            env=env,capture_output=True,text=True)

    def test_fresh_process_recovers_after_checkpoint_without_new_event(self):
        cfg,_=self.campaign();r=prep.advance(cfg,self.state,self.queue)
        # Reuse a generated event. The crash occurs after durable state closes.
        first=self.controller(r['event'],self.root/'not-written.json','--crash-after-checkpoint')
        self.assertEqual(first.returncode,86,first.stderr);self.assertFalse((self.root/'not-written.json').exists())
        second=self.controller(r['event'],self.root/'restored.json')
        self.assertEqual(second.returncode,0,second.stderr)
        restored=q.load(self.root/'restored.json');original=q.load(q.ROOT/r['controller']['path'])
        self.assertTrue(restored['duplicateEvent']);self.assertEqual(restored['checkpointCount'],original['checkpointCount'])

    def test_same_recipe_frontend_compiles_and_admits_both_tracks(self):
        ids=[]
        for ident,track in [('ios-recipe','iOS detection'),('focus-recipe','tvOS focus')]:
            cfg,entries=self.campaign(ident,track)
            recipe=self.root/(ident+'-recipe.json')
            q.save(recipe,dict(version='campaign-preparation-recipe586-v1',batch=None,
                artifacts=[entries[0]['spec']],conditions=[],budget=dict(maxJobs=1,maxSeconds=800,maxOutputBytes=100000000)))
            path=q.ROOT/cfg['path'];config=q.load(path);config.pop('manifest')
            config.update(version='campaign-preparation586-v2',recipe=pin(recipe));q.save(path,config,replace=True)
            result=prep.advance(pin(path),self.state,self.queue,admit=True)
            self.assertEqual(result['admitted'],[entries[0]['job']]);ids.append(entries[0]['job'])
            prepared=self.state/ident/'prepared/compiled.json'
            self.assertTrue(prepared.is_file());self.assertEqual(len(q.load(prepared)['jobs']),1)
        self.assertEqual(q.run(self.queue,max_jobs=2,lock=self.root/'worker.lock',job_ids=ids),[(i,'complete') for i in sorted(ids)])

    def test_numeric_values_do_not_satisfy_boolean_evidence(self):
        self.assertFalse(prep.same_value(1,True));self.assertFalse(prep.same_value(0,False))
        self.assertTrue(prep.same_value(True,True));self.assertTrue(prep.same_value([],[]))

    def test_campaign_state_cannot_follow_an_external_directory_link(self):
        cfg,_=self.campaign();(self.state/'ios586-example').symlink_to('/Users',target_is_directory=True)
        with self.assertRaises(ValueError):prep.advance(cfg,self.state,self.queue,admit=True)

    def test_conditioned_recipe_reuses_retained_compilation_and_checks_input_drift(self):
        cfg,_=self.campaign();c=q.load(q.ROOT/cfg['path'])
        source=q.load(q.ROOT/c['source']['path'])['jobs'][0]
        bundle=self.root/'bundle.json';q.save(bundle,dict(scope='Generated compilation fixture.'))
        doc=dict(version='hcf-template-description-v1',id='generated-conditioned',task='GENERATED586',owner='Maximum-mini-NUIAK',template='T42',
            question='Do conditioned jobs preserve their exact compiled identity?',decision='Preserve the submitted job and all evidence.',
            inputs=dict(bundle=pin(bundle)),parameters=dict(slice='geometry',classes=None,groups={},matching='class-aware'),
            dependencies=[dict(job=source['job'],specSHA256=source['specSHA256'],outputs=['benchmark_summary.json'])])
        batch=self.root/'batch.json';q.save(batch,dict(version='experiment-batch-v1',jobs=[doc]))
        recipe=self.root/'recipe.json';q.save(recipe,dict(version='campaign-preparation-recipe586-v1',batch=pin(batch),artifacts=[],
            conditions=[dict(job=source['job'],specSHA256=source['specSHA256'],output='benchmark_summary.json',outcome='contradicted')],
            budget=dict(maxJobs=1,maxSeconds=800,maxOutputBytes=100000000)))
        destination=self.root/'compiled';first=prep.compile_recipe(pin(recipe),destination,self.queue)
        q.submit(q.ROOT/first['jobs'][0]['spec']['path'],self.queue)
        second=prep.compile_recipe(pin(recipe),destination,self.queue);self.assertEqual(first,second)
        bundle.write_text('{}')
        with self.assertRaisesRegex(ValueError,'input_changed'):prep.compile_recipe(pin(recipe),destination,self.queue)

    def test_same_campaign_keeps_identity_across_admission_and_completion(self):
        cfg,entries=self.campaign()
        first=prep.advance(cfg,self.state,self.queue,admit=True)
        self.assertEqual(first['state'],'ready_for_admission');self.assertEqual(first['admitted'],[entries[0]['job']])
        pending=prep.advance(cfg,self.state,self.queue)
        self.assertEqual(pending['state'],'waiting_for_runner')
        self.assertEqual(q.run(self.queue,max_jobs=1,lock=self.root/'worker.lock',job_ids=[entries[0]['job']]),[(entries[0]['job'],'complete')])
        done=prep.advance(cfg,self.state,self.queue,admit=True)
        self.assertEqual(done['state'],'waiting_for_Joe_evidence_review');self.assertFalse(done['admitted'])
        journals=q.load(self.state/q.load(q.ROOT/cfg['path'])['id']/'journal.json')
        outputs=[q.load(q.ROOT/i['controller']['path']) for i in journals['invocations']]
        self.assertEqual(len({r['threadID'] for r in outputs}),1);self.assertEqual(len(outputs[-1]['history']),3)

    def test_duplicate_command_does_not_add_jobs_approvals_or_state_events(self):
        cfg,entries=self.campaign();prep.advance(cfg,self.state,self.queue,admit=True)
        one=prep.advance(cfg,self.state,self.queue,admit=True);two=prep.advance(cfg,self.state,self.queue,admit=True)
        self.assertEqual(one['event'],two['event']);self.assertFalse(two['admitted'])
        self.assertTrue(q.load(q.ROOT/two['controller']['path'])['duplicateEvent'])
        self.assertEqual(len([e for e in approval.load(self.queue)['events'] if e['action']=='approve']),1)

    def test_missing_focus_job_requirement_does_not_stop_ios(self):
        focus,_=self.campaign('focus-example','tvOS focus',missing=True,applies='jobs')
        ios,entries=self.campaign()
        a=prep.advance(focus,self.state,self.queue,admit=True);b=prep.advance(ios,self.state,self.queue,admit=True)
        self.assertEqual(a['state'],'waiting_for_prerequisite');self.assertFalse(a['admitted'])
        self.assertEqual(b['admitted'],[entries[0]['job']])
        self.assertNotEqual(q.load(q.ROOT/a['controller']['path'])['threadID'],q.load(q.ROOT/b['controller']['path'])['threadID'])

    def test_training_requirement_does_not_block_diagnostic_review(self):
        cfg,entries=self.campaign('focus-example','tvOS focus',missing=True)
        prep.advance(cfg,self.state,self.queue,admit=True)
        q.run(self.queue,max_jobs=1,lock=self.root/'worker.lock',job_ids=[entries[0]['job']])
        result=prep.advance(cfg,self.state,self.queue)
        self.assertEqual(result['state'],'waiting_for_training_evidence')
        self.assertFalse(q.load(q.ROOT/result['controller']['path'])['report']['modelAccepted'])

    def test_partial_admission_reconciles_without_duplicate_approval(self):
        cfg,entries=self.campaign(jobs=2)
        def fail(manifest,queue,approved):
            entry=manifest['jobs'][0];q.submit(q.ROOT/entry['spec']['path'],queue)
            approval.approve(queue,entry['job'],'test','Generated partial admission recovery.')
            raise RuntimeError('Generated loss of acknowledgment.')
        with patch('workflow_campaign439.admit',side_effect=fail):
            with self.assertRaisesRegex(RuntimeError,'acknowledgment'):prep.advance(cfg,self.state,self.queue,admit=True)
        result=prep.advance(cfg,self.state,self.queue,admit=True)
        self.assertEqual(result['admitted'],[entries[1]['job']])
        events=[e['job'] for e in approval.load(self.queue)['events'] if e['action']=='approve']
        self.assertEqual(sorted(events),sorted(r['job'] for r in entries))
        self.assertTrue(all(not list((self.queue/'jobs'/r['job']/'attempts').glob('*')) for r in entries))

    def test_changed_specification_and_evidence_are_rejected(self):
        cfg,entries=self.campaign();prep.advance(cfg,self.state,self.queue)
        path=q.ROOT/entries[0]['spec']['path'];path.write_text('{}')
        with self.assertRaisesRegex(ValueError,'input_changed'):prep.advance(cfg,self.state,self.queue,admit=True)
        self.assertFalse((self.queue/'jobs'/entries[0]['job']).exists())

    def test_revoked_job_is_not_readmitted(self):
        cfg,entries=self.campaign();prep.advance(cfg,self.state,self.queue,admit=True)
        approval.revoke(self.queue,entries[0]['job'],'test','Generated explicit revocation.')
        with self.assertRaisesRegex(ValueError,'revoked'):prep.advance(cfg,self.state,self.queue,admit=True)

    def test_stale_event_is_rejected(self):
        cfg,_=self.campaign();first=prep.advance(cfg,self.state,self.queue,admit=True)
        prep.advance(cfg,self.state,self.queue)
        r=self.controller(first['event'],self.root/'stale-output.json')
        self.assertNotEqual(r.returncode,0);self.assertIn('stale_preparation_event',r.stderr)

    def test_branch_not_selected_never_admits(self):
        cfg,_=self.campaign();path=q.ROOT/cfg['path'];doc=q.load(path);doc['selection']['equals']=True;q.save(path,doc,replace=True)
        result=prep.advance(pin(path),self.state,self.queue,admit=True)
        self.assertEqual(result['state'],'branch_not_selected');self.assertFalse(result['admitted'])

    def test_scope_expansion_is_rejected(self):
        cfg,entries=self.campaign();spec_path=q.ROOT/entries[0]['spec']['path'];spec=q.load(spec_path)
        spec['limits']['timeoutSeconds']=801;q.save(spec_path,spec,replace=True)
        c=q.load(q.ROOT/cfg['path']);m_path=q.ROOT/c['manifest']['path'];m=q.load(m_path)
        m['jobs'][0].update(spec=pin(spec_path),specSHA256=q.text_digest(spec));q.save(m_path,m,replace=True)
        c['manifest']=pin(m_path);p=q.ROOT/cfg['path'];q.save(p,c,replace=True)
        with self.assertRaisesRegex(ValueError,'diagnostic_scope'):prep.advance(pin(p),self.state,self.queue,admit=True)

    def test_completion_runtime_preserves_assessment_and_excludes_authoring(self):
        for gains,losses in [([],[]),(['g'],[]),(['g'],['l'])]:
            reports=[dict(version='detector-case-match-v1',gains=gains,lostPriorSuccesses=losses)]
            self.assertEqual(completion.assessment(reports),legacy.assessment(reports))
        spec=dict(adapter=dict(steps=['detector_completion586.finish']))
        paths={p['path'] for p in approval.code_pins(spec,q.MODULES)}
        self.assertIn('scripts/detector_completion586.py',paths)
        for name in ['hcf_templates395','experiment_batch402','model_decision_batch434','detector_training_batch478']:
            self.assertNotIn('scripts/'+name+'.py',paths)

    def test_authoring_change_does_not_change_runtime_pins(self):
        modules=self.root/'modules';modules.mkdir()
        runtime=modules/'detector_completion586.py';runtime.write_text((q.MODULES/runtime.name).read_text())
        author=modules/'hcf_templates395.py';author.write_text('VALUE = 1\n')
        spec=dict(adapter=dict(steps=['detector_completion586.finish']))
        before=approval.code_pins(spec,modules)
        author.write_text('VALUE = 2\n');self.assertEqual(before,approval.code_pins(spec,modules))
        runtime.write_text(runtime.read_text()+'\n# Changed runtime.\n')
        self.assertNotEqual(before,approval.code_pins(spec,modules))

    def test_schema_rejects_fabricated_approval(self):
        cfg,_=self.campaign();r=prep.advance(cfg,self.state,self.queue)
        event=q.load(q.ROOT/r['event']['path']);event['approved']=True
        p=self.root/'forged.json';q.save(p,event)
        with self.assertRaisesRegex(ValueError,'event_fields'):state.advance(pin(p),self.state/'state.sqlite')


class AuditTests(unittest.TestCase):
    def setUp(self):
        import campaign_audits586 as audits
        self.audits=audits
        folder=q.ROOT/'.build/langgraph586';folder.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=folder);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.out=self.root/'jobs/audit/attempts/1/out';self.out.mkdir(parents=True)

    def test_ios_audit_preserves_distinct_case_counts(self):
        case=dict(id='image#control',image='image',labelClass='button',slice='h16-32/w<0.5',
            baseline=dict(status='detected'),candidate=dict(status='wrong-class',fit='offset'))
        card=dict(version='detector-case-match-v1',slice='geometry',matching='class-aware',confidence=.5,
            modelAccepted=False,lostPriorSuccesses=[case['id']])
        cp=self.root/'cases.json';rp=self.root/'benchmark_summary.json'
        q.save(cp,dict(version='detector-case-rows-v1',rows=[case]));q.save(rp,card)
        q.save(self.out.parents[2]/'spec.json',{})
        deps=[dict(job='generated-'+str(i),outputs=[pin(cp),pin(rp)]) for i in range(2)]
        with patch.object(self.audits,'OUT',self.out),patch.object(q,'dependency_inputs',return_value=deps):self.audits.ios()
        r=q.load(self.out/'benchmark_summary.json')
        self.assertEqual(r['lossOccurrences'],2);self.assertEqual(r['distinctCases'],1)
        self.assertEqual(r['distinctImages'],1);self.assertFalse(r['inferenceRepeated']);self.assertFalse(r['modelAccepted'])

    def test_focus_audit_rejects_label_drift(self):
        request=self.root/'request.json';labels=self.root/'labels.json'
        q.save(request,{});q.save(labels,dict(trainingEligible=False,modelAccepted=False))
        q.save(self.out.parents[2]/'spec.json',dict(focusSources=[dict(request=pin(request),labels=pin(labels))]))
        with patch.object(self.audits,'OUT',self.out),patch.object(self.audits,'normalize',return_value={}):
            with self.assertRaisesRegex(ValueError,'labels_changed'):self.audits.focus()

    def test_actual_approval_ignores_unrelated_author_and_detects_runtime_change(self):
        # Use copied source files. Do not mutate any running job source.
        modules=self.root/'modules';modules.mkdir()
        runtime=modules/'detector_completion586.py';runtime.write_text((q.MODULES/runtime.name).read_text())
        author=modules/'hcf_templates395.py';author.write_text('VALUE = 1\n')
        queue=self.root/'approval-queue';folder=queue/'jobs/generated-approval';folder.mkdir(parents=True)
        spec=dict(version='research-spec-v2',id=folder.name,task='GENERATED586',owner='Maximum-mini-NUIAK',
            kind='screen',authority='diagnostic',jobKind='artifact',hypothesis='Unrelated authoring does not affect a runtime approval.',
            question='Does the exact runtime approval reject only applicable code changes?',controlledComparison='Use copied source files.',
            decisionRule='Keep exact runtime pins.',nextActionByOutcome=dict(supported='Review software evidence.',contradicted='Preserve the rejected software evidence.'),
            inputs=[pin(runtime)],dependencies=[],evidence=dict(reads=[q.relative(runtime)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['detector_completion586.finish'],outputAttributes=['detector_completion586.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
        q.save(folder/'spec.json',spec);approval.approve(queue,spec['id'],'test','Generated source isolation approval.',modules=modules)
        self.assertTrue(approval.is_approved(queue,spec))
        author.write_text('VALUE = 2\n');self.assertTrue(approval.is_approved(queue,spec))
        runtime.write_text(runtime.read_text()+'\n# Runtime changes.\n');self.assertFalse(approval.is_approved(queue,spec))

class IOSRequestTests(unittest.TestCase):
    def test_spatial_request_keeps_thresholds_and_development_role(self):
        import ios_spatial_review586 as adapter
        folder=q.ROOT/'.build/langgraph586';folder.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            root=Path(directory);out=root/'jobs/ios/attempts/1/out';out.mkdir(parents=True)
            p=root/'request.json';doc=dict(version='spatial-loss-preparation586-v1',dataRole='development',confidence=.5,
                matchingIoU=.5,modelAccepted=False,trainingOrInferenceRepeated=False);q.save(p,doc)
            def update():q.save(out.parents[2]/'spec.json',dict(inputs=[pin(p)],evidence=dict(reads=[q.relative(p)])),replace=True)
            update()
            with patch.object(adapter,'OUT',out),patch.object(adapter.audits,'ios') as run:adapter.run();run.assert_called_once()
            doc['confidence']=.1;q.save(p,doc,replace=True);update()
            with patch.object(adapter,'OUT',out),patch.object(adapter.audits,'ios') as run:
                with self.assertRaisesRegex(ValueError,'request_contract'):adapter.run()
                run.assert_not_called()


class FocusRequestTests(unittest.TestCase):
    def test_request_is_read_and_matches_the_fixed_source_list(self):
        import focus_eligibility586 as adapter
        folder=q.ROOT/'.build/langgraph586';folder.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            root=Path(directory);out=root/'jobs/focus/attempts/1/out';out.mkdir(parents=True)
            sources=[dict(request=dict(path='example',sha256='0'*64),labels=dict(path='labels',sha256='1'*64))]
            p=root/'request.json';q.save(p,dict(version='focus-eligibility-preparation586-v1',sources=sources,modelAccepted=False))
            q.save(out.parents[2]/'spec.json',dict(focusSources=sources,inputs=[pin(p)],evidence=dict(reads=[q.relative(p)])))
            with patch.object(adapter,'OUT',out),patch.object(adapter.audits,'focus') as run:
                adapter.run();run.assert_called_once();self.assertIsNone(adapter.audits.OUT)
            changed=q.load(p);changed['sources']=[];q.save(p,changed,replace=True)
            q.save(out.parents[2]/'spec.json',dict(focusSources=sources,inputs=[pin(p)],evidence=dict(reads=[q.relative(p)])),replace=True)
            with patch.object(adapter,'OUT',out),patch.object(adapter.audits,'focus') as run:
                with self.assertRaisesRegex(ValueError,'request_contract'):adapter.run()
                run.assert_not_called()


if __name__=='__main__':unittest.main()
