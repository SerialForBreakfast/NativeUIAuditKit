import unittest
import model_priority_preflight as p


class PreflightTests(unittest.TestCase):
    def test_diagnostic_roles_preserved(self):
        from unittest.mock import patch
        f=dict(image={'path':'fake'},screen='settings',complete=False,controls=[
            dict(id='1',bounds=[0,0,100,20],state='focused',**{'class':'listRow'})])
        with patch.object(p.s,'load_frames',return_value=[f]),patch.object(p.h,'image',return_value=(200,100)):
            d=p.full_screen()
        self.assertFalse(d['trainingReady']);self.assertFalse(d['trainingEligible'])
        self.assertFalse(d['frames'][0]['negativeLabelSafe'])
        self.assertEqual(d['frames'][0]['proposedUse'],'diagnostic_replay_only')

    def test_top_left_geometry(self):
        c,b=p.yolo_box('2 .5 .25 .4 .1',100,200)
        self.assertEqual(c,2);self.assertEqual(b,[30,40,40,20])

    def test_letterbox_scale_not_stretch(self):
        v=p.resolution([100,200,300,60],(1920,1080))
        self.assertEqual((v['width'],v['height']),(100,20))
        self.assertAlmostEqual(v['centerY'],230/1080)

    def test_invalid_label(self):
        for value in ('1 .5 .5 0 .2','1.5 .5 .5 .2 .2','41 .5 .5 .2 .2','1 nan .5 .2 .2'):
            with self.assertRaises(ValueError):p.yolo_box(value,100,100)


if __name__=='__main__':unittest.main()
