"""Check image-only boundary selection and fixed comparison requirements."""
import unittest
from unittest.mock import patch
import numpy as np
import regions331 as m


class Regions331Tests(unittest.TestCase):
    def setUp(self):m.t.set_num_threads(2)

    def test_identical_and_global_change(self):
        x=m.t.zeros(1,6,128,192)
        self.assertEqual(m.windows(x),[[]])
        x[:,3:]=.5
        self.assertTrue(m.t.equal(m.boundary_energy(x),m.t.zeros(1,1,128,192)))
        self.assertEqual(m.windows(x),m.ORIGINAL_WINDOWS(x))

    def test_first_region_and_nonoverlap(self):
        x=m.t.zeros(1,6,128,192);x[:,3:,15:30,15:30]=1;x[:,3:,90:110,150:175]=.8
        original=m.ORIGINAL_WINDOWS(x)[0]
        for policy in m.POLICIES:
            result=m.windows(x,policy)[0];self.assertEqual(len(result),2)
            for x0,y0 in result:self.assertTrue(0<=x0<=160 and 0<=y0<=96)
            x0,y0=result[0];x1,y1=result[1]
            self.assertFalse(x0<x1+32 and x0+32>x1 and y0<y1+32 and y0+32>y1)
            if policy=='retain_first':self.assertEqual(result[0],original[0])

    def test_reversal_and_batch_parity(self):
        m.t.manual_seed(42);x=m.t.rand(3,6,128,192)
        reverse=m.t.cat((x[:,3:],x[:,:3]),1)
        for policy in m.POLICIES:
            self.assertEqual(m.windows(x,policy),m.windows(reverse,policy))
            self.assertEqual(m.windows(x,policy),[m.windows(v[None],policy)[0] for v in x])

    def test_invalid_inputs(self):
        with self.assertRaisesRegex(ValueError,'input_shape'):m.windows(m.t.zeros(1,3,128,192))
        with self.assertRaisesRegex(ValueError,'nonfinite'):m.windows(m.t.full((1,6,128,192),float('nan')))
        with self.assertRaisesRegex(ValueError,'unknown_policy'):m.windows(m.t.zeros(1,6,128,192),'unknown')

    def test_support_rule(self):
        def metrics(coverage,purity):return dict(coverage=dict(mean=coverage),purity=dict(mean=purity))
        values={part:dict(old=metrics(.4,.3),boundary=metrics(.5,.3),retain_first=metrics(.6,.3)) for part in ('all','content')}
        self.assertEqual(m.eligibility(values),'retain_first')
        values['content']['retain_first']['purity']['mean']=.2
        self.assertEqual(m.eligibility(values),'boundary')
        values['all']['boundary']['coverage']['mean']=.4
        self.assertIsNone(m.eligibility(values))

    def test_existing_cropper_consumes_new_windows(self):
        x=np.zeros((1,6,128,192),np.float32);x[:,3:,45:55,75:85]=1
        with patch.object(m.r,'windows',side_effect=lambda value:m.windows(value,'retain_first')):
            detail,audit=m.r.prepare(x,[None],2)
        self.assertEqual(detail.shape,(1,12,128,192))
        self.assertEqual(audit[0]['windows'],m.windows(m.t.from_numpy(x),'retain_first')[0])
        self.assertTrue(np.isfinite(detail).all())


if __name__=='__main__':unittest.main()
