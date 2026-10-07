import unittest
import numpy as np
from scipy.optimize import least_squares
from measure_native_focus253 import warp,metrics,highlight,coordinates,formula_members,compare_formulas,OUT
from unittest.mock import patch


class GeometryTests(unittest.TestCase):
    def test_identity_and_repeat(self):
        x=np.random.default_rng(4).random((24,32,3));p=[1,1,0,0,1,0]
        np.testing.assert_array_equal(warp(x,p,[16,12]),x)
        self.assertEqual(metrics(x,x,np.ones((24,32),bool))['differingPixelFraction'],0)

    def test_translation_direction(self):
        x=np.zeros((24,32,3));x[10,10]=1
        y=warp(x,[1,1,2,3,1,0],[16,12])
        np.testing.assert_array_equal(y[13,12],[1,1,1])

    def test_known_scale_recovery(self):
        x=np.random.default_rng(8).random((32,40,3));truth=[1.15,1.12,0,0,1,0]
        target=warp(x,truth,[20,16])
        fit=least_squares(lambda p:(warp(x,[p[0],p[1],0,0,1,0],[20,16])-target).flatten(),
                          [1.14,1.11],bounds=([1,1],[1.3,1.3]),max_nfev=40)
        np.testing.assert_allclose(fit.x,truth[:2],atol=1e-5)

    def test_highlight_limits_and_repeat(self):
        image=np.random.default_rng(5).random((18,24,3));x,y=coordinates(image.shape[:2],[12,9])
        np.testing.assert_array_equal(highlight(image,x,y,[1,0,0,0,0,.5,.5]),image)
        p=[1,0,.4,-.2,-.3,.5,.8]
        result=highlight(image,x,y,p)
        self.assertTrue(np.all(result>=image));self.assertTrue(np.all(result<=1))
        np.testing.assert_array_equal(result,highlight(image,x,y,p))
        with self.assertRaisesRegex(ValueError,'invalid_highlight'):
            highlight(image,x,y,[1,0,.2,0,0,0,1])

    def test_known_highlight_recovery(self):
        image=np.random.default_rng(9).random((32,40,3));x,y=coordinates(image.shape[:2],[20,16])
        truth=[.95,.02,.3,-.3,-.5,.7,.6];target=highlight(image,x,y,truth)
        fit=least_squares(lambda p:(highlight(image,x,y,p)-target).ravel(),[1,0,.25,-.2,-.4,.8,.7],max_nfev=70)
        np.testing.assert_allclose(fit.x,truth,atol=1e-5)

    def test_membership_rejects_role_change_and_duplicates(self):
        rows=[dict(group='233:recipe-'+g,id=g+'-'+str(i),changed=True,conditions=['original_capture'],role='train')
              for g in ('00','03','04','05') for i in range(4)]
        self.assertEqual(len(formula_members(rows)),16)
        rows[0]['role']='reserved'
        with self.assertRaisesRegex(ValueError,'data_role'):formula_members(rows)
        rows[0]['role']='train';rows[0]['id']=rows[1]['id']
        with self.assertRaisesRegex(ValueError,'duplicate_pair'):formula_members(rows)

    def test_output_collision_precedes_input_reads(self):
        with patch('pathlib.Path.exists',return_value=True):
            with self.assertRaisesRegex(ValueError,'output_collision'):compare_formulas()


if __name__=='__main__':unittest.main()
