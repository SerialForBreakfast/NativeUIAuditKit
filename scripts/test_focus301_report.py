"""Check cached diagnostics without model execution."""
import copy
import unittest
import report_spatial297 as report


def row(identifier='a', truth=0, score=0.9, area=0):
    return dict(id=identifier, set='native.npy', role='train', group='g', changed=truth,
                conditions=['test'], regions={'proposal': {'area': area}},
                models={'model': {'original': score}})


class AuditTests(unittest.TestCase):
    def test_changed_only_preserves_negative_answers(self):
        result = report.audit_proposals([row(score=.1),row('b',truth=1)],'changed-only')['summaries'][0]
        self.assertEqual(result['lostCorrect'],1)
        self.assertEqual(result['diagnostic']['emittedUnchanged'],1)
        self.assertEqual(result['diagnostic']['changeAbstentions'],1)

    def test_changed_only_does_not_invent_correctness(self):
        result = report.audit_proposals([row()], 'changed-only')['summaries'][0]
        self.assertEqual(result['caughtWrong'],1)
        self.assertEqual(result['diagnostic']['correct'],0)
        with self.assertRaisesRegex(ValueError,'unknown_proposal_rule'):
            report.audit_proposals([], 'guess')

    def test_fixed_thresholds(self):
        self.assertEqual(report.proposal_decision(.15,0,'changed-only'),0)
        self.assertEqual(report.proposal_decision(.85,0,'changed-only'),-1)
        self.assertEqual(report.proposal_decision(.85,1,'changed-only'),1)

    def test_empty_support(self):
        result = report.counts([], [])
        self.assertIsNone(result['coverage'])
        self.assertIsNone(result['falseChangeRate'])

    def test_conditional_denominators(self):
        result = report.counts([1, 1, 0, 0], [0, -1, 0, 1])
        self.assertEqual(result['missedChangeRate'], 0.5)
        self.assertEqual(result['falseChangeRate'], 0.5)
        self.assertEqual(result['errorAmongUnchanged'], 0.5)
        self.assertEqual(result['coverage'], 0.75)
        self.assertEqual(result['changeAbstentions'], 1)

    def test_empty_proposal_abstains(self):
        result = report.audit_proposals([row()])['summaries'][0]
        self.assertEqual(result['caughtWrong'], 1)
        self.assertEqual(result['diagnostic']['abstentions'], 1)
        self.assertEqual(result['diagnostic']['correct'], 0)

    def test_lost_correct_is_visible(self):
        result = report.audit_proposals([row(truth=1)])['summaries'][0]
        self.assertEqual(result['lostCorrect'], 1)
        self.assertEqual(result['diagnostic']['changeAbstentions'], 1)

    def test_nonempty_preserves_decisions(self):
        result = report.audit_proposals([row(area=1)])['summaries'][0]
        self.assertEqual(result['original'], result['diagnostic'])

    def test_duplicates_fail(self):
        with self.assertRaisesRegex(ValueError, 'duplicate_case'):
            report.audit_proposals([row(), row()])

    def test_connected_roles_fail(self):
        other = row('b'); other['role'] = 'test'
        with self.assertRaisesRegex(ValueError, 'cross_role_group'):
            report.audit_proposals([row(), other])

    def test_reversed_pairs_are_not_independent(self):
        result = report.audit_proposals([row(), row('reverse')])
        self.assertEqual(result['summaries'][0]['relatedGroups'], 1)
        self.assertIsNone(result['independentBounds'])

    def test_invalid_values(self):
        for value in (float('nan'), float('inf'), -1, 2):
            with self.assertRaisesRegex(ValueError, 'invalid_score'):
                report.audit_proposals([row(score=value)])
        with self.assertRaisesRegex(ValueError, 'invalid_label'):
            report.audit_proposals([row(truth=None)])
        with self.assertRaisesRegex(ValueError, 'invalid_area'):
            report.audit_proposals([row(area=-1)])

    def test_coverage_preserves_unique_counts(self):
        item = dict(variant='original', condition='focus', imageSHA256='x', group='g', cell=[0, 0])
        data = dict(version='coverage290-v1', records=[item, copy.deepcopy(item)])
        result = report.audit_coverage(data)[0]
        self.assertEqual(result['uniqueImages'], 1)
        self.assertEqual(result['endpointEntries'], 2)
        self.assertEqual(len(result['missingCells']), 8)
        data['records'][0]['cell'] = [3, 0]
        with self.assertRaisesRegex(ValueError, 'invalid_cell'):
            report.audit_coverage(data)

    def test_unknown_versions(self):
        with self.assertRaisesRegex(ValueError, 'coverage_version'):
            report.audit_coverage({'version': 'future'})
        with self.assertRaisesRegex(ValueError, 'comparison_version'):
            report.audit_regressions({'version': 'future'})

    def test_output_collision(self):
        with self.assertRaisesRegex(ValueError, 'output_collision'):
            report.run_audit(report.ROOT)


if __name__ == '__main__':
    unittest.main()
