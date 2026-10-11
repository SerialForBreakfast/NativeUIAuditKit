"""Check contrast normalization without retained experiment files."""
import unittest
import io
from unittest.mock import patch
import torch
import contrast328 as c


class ContrastTests(unittest.TestCase):
    def setUp(self):torch.manual_seed(42);torch.set_num_threads(2)

    def pair(self):
        x=torch.zeros(2,6,128,192)
        x[:,:,:,32:160]=torch.rand(2,6,128,128)*.8+.1
        return x

    def test_affine_invariance(self):
        x=self.pair();y=x.clone();y[:,3:,:,32:160]=.5+.5*(y[:,3:,:,32:160]-.5)
        torch.testing.assert_close(c.normalize(x),c.normalize(y),atol=1e-6,rtol=0)

    def test_identical_and_constant(self):
        x=self.pair();x[:,3:]=x[:,:3]
        result=c.normalize(x)
        self.assertTrue(torch.equal(result[:,:3],result[:,3:]))
        self.assertTrue(torch.isfinite(c.normalize(torch.zeros_like(x))).all())
        self.assertEqual(torch.count_nonzero(result[:,:,:,:32]),0)

    def test_growth_is_retained(self):
        x=torch.zeros(1,6,128,192)
        x[:,:3,50:70,80:100]=1;x[:,3:,48:72,78:102]=1
        y=c.normalize(x)
        self.assertGreater(float((y[:,3:]-y[:,:3]).abs().sum()),0)

    def test_reversal(self):
        x=self.pair();reverse=lambda v:torch.cat((v[:,3:],v[:,:3]),1)
        self.assertTrue(torch.equal(c.normalize(reverse(x)),reverse(c.normalize(x))))

    def test_full_frame_fallback_keeps_edges(self):
        x=torch.rand(1,6,128,192)
        mean=x.mean((2,3),keepdim=True)
        scale=x.var((2,3),keepdim=True,unbiased=False).sqrt().clamp_min(.05)
        expected=(.5+.2*(x-mean)/scale).clamp(0,1)
        torch.testing.assert_close(c.normalize(x),expected,atol=1e-6,rtol=0)
        self.assertGreater(float(c.normalize(x)[:,:,:,:32].sum()),0)

    def test_invalid(self):
        for x in (torch.zeros(1,3,128,192),torch.full((1,6,128,192),float('nan'))):
            with self.assertRaises(ValueError):c.normalize(x)

    def test_gradients_and_frozen_weights(self):
        net=c.r.extend(c.r.s.c.model.extend(c.b.worker.make_model(torch,paired_context=True)),2)
        net.change.__class__=c.ContrastChange
        x=self.pair();d=torch.cat((self.pair(),self.pair()),1);y=torch.tensor([0.,1.])
        before={k:v.clone() for k,v in net.state_dict().items()}
        c.b.trainer.fit(net,x,y,dict(epochs=2,lr=.001,batch=2,seed=42,threads=2,detailOnly=True),detail_inputs=d)
        changes=[k for k,v in net.state_dict().items() if not torch.equal(v,before[k])]
        self.assertTrue(any(k.startswith('change.detail.0.') for k in changes))
        self.assertTrue(all(k.startswith(('change.detail.','change.correction.')) for k in changes))

    def test_checkpoint_reload_and_version(self):
        net=c.r.extend(c.r.s.c.model.extend(c.b.worker.make_model(torch,paired_context=True)),2).eval()
        net.change.__class__=c.ContrastChange
        data=io.BytesIO()
        torch.save(dict(state=net.state_dict(),representation=c.VERSION,windows=2),data);data.seek(0)
        restored=c.load_candidate(data)
        x=torch.cat((self.pair(),self.pair(),self.pair()),1)
        with torch.inference_mode():
            torch.testing.assert_close(net.change(x),restored.change(x),rtol=0,atol=0)
        data=io.BytesIO();torch.save(dict(representation='unknown',windows=2),data);data.seek(0)
        with self.assertRaises(ValueError):c.load_candidate(data)

    def test_report_roles_stay_separate(self):
        import numpy as np
        from report_contrast328 import grouped
        rows=[dict(role='train',group='a'),dict(role='development',group='b'),dict(role='development',group='b')]
        report=grouped(rows,np.array([0,1,0]),{'model':np.array([.1,.9,.5])})
        self.assertEqual(report['development']['groups'],1)
        self.assertEqual(report['development']['models']['model']['abstentions'],1)
        self.assertEqual(report['train']['models']['model']['correct'],1)

    def test_boundary_audit_separates_growth_from_content(self):
        import numpy as np
        from PIL import Image
        import report_contrast328 as report
        first=np.zeros((96,96,3),np.uint8);first[40:56,40:56]=128
        grown=np.zeros_like(first);grown[38:58,38:58]=128
        content=np.zeros_like(first);content[40:56,40:56]=255
        rows=[]
        for condition,box in [('movement',[38,38,20,20]),('artwork-only',[40,40,16,16])]:
            rows.append(dict(id=condition,group='test',role='train',sizePixels=3,widthPixels=1,contrast=.25,
                condition=condition,changed=int(condition=='movement'),images=['a','b'],
                endpoints=[dict(bodyBounds=[[40,40,16,16]]),dict(bodyBounds=[box])]))
        corpus=dict(rows=dict(independent=rows))
        diagnostic=dict(rows=[dict(cell=[3,1,.25,v['condition']]) for v in rows])
        with patch.object(report.b,'read',side_effect=lambda p:corpus if p=='corpus' else diagnostic), \
             patch.object(report.b,'checked',side_effect=lambda p:p), \
             patch.object(report.Image,'open',side_effect=[Image.fromarray(a) for a in (first,grown,first,content)]):
            result=report.boundary_audit(dict(corpus='corpus'))
        self.assertAlmostEqual(result['rows'][0]['boundaryFraction'],1)
        self.assertEqual(result['rows'][0]['commonBodyMean'],0)
        self.assertEqual(result['rows'][1]['boundaryFraction'],0)
        self.assertGreater(result['rows'][1]['commonBodyMean'],0)


if __name__=='__main__':unittest.main()
