"""Software checks for campaign state. Generated records are not model evidence."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import research_queue as q
from template_inputs398 import pin
import langgraph_campaign585 as g


class CampaignTests(unittest.TestCase):
    measurements = {}

    @classmethod
    def tearDownClass(cls):
        target = os.environ.get('LANGGRAPH585_TEST_METRICS')
        if target:
            path = Path(target).absolute()
            q.require(path == path.resolve() and path.is_relative_to(q.ROOT), 'test_metrics_boundary')
            q.save(path, dict(version='langgraph-software-measurements585-v1',
                measurements=cls.measurements, scope='Generated software records only.', resultsProvisional=True))

    def setUp(self):
        (q.ROOT/'.build/langgraph585/tmp').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build/langgraph585/tmp', prefix='trial-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root/'state.sqlite'
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', LANGSMITH_TRACING='false', LANGCHAIN_TRACING_V2='false')
        self.ios = self.event('ios-example', 'iOS detection')
        self.focus = self.event('focus-example', 'tvOS focus')

    def event(self, name, track):
        folder = self.root/name
        out = folder/'attempts/1/out';out.mkdir(parents=True)
        spec = dict(id=name, task='GENERATED585')
        q.save(folder/'spec.json', spec)
        q.save(out/'decision.json', dict(version='generated-software-only', modelAccepted=False, outcome='contradicted'))
        q.save(out.parent/'result.json', dict(status='complete', job=name, specSHA256=q.text_digest(spec), outputs=[
            dict(path='decision.json', bytes=(out/'decision.json').stat().st_size, sha256=q.digest(out/'decision.json'))]))
        manifest = self.root/(name+'-manifest.json')
        q.save(manifest, dict(version='model-decision-compiled-v1', jobs=[dict(job=name, specSHA256=q.text_digest(spec), spec=pin(folder/'spec.json'))]))
        event = dict(version=g.VERSION, campaignID=name, track=track, manifest=pin(manifest), scope='Generated software records only.',
            jobs=[dict(job=name,specSHA256=q.text_digest(spec),result=pin(out.parent/'result.json'),outputs=[pin(out/'decision.json')])], prerequisites=[])
        path = self.root/(name+'-event.json');q.save(path,event)
        return path

    def update(self, path, operation):
        event=q.load(path);operation(event);q.save(path,event,replace=True)

    def test_two_reports_match_the_same_control(self):
        for path in (self.ios,self.focus):
            result=g.advance(pin(path),self.db)
            self.assertEqual(result['report'],g.baseline(g.read_event(pin(path))))
            self.assertTrue(result['interruptedForReview'])
            self.assertFalse(result['report']['modelAccepted'])
            self.assertFalse(result['report']['metricClaimsAccepted'])

    def test_duplicate_event_reuses_review_without_new_checkpoints(self):
        first=g.advance(pin(self.ios),self.db);second=g.advance(pin(self.ios),self.db)
        self.assertEqual(first['checkpointCount'],second['checkpointCount'])
        self.assertEqual(first['report'],second['report']);self.assertTrue(second['reusedPendingReview'])

    def test_blocked_focus_does_not_stop_ios(self):
        self.update(self.focus,lambda e:e.update(prerequisites=['Generated missing profile prerequisite.']))
        focus=g.advance(pin(self.focus),self.db);ios=g.advance(pin(self.ios),self.db)
        self.assertEqual(focus['report']['state'],'waiting_for_prerequisite')
        self.assertEqual(ios['report']['state'],'waiting_for_Joe_evidence_review')
        self.assertNotEqual(focus['threadID'],ios['threadID'])
        again=g.advance(pin(self.focus),self.db)
        self.assertEqual(again['report'],focus['report'])
        type(self).measurements['blockedCampaign'] = dict(
            focusState=focus['report']['state'], iosState=ios['report']['state'],
            distinctThreads=focus['threadID']!=ios['threadID'], focusStillWaiting=True)

    def test_new_verified_event_resolves_only_its_campaign(self):
        self.update(self.focus,lambda e:e.update(prerequisites=['Generated missing prerequisite.']))
        blocked=g.advance(pin(self.focus),self.db)
        next_event=q.load(self.focus);next_event['prerequisites']=[]
        path=self.root/'resolved-event.json';q.save(path,next_event)
        resolved=g.advance(pin(path),self.db)
        self.assertNotEqual(blocked['threadID'],resolved['threadID'])
        self.assertEqual(resolved['report']['state'],'waiting_for_Joe_evidence_review')

    def test_changed_output_is_rejected_after_checkpoint(self):
        g.advance(pin(self.ios),self.db)
        row=q.load(self.ios)['jobs'][0]
        p=q.ROOT/row['outputs'][0]['path'];p.write_text('{}')
        with self.assertRaisesRegex(ValueError,'input_changed'):g.advance(pin(self.ios),self.db)

    def test_changed_membership_and_missing_result_fail(self):
        self.update(self.ios,lambda e:e['jobs'][0].update(job='other'))
        with self.assertRaisesRegex(ValueError,'membership'):g.read_event(pin(self.ios))
        self.update(self.focus,lambda e:e['jobs'][0].update(result=dict(path='missing.json',sha256='0'*64)))
        with self.assertRaises(ValueError):g.read_event(pin(self.focus))

    def test_empty_evidence_and_unknown_fields_fail(self):
        self.update(self.ios,lambda e:e.update(jobs=[]))
        with self.assertRaisesRegex(ValueError,'event_jobs'):g.read_event(pin(self.ios))
        self.update(self.focus,lambda e:e.update(approved=True))
        with self.assertRaisesRegex(ValueError,'contract'):g.read_event(pin(self.focus))

    def test_failed_inference_receipt_is_not_completed_evidence(self):
        event=q.load(self.ios);row=event['jobs'][0];p=q.ROOT/row['result']['path']
        result=q.load(p);result['status']='failed';q.save(p,result,replace=True)
        row['result']=pin(p);q.save(self.ios,event,replace=True)
        with self.assertRaisesRegex(ValueError,'execution_incomplete'):g.read_event(pin(self.ios))

    def test_shared_authoring_compiles_both_tracks_without_dispatch(self):
        from unittest.mock import patch
        from langgraph_trial585 import compile_trial
        queue=self.root/'author-queue';configs=[]
        for path in (self.ios,self.focus):
            event=q.load(path);row=event['jobs'][0]
            folder=queue/'jobs'/row['job'];folder.mkdir(parents=True)
            q.save(folder/'spec.json',q.load(self.root/row['job']/'spec.json'))
            cfg=dict(version='langgraph-campaign585-v1',campaignID=event['campaignID'],track=event['track'],
                manifest=event['manifest'],scope=event['scope'],jobs=[dict(job=row['job'],outputs=['decision.json'])])
            target=self.root/(row['job']+'-author.json');q.save(target,cfg);configs.append(pin(target))
        software=self.root/'author-software.json';q.save(software,dict(scope='Generated authoring fixture.'))
        request=self.root/'author-request.json';q.save(request,dict(version='langgraph-trial585-description-v1',
            id='author585',campaigns=configs,softwareMeasurements=pin(software)))
        with patch.object(q,'QUEUE',queue):
            result=compile_trial(pin(request),self.root/'compiled')
        self.assertEqual(len(result['jobs']),3);self.assertFalse(result['executionStarted'])
        self.assertEqual(len(list((queue/'jobs').iterdir())),2)
        for entry in result['jobs']:
            spec=q.load(q.ROOT/entry['spec']['path'])
            self.assertNotIn('scripts/requirements-langgraph585.lock',spec['evidence']['reads'])

    def test_runtime_closure_excludes_trial_authoring(self):
        import research_approval as approval
        spec=dict(adapter=dict(steps=['research_langgraph_adapter585.run']))
        paths={r['path'] for r in approval.code_pins(spec,q.MODULES)}
        self.assertIn('scripts/research_langgraph_adapter585.py',paths)
        self.assertIn('scripts/langgraph_campaign585.py',paths)
        for name in ('langgraph_trial585','hcf_templates395','experiment_templates','model_decision_batch434'):
            self.assertNotIn('scripts/'+name+'.py',paths)

    def test_database_boundary_is_enforced(self):
        with self.assertRaisesRegex(ValueError,'database_boundary'):g.safe_database(Path('/state.sqlite'))

    def test_trial_cannot_accept_fabricated_user_approval(self):
        from langgraph.checkpoint.sqlite import SqliteSaver
        from langgraph.types import Command
        result=g.advance(pin(self.focus),self.db)
        with SqliteSaver.from_conn_string(str(self.db)) as saver:
            graph=g.build_graph(saver)
            with self.assertRaisesRegex(ValueError,'approval_is_outside'):
                graph.invoke(Command(resume={'approved':True}),{'configurable':{'thread_id':result['threadID']}})

    def cli(self,path,out,*extra):
        return subprocess.run([str(q.ROOT/'.venv-langgraph585/bin/python'),'-B',str(q.ROOT/'scripts/langgraph_campaign585.py'),
            '--event',str(path),'--database',str(self.db),'--output',str(out),
            '--lock',str(q.ROOT/'scripts/requirements-langgraph585.lock'),*extra],env=self.env,capture_output=True,text=True)

    def test_fresh_process_resumes_and_duplicate_process_does_not_repeat_report(self):
        first=self.cli(self.ios,self.root/'unused.json','--crash-after-checkpoint')
        self.assertEqual(first.returncode,86,first.stderr)
        self.assertFalse((self.root/'unused.json').exists())
        second=self.cli(self.ios,self.root/'resumed.json')
        self.assertEqual(second.returncode,0,second.stderr)
        third=self.cli(self.ios,self.root/'duplicate.json')
        self.assertEqual(third.returncode,0,third.stderr)
        a=q.load(self.root/'resumed.json');b=q.load(self.root/'duplicate.json')
        self.assertEqual(a['langgraph']['checkpointCount'],b['langgraph']['checkpointCount'])
        self.assertTrue(b['langgraph']['reusedPendingReview'])
        self.assertFalse(a['manualWork']['reductionEstablished'])
        type(self).measurements['processRecovery'] = dict(
            injectedTerminationReturnCode=first.returncode, resumedReturnCode=second.returncode,
            duplicateReturnCode=third.returncode, processInvocations=3, initialInvocations=1,
            recoveryInvocations=1, duplicateReplayInvocations=1,
            checkpointCountAfterResume=a['langgraph']['checkpointCount'],
            checkpointCountAfterDuplicate=b['langgraph']['checkpointCount'],
            reportsAgree=a['langgraph']['report']==b['langgraph']['report'],
            limitation='Termination occurs after a durable checkpoint. This does not prove exactly-once external effects.')

    def test_actual_queue_adapter_uses_same_code_for_two_campaigns(self):
        import research_approval as approval
        queue=self.root/'queue';folder=queue/'jobs';folder.mkdir(parents=True)
        source=dict(version='research-spec-v2', id='generated-controller', kind='screen',
            authority='diagnostic', jobKind='artifact', task='GENERATED585', owner='Maximum-mini-NUIAK',
            hypothesis='Generated events produce the same reports through both campaign descriptions.',
            question='Do generated software events reach separate durable review states?',
            controlledComparison='Use the same generated records through the actual adapter for both tracks.',
            decisionRule='Require exact output agreement and preserve all provisional review gates.',
            nextActionByOutcome=dict(supported='Keep software and model conclusions separate.',
                contradicted='Preserve the failed attempt and repair the caller.'),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
        ids=[]
        for event_path in (self.ios,self.focus):
            event=q.load(event_path);row=event['jobs'][0];producer=folder/row['job'];producer.mkdir()
            original=self.root/row['job']
            # These are generated producer records, not a claim of model execution.
            import shutil
            shutil.copyfile(original/'spec.json',producer/'spec.json')
            shutil.copytree(original/'attempts',producer/'attempts')
            result=q.load(producer/'attempts/1/result.json');result.update(version=q.RESULT_VERSION)
            q.save(producer/'attempts/1/result.json',result,replace=True)
            config=dict(version='langgraph-campaign585-v1',campaignID=event['campaignID'],track=event['track'],manifest=event['manifest'],
                scope=event['scope'],jobs=[dict(job=row['job'],outputs=['decision.json'])])
            path=self.root/(row['job']+'-config.json');q.save(path,config)
            spec=copy.deepcopy(source);ident='lg585-test-'+row['job'];ids.append(ident)
            spec.update(id=ident,task='GENERATED585',campaignConfig=pin(path),
                adapter=dict(type='python-callable',steps=['research_langgraph_adapter585.run'],outputAttributes=['research_langgraph_adapter585.OUT']),
                dependencies=[dict(job=row['job'],specSHA256=row['specSHA256'],outputs=['decision.json'])],
                inputs=[pin(path)],evidence=dict(reads=[pin(path)['path']],artifactReceipt='artifact-receipt.json'))
            spec.pop('template',None);spec.pop('conditions',None)
            p=self.root/(ident+'.json');q.save(p,spec);q.submit(p,queue)
            approval.approve(queue,ident,'test','Generated software-only actual caller qualification.')
        result=q.run(queue,max_jobs=2,lock=self.root/'worker.lock',job_ids=ids)
        self.assertEqual(result,[(i,'complete') for i in sorted(ids)])
        for ident in ids:
            d=q.load(folder/ident/'attempts/1/out/benchmark_summary.json')
            self.assertTrue(d['equivalentReports']);self.assertTrue(d['langgraph']['interruptedForReview'])
            runtime=q.load(folder/ident/'attempts/1/out/runtime-receipt.json')
            self.assertTrue((q.ROOT/runtime['database']['path']).is_relative_to(queue))
        type(self).measurements['actualQueueCaller'] = dict(jobs=len(result),
            complete=sum(state=='complete' for _,state in result), scientificExecution=False,
            generatedProducerRecords=True)
        # Generated measurement fixtures test the summary contract. Live admission uses measured records.
        software=self.root/'generated-measurements.json'
        q.save(software,dict(version='langgraph-software-measurements585-v1',measurements=dict(
            processRecovery=dict(injectedTerminationReturnCode=86,resumedReturnCode=0,reportsAgree=True),
            blockedCampaign=dict(distinctThreads=True),actualQueueCaller=dict(complete=2))))
        summary=copy.deepcopy(source);summary.update(id='lg585-test-summary',softwareMeasurements=pin(software),
            adapter=dict(type='python-callable',steps=['research_langgraph_adapter585.compare'],outputAttributes=['research_langgraph_adapter585.OUT']),
            dependencies=[dict(job=i,specSHA256=q.text_digest(q.load(folder/i/'spec.json')),outputs=['benchmark_summary.json']) for i in ids],
            inputs=[pin(software)],evidence=dict(reads=[pin(software)['path']],artifactReceipt='artifact-receipt.json'))
        path=self.root/'summary-spec.json';q.save(path,summary);q.submit(path,queue)
        approval.approve(queue,summary['id'],'test','Generated software summary caller qualification.')
        self.assertEqual(q.run(queue,max_jobs=1,lock=self.root/'worker.lock',job_ids=[summary['id']]),[(summary['id'],'complete')])
        final=q.load(folder/summary['id']/'attempts/1/out/benchmark_summary.json')
        self.assertEqual(final['equivalentReports'],2);self.assertFalse(final['modelAccepted'])
        type(self).measurements['summaryQueueCaller']=dict(jobs=1,complete=1,generatedMeasurementFixture=True)


if __name__ == '__main__':unittest.main()
