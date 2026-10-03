"""Generated software evidence only; does not admit retained images or train a candidate."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import focus_transition_learning as t


def prediction(delta=0):
    return dict(tracking=dict(status='matched',dx=0,dy=0,correlation=.99,peakGap=.4),
        measurement=dict(lumaDelta=delta,ratios=[1+delta,1+delta],edgeStrength=.1,centerDrift=0),
        stability=dict(metrics=dict(mean=abs(delta),p95=abs(delta),changedFraction=abs(delta),maximum=abs(delta),
            directionalCoverage=dict(arrival=[max(delta,0)]*4,departure=[max(-delta,0)]*4))))


class TransitionTests(unittest.TestCase):
    def setUp(self):
        parent=t.h.ROOT/'.build/debug-output/transition49-tests';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.root=Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def write(self,name,doc,sealed=False):
        p=self.root/name;t.h.write(p,doc,sealed=sealed);return p

    def source(self,name,offset=0,complete=True):
        from PIL import Image
        refs=[]
        for i in range(2):
            image=self.root/f'{name}-{i}.png'
            Image.new('RGB',(4,4),(offset+i,0,0)).save(image)
            refs.append(t.h.ref(image))
        controls=[]
        for i,label in enumerate(t.LABELS):
            p=prediction((0,.4,-.4)[i])
            controls.append(dict(id=str(i),expected=label,prediction=p,trackingAgreesWithSemanticTarget=True,
                arms=dict(combined=dict(scorable=True,expected=label,decision=label,correct=True))))
        doc=dict(version='settings-stability-v1',**t.h.FLAGS,actions=[dict(actionID=name,
            endpoints={k:dict(sha256=refs[i]['sha256']) for i,k in enumerate(('before','after'))},
            completeEndpoints=complete,guardedControls=controls)])
        p=self.write(name+'.json',doc,True)
        return dict(report=t.h.ref(p),group=name,endpointImages=refs)

    def protocol(self,admit=False,shared=False):
        sources=[self.source('a',10),self.source('b',20)]
        if shared:sources[1]['group']='a'
        corpus=t.collect(sources)
        admission=None
        if admit:
            assignments={r['id']:('train' if r['source']==sources[0]['report'] else 'development') for r in corpus['records']}
            ap=self.write('admission.json',dict(version='focus-transition-admission-v1',approved=True,
                reviewer='software-test',decisionReference='generated-test-not-real-admission',
                corpusSHA256=corpus['corpusSHA256'],assignments=assignments))
            admission=t.h.ref(ap)
        doc=dict(version=t.VERSION,sources=sources,corpusSHA256=corpus['corpusSHA256'],admission=admission,configuration=t.CONFIG)
        doc['protocolSHA256']=t.digest(doc)
        p=self.write('protocol.json',doc)
        approval=self.write('approval.json',dict(version='focus-transition-approval-v1',approved=True,
            protocolSHA256=doc['protocolSHA256'],arm=t.ARM,runName='transition49-unit',decisionReference='software-fixture-only'))
        return p,approval,corpus

    def test_feature_order_and_truth_exclusion(self):
        arrival=t.features(prediction(.4));departure=t.features(prediction(-.4))
        self.assertEqual(len(arrival),len(t.FEATURES));self.assertEqual(arrival[0],-departure[0])
        self.assertNotEqual(arrival,departure)
        self.assertIsNone(t.features(dict(tracking=dict(status='unavailable'))))
        with self.assertRaisesRegex(ValueError,'truth_in_features'):t.features(dict(prediction(),expected='arrival'))
        p=prediction();p['measurement']['lumaDelta']=float('nan')
        with self.assertRaisesRegex(ValueError,'nonfinite'):t.features(p)

    def test_missing_absolute_metrics_are_not_stability(self):
        p=prediction(.3);del p['stability']
        self.assertEqual(t.features(p)[-2],0)
        p['illuminationWarning']=True;self.assertIsNone(t.features(p))

    def test_scene_identity_and_completeness(self):
        rows=[dict(id='a',expected='departure',decision='departure',identityVerified=True),
              dict(id='b',expected='arrival',decision='arrival',identityVerified=True)]
        self.assertTrue(t.action_score(rows,True)['correct'])
        self.assertIsNone(t.action_score(rows,False)['correct'])
        rows[0]['decision']='arrival';rows[1]['decision']='departure'
        self.assertFalse(t.action_score(rows,True)['correct'])
        rows[0]['identityVerified']=False
        self.assertEqual(t.action_score(rows,True)['prediction']['decision'],'unavailable')

    def test_audit_and_dispatch_do_not_admit(self):
        p,approval,corpus=self.protocol()
        self.assertEqual(corpus['counts']['controls'],6)
        self.assertFalse(corpus['trainingEligible'])
        from focus_learning_experiment import load_protocol
        report,_=load_protocol(p,t.ARM,'transition49-unit',approval)
        self.assertFalse(report['launchEligible']);self.assertIn('missing_exact_data_role_admission',report['blockers'])

    def test_positive_preflight_and_no_model_imports(self):
        p,approval,_=self.protocol(True)
        before=set(sys.modules)
        report,rows=t.load_protocol(p,t.ARM,'transition49-unit',approval)
        self.assertTrue(report['launchEligible']);self.assertEqual(len(rows),6)
        self.assertFalse({'torch','cv2'} & (set(sys.modules)-before))

    def test_pixel_equivalence_despite_different_png_encoding(self):
        from PIL import Image, PngImagePlugin
        source=self.source('pixels',30)
        ref=source['endpointImages'][0]
        path=self.root/'reencoded.png'
        metadata=PngImagePlugin.PngInfo();metadata.add_text('note','different bytes')
        with Image.open(t.h.checked(t.h.ROOT,ref)) as image:image.save(path,pnginfo=metadata)
        other=t.h.ref(path)
        self.assertNotEqual(ref['sha256'],other['sha256'])
        self.assertEqual(t.decoded_hash(ref),t.decoded_hash(other))

    def test_missing_pixels_blocks_admitted_members(self):
        p,approval,_=self.protocol(True)
        doc=t.h.read(p)
        for source in doc['sources']:source.pop('endpointImages')
        corpus=t.collect(doc['sources'])
        admission=t.h.read(t.h.checked(t.h.ROOT,doc['admission']))
        admission['corpusSHA256']=corpus['corpusSHA256']
        doc['admission']=t.h.ref(self.write('updated-admission.json',admission))
        doc['corpusSHA256']=corpus['corpusSHA256']
        doc['protocolSHA256']=t.digest({k:v for k,v in doc.items() if k!='protocolSHA256'})
        new=self.write('updated-protocol.json',doc)
        report,_=t.load_protocol(new,t.ARM,'transition49-unit')
        self.assertIn('missing_decoded_pixel_evidence',report['blockers'])
        self.assertFalse(report['launchEligible'])

    def test_group_leakage_rejected(self):
        p,approval,_=self.protocol(True,True)
        with self.assertRaisesRegex(ValueError,'leakage'):t.load_protocol(p,t.ARM,'transition49-unit',approval)

    def test_changed_source_and_duplicate_actions_rejected(self):
        source=self.source('source',50)
        with self.assertRaisesRegex(ValueError,'duplicate_action'):t.collect([source,source])
        (self.root/'source.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'changed_hash'):t.collect([source])

    def test_bad_score_and_duplicate_controls_rejected(self):
        source=self.source('one',60);p=self.root/'one.json';d=t.h.read(p)
        d['actions'][0]['guardedControls'][0]['arms']['combined']['correct']=False
        d.pop('seal');p.unlink();t.h.write(p,d,sealed=True);source['report']=t.h.ref(p)
        with self.assertRaisesRegex(ValueError,'changed_score'):t.collect([source])

    def test_fit_is_order_sensitive_and_deterministic(self):
        x=[t.features(prediction(delta)) for delta in (0,.4,-.4)*8];y=list(range(3))*8
        a=t.fit_head(x,y);b=t.fit_head(x,y)
        self.assertEqual(a,b);self.assertEqual(len(a['history']),30)
        for i,delta in enumerate((0,.4,-.4)):
            p=t.probabilities(a,t.features(prediction(delta)))
            self.assertEqual(max(range(3),key=lambda j:p[j]),i)
            self.assertAlmostEqual(sum(p),1)
        self.assertEqual(a['mean'][0],0)

    def test_candidate_execution_receipt_and_output_isolation(self):
        p,approval,_=self.protocol(True)
        out=self.root/'transition49-unit'
        with patch.object(t,'fresh_run',return_value=out):
            report,_=t.load_protocol(p,t.ARM,'transition49-unit',approval)
            self.assertEqual(t.run(report,'SOFTWARE-FIXTURE-NOT-EXPERIMENT'),0)
        result=t.h.read(out/'result.json')
        self.assertEqual(len(result['results']),3)
        self.assertIn('fullScene',result['summaries']['candidate']['actions'])
        self.assertFalse(result['releaseEligible'])
        self.assertEqual(len(t.h.read(out/'last.json')['history']),30)

    def test_endpoint_leakage_across_distinct_groups(self):
        p,approval,_=self.protocol(True)
        doc=t.h.read(p)
        # Change the first source group only: split protection must also cover pixels.
        original=t.collect
        def shared_pixels(sources):
            corpus=original(sources)
            for record in corpus['records']:record['decodedPixelHashes']=['same-pixels']*2
            return corpus
        with patch.object(t,'collect',side_effect=shared_pixels):
            with self.assertRaisesRegex(ValueError,'leakage'):
                t.load_protocol(p,t.ARM,'transition49-unit',approval)

    def test_missing_class_and_invalid_model_rejected(self):
        with self.assertRaisesRegex(ValueError,'training_tensors'):t.fit_head([t.features(prediction())],[0])
        model=t.fit_head([t.features(prediction(d)) for d in (0,.4,-.4)],list(range(3)))
        model['scale'][0]=0
        with self.assertRaisesRegex(ValueError,'invalid_head'):t.probabilities(model,t.features(prediction()))

    def test_actual_cli_refuses_training_and_collisions(self):
        p,approval,_=self.protocol()
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        command=[sys.executable,'scripts/train_focus_ring_detector.py','--experiment-protocol',str(p),
            '--experiment-arm',t.ARM,'--name','transition49-unit','--experiment-approval',str(approval),'--execute']
        result=subprocess.run(command,cwd=t.h.ROOT,env=env,text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertFalse(json.loads(result.stdout)['launchEligible'])
        sources=self.write('sources.json',t.h.read(p)['sources'])
        command=[sys.executable,'scripts/focus_transition_learning.py','--sources',str(sources),'--output',str(self.root/'audit')]
        result=subprocess.run(command,cwd=t.h.ROOT,env=env,text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        again=subprocess.run(command,cwd=t.h.ROOT,env=env,text=True,capture_output=True,timeout=30)
        self.assertNotEqual(again.returncode,0)

    def test_real_prediction_adapter_separates_truth_and_preserves_order(self):
        # Exercise the production adapter with a controlled pixel-service boundary.
        import focus_recorded_transition_eval as evaluator
        import settings_focus_stability as stability
        model=t.fit_head([t.features(prediction(d)) for d in (0,.4,-.4)],list(range(3)))
        request=dict(version='focus-transition-request-v1',before={'path':'before'},after={'path':'after'},
            controls=[dict(id='a',bounds=[1,2,3,4])],context={k:True for k in t.scene.CONTEXT})
        p=dict(prediction(.4),id='a')
        with patch.object(evaluator,'predict',return_value=([p],{'runtime':'unit'})) as predict, \
             patch.object(stability,'crop_metrics',return_value=({'a':p['stability']['metrics']},{'runtime':'unit'})):
            result=t.predict_pair(request,model)
            self.assertFalse(result['controlIssued'])
            predict.assert_called_once_with(request['before'],request['after'],request['controls'])
        request['afterTruth']='focused'
        with self.assertRaisesRegex(ValueError,'request_fields'):t.predict_pair(request,model)


if __name__=='__main__': unittest.main()
