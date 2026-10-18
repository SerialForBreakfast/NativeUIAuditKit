"""T52 ring pixel measurement: the gate port classifies synthetic rings, and the summary self-check works."""
import unittest
import numpy as np

from ring_pixels420 import measure, summarize


def frame(ring=200, art=None, background=20):
    pix = np.full((540, 960), background, np.uint8)
    body = [400, 200, 160, 90]
    x, y, w, h = body
    if ring is not None:
        pix[y - 6:y + h + 6, x - 6:x + w + 6] = ring        # Ring 2 px wide, 4 px outside the body.
        pix[y - 4:y + h + 4, x - 4:x + w + 4] = background  # Dark moat.
    if art is not None:
        pix[y:y + h, x:x + w] = art                          # Artwork inside the body.
    return pix, body


class MeasureTests(unittest.TestCase):
    def test_clear_ring_passes(self):
        pix, body = frame()
        value = measure(pix, body)
        self.assertEqual(value['class'], 'pass')
        self.assertEqual(set(value['sides']), {'top', 'bottom', 'left', 'right'})

    def test_dim_ring_is_below_brightness(self):
        pix, body = frame(ring=140)
        self.assertEqual(measure(pix, body)['class'], 'below-brightness')

    def test_no_ring(self):
        pix, body = frame(ring=None)
        self.assertEqual(measure(pix, body)['class'], 'no-bright-ring')

    def test_ring_merged_with_bright_artwork_fails_fill(self):
        pix, body = frame(art=230)
        x, y, w, h = body
        pix[y - 4:y + h + 4, x - 4:x + w + 4] = 230  # No moat: ring and artwork form 1 filled component.
        self.assertTrue(measure(pix, body)['class'].startswith('geometry:fill-high'))

    def test_clipped_ring_fails_geometry(self):
        pix = np.full((540, 960), 20, np.uint8)
        pix[0:60, 0:200] = 200
        pix[2:58, 2:198] = 20
        self.assertEqual(measure(pix, [4, 4, 192, 52])['class'], 'geometry:clipped')


class SummaryTests(unittest.TestCase):
    def row(self, cls, proposal):
        return dict(id=cls + str(proposal), hasProposal=proposal, hcf=dict(**{'class': cls}), standard=dict(**{'class': 'no-bright-ring'}))

    def test_self_check_and_dominant_class(self):
        rows = [self.row('pass', True), self.row('pass', True), self.row('support', False),
                self.row('support', False), self.row('no-bright-ring', False)]
        value = summarize(rows)
        self.assertTrue(value['selfCheck']['trusted'])
        self.assertEqual(value['decisions'][0]['dominantClass'], 'support')
        self.assertEqual(value['missedClasses'], {'support': 2, 'no-bright-ring': 1})
        self.assertFalse(value['modelAccepted'])

    def test_failed_self_check_is_reported(self):
        value = summarize([self.row('support', True), self.row('support', False)])
        self.assertFalse(value['selfCheck']['trusted'])


if __name__ == '__main__':
    unittest.main()
