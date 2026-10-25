"""SDK preparation qualification. Generated packets are software tests, never native evidence."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import research_queue as q
import sdk_training513 as s
from experiment_templates import pin,checked
from model_decision_batch434 import register
from test_sdk_packet502 import sample


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.queue=self.root/'queue';self.queue.mkdir()
        self.source=q.ROOT/'reports/work/SDK513/source-eb7397d9.json'
        self.tool=q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'
        self.ruby=q.ROOT/'reports/work/SDK513/ttr-tools-eb7397d9/export-evidence.rb'

    def ruby_call(self,*args):
        result=subprocess.run(['/usr/bin/ruby',str(self.ruby),*map(str,args)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        return json.loads(result.stdout)

    def pair(self,name='sample',before='button',after=None,split='train',profile='standard',version=2,known=True,family=None):
        root=self.root/name;root.mkdir();visual={};coverage={};refs={}
        source=dict(appID='software-test',sourceURL='https://example.invalid/software-test',sourceRevision='a'*40,sdkRevision='b'*40,
            instrumentationSHA256='c'*64,sourceFamily=family or name,codeLicense='software-test',contentRights='generated-test',privacy='synthetic_or_reviewed_account_free')
        for i,(side,focus) in enumerate([('before',before),('after',after)]):
            folder=root/side;folder.mkdir();image=folder/'source.png'
            Image.new('RGB',(16,16),(50+i*50,len(name),10)).save(image)
            e=sample(image);e.update(width=16,height=16,captureID=name+'-'+side)
            for snapshot in ('before','after'):
                e[snapshot]['focusID']=focus;e[snapshot]['focusKnown']=known
                element=e[snapshot]['elements'][0];element['bounds']=dict(x=2,y=2,width=8,height=8);element['className']='UIButton'
            q.save(folder/'source.json',e)
            c=dict(id=name+'-'+side,group=name,contentGroup=name,split=split,uiType='button',hcfMode=profile,motion='unknown',seed='test',platform='tvOS',osVersion='test',frames=[dict(role='single',image='source.png',evidence='source.json',evidenceSHA256=q.digest(folder/'source.json'))])
            q.save(folder/'input.json',dict(schemaVersion=1,source=source,cases=[c]));self.ruby_call('export',folder/'input.json',folder/'packet')
            refs[side]=dict(packet=side+'/packet',caseID=c['id'],manifestSHA256=q.digest(folder/'packet/manifest.json'))
            coverage[side]=dict(scope='registered_elements',rootID='test-root',coordinateSpace='screen_pixels',registeredCount=1,truncated=False,exclusions=[],unavailable=['complete_visible_inventory','occlusion','focus_effect_bounds'])
            time=dict(basis='capture_interval',clockID=e['clockID'],startNS=e['captureStartNS'],endNS=e['captureEndNS'])
            visual[side]=dict(captureID=e['captureID'],profile=dict(state=profile,source='human_reviewed',captureID=e['captureID'],observationTime=time),appearance=dict(state='none',source='human_reviewed',captureID=e['captureID'],observationTime=time),settling=dict(state='settled',source='human_reviewed',captureID=e['captureID'],observationTime=time),inventory=dict(rootID='test-root',coordinateSpace='screen_pixels',geometryKind='layout',alignment='bracketed',captureID=e['captureID'],registeredCount=1,truncated=False,unavailable=['complete_visible_inventory','occlusion','focus_effect_bounds']))
        request=dict(operationID=name,simulatorID='software-test',sequence=1,button='right')
        action=dict(request=request,receipt=dict(operationID=name,simulatorID='software-test',sequence=1,state='delivered',effectStatus='unverified'),timing=dict(clockID='supervisor',beforeStartedNS=1,beforeFinishedNS=2,actionStartedNS=3,actionFinishedNS=4,afterStartedNS=5,afterFinishedNS=6))
        d=dict(schemaVersion=version,kind='sdk_action_pair',before=refs['before'],after=refs['after'],action=action,expected=s.observed(before,after),coverage=coverage)
        if version==2:d['visualProvenance']=visual
        q.save(root/'input.json',d);self.ruby_call('export-action-pair',root/'input.json',root/'pair')
        return pin(root/'pair/manifest.json')

    def request(self,pairs,admit=False,name='sdk-test'):
        return dict(version='sdk-preparation-v1',id=name,pairs=pairs,source=pin(self.source),tool=pin(self.tool),
            exclusions=dict(groups=[],contentGroups=[],sourceFamilies=[],images=[]),
            admission=dict(reviewer='software-test',reason='Generated software contract test; not native model evidence.',pairs={p['sha256']:'train' for p in pairs}) if admit else None)

    def test_observed_absence_and_visible_negatives(self):
        ref=self.pair();r=s.intake(self.request([ref],True))
        self.assertEqual(r['pairs'][0]['changed'],1);self.assertEqual(r['pairs'][0]['observed'],'departure')
        self.assertIsNone(r['pairs'][0]['endpoints']['after']);self.assertTrue(r['pairs'][0]['trainingEligible'])
        self.assertEqual(len(r['frames'][1]['controls']),1)
        crops=s.prepare_crops(r,self.root/'crops',pin(self.tool))
        self.assertEqual([x['label'] for x in crops['rows']],[1,0])
        for row in crops['rows']:
            with Image.open(row['path']) as image:self.assertEqual(image.size,(256,256))
        self.assertEqual(crops['preprocessing']['expansion'],.16)

    def test_producer_test_data_and_excluded_groups_never_train(self):
        ref=self.pair(split='test');request=self.request([ref],True)
        with self.assertRaisesRegex(ValueError,'producer_split_not_training'):s.intake(request)
        ref=self.pair(name='excluded');request=self.request([ref],True);request['exclusions']['contentGroups']=['excluded']
        with self.assertRaisesRegex(ValueError,'excluded_contentGroups'):s.intake(request)

    def test_v1_temporal_does_not_wait_for_crop_profile(self):
        ref=self.pair(version=1);data=s.intake(self.request([ref],True))
        self.assertTrue(data['pairs'][0]['trainingEligible'])
        self.assertFalse(data['frames'][0]['trainingEligible'])
        with self.assertRaisesRegex(ValueError,'crop_prerequisites'):s.prepare_crops(data,self.root/'crops',pin(self.tool))

    def test_tampering_and_unknown_focus_fail(self):
        ref=self.pair();path=checked(ref);d=q.load(path);d['observed']='unchanged';q.save(path,d,replace=True)
        with self.assertRaisesRegex(ValueError,'pair_verification'):s.intake(self.request([pin(path)]))

    def test_unknown_focus_is_not_a_negative(self):
        ref=self.pair(known=False)
        with self.assertRaisesRegex(ValueError,'packet_unreviewable'):s.intake(self.request([ref],True))

    def test_cross_role_pixels_reject_reencoded_membership(self):
        a=self.pair(name='aaa');b=self.pair(name='bbb',split='validation')
        request=self.request([a,b],True);request['admission']['pairs'][b['sha256']]='development'
        with self.assertRaisesRegex(ValueError,'cross_role_pixels'):s.intake(request)

    def test_same_app_development_requires_explicit_policy(self):
        a=self.pair(name='training',family='same-app');b=self.pair(name='development',split='validation',family='same-app')
        request=self.request([a,b],True);request['admission']['pairs'][b['sha256']]='development'
        with self.assertRaisesRegex(ValueError,'cross_role_sourceFamilies'):s.intake(request)
        request['admission']['withinFamilyDevelopment']=True
        data=s.intake(request)
        self.assertEqual(data['sourceFamilyOverlap'],['same-app']);self.assertFalse(data['crossApplicationQualification'])

    def test_hcf_appearance_blocks_only_crop_training(self):
        ref=self.pair(profile='hcf');data=s.intake(self.request([ref],True))
        self.assertTrue(data['pairs'][0]['trainingEligible'])
        self.assertIn('hcf_appearance_unqualified',data['frames'][0]['missing'])
        with self.assertRaisesRegex(ValueError,'crop_prerequisites'):s.prepare_crops(data,self.root/'crops',pin(self.tool))

    def test_training_membership_must_match(self):
        ref=self.pair();request=self.request([ref],True);request['admission']['pairs']={}
        with self.assertRaisesRegex(ValueError,'admission_membership'):s.intake(request)
        request=self.request([ref,ref])
        with self.assertRaisesRegex(ValueError,'pair_membership'):s.intake(request)

    def test_two_campaigns_execute_same_adapters(self):
        for name,before,after in [('arrival',None,'button'),('stable','button','button')]:
            request=self.request([self.pair(name,before,after)],True,name='sdk-'+name)
            path=self.root/(name+'.json');q.save(path,request)
            m=s.compile_request(path,self.root/(name+'-compiled'));register(m,self.queue,approve=True)
            ids=[row['job'] for row in m['jobs']]
            for _ in range(2):q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=5)
            self.assertEqual([q.state(self.queue/'jobs'/i)[0] for i in ids],['complete']*3)
            temporal=q.load(self.queue/'jobs'/ids[2]/'attempts/1/out/temporal.json')
            self.assertEqual(temporal['rows'][0]['changed'],int(before!=after))
            self.assertEqual(q.run(self.queue,job_ids=ids,lock=self.root/'lock'),[])

    def test_crop_output_binds_existing_trainer(self):
        train=self.pair(name='train-group');dev=self.pair(name='development-group',split='validation')
        request=self.request([train,dev],True,name='sdk-binding')
        request['admission']['pairs'][dev['sha256']]='development'
        path=self.root/'binding.json';q.save(path,request)
        m=s.compile_request(path,self.root/'binding-compiled');register(m,self.queue,approve=True)
        for _ in range(2):q.run(self.queue,job_ids=[r['job'] for r in m['jobs']],lock=self.root/'lock',max_jobs=5)
        initial=self.root/'software-only-weights.pt';initial.write_text('Software contract only; never execute training.')
        config=self.root/'config.json';q.save(config,dict(initialization=pin(initial),profile='balanced',deduplicate=True,seed=371))
        doc=s.crop_training_description('sdk-binding-crops',pin(config),pin(initial),'sdk-fit','SDK513-SOFTWARE',self.queue)
        self.assertEqual(doc['template'],'T06');self.assertEqual(doc['training']['epochs'],30)
        self.assertEqual(doc['dependencies'][0]['job'],'sdk-binding-crops')

    def test_temporal_rows_use_existing_pixel_preprocessor(self):
        from unittest.mock import patch
        import numpy as np
        import report_additive341 as scorer
        scorer.a.t.set_num_threads(2)
        data=s.intake(self.request([self.pair(before=None,after='button')],True))
        shapes=[]
        def score(net,inputs):
            shapes.append(inputs.shape)
            return np.zeros(len(inputs),dtype=np.float32)
        with patch.object(scorer.a.b.worker,'score',side_effect=score):
            result=scorer.score_rows(None,data['pairs'],False)
        self.assertEqual(result.shape,(1,));self.assertEqual(shapes[0],(1,18,128,192))
        self.assertEqual(data['pairs'][0]['changed'],1)

    def test_queue_failure_is_explicit_and_preserved(self):
        request=self.request([self.pair()]);path=self.root/'bad.json';q.save(path,request)
        m=s.compile_request(path,self.root/'bad-compiled');spec=q.load(checked(m['jobs'][0]['spec']))
        request['admission']=dict(reviewer='software-test',reason='Negative role test',pairs={request['pairs'][0]['sha256']:'test'})
        q.save(path,request,replace=True);spec['request']=pin(path)
        spec['inputs']=[pin(path) if x['path']==q.relative(path) else x for x in spec['inputs']]
        bad=self.root/'bad-spec.json';q.save(bad,spec);q.submit(bad,self.queue)
        import research_approval as approval
        approval.approve(self.queue,spec['id'],'agent:test','Software negative path qualification.')
        q.run(self.queue,job_ids=[spec['id']],lock=self.root/'lock')
        self.assertEqual(q.state(self.queue/'jobs'/spec['id'])[0],'exhausted')
        stderr=(self.queue/'jobs'/spec['id']/'attempts/1/stderr.log').read_text()
        self.assertIn('sdk513_admission_membership',stderr)

if __name__=='__main__':unittest.main()
