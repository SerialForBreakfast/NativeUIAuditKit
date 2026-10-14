import copy
import unittest
from fallback392 import outcome, validate_reply


def element(focused=False, x=0):
    return dict(id='a', elementType='listRow', confidence=.9,
                boundingBox=dict(x=0, y=0, width=1, height=1),
                boundingBoxPixels=dict(x=x, y=0, width=10, height=10),
                state=dict(isFocused=focused))


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.frame = dict(complete=True, controls=[dict(state='focused', bounds=[0, 0, 10, 10])])

    def test_correct_and_missing(self):
        self.assertEqual(outcome(self.frame, [element(True)]), 'correct')
        self.assertEqual(outcome(self.frame, []), 'focused_control_not_localized')

    def test_abstention_and_wrong_selection(self):
        self.assertEqual(outcome(self.frame, [element()]), 'no_focus_selected')
        self.assertEqual(outcome(self.frame, [element(), element(True, 50)]), 'wrong_focus_selected')

    def test_partial_labels_are_not_complete_claims(self):
        self.frame['complete'] = False
        self.assertTrue(outcome(self.frame, [element(True)]).startswith('ineligible'))

    def test_duplicate_selection(self):
        self.assertEqual(outcome(self.frame, [element(True), element(True)]), 'multiple_focus_selected')

    def test_reply_preserves_proposals(self):
        request = dict(sha256='a'*64, observations=[element()])
        reply = dict(version=1, sha256='a'*64, policy='legacy-visual-heuristic-v1', milliseconds=1, observations=[element(True)])
        validate_reply(request, reply)
        for key, value in [('sha256', 'b'*64), ('version', 2), ('observations', [])]:
            changed = copy.deepcopy(reply)
            changed[key] = value
            with self.assertRaises(ValueError):
                validate_reply(request, changed)
        reply['observations'][0]['confidence'] = .8
        with self.assertRaises(ValueError):
            validate_reply(request, reply)


if __name__ == '__main__':
    unittest.main()
