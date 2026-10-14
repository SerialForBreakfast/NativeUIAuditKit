"""Check matched comparisons without running training or capture."""
import copy
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import standard390 as s


def document(probability):
    return dict(configuration=dict(models={'gamma': {'path': 'model.pt', 'sha256': 'a' * 64}}),
        sets={'native': dict(rows=[dict(id='one', changed=1, group='g1', role='development',
            sourceDomain='native', condition='movement')], originalProbabilities=[.99],
            probabilities={'gamma': [probability]})})


class ComparisonTests(unittest.TestCase):
    def test_candidate_only_loss(self):
        result = s.compare(document(.99), document(.1))
        self.assertEqual(result['slices'][0]['candidateOnlyLosses'], 1)
        self.assertLess(result['cases'][0]['margins']['notification'], 0)
        self.assertFalse(result['modelAccepted'])

    def test_shared_loss(self):
        result = s.compare(document(.1), document(.1))
        self.assertEqual(result['slices'][0]['sharedLosses'], 1)

    def test_abstention_is_not_success(self):
        result = s.compare(document(.99), document(.5))
        self.assertEqual(result['slices'][0]['counts']['notification']['abstentions'], 1)
        self.assertTrue(result['cases'][0]['candidateLoss'])

    def test_missing_prediction(self):
        bad = document(.99)
        bad['sets']['native']['probabilities']['gamma'] = []
        with self.assertRaisesRegex(ValueError, 'prediction_count'):
            s.compare(document(.99), bad)

    def test_changed_membership(self):
        bad = document(.99)
        bad['sets']['native']['rows'][0]['changed'] = 0
        with self.assertRaisesRegex(ValueError, 'case_membership_changed'):
            s.compare(document(.99), bad)

    def test_duplicate_membership(self):
        bad = document(.99)
        part = bad['sets']['native']
        part['rows'] *= 2
        part['originalProbabilities'] *= 2
        part['probabilities']['gamma'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate_case'):
            s.compare(bad, copy.deepcopy(bad))

    def test_final_audit_refused(self):
        bad = document(.99)
        bad['sets']['native']['rows'][0]['role'] = 'final-audit'
        with self.assertRaisesRegex(ValueError, 'final_audit_refused'):
            s.compare(bad, copy.deepcopy(bad))

    def test_invalid_score(self):
        with self.assertRaisesRegex(ValueError, 'invalid_probability'):
            s.compare(document(.99), document(float('nan')))

    def test_training_role_preserved(self):
        doc = document(.99)
        doc['sets']['native']['rows'][0]['role'] = 'train'
        self.assertEqual(s.compare(doc, doc)['slices'][0]['role'], 'train')

    def test_staged_worker_and_changed_hash(self):
        with tempfile.TemporaryDirectory(dir=s.q.ROOT / 'reports/work', prefix='standard390-test-') as folder:
            root = Path(folder)
            out = root / 'out'
            out.mkdir()
            refs = []
            for name, probability in [('control', .99), ('candidate', .1)]:
                s.q.save(root / (name + '.json'), document(probability))
                refs.append(dict(job=name, outputs=[dict(path=name + '.json', sha256=s.q.digest(root / (name + '.json')))]))
            s.q.save(out / 'dependencies.json', refs)
            s.q.save(out / 'config.json', dict(pairs=[['control', 'candidate']], decision='Review the retained loss.'))
            with patch.object(s.q, 'ROOT', root), patch.object(s, 'OUT', out):
                s.run()
                self.assertTrue(s.q.load(out / 'review.json')['comparisons'][0]['cases'][0]['candidateLoss'])
                self.assertEqual(s.q.load(out / 'sources.json'), [r['outputs'][0] for r in refs])
                s.q.save(root / 'candidate.json', document(.99), replace=True)
                with self.assertRaisesRegex(ValueError, 'dependency_changed'):
                    s.read_dependencies()

    def test_detector_gaps_preserve_limits(self):
        report = dict(partition='development', trainingEligible=False, frames=[dict(image='one',
            focusOutcome='focused_control_not_localized', controls=[dict(id='a', role='button', localized=False, predictedRole=None)])])
        inputs = dict(frames=[dict(sha256='one', controls=[dict(id='a', bounds=[1, 2, 3, 4])])])
        result = s.detector_gaps(report, inputs)
        self.assertEqual(result['byRole']['button']['missed'], 1)
        self.assertIsNone(result['falsePositiveRate'])
        self.assertEqual(result['cases'][0]['bounds'], [1, 2, 3, 4])
        inputs['frames'][0]['controls'][0]['id'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'detector_control_membership'):
            s.detector_gaps(report, inputs)


if __name__ == '__main__':
    unittest.main()
