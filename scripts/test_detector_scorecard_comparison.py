"""Check comparison boundaries without model inference."""
import copy
import unittest
from unittest.mock import patch
import detector_scorecard_comparison as adapter


class ComparisonTests(unittest.TestCase):
    def test_changed_inputs_and_controls(self):
        labels = dict(role='development', trainingEligible=False)
        card = dict(inputs=dict(path='labels', sha256='a'), partition='development', trainingEligible=False,
            settings=dict(confidence=.25, imageSize=640, engine='pytorch'),
            identity=dict(detector=dict(weightsSHA256='x', nmsIoU=.45)))
        refs = dict(labels=dict(path='labels', sha256='a'), baseline='old', candidate='new')
        for field, value, error in [('inputs', {}, 'comparison_labels'),
                                     ('partition', 'training', 'comparison_role')]:
            changed = copy.deepcopy(card); changed[field] = value
            with patch.object(adapter, 'document', side_effect=[labels, card, changed]):
                with self.assertRaisesRegex(ValueError, error): adapter.compare(refs, .25)
        changed = copy.deepcopy(card); changed['settings'].update(confidence=.1, imageSize=960)
        with patch.object(adapter, 'document', side_effect=[labels, card, changed]):
            with self.assertRaisesRegex(ValueError, 'comparison_multiple_changes'): adapter.compare(refs, .1)


if __name__ == '__main__': unittest.main()
