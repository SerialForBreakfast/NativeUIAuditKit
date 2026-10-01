import copy
import unittest
from PIL import Image, ImageDraw
import focus_brightness_spike as s


class BrightnessTests(unittest.TestCase):
    def test_settings_arrival_departure_and_noop(self):
        a=s.features(Image.new('RGB',(256,256),(40,40,40)))
        b=s.features(Image.new('RGB',(256,256),(240,240,240)))
        self.assertFalse(s.bright(a));self.assertTrue(s.bright(b))
        flags=dict(settled=True,matched=True,stable_context=True)
        self.assertEqual(s.direction(a,b,**flags),'arrival')
        self.assertEqual(s.direction(b,a,**flags),'departure')
        self.assertEqual(s.direction(a,a,**flags),'unknown')

    def test_invalid_context_is_unavailable(self):
        for key in ('settled','matched','stable_context'):
            flags=dict(settled=True,matched=True,stable_context=True);flags[key]=False
            self.assertEqual(s.direction(dict(luma=0),dict(luma=1),**flags),'unavailable')

    def test_white_art_is_counterexample_not_ground_truth(self):
        white=s.features(Image.new('RGB',(256,256),'white'))
        self.assertTrue(s.bright(white))  # Cannot distinguish a white unfocused poster.

    def test_chromatic_and_dimensions(self):
        self.assertFalse(s.bright(s.features(Image.new('RGB',(256,256),'yellow'))))
        with self.assertRaises(ValueError):s.features(Image.new('RGB',(128,128)))

    def test_compression_and_thin_highlight(self):
        im=Image.new('RGB',(256,256),'black');ImageDraw.Draw(im).rectangle((32,32,223,223),outline='white',width=1)
        f=s.features(im)
        self.assertFalse(s.bright(f))
        self.assertLess(abs(f['luma']-f['downsample']['16']['luma']),.01)

    def test_membership_rejections(self):
        with self.assertRaises(ValueError):s.membership([],[])
        rows=[dict(id='a',label=0,split='validation',use='representative-selection')]
        pred=[dict(id='a',label=0,probability=.2)]
        self.assertEqual(s.membership(rows,pred)['a'],pred[0])
        for altered in ([],pred*2,[dict(id='a',label=1,probability=.2)],
                        [dict(id='a',label=0,probability=float('nan'))],
                        [dict(id='a',label=0,probability=2)]):
            with self.assertRaises(ValueError):s.membership(rows,altered)
        for role in ('final-challenge','train'):
            r=copy.deepcopy(rows);r[0]['split']=role
            with self.assertRaises(ValueError):s.membership(r,pred)

    def test_oracle_scope_and_truth_independence(self):
        rows=[dict(id='a',label=0,family='home'),dict(id='b',label=1,family='settings')]
        scores={r['id']:dict(probability=.1) for r in rows}
        values={r['id']:dict(luma=.9,neutral=.9) for r in rows}
        p=s.arm_predictions(rows,scores,values,'settings-oracle-hybrid')
        self.assertEqual([r['probability'] for r in p],[.1,1.])
        for r in rows:r['label']=1-r['label']
        self.assertEqual([r['probability'] for r in s.arm_predictions(rows,scores,values,'settings-oracle-hybrid')],[.1,1.])
        with self.assertRaises(ValueError):s.arm_predictions(rows,scores,values,'unknown')

    def test_nonfinite_delta(self):
        with self.assertRaises(ValueError):
            s.direction(dict(luma=0),dict(luma=float('nan')),settled=True,matched=True,stable_context=True)

    def test_equal_bright_competitors_remain_multiple(self):
        rows=[dict(id='a',label=0),dict(id='b',label=1)]
        scores={r['id']:dict(probability=.1) for r in rows}
        values={r['id']:dict(luma=.9,neutral=.9) for r in rows}
        p=s.arm_predictions(rows,scores,values,'brightness')
        self.assertEqual(sum(r['probability']>=.85 for r in p),2)
        self.assertEqual(s.counts(rows,p),dict(fp=1,tp=1))


if __name__=='__main__':unittest.main()
