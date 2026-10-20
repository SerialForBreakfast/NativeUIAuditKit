"""Check display classification without changing execution state."""
import unittest
from research_dashboard_states import classify


class UnselectedTests(unittest.TestCase):
    def row(self, reason, attempts=0):
        return dict(state='blocked', attempts=attempts, requirements=[reason])

    def test_verified_opposite_outcome(self):
        for outcome in ('supported', 'contradicted'):
            row = self.row('condition_not_met:decision:' + outcome + ':Measured outcome.')
            self.assertEqual(classify(row)[0], 'unselected')
            self.assertEqual(row['state'], 'blocked')

    def test_uncertain_and_invalid_evidence_remain_blocked(self):
        for reason in ('condition_not_met:decision:inconclusive:Insufficient evidence.',
                       'condition_evidence_changed', 'dependency_incomplete:decision',
                       'condition_not_met:decision:unsupported:Invalid.'):
            self.assertEqual(classify(self.row(reason))[0], 'blocked')

    def test_attempt_and_additional_blocker_remain_visible(self):
        reason = 'condition_not_met:decision:contradicted:Regression.'
        self.assertEqual(classify(self.row(reason, 1))[0], 'blocked')
        row = self.row(reason)
        row['requirements'].append('input_changed')
        self.assertEqual(classify(row)[0], 'blocked')

    def test_read_only_display_keeps_closed_branches_separate(self):
        from generate_research_dashboard import render_html
        page = render_html({'jobs': []})
        self.assertIn('id="unselected-rows"', page)
        self.assertIn("$('unselected-rows').replaceChildren()", page)
        self.assertIn("stateOf(j)==='unselected'?'unselected-rows'", page)
        self.assertIn('No repair is required.', page)


if __name__ == '__main__':
    unittest.main()
