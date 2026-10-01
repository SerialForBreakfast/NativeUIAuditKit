"""Generated offline fixtures only; no real labels, encoder or training runs."""
import base64
import copy
import hashlib
import io
from contextlib import redirect_stdout
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from PIL import Image,ImageDraw
import focus_review_continuation as c
import test_human_annotation_review as fixtures


def base_rows():
    rows=[]
    for source in ('train-candidate','human-static-auxiliary'):
        for y in (0,1):
            sid=source+str(y)
            rows.append(dict(id=sid,split='train',use=source,label=y,frameID='original',crop=dict(pixelSHA256=sid)))
    return dict(samples=rows,fullFit=dict(weights={r['id']:(.4 if r['use']=='train-candidate' else .1) for r in rows}))


class WeightTests(unittest.TestCase):
    def additions(self):
        return [dict(id='added:'+str(y),frameID='new',split='train',use='human-static-auxiliary',label=y,crop=dict(pixelSHA256='new'+str(y))) for y in (0,1)]

    def test_exact_mass_and_old_native_preserved(self):
        base=base_rows();rows,w=c.weights(base,self.additions())
        self.assertEqual(len(rows),6);self.assertAlmostEqual(sum(w.values()),1)
        self.assertEqual(w['train-candidate0'],.4)
        self.assertEqual(w['added:1'],.05)
        for y in (0,1):self.assertAlmostEqual(sum(w[r['id']] for r in rows if r['label']==y),.5)

    def test_pending_frame_conflict_and_pair_rejected(self):
        for mode in ('one-label','duplicate','conflict','pair'):
            additions=self.additions()
            if mode=='one-label':additions.pop()
            if mode=='duplicate':additions[1]['id']=additions[0]['id']
            if mode=='conflict':additions[1]['crop']=additions[0]['crop']
            if mode=='pair':additions[0]['pairID']='invented'
            with self.subTest(mode=mode),self.assertRaises(ValueError):c.weights(base_rows(),additions)

    def test_duplicate_mass_shared_not_multiplied(self):
        additions=self.additions();same=copy.deepcopy(additions[0]);same['id']='repeat';additions.append(same)
        _,w=c.weights(base_rows(),additions)
        self.assertAlmostEqual(w['repeat']+w['added:0'],.05)


class ReviewIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ReviewTests();self.f.setUp();h=c.h
        # Every generated frame has contrasting pixels and both focus labels.
        for n,frame in enumerate(self.f.spec['frames']):
            path=h.checked(h.ROOT,frame['image'])
            with Image.open(path) as im:
                im=im.convert('RGB');ImageDraw.Draw(im).rectangle((65,5,95,45),fill=('red' if n==0 else 'blue'));im.save(path)
            frame['image']=h.ref(path)
            obs=h.checked(h.ROOT,frame['observation']);d=h.read(obs);d['data']['observation']['_0']['imageBase64']=base64.b64encode(path.read_bytes()).decode()
            self.f.dump(obs,d);frame['observation']=h.ref(obs)
            frame['proposals'][0]['state']='focused'
            frame['proposals'].append(dict(id='negative',**{'class':'primaryButton'},bounds=[65,5,30,40],state='unfocused'))
        self.f.spec['pairs']=[]  # Static human frames, not native transition pairs.
        self.f.save_spec();self.batch=self.f.imported();self.f.annotate();self.f.finish()
        self.revision=self.f.root/'revision/revision.json'
        h.crop_qa(self.f.batch/'batch.json',self.f.root/'crops',self.revision)
        self.crops=self.f.root/'crops/crop-qa.json'
        self.report=c.review.audit(self.revision,self.crops)
        authority=self.f.root/'authority.txt';authority.write_text('GENERATED TEST ONLY, NOT REAL APPROVAL')
        self.base={**base_rows(),'protocolSHA256':'fixture'}
        self.decision=dict(version='focus-static-addition-admission-v1',approved=True,reviewer='generated-fixture',
            authorizationReference=h.ref(authority),revision=h.ref(self.revision),crops=h.ref(self.crops),baseline='fixture',
            sessionID=self.batch['sessionID'],selectedIDs=[s['id'] for s in self.report['samples']],excluded={},
            sourceReview=dict(evidence=h.ref(authority),decision='development-exposed-no-independent-claim',protectedRolesUnchanged=True,developmentMembershipUnchanged=True))

    def tearDown(self):self.f.tearDown()

    def admit(self):
        return c.admit(self.report,self.decision,c.h.ref(self.revision),c.h.ref(self.crops),self.base,self.batch,set())

    def test_real_review_crop_admission_weight_chain(self):
        before=c.h.sha(self.revision);rows=self.admit()
        self.assertEqual(len(rows),4);self.assertTrue(all('pairID' not in r for r in rows))
        combined,w=c.weights(self.base,rows)
        self.assertEqual(len(combined),8);self.assertAlmostEqual(sum(w.values()),1)
        self.assertEqual(c.h.sha(self.revision),before)
        self.assertEqual({r['label'] for r in rows},{0,1})

    def test_unconfirmed_software_or_stale_cannot_admit(self):
        for mode in ('reviewer','state','approval','membership','revision','relationship'):
            with self.subTest(mode=mode):
                report=copy.deepcopy(self.report);decision=copy.deepcopy(self.decision)
                if mode=='reviewer':report['reviewer']['kind']='software-test'
                if mode=='state':report['samples'][0]['state']='unknown'
                if mode=='approval':decision['approved']=False
                if mode=='membership':decision['selectedIDs'].pop()
                if mode=='revision':decision['revision']['sha256']='bad'
                if mode=='relationship':decision['sourceReview']['protectedRolesUnchanged']=False
                with self.assertRaises(ValueError):c.admit(report,decision,c.h.ref(self.revision),c.h.ref(self.crops),self.base,self.batch,set())

    def test_protected_crop_frame_and_baseline_duplicate(self):
        for px in (self.report['samples'][0]['pixelSHA256'],self.report['frames'][0]['pixelSHA256']):
            with self.assertRaisesRegex(ValueError,'overlap'):
                c.admit(self.report,self.decision,c.h.ref(self.revision),c.h.ref(self.crops),self.base,self.batch,{px})
        self.base['samples'][0]['crop']['pixelSHA256']=self.report['samples'][0]['pixelSHA256']
        with self.assertRaisesRegex(ValueError,'duplicate'):self.admit()

    def test_corrupt_crop_rejected_by_actual_audit(self):
        c.h.checked(c.h.ROOT,self.report['samples'][0]['crop']).write_bytes(b'bad')
        with self.assertRaises(ValueError):c.review.audit(self.revision,self.crops)

    def test_trainer_dispatch_missing_approval_no_torch_import(self):
        doc=dict(version=c.VERSION,inputs={},blockers=['missing_new_feature_cache'],configuration={},selection={},representation={},warmCheckpoint=None,
                 runtime={},counts={},fullFit={},unmetQualificationBlockers=[],baseCachedInputs={},samples=[])
        doc['protocolSHA256']=c.digest(doc);path=self.f.root/'protocol.json';c.h.write(path,doc)
        import focus_learning_experiment as dispatch
        with patch.object(c,'assemble',return_value=doc):
            report,rows=dispatch.load_protocol(path,c.ARM,'generated-preflight-only')
        self.assertFalse(report['launchEligible']);self.assertIn('missing_run_approval',report['blockers']);self.assertEqual(rows,[])
        with patch.object(c,'assemble',return_value=doc),self.assertRaises(ValueError):dispatch.load_protocol(path,'full-corpus-fit','generated-preflight-only')

    def test_actual_assembly_and_trainer_dispatch_with_generated_data(self):
        h=c.h;root=self.f.root
        def save(name,doc,seal=None):
            if seal:doc[seal]=c.digest(doc)
            path=root/name;h.write(path,doc);return h.ref(path)
        protected=save('protected.json',{})
        reserved=save('reserved.json',dict(samples=[]),'seal')
        assembly=save('assembly.json',dict(protectedMetadata=protected,reservedPixels=reserved),'assemblySHA256')
        static=save('static.json',dict(inputs=dict(assembly=assembly)),'protocolSHA256')
        receipt=save('baseline-receipt.json',dict(featureStateSHA256='encoder-state'))
        base=copy.deepcopy(self.base);base.pop('protocolSHA256')
        for n,row in enumerate(base['samples']):
            im=root/f'old-{n}.png';Image.new('RGB',(256,256),(n*30,100,80)).save(im)
            row['crop']={**h.ref(im),'pixelSHA256':h.pixel_digest(h.ROOT,h.ref(im))};row['image']=h.ref(im)
        val=copy.deepcopy(base['samples'][0]);val['id']='validation';val['split']='validation'
        im=root/'val.png';Image.new('RGB',(256,256),'green').save(im)
        val['crop']={**h.ref(im),'pixelSHA256':h.pixel_digest(h.ROOT,h.ref(im))};val['image']=h.ref(im)
        base['samples'].append(val)
        base.update(version='focus-full-fit-v1',inputs=dict(base=static,receipt=receipt,cache=receipt,preflight=receipt),configuration=dict(c.full.CONFIG),selection={},representation={},counts=dict(development=1,retention=0),unmetQualificationBlockers=[])
        baseline=save('baseline.json',base,'protocolSHA256')
        decision=copy.deepcopy(self.decision);decision['baseline']=base['protocolSHA256']
        admission=save('admission.json',decision)
        spec=dict(version='focus-review-continuation-input-v1',baseline=baseline,batch=h.ref(self.f.batch/'batch.json'),revision=h.ref(self.revision),crops=h.ref(self.crops),admission=admission)
        import focus_learning_experiment as dispatch
        with patch.object(c,'BASE_SEAL',base['protocolSHA256']),patch.object(c.full.s,'SESSION','session'):
            doc=c.assemble(spec)
            self.assertEqual(doc['counts'],dict(training=8,added=4,development=1,retention=0))
            self.assertEqual(doc['samples'][-1],val)
            self.assertEqual(doc['blockers'],['missing_new_feature_cache'])
            path=root/'assembled.json';h.write(path,doc)
            report,rows=dispatch.load_protocol(path,c.ARM,'generated-review-preflight')
            self.assertEqual(len(rows),9);self.assertFalse(report['launchEligible'])
            authority=h.ref(root/'authority.txt')
            wrong=save('encoding-denied.json',dict(approved=False))
            with self.assertRaisesRegex(ValueError,'missing_encoding_approval'):
                c.encode_new(path,h.checked(h.ROOT,wrong),root/'never-created')
            self.assertFalse((root/'never-created').exists())
            members=[dict(id=r['id'],label=r['label'],crop=r['crop']) for r in doc['samples'] if r['id'].startswith('added:')]
            feature_receipt=save('new-receipt.json',dict(version='focus-static-addition-features-v1',members=members,representation={},backboneUnchanged=True,featureStateSHA256='encoder-state',featureSHA256='0'*64))
            cache=root/'cache.pt';cache.write_bytes(b'fixture cache: metadata preflight only')
            spec['newFeatures']=dict(receipt=feature_receipt,cache=h.ref(cache))
            ready=c.assemble(spec);self.assertEqual(ready['blockers'],[])
            path=root/'ready.json';h.write(path,ready)
            approval=save('run-approval.json',dict(version='focus-reviewed-full-fit-approval-v1',approved=True,protocolSHA256=ready['protocolSHA256'],arm=c.ARM,runName='generated-review-preflight',scope='one-run-no-export-no-promotion',authorizationReference=authority))
            report,_=dispatch.load_protocol(path,c.ARM,'generated-review-preflight',h.checked(h.ROOT,approval))
            self.assertTrue(report['launchEligible']);self.assertFalse(report['executionAuthorized'])
            import train_focus_ring_detector as trainer
            stdout=io.StringIO()
            with patch.object(sys,'argv',['trainer','--experiment-protocol',str(path),'--experiment-arm',c.ARM,'--name','generated-review-preflight','--preflight']),redirect_stdout(stdout):
                self.assertEqual(trainer.main(),2)
            self.assertEqual(json.loads(stdout.getvalue())['blockers'],['missing_run_approval'])
            # Changing either the pinned review bytes or feature membership is rejected.
            bad=copy.deepcopy(h.read(h.checked(h.ROOT,feature_receipt)));bad['members'].pop()
            spec['newFeatures']['receipt']=save('bad-receipt.json',bad)
            with self.assertRaisesRegex(ValueError,'membership'):c.assemble(spec)
            h.checked(h.ROOT,admission).write_bytes(b'changed')
            with self.assertRaises(ValueError):c.assemble(spec)


