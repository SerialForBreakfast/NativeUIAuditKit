"""Check boundary diagnostics without retained training files."""
import unittest
from unittest.mock import patch
import numpy as np
import boundary329 as m


class BoundaryTests(unittest.TestCase):
    def test_band_excludes_common_body_and_clips(self):
        inner,band=m.masks((20,20),[[[0,0,8,8],[-2,-2,12,12]]],2)
        self.assertFalse((inner&band).any())
        self.assertEqual(int(inner.sum()),64)
        self.assertTrue(band[9,9]);self.assertFalse(band[19,19])

    def test_interior_and_edge_changes(self):
        inner,band=m.masks((30,30),[[[10,10,8,8],[10,10,8,8]]],3)
        a=m.measure(inner.astype(float),inner,band,np.ones((30,30),bool))
        b=m.measure(band.astype(float),inner,band,np.ones((30,30),bool))
        self.assertEqual(a['boundaryFraction'],0)
        self.assertEqual(b['boundaryFraction'],1)
        self.assertEqual(b['proposalBoundaryCoverage'],1)
        zero=m.measure(np.zeros((30,30)),inner,band,inner)
        self.assertIsNone(zero['boundaryFraction'])

    def test_missing_and_invalid_body(self):
        row={'observedIDs':['x','x']}
        self.assertEqual(m.bodies(row,[{},{}])[2],'missing_body')
        scene={'elements':[{'element_id':'x'}]}
        self.assertEqual(m.bodies(row,[scene,scene])[2],'missing_body')
        scene['elements'][0]['rendered_body_geometry']={'availability':'measured','coordinate_space':'image_top_left_pixels','visible_pixel_bounds':[0,0,-1,2]}
        with self.assertRaises(Exception):m.bodies(row,[scene,scene])

    def test_body_population_does_not_follow_focus(self):
        g={'availability':'measured','coordinate_space':'image_top_left_pixels','visible_pixel_bounds':[1,2,3,4]}
        scene={'elements':[{'element_id':v,'rendered_body_geometry':g} for v in ('x','y')]}
        same=m.bodies({'observedIDs':['x','x']},[scene,scene])[0]
        moved=m.bodies({'observedIDs':['x','y']},[scene,scene])[0]
        self.assertEqual(same,moved);self.assertEqual(len(same),2)
        missing={'elements':scene['elements'][:1]}
        self.assertEqual(m.bodies({'observedIDs':['x','x']},[scene,missing])[2],'body_population_changed')

    def test_scene_identity_and_ambiguity(self):
        row={'observedIDs':['x','x'],'images':[{'sha256':'a'}]*2,'metadata':[{}]*2}
        with patch.object(m.b,'checked',return_value='unused'),patch.object(m.b,'read',return_value={}):
            self.assertEqual(m.scenes_for(row)[1],'missing_scene')
        doc={'unfocused_sha256':'a','baseline_scene':{'focused_element_id':'y'}}
        with patch.object(m.b,'checked',return_value='unused'),patch.object(m.b,'read',return_value=doc):
            with self.assertRaises(Exception):m.scenes_for(row)
        doc={'unfocused_sha256':'a','focused_sha256':'a','baseline_scene':{'focused_element_id':'x'},'focused_scene':{'focused_element_id':'x','generation':2}}
        with patch.object(m.b,'checked',return_value='unused'),patch.object(m.b,'read',return_value=doc):
            with self.assertRaises(Exception):m.scenes_for(row)

    def test_edge_features_reversal_and_identical(self):
        t=m.t;t.manual_seed(42);x=t.rand(2,12,128,192)
        self.assertTrue(t.equal(m.edge_features(x),m.edge_features(t.from_numpy(m.r.reverse_details(x.numpy())))))
        x[:,3:6]=x[:,:3];x[:,9:12]=x[:,6:9]
        self.assertTrue(t.equal(m.edge_features(x),t.zeros(2,3)))
        x[0,0,0,0]=float('nan')
        with self.assertRaises(Exception):m.edge_features(x)

    def test_auc_ties_and_missing_support(self):
        self.assertEqual(m.auc([0,1],[0,1]),1)
        self.assertEqual(m.auc([1,0],[0,1]),0)
        self.assertEqual(m.auc([1,1],[0,1]),.5)
        self.assertIsNone(m.auc([1],[0]))


if __name__=='__main__':unittest.main()
