"""Queue and cleanup checks for the native profile producer. No live capture."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import research_queue as q
from experiment_templates import pin
from test_sdk_capture527 import CaptureTests
import sdk_profile538 as m

class ProfileTests(CaptureTests):
    def config(self):
        producer=self.root/'export-evidence.rb';producer.write_text('# synthetic producer')
        plan=dict(case=dict(split='test',platform='tvOS'),source=dict(appID=self.config['expectedAppID']),
                  endpoint=self.config['endpoint'],enrollment=self.config['enrollment']['path'],button='right',expected='move')
        pp=self.root/'plan.json';q.save(pp,plan)
        return dict(version='sdk-profile-pair-v1',id=self.config['id'],capture=self.config,plan=pin(pp),producer=pin(producer),sources=[pin(producer)])
    def test_two_recipes_use_same_queue_adapter(self):
        c=ProfileTests.config(self)
        for i,button in enumerate(['right','left']):
            d=copy.deepcopy(c);d['id']=d['capture']['id']='profile-test-'+str(i)
            plan=q.load(Path(d['plan']['path']));plan['button']=button;p=self.root/f'plan-{i}.json';q.save(p,plan);d['plan']=pin(p)
            cp=self.root/f'config-{i}.json';q.save(cp,d);spec=m.build(cp);q.validate(spec)
            self.assertEqual(spec['adapter']['steps'],['sdk_profile538.run'])
            self.assertEqual(spec['limits']['timeoutSeconds'],800)
            sp=self.root/f'spec-{i}.json';q.save(sp,spec)
            self.assertEqual(q.submit(sp,self.root/'queue',q.MODULES),'submitted')
            changed=copy.deepcopy(spec);changed['hypothesis']='Changed immutable plan';q.save(sp,changed,replace=True)
            with self.assertRaisesRegex(ValueError,'job_exists'):q.submit(sp,self.root/'queue',q.MODULES)
    def test_train_role_rejected_before_dispatch(self):
        c=ProfileTests.config(self);p=Path(c['plan']['path']);d=q.load(p);d['case']['split']='train';p.write_text(json.dumps(d));c['plan']=pin(p)
        with self.assertRaisesRegex(ValueError,'test_only'):m.validate_config(c)
    def test_unpinned_source_rejected(self):
        c=ProfileTests.config(self);(self.root/'new.rb').write_text('# changed closure')
        with self.assertRaisesRegex(ValueError,'source_closure'):m.validate_config(c)
    def test_project_scope_used_for_all_calls(self):
        response=SimpleNamespace(returncode=0,stdout=json.dumps(dict(success=True,data=dict(x={'_0':{}}))),stderr='')
        with patch.object(m.subprocess,'run',return_value=response) as run:
            m.Client(self.config,self.root).call('configuration','status')
            self.assertEqual(run.call_args.args[0][1:3],['--project',str(m.capture.TTR)])
    def acquisition(self,failed=False,cleanup_failed=False):
        c=ProfileTests.config(self);session='00000000-0000-4000-8000-000000000001';calls=[]
        def call(client,*args):
            calls.append(args)
            if args[:2]==('simulator','remote'):
                return dict(simulatorID=self.config['target'],operationID=session,state='closed' if args[2]=='disconnect' else 'ready')
            return dict(inFlight=False,pending=[],record=dict(session=session,target=self.config['target'],phase='restore_failed' if cleanup_failed and args[1]=='cancel' else 'prepared'))
        with patch.object(m.capture,'wait_observed'),patch.object(m.Client,'call',call),patch.object(m,'restore_sample',return_value={'nativeReady':True}),patch.object(m,'collect',side_effect=ValueError('uncertain') if failed else None,return_value={'state':'completed_review_only'}) as collect:
            if failed or cleanup_failed:
                with self.assertRaises(ValueError):m.acquire(c,self.root)
            else:self.assertEqual(m.acquire(c,self.root)['state'],'completed_review_only')
            self.assertEqual(collect.call_count,1)
        self.assertEqual(calls.count(('configuration','cancel')),1)
        self.assertEqual(sum(a[:3]==('simulator','remote','disconnect') for a in calls),1)
        return q.load(self.root/'cleanup.json')
    def test_owned_cleanup_on_success(self):self.acquisition()
    def test_uncertain_collection_not_repeated(self):self.acquisition(failed=True)
    def test_cleanup_failure_blocks_publication(self):
        self.assertIn('configurationError',self.acquisition(cleanup_failed=True))

if __name__=='__main__':unittest.main()

class PublishTests(unittest.TestCase):
    def test_real_episode_publication_preserves_review_role(self):
        import shutil
        from test_sdk_episode529 import EpisodeTests
        fixture=EpisodeTests();fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        request=fixture.request('publish-input');dest=fixture.root/'external';dest.mkdir()
        for side,frame in zip(('before','after'),request['episodes'][0]['frames']):
            folder=dest/side;folder.mkdir()
            for name,ref in [('frame.png',frame['image']),('evidence.json',frame['evidence'])]:
                shutil.copyfile(q.ROOT/ref['path'],folder/name)
        out=fixture.root/'out';out.mkdir()
        config=dict(id='publish-check',capture=dict(output=str(dest),group='one-related-group'))
        m.publish(config,out,{'state':'completed_review_only'})
        summary=q.load(out/'benchmark_summary.json')
        self.assertFalse(summary['trainingEligible'])
        self.assertFalse(summary['exactOriginalFocusRestored'])
        published=q.load(out/'episode-request.json')
        self.assertEqual(published['episodes'][0]['role'],'review_only')
        self.assertEqual(len(published['episodes'][0]['frames']),2)
        for ref in published['episodes'][0]['frames']:
            self.assertTrue((q.ROOT/ref['image']['path']).exists())

class ForegroundTests(unittest.TestCase):
    def test_transient_observation_waits_without_input(self):
        with patch.object(m.capture, 'wait_observed', side_effect=[ValueError('sdk_sequence_observation_unknown'), None]) as observe, patch.object(m.time, 'sleep'):
            m.wait_sample(None, {})
            self.assertEqual(observe.call_count, 2)
    def test_identity_mismatch_never_retries(self):
        with patch.object(m.capture, 'wait_observed', side_effect=ValueError('sdk_sequence_identity')) as observe:
            with self.assertRaisesRegex(ValueError, 'identity'): m.wait_sample(None, {})
            self.assertEqual(observe.call_count, 1)
