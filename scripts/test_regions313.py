"""Check region selection, source crops, frozen weights, and saved models."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
import regions313 as r


class RegionTests(unittest.TestCase):
    def setUp(self):r.t.set_num_threads(2)

    def test_windows_edges_reverse_and_overlap(self):
        x=r.t.zeros(4,6,128,192)
        for i,(y,z) in enumerate([(0,0),(0,188),(124,0),(124,188)]):
            x[i,3:,y:y+4,z:z+4]=1;x[i,3:,55:60,90:95]=.8
        boxes=r.windows(x)
        self.assertEqual(boxes,r.windows(r.t.cat((x[:,3:],x[:,:3]),1)))
        for a,b in boxes:
            self.assertTrue(a[0]+32<=b[0] or b[0]+32<=a[0] or a[1]+32<=b[1] or b[1]+32<=a[1])
            for xx,yy in (a,b):self.assertTrue(0<=xx<=160 and 0<=yy<=96)

    def test_empty_and_single_region(self):
        x=r.t.rand(1,3,128,192);pair=r.t.cat((x,x),1)
        self.assertEqual(r.windows(pair),[[]])
        out=r.encoded_details(pair,2)
        self.assertTrue(r.t.equal(out[:,:6],pair));self.assertTrue(r.t.equal(out[:,6:],pair))
        pair=r.t.zeros(1,6,128,192);pair[:,3:,60:64,90:94]=1
        self.assertEqual(len(r.windows(pair)[0]),1)

    def test_source_and_identity(self):
        a=Image.new('RGB',(384,216),(20,40,60));b=a.copy();b.paste((255,255,255),(330,170,340,180))
        x=r.s.encoded(a,b,(192,128))[0][None];row=dict(images=[dict(path='a',sha256='a'),dict(path='b',sha256='b')])
        with patch.object(r.s,'image',side_effect=[a,b]):out,audit=r.prepare(x,[row],2)
        self.assertEqual(out.shape,(1,12,128,192));self.assertTrue(audit[0]['sourceAvailable'])
        with patch.object(r.s,'image',side_effect=[b,a]):
            with self.assertRaises(Exception):r.prepare(x,[row],2)

    def test_matched_parameters_frozen_fit_and_reload(self):
        old=r.s.c.model.extend(r.b.worker.make_model(r.t,paired_context=True)).eval()
        x=r.t.rand(2,6,128,192);y=r.t.tensor([0.,1.]);counts=[]
        expected=r.b.worker.score(old,x.numpy())
        import copy
        for count in (1,2):
            net=r.extend(copy.deepcopy(old),count);counts.append(sum(p.numel() for p in net.parameters()))
            detail=r.encoded_details(x,count)
            np.testing.assert_allclose(r.b.worker.score(net,r.t.cat((x,detail),1).numpy()),expected,atol=1e-6,rtol=0)
            frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith(('change.detail.','change.correction.'))}
            config=dict(epochs=1,lr=.0001,batch=2,seed=42,threads=2,detailOnly=True)
            r.b.trainer.fit(net,x,y,config,detail_inputs=detail)
            self.assertTrue(all(r.t.equal(v,net.state_dict()[k]) for k,v in frozen.items()))
            self.assertTrue(r.t.count_nonzero(net.change.correction.weight)>0)
            with patch.object(r.t,'load',return_value=dict(state=net.state_dict(),representation=r.VERSION,windows=count)):
                restored=r.load_candidate('unused')
            self.assertTrue(np.array_equal(r.b.worker.score(net,x.numpy()),r.b.worker.score(restored,x.numpy())))
        self.assertEqual(counts[0],counts[1])

    def test_invalid_contracts(self):
        with self.assertRaises(Exception):r.windows(r.t.zeros(1,3,128,192))
        with self.assertRaises(Exception):r.extend(None,3)
        with patch.object(r.t,'load',return_value=dict(representation='wrong')):
            with self.assertRaises(Exception):r.load_candidate('unused')


if __name__=='__main__':unittest.main()
