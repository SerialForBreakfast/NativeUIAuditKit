"""Generated contract checks. These records do not qualify native images."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import research_queue as q
from template_inputs398 import pin
import native_profile587 as native
import sdk_profile538 as profile


class NativeTests(unittest.TestCase):
    def setUp(self):
        parent=q.ROOT/'.build/native587-tests';parent.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent);self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        helper=self.root/'aatv';helper.write_text('generated helper')
        tools=self.root/'Tools';tools.mkdir();producer=tools/'export-evidence.rb';producer.write_text('# generated producer')
        app=self.root/'NavigationConsumer.app';app.mkdir()
        for name in ['NavigationConsumer','Info.plist']:(app/name).write_text('generated app')
        self.scene=self.root/'construction.json';q.save(self.scene,dict(scenes=[dict(id='fresh-train',split='train'),dict(id='fresh-dev',split='validation')]))
        self.config=dict(version='sdk-profile-pair-v2',id='native587-generated',
            capture=dict(id='native587-generated',target=native.capture.TARGET,endpoint=native.capture.ENDPOINT,
                helper=pin(helper),expectedAppID='example.ttr.navigation.consumer',sourceRevision='a'*40,
                enrollment=str(native.capture.TTR/'.local-work/native587/test/enrollment.json'),
                output=str(native.capture.TTR/'.local-work/native587/test/output'),group='fresh-train'),
            nativeScene=dict(app=q.relative(app),sources=[pin(app/'NavigationConsumer'),pin(app/'Info.plist')],construction=pin(self.scene),
                scene='fresh-train',partition='train',style='opaque',noFocus=False),
            producer=pin(producer),sources=[pin(producer)])
        self.plan=self.root/'plan.json';self.make_plan()
        self.addCleanup(patch.stopall);patch.object(native.capture,'external',side_effect=lambda ref,root:q.ROOT/ref['path']).start()

    def make_plan(self):
        a=self.config['capture'];n=self.config['nativeScene']
        p=dict(schemaVersion=2,source=dict(appID=a['expectedAppID'],sourceRevision=a['sourceRevision']),
            case=dict(split=n['partition'],group=n['scene'],contentGroup=n['scene']),enrollment=a['enrollment'],endpoint=a['endpoint'],button='right',expected='move')
        q.save(self.plan,p,replace=True);self.config['plan']=pin(self.plan)

    def test_train_and_validation_use_existing_capture_entrypoint(self):
        for scene,role in [('fresh-train','train'),('fresh-dev','validation')]:
            self.config['nativeScene'].update(scene=scene,partition=role);self.config['capture']['group']=scene;self.make_plan()
            cp=self.root/('config-'+role+'.json');q.save(cp,self.config)
            spec=profile.build(cp);q.validate(spec)
            self.assertEqual(spec['adapter']['steps'],['sdk_profile538.run']);self.assertEqual(spec['limits']['timeoutSeconds'],800)
            self.assertEqual(profile.validate_config(self.config)['case']['split'],role)

    def test_role_mismatch_is_rejected(self):
        p=q.load(self.plan);p['case']['split']='test';q.save(self.plan,p,replace=True);self.config['plan']=pin(self.plan)
        with self.assertRaisesRegex(ValueError,'plan_role'):native.validate_config(self.config)

    def test_unbound_source_and_unrecognized_controls_fail(self):
        c=copy.deepcopy(self.config);c['nativeScene']['sources']=[]
        with self.assertRaisesRegex(ValueError,'app_binding'):native.validate_config(c)
        c=copy.deepcopy(self.config);c['nativeScene']['scene']='old-review-group'
        with self.assertRaisesRegex(ValueError,'scene_role'):native.validate_config(c)
        p=q.load(self.plan);p['button']='select';q.save(self.plan,p,replace=True);self.config['plan']=pin(self.plan)
        with self.assertRaisesRegex(ValueError,'direction'):native.validate_config(self.config)

    def test_enrollment_and_output_stay_in_the_named_ttr_work_area(self):
        for field in ['enrollment','output']:
            c=copy.deepcopy(self.config);c['capture'][field]='/Users/other/outside'
            with self.assertRaisesRegex(ValueError,'native587_'+field):native.validate_config(c)

    def test_runtime_reads_every_declared_input(self):
        cp=self.root/'config.json';q.save(cp,self.config);s=native.build(cp)
        self.assertEqual(set(s['evidence']['reads']),{r['path'] for r in s['inputs']})
        self.assertIn(self.config['plan'],s['inputs']);self.assertFalse('training' in s)


class PreparationGraphTests(unittest.TestCase):
    def test_internal_hashes_remain_valid_with_and_without_branch_conditions(self):
        from test_campaign_preparation586 import PreparationTests
        import campaign_preparation586 as prep
        test=PreparationTests();test.setUp();self.addCleanup(test.doCleanups)
        cfg,_=test.campaign();source=q.load(q.ROOT/q.load(q.ROOT/cfg['path'])['source']['path'])['jobs'][0]
        bundle=test.root/'bundle.json';q.save(bundle,dict(scope='Generated graph binding only.'))
        for branch in [False,True]:
            docs=[]
            for index in range(2):
                deps=[dict(job=source['job'],specSHA256=source['specSHA256'],outputs=['benchmark_summary.json'])]
                if index:deps.append(dict(job='generated-parent-'+str(branch),outputs=['benchmark_summary.json']))
                docs.append(dict(version='hcf-template-description-v1',id=('generated-parent-' if index==0 else 'generated-child-')+str(branch),task='GENERATED587',owner='Maximum-mini-NUIAK',template='T42',
                    question='Does the compiled graph preserve each final parent hash?',decision='Reject mismatched graph identities before admission.',inputs=dict(bundle=pin(bundle)),
                    parameters=dict(slice='class',classes=None,groups={},matching='class-aware'),dependencies=deps))
            batch=test.root/('batch-'+str(branch)+'.json');q.save(batch,dict(version='experiment-batch-v1',jobs=docs))
            recipe=test.root/('recipe-'+str(branch)+'.json');q.save(recipe,dict(version='campaign-preparation-recipe586-v1',batch=pin(batch),artifacts=[],
                conditions=[dict(job=source['job'],specSHA256=source['specSHA256'],output='benchmark_summary.json',outcome='contradicted')] if branch else [],
                budget=dict(maxJobs=2,maxSeconds=1600,maxOutputBytes=200000000)))
            manifest=prep.compile_recipe(pin(recipe),test.root/('compiled-'+str(branch)),test.queue)
            parent,child=[q.load(q.ROOT/r['spec']['path']) for r in manifest['jobs']]
            dep=next(d for d in child['dependencies'] if d['job']==parent['id'])
            self.assertEqual(dep['specSHA256'],q.text_digest(parent))


if __name__=='__main__':unittest.main()
