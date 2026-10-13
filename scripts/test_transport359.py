import unittest
from PIL import Image
from transport359 import transform


class TransformTests(unittest.TestCase):
    def test_original_preserved(self):
        image=Image.new('RGB',(20,10),(12,40,80));raw=image.tobytes()
        self.assertEqual(transform(image).tobytes(),raw)
        self.assertEqual(transform(image,True).size,(10,5))
        self.assertEqual(image.tobytes(),raw)

    def test_odd_dimensions(self):
        self.assertEqual(transform(Image.new('RGB',(21,11)),True).size,(10,5))
