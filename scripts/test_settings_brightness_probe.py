import unittest
from PIL import Image
from settings_brightness_probe import proposals,decide


class BrightnessTests(unittest.TestCase):
    def pair(self,a,b):return proposals(dict(tracking=dict(status='matched')),[a,b])['decisions']
    def test_identical(self):
        a=Image.new('RGB',(256,256),(80,80,80));self.assertEqual(self.pair(a,a)['guardedMean'],'unchanged')
    def test_noise(self):
        r=self.pair(Image.new('RGB',(256,256),(80,80,80)),Image.new('RGB',(256,256),(81,81,81)))
        self.assertEqual(r['sign'],'arrival');self.assertEqual(r['guardedMean'],'unchanged')
    def test_highlight(self):
        r=self.pair(Image.new('RGB',(256,256),'black'),Image.new('RGB',(256,256),'white'))
        self.assertEqual(r['guardedMean'],'arrival')
    def test_content_patch(self):
        a=Image.new('RGB',(256,256),'black');b=a.copy();b.paste('white',(64,64,192,128))
        self.assertEqual(self.pair(a,b)['guardedMean'],'unknown')
    def test_missing_tracking(self):
        self.assertEqual(decide(dict(tracking=dict(status='unavailable')),None,None,True),'unavailable')
    def test_illumination(self):
        self.assertEqual(decide(dict(tracking=dict(status='matched'),illuminationWarning=True),.5,None,True),'unknown')
    def test_invalid(self):
        with self.assertRaises(Exception):decide(dict(tracking=dict(status='matched')),float('nan'),None,False)


if __name__=='__main__':unittest.main()
