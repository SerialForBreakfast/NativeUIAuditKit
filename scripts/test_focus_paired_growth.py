import unittest
import numpy as np
from PIL import Image,ImageDraw
import focus_paired_growth as g


def rectangle(size=194,shade=240,offset=(0,0)):
    im=Image.new('RGB',(256,256),(40,40,40));x=(256-size)//2+offset[0];y=(256-size)//2+offset[1]
    ImageDraw.Draw(im).rectangle((x,y,x+size-1,y+size-1),fill=(shade,shade,shade))
    return im


def predict(a,b,**kw):
    args=dict(settled=True,matched=True,stable_context=True,fresh=True);args.update(kw)
    return g.predict(a,b,**args)


class PairedGrowthTests(unittest.TestCase):
    def test_growth_shrink_and_identical(self):
        a,b=rectangle(),rectangle(222)
        self.assertEqual(predict(a,b)['growth'],'arrival')
        # Before-anchor normalization puts either initial body at194px.
        self.assertEqual(predict(a,rectangle(170))['growth'],'departure')
        self.assertEqual(predict(a,a)['combined'],'unchanged')

    def test_common_window_not_normalized_both(self):
        a=rectangle();self.assertEqual(predict(a,rectangle(222))['growth'],'arrival')
        self.assertEqual(predict(a,a)['growth'],'unchanged')

    def test_low_contrast_and_translation_abstain(self):
        self.assertEqual(predict(rectangle(shade=41),rectangle(222,shade=41))['growth'],'unknown')
        self.assertEqual(predict(rectangle(),rectangle(offset=(15,15)))['growth'],'unknown')

    def test_content_replacement_is_not_geometry_growth(self):
        self.assertEqual(predict(rectangle(shade=80),rectangle(shade=240))['growth'],'unknown')
        # Known limitation: brightness alone mistakes content/illumination change for focus.
        self.assertEqual(predict(rectangle(shade=80),rectangle(shade=240))['brightness'],'arrival')

    def test_external_safety_flags_and_missing_context(self):
        a=rectangle()
        for flag in ('settled','matched','stable_context','fresh'):
            self.assertEqual(predict(a,rectangle(222),**{flag:False})['combined'],'unavailable')
        self.assertEqual(predict(a,a,clipped=True)['growth'],'unavailable')
        with self.assertRaises(TypeError):g.predict(a,a)

    def test_anisotropic_change_rejected(self):
        a=rectangle();b=a.copy();ImageDraw.Draw(b).rectangle((16,31,239,224),fill='white')
        self.assertEqual(predict(a,b)['growth'],'unknown')

    def test_geometry_matching_is_label_blind_and_ambiguous_rejected(self):
        a=[dict(id='a',control='row',bounds=[20,20,100,60],label=1)]
        b=[dict(id='b',control='row',bounds=[18,18,104,64],label=0)]
        self.assertEqual(g.match(a,b),[('a','b')])
        b[0]['label']=1;self.assertEqual(g.match(a,b),[('a','b')])
        self.assertEqual(g.match(a,b+[dict(b[0],id='duplicate')]),[])
        self.assertEqual(g.match(a,[dict(b[0],control='tab')]),[])
        with self.assertRaises(ValueError):g.match(a,[dict(b[0],bounds=[0,0,float('nan'),2])])

    def test_baseline_thresholds_truth_and_dimensions(self):
        self.assertEqual(g.score_direction(.1,.9),'arrival')
        self.assertEqual(g.score_direction(.9,.1),'departure')
        self.assertEqual(g.score_direction(.9,.9),'unchanged')
        self.assertEqual(g.score_direction(.4,.9),'unknown')
        with self.assertRaises(ValueError):g.score_direction(float('nan'),.1)
        with self.assertRaises(ValueError):g.truth(True,0)
        with self.assertRaises(ValueError):predict(Image.new('RGB',(2,2)),rectangle())

    def test_frame_selection_does_not_guess(self):
        a=dict(after='a',truth='arrival',arms=dict(growth='arrival'))
        b=dict(after='b',truth='unchanged',arms=dict(growth='unknown'))
        self.assertEqual(g.frame_decision([a,b],'growth'),'correct')
        b['arms']['growth']='arrival'
        self.assertEqual(g.frame_decision([a,b],'growth'),'ambiguous')
        a['arms']['growth']='unknown'
        self.assertEqual(g.frame_decision([a,b],'growth'),'wrong')
        b['arms']['growth']='unknown'
        self.assertEqual(g.frame_decision([a,b],'growth'),'abstained')
        a['truth']='unchanged'
        self.assertEqual(g.frame_decision([a,b],'growth'),'safe_no_arrival')

    def test_frame_eligibility_preserved(self):
        group=['real','settings','frame1','frame2']
        row=dict(lane='real-development-contrast',kind='forward',group=group,
                 after='a',truth='arrival',arms=dict(growth='arrival'))
        inventory=dict(framePairs=[dict(group=group,before=1,after=1,matched=1)])
        baseline=[dict(id='frame1',outcome='unique_correct'),dict(id='frame2',outcome='unavailable')]
        self.assertFalse(g.frame_analysis([row],inventory,baseline)[0]['eligible'])
        baseline[1]['outcome']='no_focus'
        self.assertTrue(g.frame_analysis([row],inventory,baseline)[0]['eligible'])
        inventory['framePairs'][0]['before']=2
        self.assertFalse(g.frame_analysis([row],inventory,baseline)[0]['eligible'])


if __name__=='__main__':unittest.main()
