import unittest

from PIL import Image

from harvest_focus_pairs import CROP_SIZE, EXPANSION, crop_rgb, expanded_clamp


class HarvestFocusPairsTests(unittest.TestCase):
    def test_expanded_crop_uses_sixteen_percent_on_each_side(self):
        self.assertEqual(expanded_clamp(100, 50, 200, 150, 400, 300, EXPANSION), (84, 34, 216, 166))

    def test_expanded_crop_clamps_to_frame_and_resizes_to_contract(self):
        box = expanded_clamp(0, 0, 20, 20, 30, 30, EXPANSION)
        self.assertEqual(box, (0, 0, 23, 23))
        image = Image.new("RGB", (30, 30), "white")
        self.assertEqual(crop_rgb(image, box).size, (CROP_SIZE, CROP_SIZE))


if __name__ == "__main__":
    unittest.main()
