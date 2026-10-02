import unittest
from PIL import Image,ImageDraw
import numpy as np
import focus_transition_verifier as v


def scene(dx=0,dy=0,scale=1,shade=80):
    im=Image.new('RGB',(640,480),(25,25,25));d=ImageDraw.Draw(im)
    x,y=200+dx,200+dy;w,ht=int(160*scale),int(60*scale)
    d.rectangle((x-(w-160)//2,y-(ht-60)//2,x+(w+160)//2-1,y+(ht+60)//2-1),fill=(shade,)*3)
    d.text((x+22,y+25),'Settings unique 129',fill=(240 if shade<128 else 15,)*3)
    return im


class TransitionTests(unittest.TestCase):
    def test_translation_and_polarity(self):
        r=v.track(scene(),scene(dy=-100,shade=235),[200,200,160,60])
        self.assertEqual(r['status'],'matched',r)
        self.assertLess(abs(r['dy']+100),2)
        self.assertEqual(r['afterBounds'][2:],[160,60])

    def test_growth_does_not_resize_window(self):
        r=v.track(scene(),scene(dx=10,scale=1.15),[200,200,160,60])
        self.assertEqual(r['status'],'matched',r)
        self.assertEqual(r['afterBounds'][2:],[160,60])

    def test_low_texture_and_missing_target(self):
        self.assertEqual(v.track(Image.new('RGB',(640,480),'gray'),scene(),[200,200,160,60])['reason'],'low_texture')
        self.assertEqual(v.track(scene(),Image.new('RGB',(640,480),'gray'),[200,200,160,60])['status'],'unavailable')

    def test_identical_and_viewport(self):
        self.assertEqual(v.track(scene(),scene(),[200,200,160,60])['status'],'identical')
        self.assertEqual(v.track(scene(),Image.new('RGB',(640,400)),[200,200,160,60])['reason'],'viewport_changed')

    def test_duplicate_texture_rejected(self):
        im=scene();d=ImageDraw.Draw(im);d.rectangle((200,100,359,159),fill=(80,)*3)
        d.text((222,125),'Settings unique 129',fill=(240,)*3)
        self.assertEqual(v.track(scene(),im,[200,200,160,60])['reason'],'ambiguous_texture')

    def test_disabled_and_invalid_context_no_io(self):
        self.assertEqual(v.verify({},False)['status'],'disabled')
        with self.assertRaises(ValueError):v.verify(dict(version=1,context={}),True)
        flags=dict(sameScene=True,settled=True,fresh=False,identityVerified=True)
        self.assertEqual(v.verify(dict(version=1,context=flags,before={},after={},beforeBounds=[]),True)['reason'],'context_not_verified')

    def test_request_rejects_truth_fields_and_boolean_version(self):
        with self.assertRaises(ValueError):v.verify(dict(version=True),True)
        request=dict(version=1,before={},after={},beforeBounds=[],context={})
        with self.assertRaises(ValueError):v.verify(dict(request,afterBounds=[0,0,1,1]),True)
        with self.assertRaises(ValueError):v.verify(dict(request,focused=True),True)

    def test_illumination_gate(self):
        a=Image.new('RGB',(256,256),(70,)*3);b=Image.new('RGB',(256,256),(110,)*3)
        r=v.compare_crops(a,b)
        self.assertEqual(r['rawCombined'],'arrival');self.assertEqual(r['decision'],'unknown')

    def test_invalid_box(self):
        with self.assertRaises(ValueError):v.track(scene(),scene(),[200,200,float('nan'),60])
        self.assertEqual(v.track(scene(),scene(),[600,200,160,60])['reason'],'body_outside')

    def test_common_support_preserves_translation_and_scale(self):
        before=[600,200,160,60];after=[620,210,160,60]
        a,b=v.common_support(before,after,(800,480))
        self.assertEqual(a[2:],b[2:]);self.assertAlmostEqual(b[0]-a[0],20)
        self.assertAlmostEqual(b[1]-a[1],10)
        self.assertLessEqual(max(v.footprint(a,(800,480))),1e-7)
        self.assertLessEqual(max(v.footprint(b,(800,480))),1e-7)
        self.assertIsNone(v.common_support(before,[700,200,160,60],(800,480)))
        with self.assertRaises(ValueError):v.common_support(before,[620,200,180,60],(800,480))

    def test_common_support_reciprocal_geometry(self):
        a,b=[600,200,160,60],[620,210,160,60]
        first=v.common_support(a,b,(800,480));second=v.common_support(b,a,(800,480))
        self.assertEqual(first,list(reversed(second)))


if __name__=='__main__':unittest.main()
