"""Deterministic offline rectangle proposal checks; no capture/model dependencies."""
import unittest
from PIL import Image, ImageDraw
import numpy as np
from human_auto_boxes import detect, overlap


class AutoBoxesTests(unittest.TestCase):
    def panels(self):
        image=Image.new('RGB',(640,360),(20,20,20)); draw=ImageDraw.Draw(image)
        for x in (40,230,420):
            draw.rounded_rectangle((x,60,x+150,150),radius=10,fill='white')
            draw.text((x+30,95),'APP',fill='black')
        return image

    def test_panels_original_coordinates_and_order(self):
        boxes=detect(self.panels())
        self.assertEqual(len(boxes),3)
        for box,x in zip(boxes,(40,230,420)):
            self.assertLessEqual(abs(box[0][0]-x),2)
            self.assertLessEqual(abs(box[1][1]-151),2)
        large=detect(self.panels().resize((1920,1080)))
        self.assertEqual(len(large),3)
        for small,big in zip(boxes,large):
            self.assertLess(abs(big[0][0]-small[0][0]*3),6)

    def test_existing_suppression_repeat_and_limit(self):
        image=self.panels(); boxes=detect(image)
        self.assertEqual(detect(image,boxes),[])
        self.assertEqual(len(detect(image,boxes[:1])),2)
        self.assertEqual(len(detect(image,limit=1)),1)
        self.assertEqual(detect(image,limit=0),[])
        self.assertEqual(overlap(boxes[0],boxes[0]),1)
        self.assertEqual(detect(image),boxes)

    def test_blank_noise_clipped_and_tiny_abstain(self):
        self.assertEqual(detect(Image.new('RGB',(640,360),'white')),[])
        self.assertEqual(detect(Image.new('RGB',(1,1),'white')),[])
        image=Image.new('RGB',(640,360),'black'); draw=ImageDraw.Draw(image)
        draw.rectangle((0,50,150,150),fill='white')
        self.assertEqual(detect(image),[])
        noise=Image.fromarray(np.random.default_rng(42).integers(0,256,(360,640,3),dtype=np.uint8))
        self.assertEqual(detect(noise),[])

    def test_textured_panel_outline_and_source_preservation(self):
        image=Image.new('RGB',(640,360),(20,20,20))
        texture=Image.fromarray(np.random.default_rng(5).integers(90,220,(90,150,3),dtype=np.uint8))
        image.paste(texture,(50,60))
        before=image.tobytes(); boxes=detect(image)
        self.assertTrue(any(overlap(b,[[50,60],[200,150]])>.95 and
                            abs(b[1][0]-200)<4 for b in boxes))
        self.assertEqual(image.tobytes(),before)


if __name__=='__main__': unittest.main()
