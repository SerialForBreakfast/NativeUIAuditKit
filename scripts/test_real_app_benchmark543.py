"""Software fixtures only. No app, model, capture, or human-review qualification."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import research_queue as q
from experiment_templates import pin
import real_app_benchmark543 as m

class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.root=Path(self.tmp.name)
        marker=self.root/'receipt.json';q.save(marker,{'softwareFixture':True});self.ref=pin(marker)
        image=self.root/'frame.png';Image.new('RGB',(100,80),(12,34,56)).save(image)
        self.case=dict(id='case-one',app='test-app',flow='flow-one',group='group-one',status='captured',width=100,height=80,
                       image=pin(image),pixelSHA256=hashlib.sha256(Image.open(image).convert('RGB').tobytes()).hexdigest(),sdkEvidence=self.ref)
        self.labels=dict(imageSHA256=self.case['image']['sha256'],complete=True,objects=[dict(id='control',**{'class':'button'},box=[10,10,30,20],visibility='visible',provenance='synthetic software fixture')],focus=dict(state='focused',box=[10,10,30,20]),review=dict(blinded=True,reviewer='test-only',status='accepted'))
        self.lp=self.root/'labels.json';q.save(self.lp,self.labels);self.case['labels']=pin(self.lp)
        baseline=dict(inputMode='screenshots-only',coordinates='xywh-top-left-pixels',orientation='upright',confidence=.5,matchingIoU=.5,ttrRevision='a'*40,**{k:self.ref for k in ('detector','focus','runtimeReceipt','preprocessing','taxonomy')})
        runtime=self.root/'runtime.json';q.save(runtime,dict(version='real-app-runtime-v1',observedLoaded=True,inputMode='screenshots-only',ttrRevision='a'*40,**{k+'SHA256':self.ref['sha256'] for k in ('detector','focus','preprocessing','taxonomy')}));baseline['runtimeReceipt']=pin(runtime)
        self.manifest=dict(version=m.VERSION,platform='tvOS',profile='standard',phase='pilot',trainingEligible=False,classes=['button','label'],baseline=baseline,apps=[dict(id='test-app',ancestry='independent-source',kind='independent-app',trainingExposure='excluded',sourceRevision='b'*40,qualification=self.ref)],exclusions=dict(groups=[],flows=[],images=[],pixels=[]),cases=[self.case])
        app=self.manifest['apps'][0];ap=self.root/'app.json';q.save(ap,dict(version='real-app-qualification-v1',**{k:app[k] for k in ('id','ancestry','sourceRevision','trainingExposure')},independent=True,controlledContent=True,sdkObservationsVerified=True,softwareFixture=True));app['qualification']=pin(ap)
        self.mp=self.root/'manifest.json';self.fp=self.root/'freeze.json'
    def tearDown(self):self.tmp.cleanup()
    def frozen(self):
        q.save(self.lp,self.labels,replace=True);self.case['labels']=pin(self.lp);q.save(self.mp,self.manifest,replace=True)
        m.freeze(self.mp,self.fp);return pin(self.fp)
    def prediction(self,fr):
        digest=q.text_digest(self.manifest['baseline'])
        return dict(freeze=fr,inputMode='screenshots-only',baselineSHA256=digest,cases=[dict(id='case-one',status='ok',imageSHA256=self.case['image']['sha256'],pixelSHA256=self.case['pixelSHA256'],baselineSHA256=digest,runtimeReceipt=self.manifest['baseline']['runtimeReceipt'],latencyMs=12,latencyScope='end-to-end-consumer',detections=[dict(**{'class':'button'},box=[10,10,30,20],score=.9)],focusBox=[10,10,30,20])])
    def report(self,edit=None):
        f=self.frozen();p=self.prediction(f)
        if edit:edit(p['cases'][0])
        return m.score(f,p)
    def test_exact_and_blind_pixels(self):
        r=self.report();self.assertEqual(r['overall']['correctFocus']['value'],1);self.assertEqual(r['overall']['perClass']['button']['recall']['value'],1)
        pixels=q.load(self.fp.with_name('freeze-pixels.json'));self.assertEqual(set(pixels['cases'][0]),{'id','image'})
        self.assertNotIn('sdkEvidence',json.dumps(pixels));self.assertFalse(r['modelAccepted'])
    def test_durable_timing_is_not_full_latency(self):
        r=self.report(lambda p:p.update(latencyScope='request-to-result-durable'))
        self.assertEqual(r['overall']['latencyMs']['count'],0)
        self.assertEqual(r['overall']['latencyMs']['missing'],1)
        self.assertIsNone(r['overall']['latencyMs']['median'])
        self.assertEqual(r['overall']['timingByScope']['request-to-result-durable']['median'],12)
        self.assertEqual(r['overall']['correctFocus']['value'],1)
    def test_unavailable_timing_preserves_accuracy_and_reason(self):
        r=self.report(lambda p:p.update(latencyScope='unavailable',latencyMs=None,latencyUnavailableReason='Producer does not measure caller timing.'))
        self.assertEqual(r['overall']['unavailableTiming'],1)
        self.assertEqual(r['overall']['latencyMs']['missing'],1)
        self.assertEqual(r['overall']['correctFocus']['value'],1)
        self.assertTrue(r['rows'][0]['latencyUnavailableReason'])
    def test_unavailable_timing_requires_reason(self):
        with self.assertRaisesRegex(ValueError,'latency_unavailable_reason'):
            self.report(lambda p:p.update(latencyScope='unavailable',latencyMs=None))
    def test_unavailable_timing_rejects_fabricated_number(self):
        with self.assertRaisesRegex(ValueError,'latency_unavailable_reason'):
            self.report(lambda p:p.update(latencyScope='unavailable',latencyUnavailableReason='missing'))
    def test_unknown_timing_scope_rejected(self):
        with self.assertRaisesRegex(ValueError,'latency_scope'):
            self.report(lambda p:p.update(latencyScope='fast-inference'))
    def test_timing_zero_is_not_missing(self):
        r=self.report(lambda p:p.update(latencyMs=0))
        self.assertEqual(r['overall']['latencyMs']['count'],1)
        self.assertEqual(r['overall']['latencyMs']['missing'],0)
        self.assertEqual(r['overall']['latencyMs']['median'],0)
    def test_failed_timing_does_not_enter_latency(self):
        r=self.report(lambda p:p.update(status='failed',error='timeout',detections=[],focusBox=None,latencyMs=120))
        self.assertEqual(r['overall']['latencyMs']['missing'],1)
        self.assertEqual(r['overall']['timingByScope']['end-to-end-consumer']['count'],0)
    def test_wrong_class(self):
        r=self.report(lambda p:p['detections'][0].update({'class':'label'}));self.assertEqual(r['overall']['wrongClasses'],1);self.assertEqual(r['overall']['perClass']['button']['recall']['value'],0)
    def test_duplicate_prediction_is_false_detection(self):
        r=self.report(lambda p:p['detections'].append(copy.deepcopy(p['detections'][0])));self.assertEqual(r['overall']['perClass']['button']['precision']['value'],.5)
    def test_localization(self):
        r=self.report(lambda p:p['detections'][0].update(box=[25,10,30,20]));self.assertEqual(r['overall']['localizationErrors'],1)
    def test_empty_prediction_abstains(self):
        r=self.report(lambda p:p.update(detections=[],focusBox=None));self.assertEqual(r['overall']['focusCounts'],{'abstention':1})
    def test_no_focus_false_selection(self):
        self.labels['focus']={'state':'no_focus','box':None};r=self.report();self.assertEqual(r['overall']['falseNoFocusSelection']['value'],1)
    def test_no_focus_correct_abstention(self):
        self.labels['focus']={'state':'no_focus','box':None};r=self.report(lambda p:p.update(focusBox=None));self.assertEqual(r['overall']['focusCounts'],{'correct-abstention':1})
    def test_unknown_focus_not_zero(self):
        self.labels['focus']={'state':'unknown','box':None};r=self.report();self.assertIsNone(r['overall']['correctFocus']['value'])
    def test_failed_inference_stays_in_denominator(self):
        r=self.report(lambda p:p.update(status='failed',error='test_timeout',detections=[],focusBox=None,latencyMs=None));self.assertEqual(r['overall']['executionFailures'],1);self.assertEqual(r['overall']['correctFocus']['denominator'],1);self.assertEqual(r['overall']['correctFocus']['value'],0)
    def test_partial_labels_do_not_establish_precision(self):
        self.labels['complete']=False;r=self.report();self.assertIsNone(r['overall']['perClass']['button']['precision']['value']);self.assertEqual(r['officialCOCO']['status'],'unavailable')
    def test_unresolved_labels_not_false_positives(self):
        self.labels['objects'][0]['class']=None;r=self.report();self.assertEqual(r['overall']['unresolvedAnnotations'],1);self.assertIsNone(r['overall']['perClass']['button']['precision']['value'])
    def test_unreviewed_rejected(self):
        self.labels['review']['status']='pending'
        with self.assertRaisesRegex(ValueError,'human_review'):self.frozen()
    def test_nonblind_rejected(self):
        self.labels['review']['blinded']=False
        with self.assertRaisesRegex(ValueError,'human_review'):self.frozen()
    def test_leakage_rejected(self):
        self.manifest['exclusions']['groups']=['group-one']
        with self.assertRaisesRegex(ValueError,'flow_leakage'):self.frozen()
    def test_duplicate_pixels_rejected(self):
        other=copy.deepcopy(self.case);other['id']='other';self.manifest['cases'].append(other)
        with self.assertRaisesRegex(ValueError,'pixel_leakage'):self.frozen()
    def test_missing_runtime_rejected(self):
        f=self.frozen();p=self.prediction(f);p['cases'][0]['runtimeReceipt']={'path':'bad','sha256':'0'*64}
        with self.assertRaisesRegex(ValueError,'loaded_runtime'):m.score(f,p)
    def test_missing_prediction_rejected(self):
        f=self.frozen();p=self.prediction(f);p['cases']=[]
        with self.assertRaisesRegex(ValueError,'prediction_membership'):m.score(f,p)
    def test_nan_rejected(self):
        with self.assertRaisesRegex(ValueError,'prediction_values'):self.report(lambda p:p['detections'][0].update(score=float('nan')))
    def test_dimension_mismatch(self):
        self.case['width']=101
        with self.assertRaisesRegex(ValueError,'image_geometry'):self.frozen()
    def test_modified_label_hash_rejected(self):
        f=self.frozen();p=self.prediction(f);self.lp.write_text('{}')
        with self.assertRaises(ValueError):m.score(f,p)
    def test_missing_case_remains_counted(self):
        self.manifest['cases'].append(dict(id='missing',app='test-app',flow='flow-two',group='group-two',status='missing',reason='not captured'))
        r=self.report();self.assertEqual(r['overall']['planned'],2);self.assertEqual(r['overall']['missing'],1)
    def test_review_contains_no_predictions(self):
        q.save(self.mp,self.manifest);dest=self.root/'review';m.blind_review(self.mp,dest)
        draft=q.load(dest/'case-one.json');self.assertEqual(draft['review']['status'],'pending');self.assertNotIn('detections',draft)
    def test_predeclared_candidate_and_comparison(self):
        candidate=copy.deepcopy(self.manifest['baseline']);candidate['confidence']=.95
        self.manifest['candidates']=[candidate];f=self.frozen();p=self.prediction(f);a=m.score(f,p)
        digest=q.text_digest(candidate);p['baselineSHA256']=digest;p['cases'][0]['baselineSHA256']=digest
        b=m.score(f,p);self.assertEqual(m.compare(a,b)['lostControls'],[('case-one','control')])
    def test_undeclared_candidate_rejected(self):
        f=self.frozen();p=self.prediction(f);p['baselineSHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'undeclared_candidate'):m.score(f,p)
    def test_qualification_requires_200_and_five_apps(self):
        self.manifest['phase']='qualification'
        with self.assertRaisesRegex(ValueError,'qualification_membership'):self.frozen()
    def test_runtime_observation_required(self):
        self.manifest['baseline']['runtimeReceipt']=self.ref
        with self.assertRaisesRegex(ValueError,'runtime_observation'):self.frozen()
    def test_empty_known_no_focus(self):
        self.labels['objects']=[];self.labels['focus']={'state':'no_focus','box':None}
        r=self.report(lambda p:p.update(detections=[],focusBox=None))
        self.assertEqual(r['overall']['correctFocus']['value'],1)
        self.assertIsNone(r['overall']['perClass']['button']['recall']['value'])
    def test_official_coco_exact(self):
        r=self.report();self.assertEqual(r['officialCOCO']['status'],'available')
        self.assertAlmostEqual(r['officialCOCO']['metrics']['AP50_95'],1)
        self.assertAlmostEqual(r['officialCOCO']['customCrossCheck']['officialMinusCustom']['AP50'],0)
    def test_official_coco_empty(self):
        r=self.report(lambda p:p.update(detections=[],focusBox=None))
        self.assertEqual(r['officialCOCO']['metrics']['AP50'],0)
    def test_changed_pixels_rejected(self):
        with self.assertRaisesRegex(ValueError,'runtime_pixels'):self.report(lambda p:p.update(pixelSHA256='0'*64))
    def test_changed_crop_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'crop_source'):
            self.report(lambda p:p.update(crops=[dict(image=self.ref,sourceSHA256='0'*64,sourceBox=[0,0,1,1])]))
    def test_historical_ap_exact(self):
        r=self.report();ap=m.custom_ap(r['rows'],self.manifest['classes'])
        self.assertEqual(ap['metrics']['AP50_95'],1)
    def test_dashboard_states_metric_limits(self):
        from generate_research_dashboard import render_html
        self.assertIn('Real-app accuracy is not independently established',render_html({'jobs':[]}))
    def test_rotated_image_rejected(self):
        image=Path(self.case['image']['path']);im=Image.new('RGB',(100,80),(12,34,56));exif=im.getexif();exif[274]=6;im.save(image,exif=exif)
        self.case['image']=pin(image);self.labels['imageSHA256']=self.case['image']['sha256']
        with self.assertRaisesRegex(ValueError,'image_geometry'):self.frozen()
    def test_unknown_prediction_taxonomy_rejected(self):
        with self.assertRaisesRegex(ValueError,'prediction_values'):
            self.report(lambda p:p['detections'][0].update({'class':'unmapped-native-class'}))
    def test_evaluator_version_drift_rejected(self):
        f=self.frozen();p=self.prediction(f)
        with patch.object(m,'evaluator_identity',return_value={}):
            with self.assertRaisesRegex(ValueError,'evaluator_changed'):m.score(f,p)
    def test_compiled_model_tree_identity(self):
        from observer_identity398 import compiled_digest
        tree=self.root/'model.mlmodelc';tree.mkdir();(tree/'weights.bin').write_bytes(b'model-test')
        descriptor=self.root/'model-reference.json';q.save(descriptor,dict(version='compiled-model-reference-v1',root=q.relative(tree),compiledSHA256=compiled_digest(tree)))
        digest,files=m.model_identity(pin(descriptor));self.assertEqual(digest,compiled_digest(tree));self.assertEqual(len(files),1)
        (tree/'weights.bin').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'compiled_model_changed'):m.model_identity(pin(descriptor))
    def test_two_queue_campaigns_reuse_adapter(self):
        f=self.frozen();p=self.prediction(f);pp=self.root/'predictions.json';q.save(pp,p)
        queue=self.root/'queue'
        for ident in ('benchmark-one','benchmark-two'):
            rp=self.root/(ident+'.json');q.save(rp,dict(id=ident,freeze=f,predictions=pin(pp)))
            spec=m.build(rp);sp=self.root/(ident+'-spec.json');q.save(sp,spec);q.submit(sp,queue)
            from research_approval import approve
            approve(queue,ident,"test","Isolated benchmark adapter software test")
        q.run(queue,job_ids=['benchmark-one','benchmark-two'],lock=self.root/'queue.lock',max_jobs=2)
        for ident in ('benchmark-one','benchmark-two'):self.assertEqual(q.state(queue/'jobs'/ident)[0],'complete')

if __name__=='__main__':unittest.main()
