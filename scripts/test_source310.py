"""Check aligned detail, source identity, and the optional trainer input."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
import source310 as s


class SourceTests(unittest.TestCase):
    def setUp(self):s.torch.set_num_threads(2)

    def test_letterbox_and_reverse(self):
        x=s.torch.zeros(1,6,128,192);x[:,3:,50:54,180:184]=1
        detail=s.enlarged(x)
        self.assertEqual(tuple(detail.shape),tuple(x.shape))
        self.assertTrue((detail[:,:,:,:32]==0).all())
        self.assertTrue((detail[:,:,:,160:]==0).all())
        self.assertTrue(s.torch.equal(s.enlarged(s.torch.cat((x[:,3:],x[:,:3]),1)),
                                     s.torch.cat((detail[:,3:],detail[:,:3]),1)))

    def test_same_frame_fallback(self):
        x=s.torch.rand(2,3,128,192);pair=s.torch.cat((x,x),1)
        self.assertTrue(s.torch.equal(s.enlarged(pair),pair))

    def test_source_window_keeps_top_padding(self):
        image=Image.new('RGB',(384,216),(255,255,255))
        value=s.crop_pair([image,image],[0,0,32,32],preserve_padding=True)
        self.assertTrue((value[:,:40]==0).all())
        self.assertTrue((value[:,44:100,40:150]==1).all())
        self.assertTrue((value[:,:,:32]==0).all())
        self.assertTrue(np.array_equal(value[:3],value[3:]))

    def test_source_parity_and_shape(self):
        a=Image.new('RGB',(384,216),(20,40,60));b=a.copy()
        b.paste((250,100,30),(100,60,108,68))
        x=s.encoded(a,b,(192,128))[0][None]
        rows=[dict(images=[dict(path='a',sha256='a'),dict(path='b',sha256='b')])]
        with patch.object(s,'image',side_effect=[a,b]):
            low,high,records=s.prepare_views(x,rows)
        self.assertEqual(low.shape,high.shape)
        self.assertFalse(np.array_equal(low,high))
        self.assertTrue(records[0]['sourceAvailable'])
        with patch.object(s,'image',side_effect=[b,a]):
            with self.assertRaises(Exception):s.prepare_views(x,rows)

    def test_unknown_sizes_are_not_small(self):
        rows=[dict(sourceAvailable=False,weight=1),dict(sourceAvailable=True,weight=2,
              endpoints=[dict(status='missing_body')]),dict(sourceAvailable=True,weight=3,
              endpoints=[dict(status='measured',minimumEncodedSize=3)]*2)]
        result=s.size_summary(rows)
        self.assertEqual(result['scheduleEntries'],dict(encoded_only=1,missing_body_measurement=1,below4=1))

    def test_report_window_coverage(self):
        from report_source310 import coverage
        row=dict(window=[0,0,32,32],endpoints=[dict(status='measured',sourceSize=[192,128],visibleBody=[8,8,8,8])])
        self.assertEqual(coverage(row),[dict(fraction=1.,centerInside=True)])
        row['window']=[32,32,64,64]
        self.assertEqual(coverage(row),[dict(fraction=0.,centerInside=False)])

    def test_initial_parity_and_detail_training(self):
        s.torch.manual_seed(42)
        old=s.c.model.extend(s.base.worker.make_model(s.torch,paired_context=True)).eval()
        x=s.torch.rand(2,6,128,192);y=s.torch.tensor([0.,1.])
        detail=s.enlarged(x)
        expected=s.base.worker.score(old,x.numpy())
        net=s.extend(old)
        actual=s.base.worker.score(net,s.torch.cat((x,detail),1).numpy())
        np.testing.assert_allclose(actual,expected,atol=1e-6,rtol=0)
        config=dict(epochs=1,lr=.0001,batch=2,seed=42,threads=2)
        s.base.trainer.fit(net,x,y,config,detail_inputs=detail)
        self.assertTrue(s.torch.count_nonzero(net.change.correction.weight)>0)
        with self.assertRaises(Exception):
            s.base.trainer.fit(net,x,y,config,detail_inputs=detail[:1])
        with self.assertRaises(Exception):
            s.base.trainer.fit(net,x,y,config,detail_inputs=detail,alternate_inputs=x)


if __name__=='__main__':unittest.main()
