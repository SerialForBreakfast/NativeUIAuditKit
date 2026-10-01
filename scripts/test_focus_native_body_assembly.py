"""Native assembly tests use isolated generated data, no model or real admission."""
import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import focus_native_body_assembly as a
import test_fixture_batch_review as fixtures
from test_fixture_rendered_body import body


def row(sid,px,label,**kw):
    return dict(id=sid,label=label,crop=dict(pixelSHA256=px),frame=dict(pixelSHA256='frame-'+sid),
        sourceKind='tvos_native_generator',relatedGroup=a.SOURCE_GROUP,intrinsicGroup=a.SOURCE_GROUP,
        recipeSeed=7,reasons=[],split='development',scene='grid',style='dark',control='primaryButton',**kw)


class AccountingTests(unittest.TestCase):
    def test_capture_generation_is_not_an_annotation_conflict(self):
        proposal=dict(bounds=[1,2,3,4],state='focused',renderedBodyGeometry=dict(generation=1,role='rendered_control_body'))
        first=dict(id='a',pixelSHA256='same',proposals=[proposal])
        second=copy.deepcopy(first);second['id']='b'
        second['proposals'][0]['renderedBodyGeometry']['generation']=2
        before=copy.deepcopy([first,second])
        self.assertEqual(a.annotation_conflicts([first,second]),set())
        self.assertEqual([first,second],before)
        for key,value in [('state','unfocused'),('bounds',[2,2,3,4])]:
            changed=copy.deepcopy(second);changed['proposals'][0][key]=value
            self.assertEqual(a.annotation_conflicts([first,changed]),{'a','b'})

    def test_deterministic_duplicates_and_all_conflicting_labels_blocked(self):
        rows=[row('b','same',1),row('a','same',1),row('c','other',0)]
        one=a.classify(rows,[],set());two=a.classify(list(reversed(rows)),[],set())
        self.assertEqual(one,two);self.assertEqual(one[1]['duplicateOf'],'a')
        rows.append(row('d','same',0));result=a.classify(rows,[],set())
        self.assertEqual(sum('conflicting_crop_labels' in r['reasons'] for r in result),3)

    def test_baseline_protected_pixels_lineage_and_unknown_body(self):
        old=dict(row('old','old-pixel',0),split='validation')
        for candidate,reason in [(row('x','old-pixel',0),'baseline_duplicate_crop'),
                                 (row('x','protected',0),'protected_or_evaluation_overlap'),
                                 (row('x','other',1),'evaluation_lineage_overlap')]:
            self.assertIn(reason,a.classify([candidate],[old],{'protected'})[0]['reasons'])
        r=row('x','other',1);r['reasons']=['incomplete_body_inventory']
        self.assertEqual(a.classify([r],[],set())[0]['disposition'],'blocked')
        r['label']=True
        with self.assertRaisesRegex(ValueError,'invalid_native_label'):a.classify([r],[],set())

    def test_weights_preserve_human_mass_and_balance_native_strata(self):
        native=[dict(row(kind+str(y),kind+str(y),y),split='train',use='train-candidate',sourceKind=kind)
                for kind in ('tvos_simulator_os','simulatorFixture') for y in (0,1)]
        human=[dict(row('human'+str(y),'human'+str(y),y),split='train',use='human-static-auxiliary') for y in (0,1)]
        base=dict(samples=native+human,fullFit=dict(weights={r['id']:(.1 if r in human else .2) for r in native+human}))
        additions=[dict(row('new'+str(y),'new'+str(y),y),split='train',use='train-candidate') for y in (0,1)]
        w=a.weighting(base,additions)
        self.assertAlmostEqual(sum(w.values()),1)
        self.assertEqual(w['human0'],.1);self.assertEqual(w['human1'],.1)
        self.assertEqual(a.weighting(base,[]),base['fullFit']['weights'])
        for y in (0,1):self.assertAlmostEqual(sum(w[r['id']] for r in native+additions if r['label']==y),.4)
        additions[0]['control']='unpaired-class'
        with self.assertRaisesRegex(ValueError,'label_support'):a.weighting(base,additions)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReviewTests();self.f.setUp();self.f.attach();self.root=self.f.root
        def walk(value):
            if isinstance(value,dict):
                for child in list(value.values()):walk(child)
                if 'scene_width' in value:
                    for e in value['elements']:
                        x,y,w,ht=e['pixel_bounds'];W,H=value['scene_width'],value['scene_height']
                        b=body(e['element_id'],value['focus_observation']['generation'])
                        b.update(full_pixel_bounds=[x,y,w,ht],visible_pixel_bounds=[x,y,w,ht],
                                 visible_normalized_bounds=[x/W,y/H,(x+w)/W,(y+ht)/H])
                        e['rendered_body_geometry']=b
            elif isinstance(value,list):
                for child in value:walk(child)
        walk(self.f.f.meta);self.f.f.mutate(lambda m:None)
        self.f.prepare(body_geometry=True,count=1)
        self.entry=dict(batch=a.h.ref(self.root/'qa/native-review/batch.json'),crops=a.h.ref(self.root/'qa/crops/crop-qa.json'))

    def tearDown(self):self.f.tearDown()

    def save(self,name,doc):
        p=self.root/name;a.h.write(p,doc);return a.h.ref(p)

    def test_native_crop_projection_preserved_no_fake_human_or_pairs(self):
        before=a.h.sha(self.root/'qa/native-review/batch.json')
        rows,accounting,pairs=a.candidates([self.entry],set())
        self.assertEqual(len(rows),2);self.assertEqual({r['label'] for r in rows},{0,1})
        self.assertTrue(pairs);self.assertTrue(accounting)
        self.assertTrue(all(r['labelSource']=='observed_native_bracket' and 'pairID' not in r for r in rows))
        self.assertEqual(a.h.sha(self.root/'qa/native-review/batch.json'),before)

    def test_protected_rejected_before_native_decode(self):
        raw=a.h.read(self.root/'qa/native-review/batch.json')
        with patch.object(a.native,'source_record',side_effect=AssertionError('must not decode')):
            rows,accounting,pairs=a.candidates([self.entry],{raw['frames'][0]['image']['sha256']})
        self.assertEqual(rows,[]);self.assertEqual(pairs,[])
        self.assertEqual(accounting[0]['reason'],'protected_reference_before_decode')
        self.assertEqual(len(accounting[0]['controlIDs']),2)

    def test_resealed_annotation_cannot_override_native_projection(self):
        raw=a.h.read(self.root/'qa/native-review/batch.json')
        raw.pop('seal');proposal=raw['frames'][0]['proposals'][0]
        proposal['state']='unfocused' if proposal['state']=='focused' else 'focused'
        raw['seal']=a.h.digest(raw)
        ref=self.save('tampered-batch.json',raw)
        with self.assertRaisesRegex(ValueError,'native_review_projection_changed'):
            a.candidates([dict(self.entry,batch=ref)],set())

    def test_larger_assembly_is_bounded_and_still_reassembled(self):
        doc=dict(version=a.VERSION,inputs={});doc['protocolSHA256']=a.h.digest(doc)
        path=self.root/'large-protocol.json'
        path.write_text(' '*(9*1024*1024)+json.dumps(doc))
        with patch.object(a,'assemble',side_effect=ValueError('reassembly_required')) as check:
            with self.assertRaisesRegex(ValueError,'reassembly_required'):
                a.load_protocol(path,a.ARM,'large-test')
            check.assert_called_once_with({})
        path.write_text(' '*(a.ASSEMBLY_MAX_BYTES+1))
        with patch.object(a,'assemble',side_effect=AssertionError('must not parse oversized document')):
            with self.assertRaisesRegex(ValueError,'json_size_limit'):
                a.load_protocol(path,a.ARM,'large-test')

    def test_membership_and_protocol_and_changed_crop_rejected(self):
        original=a.h.read(self.root/'qa/crops/crop-qa.json')
        for index,mode in enumerate(('missing','duplicate','protocol','batch')):
            qa=copy.deepcopy(original);qa.pop('seal')
            if mode=='missing':qa['crops'].pop()
            if mode=='duplicate':qa['crops'].append(qa['crops'][0])
            if mode=='protocol':qa['preprocessing']['expansion']=.35
            if mode=='batch':qa['batch']['sha256']='0'*64
            qa['seal']=a.h.digest(qa);ref=self.save(str(index)+'.json',qa)
            with self.subTest(mode=mode),self.assertRaises(ValueError):a.candidates([dict(self.entry,crops=ref)],set())
        crop=a.h.checked(a.h.ROOT,original['crops'][0]['crop']);crop.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'changed_hash'):a.candidates([self.entry],set())

    def decision(self,rows,spec):
        evidence=self.save('generated-approval-evidence.json',{'softwareFixtureOnly':True})
        return dict(version='focus-native-body-admission-v1',approved=True,reviewer='software-test',authorizationReference=evidence,
            inputs={k:spec[k] for k in ('inventory','sources')},selectedIDs=[r['id'] for r in rows],excluded={},
            sourceReview=dict(evidence=evidence,relationshipsKnown=True,protectedRolesUnchanged=True,group=a.SOURCE_GROUP,
                              role='training-candidate',independentEvaluationClaim=False),
            geometryAcceptance=dict(evidence=evidence,accepted=True,batches=[self.entry['batch']]))

    def test_exact_admission_and_blocked_diagnostic_cannot_slip_through(self):
        rows,_,_=a.candidates([self.entry],set());rows=a.classify(rows,[],set())
        spec=dict(inventory={},sources=[self.entry]);decision=self.decision(rows,spec)
        self.assertEqual(len(a.admit(rows,decision,spec,[])),2)
        for mode in ('approval','selected','input','scope','source','blocked'):
            d=copy.deepcopy(decision);r=copy.deepcopy(rows)
            if mode=='approval':d['approved']=False
            if mode=='selected':d['selectedIDs'].pop()
            if mode=='input':d['inputs']['inventory']={'changed':True}
            if mode=='scope':d['geometryAcceptance']['batches']=[]
            if mode=='source':d['sourceReview']['relationshipsKnown']=False
            if mode=='blocked':r[0]['reasons']=['incomplete_body_inventory']
            with self.subTest(mode=mode),self.assertRaises(ValueError):a.admit(r,d,spec,[])

    def test_real_assembly_cli_dispatch_and_trainer_refuses_execution(self):
        # Only the historical baseline audit is substituted. New native input,
        # cropping, admission, weighting, sealing and real trainer dispatch run.
        from PIL import Image
        baseline_rows=[]
        for n,(kind,use,split) in enumerate([('tvos_simulator_os','train-candidate','train'),
                                           ('simulatorFixture','train-candidate','train'),
                                           ('human','human-static-auxiliary','train'),
                                           ('real','representative-selection','validation')]):
            for y in (0,1):
                p=self.root/f'base-{n}-{y}.png';Image.new('RGB',(256,256),(20+n*40,10+y*70,110)).save(p)
                ref=a.h.ref(p);r=row(f'{n}-{y}',a.h.pixel_digest(a.h.ROOT,ref),y)
                r.update(sourceKind=kind,use=use,split=split,crop=dict(ref,pixelSHA256=r['crop']['pixelSHA256']),
                         frame=dict(ref,pixelSHA256=r['crop']['pixelSHA256']),recipeSeed=100+n,relatedGroup=kind,intrinsicGroup=kind)
                baseline_rows.append(r)
        cache=self.save('cache.json',{'featureStateSHA256':'test-encoder'})
        protected=self.save('protected-meta.json',{})
        reserved=dict(samples=[]);reserved['seal']=a.h.digest(reserved)
        reservation=self.save('reserved.json',reserved)
        admission=self.save('prior-admission.json',dict(reservedPixels=reservation))
        base=dict(protocolSHA256=a.BASE_SEAL,samples=baseline_rows,
            fullFit=dict(weights={r['id']:(.1 if r['use']=='human-static-auxiliary' else .2) for r in baseline_rows if r['split']=='train'}),
            baseCachedInputs=dict(cache=cache,receipt=cache,preflight=cache),inputs=dict(newFeatures=dict(cache=cache,receipt=cache)),
            configuration=dict(epochs=1000,batch=6,lr=.01,model='mobilenet_v3_small_frozen'),selection={'untouched':True},representation={})
        invref=self.save('inventory.json',{});inventory=dict(protocol=cache,admission=admission,protectedMetadata=protected)
        spec=dict(version=a.INPUT_VERSION,inventory=invref,sources=[self.entry])
        verified=(inventory,base,dict(records=[]),set(),{})
        import focus_mixed_assembly as mixed
        import train_focus_ring_detector as trainer
        with patch.object(a,'verified_inventory',return_value=verified):
            blocked=mixed.assemble(spec);self.assertEqual(blocked['samples'],baseline_rows)
            self.assertEqual(blocked['counts']['added'],0)
            decision=self.decision(blocked['candidates'],spec);spec['admission']=self.save('admit.json',decision)
            doc=mixed.assemble(spec);self.assertEqual(doc['counts']['added'],2)
            continuous=mixed.assemble(dict(spec,weightPolicy=a.CONTINUITY_POLICY))
            self.assertEqual(continuous['samples'],doc['samples'])
            self.assertEqual(continuous['fullFit']['weights'],a.continuous_weights(base,continuous['samples'][len(baseline_rows)-2:-2]))
            cpath=a.h.checked(a.h.ROOT,self.save('continuous.json',continuous))
            creport,_=a.load_protocol(cpath,a.ARM,'continuous-dry-run')
            self.assertFalse(creport['launchEligible'])
            self.assertEqual(doc['samples'][-2:],baseline_rows[-2:]);self.assertEqual(doc['selection'],base['selection'])
            self.assertEqual(len(doc['encodingPlan']['members']),2)
            ref=self.save('assembled.json',doc);path=a.h.checked(a.h.ROOT,ref)
            report,rows=a.load_protocol(path,a.ARM,'fixture-dry-run');self.assertFalse(report['launchEligible']);self.assertEqual(len(rows),10)
            with self.assertRaisesRegex(ValueError,'not_execution'):a.load_protocol(path,a.ARM,'fixture-dry-run',path)
            output=io.StringIO()
            with patch.object(sys,'argv',['trainer','--experiment-protocol',str(path),'--experiment-arm',a.ARM,'--name','fixture-dry-run','--execute']),redirect_stdout(output),patch.dict(sys.modules,{'torch':None,'torchvision':None}):
                self.assertEqual(trainer.main(),2)
            self.assertFalse(json.loads(output.getvalue())['launchEligible'])
            self.assertFalse((a.h.ROOT/'NativeUITrainer/focus_ring_runs/fixture-dry-run').exists())
            dataset=self.root/'dataset';dataset.mkdir();a.h.write(dataset/'focus_dataset_manifest.json',doc)
            from focus_training_preflight import preflight
            ordinary=preflight(dataset,'fixture-dry-run')
            self.assertIn('data_admission_is_not_training_execution_approval',ordinary['blockers'])
            with self.assertRaisesRegex(ValueError,'explicit_dry_run'):trainer.load_samples(dataset,'train')
            bad=copy.deepcopy(doc);bad['samples'][-1]['label']=1-bad['samples'][-1]['label']
            bad.pop('protocolSHA256');bad['protocolSHA256']=a.h.digest(bad)
            badpath=a.h.checked(a.h.ROOT,self.save('resealed-bad.json',bad))
            with self.assertRaisesRegex(ValueError,'changed_native_assembly_inputs'):a.load_protocol(badpath,a.ARM,'fixture-dry-run')


if __name__=='__main__':unittest.main()
