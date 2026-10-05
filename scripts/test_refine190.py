import copy
import unittest
from unittest.mock import patch
import refine190 as r


def detection(box=(0, 0, 10, 10), cid=18, score=.8):
    return dict(classID=cid, score=score, xyxyPixels=list(box))


def artifact(detections):
    return dict(results=[dict(imageID='one', imageSHA256='pixels', labelSHA256='labels',
                             width=100, height=100, status='ok', detections=detections)])


class Tests(unittest.TestCase):
    def test_geometry_only_and_no_mutation(self):
        a = artifact([detection(), detection(cid=2)])
        b = artifact([detection((0, 0, 10, 5), score=.4)])
        original = copy.deepcopy(a)
        result = r.derive(a, b, 18)
        self.assertEqual(a, original)
        self.assertEqual(result['results'][0]['detections'], [detection((0, 0, 10, 5)), detection(cid=2)])
        r.validate_derived(result, a, b, 18)

    def test_ambiguity_both_directions(self):
        for a, b in [(artifact([detection(), detection()]), artifact([detection()])),
                     (artifact([detection()]), artifact([detection(), detection()]))]:
            result = r.derive(a, b, 18)
            self.assertEqual(result['results'], a['results'])
            self.assertTrue(all(x['reason'] == 'ambiguous' for x in result['audit']))

    def test_boundaries_and_no_donor(self):
        for score, height, reason in [(.25, 2.5, 'matched'), (.24999, 2.5, 'no_match'),
                                      (.25, 2.499, 'no_match')]:
            result = r.derive(artifact([detection(score=.001)]),
                              artifact([detection((0, 0, 10, height), score=score)]), 18)
            self.assertEqual(result['audit'][0]['reason'], reason)
        self.assertEqual(r.derive(artifact([detection()]), artifact([]), 18)['audit'][0]['reason'], 'no_match')

    def test_membership_and_identity(self):
        a = artifact([detection()])
        for key in ('imageSHA256', 'labelSHA256', 'width', 'height', 'status', 'imageID'):
            b = copy.deepcopy(a)
            b['results'][0][key] = 'changed'
            with self.assertRaises(Exception): r.derive(a, b, 18)
        for rows in ([], a['results'] * 2):
            with self.assertRaises(Exception): r.derive(a, dict(results=rows), 18)

    def test_tamper_and_version(self):
        a = artifact([detection()]); b = artifact([detection((0, 0, 10, 5))])
        original = r.derive(a, b, 18)
        for key, value in [('formatVersion', 'v999'), ('rule', {}), ('audit', []), ('productionEligible', True)]:
            bad = copy.deepcopy(original); bad[key] = value
            with self.assertRaisesRegex(Exception, 'invalid_derivation'): r.validate_derived(bad, a, b, 18)
        bad = copy.deepcopy(original); bad['results'][0]['detections'][0]['score'] = .9
        with self.assertRaisesRegex(Exception, 'invalid_derivation'): r.validate_derived(bad, a, b, 18)

    def test_empty_success_is_not_failed_inference(self):
        empty = artifact([]); empty['results'][0]['status'] = 'empty'
        populated = artifact([detection()])
        self.assertEqual(r.derive(empty, populated, 18)['results'], empty['results'])
        self.assertEqual(r.derive(populated, empty, 18)['results'], populated['results'])
        bad = copy.deepcopy(empty); bad['results'][0]['status'] = 'failed'
        with self.assertRaisesRegex(Exception, 'unsuccessful_input'): r.derive(populated, bad, 18)

    def test_collision_before_inputs(self):
        with patch.object(r, 'OUT', r.h.ROOT), patch.object(r.c, 'inputs') as inputs:
            with self.assertRaisesRegex(Exception, 'output_collision'): r.run()
            inputs.assert_not_called()


if __name__ == '__main__': unittest.main()
