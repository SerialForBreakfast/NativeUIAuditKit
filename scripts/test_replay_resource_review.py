"""Keep scientific changes separate from resource differences."""
import copy
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import replay_resource_review as review


class ReviewTests(unittest.TestCase):
    def spec(self):
        return dict(replay=dict(recordedDirectory='recorded', files=[
            dict(name='preparation.json', compare='json', tolerance=0, ignore=[])]))

    def test_memory_is_reported_and_original_is_preserved(self):
        spec = self.spec()
        original = copy.deepcopy(spec)
        with patch.object(review.q, 'load', side_effect=[dict(peakBytes=100), dict(peakBytes=140)]), \
             patch.object(review.q, 'compare_replay', return_value=dict(matched=True, files=[])) as compare:
            result = review.comparison(spec, review.q.ROOT / 'replayed')
        self.assertEqual(spec, original)
        self.assertEqual(result['resourceMeasurements']['deltaPeakBytes'], 40)
        self.assertEqual(compare.call_args.args[0]['replay']['files'][0]['ignore'][0]['path'], 'peakBytes')

    def test_scientific_mismatch_stays_failed(self):
        with patch.object(review.q, 'load', side_effect=[dict(peakBytes=100), dict(peakBytes=140)]), \
             patch.object(review.q, 'compare_replay', return_value=dict(matched=False, files=[])):
            self.assertFalse(review.comparison(self.spec(), review.q.ROOT)['scientificMatched'])

    def test_missing_memory_fails(self):
        with patch.object(review.q, 'load', side_effect=[{}, dict(peakBytes=140)]):
            with self.assertRaisesRegex(ValueError, 'review_peak_memory_missing'):
                review.comparison(self.spec(), review.q.ROOT)

    def test_nonzero_tolerance_fails(self):
        spec = self.spec()
        spec['replay']['files'][0]['tolerance'] = .1
        with self.assertRaisesRegex(ValueError, 'review_exact_required'):
            review.comparison(spec, review.q.ROOT)

    def test_real_comparison_keeps_scientific_fields_and_weights_strict(self):
        with tempfile.TemporaryDirectory(dir=review.q.ROOT / '.build') as temporary:
            root = Path(temporary)
            original, replayed = root / 'original', root / 'replayed'
            original.mkdir()
            replayed.mkdir()
            review.q.save(original / 'preparation.json', dict(peakBytes=100, acceptedFrames=12))
            review.q.save(replayed / 'preparation.json', dict(peakBytes=140, acceptedFrames=12))
            (original / 'last.pt').write_bytes(b'fixed-model')
            (replayed / 'last.pt').write_bytes(b'fixed-model')
            spec = dict(replay=dict(recordedDirectory='original', files=[
                dict(name='preparation.json', compare='json', sha256=review.q.digest(original / 'preparation.json')),
                dict(name='last.pt', compare='sha256', sha256=review.q.digest(original / 'last.pt'))]))
            with patch.object(review.q, 'ROOT', root):
                self.assertTrue(review.comparison(spec, replayed)['scientificMatched'])
                review.q.save(replayed / 'preparation.json', dict(peakBytes=140, acceptedFrames=11), replace=True)
                self.assertFalse(review.comparison(spec, replayed)['scientificMatched'])
                review.q.save(replayed / 'preparation.json', dict(peakBytes=140, acceptedFrames=12), replace=True)
                (replayed / 'last.pt').write_bytes(b'changed-model')
                self.assertFalse(review.comparison(spec, replayed)['scientificMatched'])


if __name__ == '__main__':
    unittest.main()
