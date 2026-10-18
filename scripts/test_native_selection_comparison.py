"""Test matched T37 comparisons without model execution."""
import copy
import unittest
from native_selection_comparison import compare, ARMS


def report(no_focus=False, score=.9, outcome='correct'):
    return dict(threshold=.85, rows=[dict(id='frame', group='group', profile='standard', noFocus=no_focus,
        arms={a: dict(boxes=[[0, 0, 10, 10]], scores=[score], outcome=outcome) for a in ARMS})])


class ComparisonTests(unittest.TestCase):
    def test_loss(self):
        result=compare(report(), report(score=.1, outcome='miss'))
        self.assertEqual(result['slices']['standard']['known-box']['losses'], ['frame'])
        self.assertFalse(result['modelAccepted'])

    def test_no_focus(self):
        result=compare(report(True, .1, 'correct-abstention'), report(True, .9, 'false-selection'))
        self.assertEqual(result['slices']['standard']['known-box']['newWrongSelections'], ['frame'])

    def test_empty_duplicate_and_identity(self):
        base=report()
        for value in [dict(threshold=.85, rows=[]), dict(threshold=.85, rows=base['rows']*2)]:
            with self.assertRaises(ValueError): compare(value, base)
        changed=copy.deepcopy(base);changed['rows'][0]['group']='other'
        with self.assertRaisesRegex(ValueError, 'comparison_identity'): compare(base, changed)

    def test_geometry_threshold_and_score(self):
        base=report();changed=copy.deepcopy(base);changed['rows'][0]['arms']['known-box']['boxes'][0][0]=1
        with self.assertRaisesRegex(ValueError, 'comparison_geometry'): compare(base, changed)
        with self.assertRaisesRegex(ValueError, 'comparison_threshold'): compare(base, dict(base, threshold=.7))
        with self.assertRaisesRegex(ValueError, 'comparison_scores'): compare(base, report(score=float('nan')))

    def test_false_no_focus_claim(self):
        with self.assertRaisesRegex(ValueError, 'comparison_no_focus'): compare(report(True), report(True))
