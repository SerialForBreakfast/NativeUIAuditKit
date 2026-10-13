"""Check accounting before native Vision execution."""
import unittest
import vision353 as v
import vision_text353 as text


class VisionTests(unittest.TestCase):
    def setUp(self):
        self.pairs = [dict(case='a', condition='movement', before='a', after='b', changed=True),
                      dict(case='b', condition='content', before='c', after='d', changed=False)]
        self.scores = [dict(id='a-movement', before='a', after='b', distance=.01),
                       dict(id='b-content', before='c', after='d', distance=.2)]

    def test_counts_do_not_select_a_threshold(self):
        r = v.pair_report(self.pairs, self.scores)
        p = next(p for p in r['operatingPoints'] if p['threshold'] == .05)
        self.assertEqual((p['missedChange'],p['falseChange']), (1,1))
        self.assertIsNone(r['selectedThreshold'])

    def test_missing_scores(self):
        with self.assertRaisesRegex(ValueError, 'pair_membership'):
            v.pair_report(self.pairs, self.scores[:1])

    def test_duplicate_scores(self):
        with self.assertRaisesRegex(ValueError, 'pair_membership'):
            v.pair_report(self.pairs, self.scores[:1]*2)

    def test_nonfinite(self):
        self.scores[0]['distance'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'distance_invalid'):
            v.pair_report(self.pairs, self.scores)

    def test_wrong_frame_order(self):
        self.scores[0]['before'] = 'b'
        with self.assertRaisesRegex(ValueError, 'pair_order'):
            v.pair_report(self.pairs, self.scores)

    def test_rectangle_error_is_not_zero_accuracy(self):
        with self.assertRaisesRegex(ValueError, 'vision_request_failed'):
            v.rectangle_report({'a':{}}, [dict(id='a',errors=['failed'])])

    def test_empty_proposals_are_measured_missing_coverage(self):
        frames={'a':dict(sha256='hash', after=dict(scene=dict(elements=[dict(element_id='x',is_focused=True,
            rendered_body_geometry=dict(visible_pixel_bounds=[10,20,30,40]))])))}
        result=v.rectangle_report(frames,[dict(id='a',sha256='hash',errors=[],rectangles=[])])
        self.assertEqual((result['observedBodies'],result['coveredAt50']), (1,0))

    def test_empty_ocr_is_not_accuracy(self):
        rows=[dict(id=k,errors=[],text=[]) for k in ('a','b','c','d')]
        result=text.stability(self.pairs,rows)
        self.assertIsNone(result['textAccuracy'])
        self.assertTrue(all(r['bothEmpty'] for r in result['rows']))

    def test_ocr_errors_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'ocr_request_failed'):
            text.stability(self.pairs,[dict(id='a',errors=['failed'])])

    def test_ocr_missing_endpoint(self):
        with self.assertRaisesRegex(ValueError,'missing_endpoint'):
            text.stability(self.pairs,[])
