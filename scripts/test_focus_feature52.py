"""Pixel-feature correspondence tests; generated fixtures are not model evidence."""
import unittest
import json
from unittest.mock import patch
import numpy as np
from PIL import Image
import focus_transition_verifier as v
import focus_motion_diagnostics as diagnostics


def pair():
    rng=np.random.default_rng(52)
    patch=np.repeat(rng.integers(0,256,(45,75),dtype=np.uint8),4,axis=0).repeat(4,axis=1)
    a=Image.new('RGB',(800,600),'black');a.paste(Image.fromarray(patch).convert('RGB'),(200,200))
    b=Image.new('RGB',a.size,'black');b.paste(Image.fromarray(255-patch).convert('RGB'),(225,120))
    return a,b,[200,200,300,180]


class FeatureTests(unittest.TestCase):
    def test_diagnostic_counts_are_json_native_and_not_labels(self):
        rows=[dict(nearStationary=9,nearNativeMotion=7,nativeCenterDisplacement=[0,-162]),
              dict(reason='insufficient_features')]
        result=diagnostics.mixed_motion_count(rows)
        self.assertIs(type(result),int);self.assertEqual(json.dumps(result),'1')

    def test_translation_polarity_and_fixed_geometry(self):
        a,b,box=pair();r=v.track(a,b,box,tracker='feature-consensus-v1')
        self.assertEqual(r['status'],'matched',r)
        self.assertLess(abs(r['dx']-25),2);self.assertLess(abs(r['dy']+80),2)
        self.assertEqual(r['afterBounds'][2:],box[2:])
        self.assertNotIn('correlation',r);self.assertNotIn('peakGap',r)
        self.assertGreaterEqual(r['featureQuality']['inliers'],6)
        self.assertEqual(r,v.track(a,b,box,tracker='feature-consensus-v1'))

    def test_duplicate_features_do_not_match(self):
        a,_,box=pair();b=Image.new('RGB',a.size,'black')
        patch=a.crop((200,200,500,380));b.paste(patch,(200,10));b.paste(patch,(200,400))
        self.assertEqual(v.track(a,b,box,tracker='feature-consensus-v1')['status'],'unavailable')

    def test_blank_identical_viewport_and_missing(self):
        a,b,box=pair()
        self.assertEqual(v.track(a,a,box,tracker='feature-consensus-v1')['status'],'identical')
        self.assertEqual(v.track(a,b.resize((500,500)),box,tracker='feature-consensus-v1')['reason'],'viewport_changed')
        self.assertEqual(v.track(a,Image.new('RGB',a.size),box,tracker='feature-consensus-v1')['status'],'unavailable')
        self.assertEqual(v.track(a,b,[700,200,300,180],tracker='feature-consensus-v1')['reason'],'body_outside')

    def test_invalid_coordinates_and_closed_policy(self):
        a,b,box=pair()
        with self.assertRaises(ValueError):v.track(a,b,[0,0,float('nan'),100],tracker='feature-consensus-v1')
        p=v.tracker_policy('feature-consensus-v1');p['ratio']=1
        self.assertEqual(v.FEATURE_POLICY['ratio'],.7)
        with self.assertRaises(ValueError):v.track(a,b,box,tracker='truth-guided')

    def test_disagreeing_layers_and_spread_fail_closed(self):
        a,b,box=pair()
        points=np.array([[i*20,j*10] for i in range(6) for j in range(2)],dtype=float)
        moved=points.copy();moved[:6,1]-=80
        with patch.object(v,'feature_matches',return_value=((points,moved,1.),None)):
            self.assertEqual(v.track(a,b,box,tracker='feature-consensus-v1')['reason'],'inconsistent_feature_motion')
        points=np.array([[i*.1,j*.1] for i in range(6) for j in range(2)])
        with patch.object(v,'feature_matches',return_value=((points,points,1.),None)):
            self.assertEqual(v.track(a,b,box,tracker='feature-consensus-v1')['reason'],'insufficient_feature_spread')

    def test_clipping_never_resizes_independent_windows(self):
        a,b,box=pair();points=np.array([[i*20,j*10] for i in range(6) for j in range(2)],dtype=float)
        with patch.object(v,'feature_matches',return_value=((points,points+[0,-195],1.),None)):
            self.assertEqual(v.track(a,b,box,tracker='feature-consensus-v1')['reason'],'clipping_footprint_changed')
            r=v.track(a,b,box,tracker='feature-consensus-v1',common=True)
            self.assertEqual(r['status'],'matched')
            self.assertEqual(r['beforeCropBounds'][2:],r['afterCropBounds'][2:])


if __name__=='__main__':unittest.main()
