"""Offline tests for rendered-body rule v2 (body_measure417) and its T46 report next to rule v1."""
import unittest

import numpy as np

import body_measure417 as b


def window(height=40, width=60):
    """A window with an inner box at [10:30, 10:50] (rows, columns)."""
    inside = np.zeros((height, width), bool)
    inside[10:30, 10:50] = True
    return np.zeros((height, width), bool), inside


class BodyRuleV2Tests(unittest.TestCase):
    def test_divider_that_never_touches_the_box_is_a_neighbour(self):
        mask, inside = window()
        mask[15:25, 20:30] = True   # text inside the box
        mask[8, 0:60] = True        # divider 2 px above the box, full window width
        self.assertEqual(b.body_v2(mask, inside, np.zeros_like(mask), scale=1), [20, 15, 30, 25])

    def test_body_that_passes_the_box_still_passes_it(self):
        # A switch drawn 2 px past the right edge of its box is 1 component that touches the interior.
        mask, inside = window()
        mask[12:28, 10:52] = True
        self.assertEqual(b.body_v2(mask, inside, np.zeros_like(mask), scale=1), [10, 12, 52, 28])

    def test_next_glyph_within_the_gap_counts(self):
        # A glyph fully outside the box but 1 px from an included glyph is part of the body (overflowing text).
        mask, inside = window()
        mask[15:25, 44:50] = True
        mask[15:25, 51:55] = True
        self.assertEqual(b.body_v2(mask, inside, np.zeros_like(mask), scale=1)[2], 55)

    def test_far_component_is_dropped(self):
        mask, inside = window()
        mask[15:25, 44:50] = True
        mask[15:25, 56:60] = True   # 6 px away, gap is 2 px at scale 1
        self.assertEqual(b.body_v2(mask, inside, np.zeros_like(mask), scale=1)[2], 50)

    def test_sibling_pixels_outside_the_box_are_ignored(self):
        mask, inside = window()
        mask[5:20, 20:30] = True    # a neighbour label that overlaps the top of the box
        mask[20:28, 20:30] = True
        box, sibling = [10, 10, 50, 30], [15, 0, 35, 20]
        ignored = b.sibling_mask(box, [box, sibling], (0, 0, 60, 40))
        self.assertEqual(b.body_v2(mask, inside, ignored, scale=1)[1], 10)

    def test_nested_boxes_are_not_siblings(self):
        box, row = [10, 10, 50, 30], [0, 0, 60, 40]
        self.assertFalse(b.sibling_mask(box, [box, row], (0, 0, 60, 40)).any())

    def test_no_component_inside_is_empty(self):
        mask, inside = window()
        mask[0:5, 0:60] = True
        self.assertIsNone(b.body_v2(mask, inside, np.zeros_like(mask), scale=1))


if __name__ == '__main__':
    unittest.main()