class FeatureTests(unittest.TestCase):
    def test_merge_cached_features_preserves_baseline_and_rejects_order(self):
        import torch
        f=fixtures.ReviewTests();f.setUp()
        try:
            old=[dict(id='old',label=0)];val=[dict(id='val',label=1)];extra=[dict(id='new',label=1,crop={})]
            x=torch.zeros(1,576);y=torch.zeros(1,1);vx=torch.ones(1,576);vy=torch.ones(1,1)
            sha=lambda t:hashlib.sha256(t.numpy().tobytes()).hexdigest()
            receipt=dict(trainCount=1,validationCount=1,trainFeatureSHA256=sha(x),validationFeatureSHA256=sha(vx),featureStateSHA256='encoder')
            cache=f.root/'old.pt';torch.save(dict(train=(x,y),validation=(vx,vy),receipt=receipt),cache)
            base=f.root/'base.json';c.h.write(base,dict(samples=[dict(old[0],split='train'),dict(val[0],split='validation')]))
            receipt_path=f.root/'old.json';c.h.write(receipt_path,receipt)
            new_receipt=dict(featureSHA256=sha(vx),featureStateSHA256='encoder',members=extra);new_path=f.root/'new.json';c.h.write(new_path,new_receipt)
            new_cache=f.root/'new.pt';torch.save(dict(train=(vx,vy),receipt=new_receipt),new_cache)
            report=dict(baseCachedInputs=dict(base=c.h.ref(base),cache=c.h.ref(cache),receipt=c.h.ref(receipt_path)),reviewedExtension=dict(cache=c.h.ref(new_cache),receipt=c.h.ref(new_path)))
            out=f.root/'output';out.mkdir()
            model,train,validation=c.prepare_features(report,old+extra,val,torch.device('cpu'),out)
            self.assertEqual(sum(p.numel() for p in model.parameters()),577)
            self.assertTrue(torch.equal(train.tensors[0][0],x[0]));self.assertTrue(torch.equal(validation.tensors[0],vx))
            with self.assertRaises(ValueError):c.prepare_features(report,extra+old,val,torch.device('cpu'),out)
            for mode in ('nan','label','width','receipt'):
                bad_x=vx.clone();bad_y=vy.clone();bad_receipt=copy.deepcopy(new_receipt)
                if mode=='nan':bad_x[0,0]=float('nan')
                if mode=='label':bad_y[0,0]=0
                if mode=='width':bad_x=bad_x[:,:2]
                if mode=='receipt':bad_receipt['featureStateSHA256']='different'
                bad_path=f.root/f'{mode}.pt';torch.save(dict(train=(bad_x,bad_y),receipt=bad_receipt),bad_path)
                changed=copy.deepcopy(report);changed['reviewedExtension']['cache']=c.h.ref(bad_path)
                with self.subTest(mode=mode),self.assertRaises(ValueError):
                    c.prepare_features(changed,old+extra,val,torch.device('cpu'),out)
        finally:f.tearDown()


if __name__=='__main__':unittest.main()
