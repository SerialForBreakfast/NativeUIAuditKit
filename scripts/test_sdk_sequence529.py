"""Bounded producer tests use generated packets, never native training evidence."""
import copy
import unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image
import research_queue as q
import sdk_capture527 as m
import test_sdk_capture527 as base
from test_sdk_packet502 import sample

class SequenceTests(base.CaptureTests):
    def sequence(self,uncertain=False,gap=False,wrong=False,retained=False,removal=False):
        self.config['version']='sdk-removal-restoration-request-v1' if removal else 'sdk-arrival-departure-request-v1';q.save(self.path,self.config,replace=True)
        spec=m.build(self.path);q.validate(spec)
        job=self.root/'sequence';out=job/'attempts/1/out';out.mkdir(parents=True);q.save(job/'spec.json',spec)
        session='00000000-0000-4000-8000-000000000001';self.calls=[];state={'focused':removal,'frame':0}
        def call(client,*args):
            self.calls.append(args)
            if args[:2]==('simulator','readiness'):return dict(can_run=True,ownership=[dict(state='clear')])
            if args[:2]==('simulator','remote'):
                action=args[2]
                if action=='press':state['focused']=True if retained else not state['focused']
                return dict(simulatorID=m.TARGET,operationID=session,state='closed' if action=='disconnect' else ('uncertain' if uncertain else 'delivered') if action=='press' else 'ready')
            if args[:2]==('sdk','snapshot'):
                return dict(appID=self.config['expectedAppID'],processID='wrong' if wrong else 'p',runID='r',fresh=True,sourceKind='authenticated_sdk_challenge',currentFocusKnown=True,
                    currentFocusID='button' if state['focused'] else None,controlEventGap=False,
                    control=dict(ready=True,focusSource='nativeCallback',presentationIDs=[],sampledAt=10,focusObservedAt=9))
            self.assertEqual(args[:2],('sdk','packet'))
            folder=Path(args[-1]);folder.mkdir();image=folder/'frame.png';Image.new('RGB',(1,1),(state['frame'],0,0)).save(image)
            e=sample(image);index=state['frame'];start=10000+index*1000
            e.update(sourceID=m.TARGET,captureID='frame-'+str(index),captureStartNS=start,captureEndNS=start+1,observationEndNS=start+5)
            for j,side in enumerate(('before','after')):
                host=start-10 if j==0 else start+3;high=index*2+j+1
                e[side].update(appID=self.config['expectedAppID'],processID='p',runID='r',focusID='button' if state['focused'] else None)
                if removal and index==1:e[side]['elements']=[]
                events=[dict(schemaVersion=1,processID='p',runID='r',sequence=n,monotonicNanoseconds=19000+n*100,source='nativeCallback',name='ui.focus',fields={}) for n in range(1,high+1) if not(gap and n==3)]
                if retained and index==2:e[side]['elements'][0]['observedState']['enabled']=False
                e[side]['timeline']=dict(schemaVersion=1,processID='p',runID='r',highestSequence=high,producerDroppedEvents=0,omittedEvents=0,events=events,
                    clockBracket=dict(hostRequestStartNS=host,hostResponseEndNS=host+1,producerSampleNS=host+10000))
            q.save(folder/'evidence.json',e);state['frame']+=1;return dict(state='collected')
        return out,call
    def test_full_sequence_preserves_events_and_closes_session(self):
        out,call=self.sequence()
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):m.run()
        result=q.load(out/'benchmark_summary.json')
        self.assertEqual(result['frames'],3);self.assertEqual(result['inputsDispatched'],2)
        self.assertTrue(result['episode']['eligibility']['temporalReview'])
        self.assertEqual([f['focusState'] for f in result['episode']['frames']],['no_focus','focused','no_focus'])
        self.assertEqual(q.load(out/'remote-cleanup.json')['state'],'closed')
        self.assertTrue((out/'input-0.json').is_file());self.assertTrue((out/'input-0.receipt.json').is_file())
    def test_uncertain_input_is_not_retried_and_cleanup_runs(self):
        out,call=self.sequence(uncertain=True)
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):
            with self.assertRaisesRegex(ValueError,'input_unconfirmed'):m.run()
        self.assertEqual(sum(a[:3]==('simulator','remote','press') for a in self.calls),1)
        self.assertEqual(q.load(out/'remote-cleanup.json')['state'],'closed')
        self.assertTrue((out/'frame-0/frame.png').exists())
    def test_missing_events_preserve_frames_and_report_inconclusive(self):
        out,call=self.sequence(gap=True)
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):
            m.run()
        self.assertEqual(q.load(out/'benchmark_summary.json')['hypothesisOutcome'],'inconclusive')
        self.assertFalse(q.load(out/'benchmark_summary.json')['departureQualified'])
        self.assertEqual(q.load(out/'benchmark_summary.json')['frames'],3)
        self.assertEqual(q.load(out/'remote-cleanup.json')['state'],'closed')
    def test_disabled_focus_is_captured_as_contradiction_not_timeout(self):
        out,call=self.sequence(retained=True)
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):m.run()
        r=q.load(out/'benchmark_summary.json')
        self.assertEqual(r['frames'],3)
        self.assertEqual(r['observedNativeStates'],['no_focus','focused','focused'])
        self.assertEqual(r['hypothesisOutcome'],'contradicted')
        self.assertFalse(r['departureQualified'])
        self.assertTrue(r['nativeFocusOnDisabledControl'][2])
        self.assertEqual(r['alignedImageStates'][2],'unknown')
        self.assertFalse(r['trainingAdmitted'])
        self.assertEqual(sum(a[:3]==('simulator','remote','press') for a in self.calls),2)
        self.assertEqual(q.load(out/'remote-cleanup.json')['state'],'closed')
    def test_removal_and_restoration_preserves_empty_inventory(self):
        out,call=self.sequence(removal=True)
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):m.run()
        result=q.load(out/'benchmark_summary.json')
        self.assertEqual(result['observedNativeStates'],['focused','no_focus','focused'])
        self.assertEqual(result['episode']['scenario'],'native-removal-restoration')
        self.assertEqual(result['episode']['frames'][1]['controls'],[])
        self.assertTrue(result['imageSequenceQualified'])
        self.assertEqual(q.load(out/'remote-cleanup.json')['state'],'closed')

    def test_wrong_launch_identity_stops_before_connect(self):
        out,call=self.sequence(wrong=True)
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):
            with self.assertRaisesRegex(ValueError,'sequence_identity'):m.run()
        self.assertFalse(any(a[:2]==('simulator','remote') for a in self.calls))

if __name__=='__main__':unittest.main()
