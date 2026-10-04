import unittest
import numpy as np
from PIL import Image
import focus_direct_transition as d
from evaluate_direct_transition import parity
from localization_diagnostics import overflow,diagnose,summarize


class LocalizationTests(unittest.TestCase):
    def test_encoded_prediction_matches_image_path(self):
        t=d.torch_runtime();t.manual_seed(42)
        a=Image.new('RGB',(160,90),'red');b=Image.new('RGB',(160,90),'blue');encoded=d.encode(a,b)
        for config in (d.EXPOSURE_CONFIG,d.TEMPORAL_CONFIG):
            net=d.model(config).eval()
            parity(d.infer(net,a,b),d.infer_encoded(net,encoded,a.size))
        for bad in (encoded.astype(np.float64),encoded[:3],np.full_like(encoded,np.nan),np.full_like(encoded,2)):
            with self.assertRaisesRegex(ValueError,'encoded_input'):d.infer_encoded(net,bad,a.size)
        with self.assertRaisesRegex(ValueError,'image_size'):d.infer_encoded(net,encoded,(True,90))

    def test_unclipped_geometry_is_not_a_detection(self):
        box=d.raw_image_box([.01,.5,.5,.1],[1920,1080])
        self.assertGreater(overflow(box,[1920,1080])[0],0)
        self.assertIsNone(d.image_box([.01,.5,.5,.1],[1920,1080]))
        self.assertEqual(overflow([0,0,10,10],[10,10]),[0,0,0,0])

    def test_diagnostic_does_not_change_predictions(self):
        t=d.torch_runtime();t.manual_seed(42);net=d.model(d.TEMPORAL_CONFIG).eval()
        a=Image.new('RGB',(160,90),'red');encoded=d.encode(a,a)
        before=d.infer_encoded(net,encoded,a.size)
        row=dict(size=[160,90],boxes=[[20,20,40,10]]*2)
        details=diagnose(net,encoded,row,before)
        self.assertEqual(len(details),2);self.assertEqual(summarize([dict(endpoints=details)])['endpoints'],2)
        parity(before,d.infer_encoded(net,encoded,a.size))
        self.assertEqual(set(details[0]['scoringOnlyOracleIoU']),{'center','extent','cell'})


if __name__=='__main__':unittest.main()
