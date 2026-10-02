import unittest
import numpy as np
from PIL import Image
import settings_swift_spike as s
import settings_focus_stability as st
import focus_transition_verifier as v


class SwiftProbeTests(unittest.TestCase):
    def test_measurement_and_decision_parity(self):
        rng=np.random.default_rng(25)
        a=rng.integers(0,180,(256,256,3),dtype=np.uint8)
        for delta in (0,1,30):
            ims=[Image.fromarray(a),Image.fromarray(np.clip(a.astype(int)+delta,0,255).astype('uint8'))]
            py=st.measure(*ims);p=dict(id='x',tracking={'status':'matched'},**v.compare_crops(*ims))
            expected=st.guard(st.extend(p,py,settings_context=True),py)['decision']
            result=s.measure(ims,'x',False)
            self.assertEqual(expected,result['decision'])
            for k in ('mean','p95','maximum','changedFraction'): self.assertAlmostEqual(py[k],result['metrics'][k],places=9)

    def test_invalid_bytes_and_mode(self):
        for mode,items in [('measure',[dict(id='x',beforeRGB='',afterRGB='')]),('invalid',[dict(id='x')])]:
            with self.assertRaises(ValueError):s.invoke(mode,items)

    def test_invalid_bounds_rejected_before_io(self):
        with self.assertRaises(ValueError):
            s.invoke('track',[dict(id='x',before=dict(path='/bad',sha256='x'),after=dict(path='/bad',sha256='x'),bounds=[0,0,-1,1])])

if __name__=='__main__':unittest.main()
