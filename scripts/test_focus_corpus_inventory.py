"""Offline corpus accounting; no models, prior reports or device dependency."""
import copy
import unittest
from unittest.mock import Mock, patch

import focus_corpus_inventory as c


def sample(sid='a', label=1, use='train-candidate'):
    return dict(id=sid, label=label, use=use,
                split='train' if use == 'train-candidate' else 'validation', control='collectionItem',
                sourceID='fixture', pairID='pair', relatedGroup='layout',
                frame=dict(path='frame-'+sid, sha256='frame-'+sid),
                crop=dict(path='crop-'+sid, sha256='crop-'+sid))


def check(ref, size):
    return ref['sha256']


class CorpusTests(unittest.TestCase):
    def test_complete_accounting_and_no_mutation(self):
        rows = [sample(), sample('b', 0)]
        before = copy.deepcopy(rows)
        result = c.audit_rows(rows, set(), check)
        self.assertEqual(result['dispositions'], {'accepted': 2})
        self.assertEqual(rows, before)
        coverage = c.coverage(result['records'])
        art = next(r for r in coverage if r['role'] == 'training' and r['stratum'] == 'artwork')
        self.assertEqual((art['focused'], art['unfocused']), (1, 1))
        self.assertEqual(next(r for r in coverage if r['stratum'] == 'keyboard')['status'], 'absent')

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate_membership'):
            c.audit_rows([sample(), sample()], set(), check)

    def test_missing_corrupt_and_hash_failures_are_accounted(self):
        for failure in ('missing_pixels', 'corrupt_image', 'changed_hash'):
            result = c.audit_rows([sample()], set(), Mock(side_effect=ValueError(failure)))
            self.assertEqual(result['dispositions'], {'blocked': 1})
            self.assertEqual(result['records'][0]['reasons'], [failure])

    def test_pixel_tamper(self):
        row = sample(); row['pixelSHA256'] = 'different'
        self.assertIn('changed_pixels', c.audit_rows([row], set(), check)['records'][0]['reasons'])

    def test_protected_and_role_change(self):
        row = sample(use='final-challenge')
        self.assertEqual(c.audit_rows([row], set(), check)['dispositions'], {'blocked': 1})
        self.assertIn('protected_overlap', c.audit_rows([sample()], {'frame-a'}, check)['records'][0]['reasons'])
        row = sample(); row['split'] = 'validation'
        self.assertIn('changed_role_split', c.audit_rows([row], set(), check)['records'][0]['reasons'])

    def test_duplicate_pixels_do_not_inflate_diversity(self):
        a, b = sample(), sample('b'); b['crop'] = a['crop']
        result = c.audit_rows([a, b], set(), check)
        self.assertEqual(result['duplicateCropGroups'], [['a', 'b']])
        self.assertEqual(next(r for r in c.coverage(result['records']) if r['stratum'] == 'artwork')['distinctCrops'], 1)
        b['label'] = 0
        self.assertEqual(c.audit_rows([a, b], set(), check)['dispositions'], {'blocked': 2})

    def test_train_eval_pixel_leakage(self):
        a, b = sample(), sample('b', use='representative-selection'); b['crop'] = a['crop']
        self.assertEqual(c.audit_rows([a, b], set(), check)['dispositions'], {'blocked': 2})
        b['crop'] = dict(path='crop-b', sha256='crop-b'); b['frame'] = a['frame']
        self.assertEqual(c.audit_rows([a, b], set(), check)['dispositions'], {'blocked': 2})

    def test_session_relationship_does_not_forge_independence(self):
        a, b = sample(), sample('b', use='representative-selection')
        result = c.audit_rows([a, b], set(), check)
        self.assertEqual(result['dispositions'], {'accepted': 2})
        self.assertEqual(result['crossRoleRelationships'][0]['roles'], ['development', 'training'])

    def test_invalid_label_and_unmapped_role(self):
        row = sample(); row['label'] = True
        self.assertEqual(c.audit_rows([row], set(), check)['dispositions'], {'blocked': 1})
        row = sample(); row['control'] = '75'
        self.assertEqual(c.audit_rows([row], set(), check)['records'][0]['stratum'], 'other')

    def test_deterministic_output(self):
        rows = [sample(), sample('b', 0)]
        self.assertEqual(c.audit_rows(rows, set(), check), c.audit_rows(rows, set(), check))

    def test_runtime_refresh_cannot_change_data(self):
        original = dict(inputs={}, samples=[sample()], runtime={'a': 1}, protocolSHA256='old')
        new = dict(original, runtime={'a': 2}, protocolSHA256='new')
        with patch('focus_review_continuation.assemble', return_value=new):
            self.assertEqual(c.refresh_runtime(original), new)
        new = dict(new, samples=[])
        with patch('focus_review_continuation.assemble', return_value=new):
            with self.assertRaisesRegex(ValueError, 'reassembly_changed_data_or_policy'):
                c.refresh_runtime(original)

    def test_role_applicability_not_admission(self):
        report = dict(policy='retained_geometry_coverage_v1', unique_sidecars=8, recapture_matrix=[
            dict(recipe_hash='a', sidecars=4, focus_treatment=['native_button'], sidecars_with_missing_role=4),
            dict(recipe_hash='b', sidecars=4, focus_treatment=['native_image'], sidecars_with_missing_role=4)])
        result = c.artwork_decisions(report)
        self.assertEqual(result[0]['decision'], 'artwork-not-applicable-use-control-wrapper')
        self.assertFalse(any(r['newTrainingAdmission'] or r['automaticRecapture'] for r in result))
        report['unique_sidecars'] = 9
        with self.assertRaisesRegex(ValueError, 'geometry_count_mismatch'):
            c.artwork_decisions(report)


if __name__ == '__main__':
    unittest.main()
