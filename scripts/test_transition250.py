import unittest
import numpy as np
import transition250 as d
from transition249_result_checks import validate


class DiagnosticTests(unittest.TestCase):
    def test_interpolation_endpoints(self):
        x=np.arange(24,dtype=np.float32).reshape(1,6,2,2)/24
        np.testing.assert_array_equal(d.interpolate(x,1),x)
        y=d.interpolate(x,0);np.testing.assert_array_equal(y[:,:3],y[:,3:])
        np.testing.assert_allclose(d.interpolate(x,.5)[:,3:],(x[:,:3]+x[:,3:])/2,
                                   rtol=0,atol=np.finfo(np.float32).eps)

    def test_result_errors(self):
        r=dict(id='DTM068',manifestSHA256='pin',backend='cpu',predictions={'native':[.2,.8]},
               history=[dict(epoch=i,loss=.1) for i in range(1,121)])
        self.assertTrue(validate(r,'DTM068','pin',{'native':2}))
        with self.assertRaisesRegex(ValueError,'identity'):validate(r,'DTM069','pin',{'native':2})
        with self.assertRaisesRegex(ValueError,'invalid_predictions'):validate(r,'DTM068','pin',{'native':3})
        r['predictions']['native'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'invalid_predictions'):validate(r,'DTM068','pin',{'native':2})


if __name__=='__main__':unittest.main()
