import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import research_queue as q
from experiment_templates import pin
import native_scene572 as scene


class NativeSceneTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='scene572-test-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.workspace=self.root/'TTR';self.local=self.workspace/'.local-work';self.local.mkdir(parents=True)
        self.helper=self.local/'App/Helpers/aatv';self.helper.parent.mkdir(parents=True);self.helper.write_text('software-test')
        self.app=self.root/'NavigationConsumer.app';self.app.mkdir();(self.app/'NavigationConsumer').write_bytes(b'software app');(self.app/'Info.plist').write_bytes(b'software plist')
        self.construction=self.root/'construction.json';q.save(self.construction,[dict(id='source-train',split='train'),dict(id='source-qualification',split='qualification')])
        self.patch=patch.object(scene,'WORKSPACE',self.workspace);self.patch.start();self.addCleanup(self.patch.stop)
        self.config=dict(version='native-scene572-v1',id='software-scene',target=scene.TARGET,workspace=str(self.workspace),style='opaque',moving=False,noFocus=False,construction=pin(self.construction),scene='source-train',partition='train',offsets=[0,.35,.8],helper=str(self.helper),helperSHA256=q.digest(self.helper),sources=[pin(self.app/'NavigationConsumer'),pin(self.app/'Info.plist')],app=q.relative(self.app))

    def test_training_and_qualification_are_configurations_of_one_adapter(self):
        self.assertEqual(scene.validate_config(self.config)['partition'],'train')
        c=copy.deepcopy(self.config);c.update(scene='source-qualification',partition='qualification',moving=True,style='ring')
        self.assertEqual(scene.validate_config(c)['partition'],'qualification')

    def test_partition_or_helper_changes_fail(self):
        c=copy.deepcopy(self.config);c['partition']='qualification'
        with self.assertRaisesRegex(ValueError,'partition'):scene.validate_config(c)
        c=copy.deepcopy(self.config);c['helperSHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'helper'):scene.validate_config(c)

    def test_unsupported_capture_points_and_target_fail(self):
        for field,value,reason in [('target','different','scope'),('offsets',[0,1,2],'capture_points'),('style','guessed','style')]:
            c=copy.deepcopy(self.config);c[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,reason):scene.validate_config(c)

    def spec(self):
        path=self.root/(self.config['id']+'-configuration.json');q.save(path,self.config)
        return scene.build(path)

    def test_queue_accepts_both_constructions_with_exact_pins(self):
        for index,(name,partition) in enumerate([('source-train','train'),('source-qualification','qualification')]):
            self.config.update(id='native-software-'+str(index),scene=name,partition=partition)
            spec=self.spec();q.validate(spec);q.verify_pins(spec)
            path=self.root/('spec-'+str(index)+'.json');q.save(path,spec)
            self.assertEqual(q.submit(path,self.root/'queue'),'submitted')
            self.assertEqual(q.submit(path,self.root/'queue'),'already_submitted')
            changed=copy.deepcopy(spec);changed['hypothesis']='Changed submitted science';path.write_text(__import__('json').dumps(changed))
            with self.assertRaisesRegex(ValueError,'job_exists'):q.submit(path,self.root/'queue')

    def test_spec_refuses_task_budget_and_missing_source_pins(self):
        spec=self.spec()
        for mutate,reason in [(lambda s:s.update(task='OTHER'),'scene572_task'),
                              (lambda s:s['limits'].update(timeoutSeconds=801),'scene572_limits'),
                              (lambda s:s['inputs'].pop(),'scene572_input_pins'),
                              (lambda s:s['evidence']['reads'].pop(),'scene572_read_pins')]:
            changed=copy.deepcopy(spec);mutate(changed)
            with self.subTest(reason=reason),self.assertRaisesRegex(ValueError,reason):q.validate(changed)

    def test_app_without_binary_pin_fails(self):
        self.config['sources']=[pin(self.app/'Info.plist')]
        with self.assertRaisesRegex(ValueError,'app_identity'):scene.validate_config(self.config)

    def test_ownership_check_routes_to_native_readiness(self):
        import research_approval as approval
        spec=self.spec();queue=self.root/'queue'
        with patch.object(scene,'readiness',return_value=dict(can_run=True,ownership=[dict(state='clear')])) as ready:
            receipt=approval.capture_ownership(spec,queue)
        self.assertEqual(ready.call_count,1)
        self.assertEqual(q.digest(q.ROOT/receipt['path']),receipt['sha256'])

    def test_busy_target_refuses_before_alert_or_capture(self):
        with patch.object(scene.metadata,'cli',return_value=dict(can_run=False,ownership=[])),patch('real_app_session554.alert_check') as alert:
            with self.assertRaisesRegex(ValueError,'target_busy'):scene.readiness(self.config,self.root)
            alert.assert_not_called()

    def test_unknown_alert_refuses_before_capture(self):
        with patch.object(scene.metadata,'cli',return_value=dict(can_run=True,ownership=[dict(state='clear')])),patch('real_app_session554.alert_check',return_value=dict(status='unavailable')):
            with self.assertRaisesRegex(ValueError,'system_alert:unavailable'):scene.readiness(self.config,self.root)

    def collect(self,packet_failure=False):
        import json
        from types import SimpleNamespace
        from unittest.mock import Mock
        from PIL import Image
        from test_sdk_packet502 import sample
        spec=self.spec();out=self.root/'queue/jobs'/spec['id']/'attempts/1/out';out.mkdir(parents=True)
        q.save(out.parents[2]/'spec.json',spec)
        (self.local/'nuiak572').mkdir()
        identity=dict(appID='example.ttr.navigation.consumer',processID='test-process',runID='test-run',endpoint=scene.ENDPOINT)
        calls=[];counter=[0];session='00000000-0000-4000-8000-000000000001'
        def cli(config,args,name):
            calls.append(args)
            if args[:2]==['simulator','remote']:
                return dict(simulatorID=scene.TARGET,operationID=session,state='closed'if args[2]=='disconnect'else'ready')
            if args[:2]==['simulator','readiness']:return dict(can_run=True,ownership=[dict(state='clear')])
            if args[:2]==['sdk','snapshot']:return dict(sourceKind='authenticated_sdk_challenge',fresh=True)
            if args[:2]==['sdk','packet']:
                if packet_failure:raise ValueError('software_packet_failure')
                dest=Path(args[-1]);dest.mkdir();image=dest/'frame.png';Image.new('RGB',(1,1)).save(image)
                doc=sample(image);doc['sourceID']=scene.TARGET;doc['captureID']='capture-'+str(counter[0]);counter[0]+=1
                for side in ('before','after'):doc[side]['appID']=identity['appID']
                q.save(dest/'evidence.json',doc);return dict()
            raise AssertionError(args)
        child=Mock()
        with patch.object(scene,'OUT',out),patch.object(scene,'readiness',return_value={}),patch.object(scene.metadata,'cli',side_effect=cli),patch.object(scene.metadata,'identity',return_value=identity) as observed,patch.object(scene.subprocess,'Popen',return_value=child),patch.object(scene.subprocess,'run',return_value=SimpleNamespace(returncode=0)),patch('real_app_session554.alert_check',return_value=dict(status='clear')):
            if packet_failure:
                with self.assertRaisesRegex(ValueError,'software_packet_failure'):scene.run()
            else:scene.run()
            self.assertEqual(observed.call_args.kwargs['prefix'],b'TTR_SAMPLE_READY ')
        self.assertTrue(any(args[:3]==['simulator','remote','disconnect']for args in calls))
        self.assertFalse(list((self.local/'nuiak572/enrollments').glob('*')))
        return out,spec

    def test_full_capture_preserves_roles_and_releases_ownership(self):
        out,spec=self.collect();r=q.load(out/'benchmark_summary.json')
        self.assertEqual(r['group'],self.config['scene'])
        self.assertEqual(len(r['frames']),3)
        self.assertEqual(r['role'],'review_only');self.assertFalse(r['trainingAdmitted'])
        self.assertTrue(r['cleanup']['targetReady']);self.assertTrue((out/'capture-evidence.json').is_file())
        review_spec=scene.build_review(spec);q.validate(review_spec)
        review_out=self.root/'queue/jobs'/review_spec['id']/'attempts/1/out';review_out.mkdir(parents=True)
        q.save(review_out.parents[2]/'spec.json',review_spec)
        refs=[pin(out/name)for name in ('benchmark_summary.json','cleanup.json')]
        with patch.object(scene,'OUT',review_out),patch.object(q,'dependency_inputs',return_value=[dict(outputs=refs)]):scene.run_review()
        report=q.load(review_out/'benchmark_summary.json')
        self.assertEqual(report['focusStates'],dict(focused=3))
        self.assertFalse(report['trainingAdmitted']);self.assertEqual(report['independentApplications'],0)

    def test_capture_failure_keeps_partial_receipt_and_releases_ownership(self):
        out,spec=self.collect(packet_failure=True)
        self.assertFalse((out/'capture-evidence.json').exists())
        self.assertEqual(q.load(out/'benchmark_summary.json')['capturesDispatched'],0)
        self.assertTrue(q.load(out/'cleanup.json')['targetReady'])


if __name__=='__main__':unittest.main()
