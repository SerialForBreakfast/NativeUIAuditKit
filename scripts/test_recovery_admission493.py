"""Check the exact recovery successors without contacting TTR."""
import copy
import unittest
from unittest.mock import patch
import research_queue as q


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.folder = q.ROOT / 'reports/work/ADRSPIKES493/retained-resume-v3'
        self.spec = q.load(self.folder / 'adr493-retained-campaign-resume-v3.json')

    def test_recovery_and_four_sessions(self):
        q.validate(self.spec)
        for n in range(1, 5):
            q.validate(q.load(self.folder / f'adr493-session-{n}-r3.json'))

    def test_unknown_id(self):
        self.spec['id'] = 'adr493-retained-campaign-resume-v4'
        with self.assertRaisesRegex(ValueError, 'recovery_approved_scope'):
            q.validate(self.spec)

    def test_legacy_id_cannot_use_retained_version(self):
        self.spec['id'] = 'adr493-retained-campaign-recovery'
        with self.assertRaisesRegex(ValueError, 'recovery_approved_scope'):
            q.validate(self.spec)

    def test_wrong_target(self):
        self.spec['capture']['target'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'capture_target'):
            q.validate(self.spec)

    def test_budget_expansion(self):
        self.spec['limits']['maxOutputBytes'] = 250000001
        with self.assertRaisesRegex(ValueError, 'capture_limits'):
            q.validate(self.spec)

    def test_altered_proof(self):
        import ttr_campaign_recovery493 as recovery
        with patch.object(recovery, 'retained_restart', side_effect=ValueError('recovery_export_bytes')):
            with self.assertRaisesRegex(ValueError, 'recovery_export_bytes'):
                q.validate(self.spec)


if __name__ == '__main__':
    unittest.main()
