"""Test the native detector adapter with fixed software predictions."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import research_queue as q
import detector_native_inputs as inputs
import detector_native_inference as adapter
import detector_case_match411 as matching
from template_inputs398 import pin


class InferenceTests(unittest.TestCase):
    def test_adapter_matches_existing_matcher(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='native-detector-test-') as folder:
            root=Path(folder);out=root/'job/attempts/1/out';out.mkdir(parents=True)
            image=root/'image.png';Image.new('RGB',(100,80),'white').save(image)
            model=root/'model';model.write_bytes(b'software test only')
            frame=dict(id='frame',group='group',screen='button',image=pin(image),sha256=q.digest(image),width=100,height=80,
                controls=[dict(id='button',**{'class':'primaryButton'},bounds=[10,20,30,40],state='focused')])
            labels=dict(version=inputs.VERSION,platform='tvOS',role='development',trainingEligible=False,
                labelReview='unknown',frames=[frame])
            path=root/'labels.json';q.save(path,labels)
            cfg=dict(inputs=dict(labels=pin(path),model=pin(model)),parameters=dict(engine='pytorch',confidence=.5,imageSize=640,slice='class'))
            q.save(out.parents[2]/'spec.json',dict(template=cfg))
            def predict(weights,frames,confidence,size,raw):
                identity=dict(engine='software-test',weightsSHA256=q.digest(weights))
                q.save(raw/'000.json',dict(status='success',inputSHA256=frame['sha256'],width=100,height=80,
                    coordinates='boundingBoxPixels: pixels top-left',runtime=dict(detector=identity,result=dict(elements=[
                        dict(elementType='primaryButton',confidence=.9,boundingBoxPixels=dict(x=10,y=20,width=30,height=40))]))))
                return identity
            with patch.object(adapter,'OUT',out),patch.object(adapter.inference,'pytorch',side_effect=predict):
                adapter.run()
            report=q.load(out/'benchmark_summary.json')
            self.assertEqual(report['totals']['candidate']['detected'],1)
            self.assertEqual(report['gains'],[])
            self.assertEqual(report['lostPriorSuccesses'],[])
            self.assertFalse(report['modelAccepted'])
            images,predictions,meta=matching.load_bundle(q.load(out/'bundle.json'))
            rows,extra=matching.evaluate(images,predictions,('class',None,{},'class-aware'),.5)
            expected=matching.summarize(rows,extra,('class',None,{},'class-aware'),meta)
            self.assertEqual(report['totals'],expected['totals'])
            for change,reason in [(dict(role='train'),'detector_role'),(dict(platform='macOS'),'detector_platform'),
                                  (dict(frames=[frame,frame]),'detector_membership')]:
                with self.assertRaisesRegex(ValueError,reason):adapter.validate(dict(labels,**change))
            broken=copy.deepcopy(labels);broken['frames'][0]['image']['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'detector_identity'):adapter.validate(broken)
            receipt=q.load(out/'artifact-receipt.json')
            self.assertIn('raw/000.json',{r['path'] for r in receipt['outputs']})


if __name__=='__main__':unittest.main()
