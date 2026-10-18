"""Test fixed proposal conversion and focus comparisons without model claims."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import detector_focus_pilot as pilot
from template_inputs398 import pin


def candidate(box, source='detector'):
    return dict(box=box,source=source,sourceIndex=0)


class PilotTests(unittest.TestCase):
    def test_merge_preserves_detector_boxes(self):
        a=candidate([10,20,30,40]); b=candidate([11,20,30,40],'mapped-ring')
        kept,removed=pilot.merge([a,a],[b,candidate([70,20,20,20],'mapped-ring')])
        self.assertEqual(len(kept),2);self.assertEqual(len(removed),2)
        self.assertEqual(kept[0],a)

    def test_complete_path_and_standard_isolation(self):
        frame=dict(id='a',sha256='a'*64,case='group',profile='standard')
        box=[10,20,30,40]
        def score(model,boxes):return ([.9 if model=='candidate' else .2]*len(boxes),['b'*64]*len(boxes))
        row=pilot.compare_frame(frame,[box],box,[],[candidate(box,'mapped-ring')],score)
        self.assertTrue(row['arms']['known-box']['gain'])
        self.assertEqual(row['arms']['detector']['models']['candidate']['outcome'],'miss')
        self.assertEqual(row['arms']['detector-plus-ring']['candidates'],[])
        hcf=pilot.compare_frame(dict(frame,profile='hcf'),[box],box,[],[candidate(box,'mapped-ring')],score)
        self.assertEqual(hcf['arms']['detector-plus-ring']['models']['candidate']['outcome'],'correct')
        self.assertFalse(pilot.summarize([row])['modelAccepted'])
        with self.assertRaisesRegex(ValueError,'pilot_frame_membership'):pilot.summarize([row,row])
        with self.assertRaisesRegex(ValueError,'pilot_frame_membership'):pilot.summarize([])

    def test_no_focus_and_bad_scores(self):
        frame=dict(id='a',sha256='a'*64,case='g',profile='hcf');box=[0,0,10,10]
        def score(model,boxes):return ([.9]*len(boxes),['a']*len(boxes))
        row=pilot.compare_frame(frame,[],None,[candidate(box)],[],score)
        self.assertEqual(row['arms']['detector']['models']['candidate']['outcome'],'false-selection')
        empty=pilot.compare_frame(frame,[],None,[],[],score)
        self.assertEqual(empty['arms']['detector']['models']['candidate']['outcome'],'correct-abstention')
        with self.assertRaisesRegex(ValueError,'pilot_score_count'):
            pilot.compare_frame(frame,[box],box,[],[],lambda m,b:([.9],[]))
        with self.assertRaisesRegex(ValueError,'native_score_invalid'):
            pilot.compare_frame(frame,[box],box,[],[],lambda m,b:([float('nan')]*len(b),['a']*len(b)))

    def test_detector_contract_failures(self):
        label=dict(sha256='a'*64,width=100,height=100)
        labels=dict(role='development',trainingEligible=False,frames=[label])
        raw=dict(status='success',inputSHA256='a'*64,width=100,height=100,
                 coordinates='boundingBoxPixels: pixels top-left',runtime=dict(detector={'id':'fixed'},result=dict(elements=[
                     dict(confidence=.9,elementType='wrong-class-is-allowed',boundingBoxPixels=dict(x=10,y=20,width=30,height=40))])))
        card=dict(version='real-model-scorecard-v1',partition='development',trainingEligible=False,
                  inputs='labels',rawPredictions=['raw'],frames=['a'*64],identity=dict(detector={'id':'fixed'}),settings=dict(confidence=.5))
        def read(ref):return labels if ref=='labels' else raw
        with patch.object(pilot,'document',side_effect=read):
            result=pilot.detector_predictions(card)
            self.assertEqual(result['a'*64]['candidates'][0]['box'],[10,20,30,40])
            for key,value,reason in [('coordinates','bottom-left','pilot_coordinates'),('inputSHA256','b'*64,'pilot_detector_pixels'),
                                     ('width',200,'pilot_dimensions'),('status','failed','pilot_detector_failed')]:
                old=raw[key];raw[key]=value
                with self.assertRaisesRegex(ValueError,reason):pilot.detector_predictions(card)
                raw[key]=old
            for value in (-1,float('nan'),2):
                raw['runtime']['result']['elements'][0]['confidence']=value
                with self.assertRaisesRegex(ValueError,'pilot_detector_score'):pilot.detector_predictions(card)
            raw['runtime']['result']['elements'][0]['confidence']=.9
            raw['runtime']['result']['elements'][0]['boundingBoxPixels']['x']=-1
            rejected=pilot.detector_predictions(card)['a'*64]
            self.assertEqual(rejected['candidates'],[])
            self.assertEqual(rejected['rejected'][0]['reason'],'detector_bounds')
            with self.assertRaisesRegex(ValueError,'pilot_role'):pilot.detector_predictions(dict(card,partition='train'))
            with self.assertRaisesRegex(ValueError,'pilot_detector_membership'):
                pilot.detector_predictions(dict(card,frames=['a'*64,'a'*64]))

    def test_changed_pinned_input(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='pilot-input-') as folder:
            path=Path(folder)/'data.json';q.save(path,dict(before=True));ref=pin(path)
            q.save(path,dict(after=True),replace=True)
            with self.assertRaisesRegex(ValueError,'input_changed'):pilot.document(ref)


if __name__=='__main__':unittest.main()
