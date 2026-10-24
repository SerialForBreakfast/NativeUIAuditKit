"""Qualify retained evidence views without a device or training run."""
import copy
import unittest
from pathlib import Path

import fixture_evidence501 as a
import research_queue as q
from experiment_templates import pin


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        old = q.load(q.QUEUE/'jobs/adr493-session-1-r4/spec.json')
        campaign = old['capture']['plan']
        cases = q.load(q.ROOT/campaign['path'])['manifest']['cases']
        self.request = dict(version='fixture-evidence-request-v1', id='sdk501-test', view='geometry',
            export=pin(q.QUEUE/'jobs/adr493-session-1-r4/attempts/1/out/export-receipt.json'),
            campaign=campaign, cases=[c['case_id'] for c in cases])

    def test_geometry_preserves_role_and_unknown_coverage(self):
        report = a.audit(self.request)
        self.assertEqual(report['counts']['frames'], 8)
        self.assertEqual(report['counts']['independentGroups'], 1)
        self.assertGreater(report['counts']['measuredBodies'], 0)
        for frame in report['frames']:
            self.assertEqual(frame['role'], 'calibration')
            self.assertEqual(frame['annotationCompleteness'], 'unknown')
            self.assertFalse(frame['trainingEligible'])

    def test_second_view_reuses_same_adapter(self):
        request = copy.deepcopy(self.request)
        request['view'] = 'transitions'
        request['cases'] = request['cases'][:2]
        report = a.audit(request)
        self.assertEqual(report['counts']['pairs'], 2)
        self.assertEqual(report['frames'], [])
        self.assertTrue(all(type(p['observedFocusChanged']) is bool for p in report['pairs']))
        self.assertFalse(report['trainingEligible'])

    def test_invalid_requests_fail_with_named_errors(self):
        for key, value, reason in [('version', 'unknown', 'sdk_request_version'),
                ('view', 'no-focus', 'sdk_request_view'), ('cases', [], 'sdk_case_membership'),
                ('cases', ['missing'], 'sdk_case_unknown')]:
            request = copy.deepcopy(self.request)
            request[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, reason):
                a.audit(request)

    def test_changed_receipt_and_duplicate_membership_fail(self):
        request = copy.deepcopy(self.request)
        request['export']['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'input_changed'):
            a.audit(request)
        request = copy.deepcopy(self.request)
        request['cases'].append(request['cases'][0])
        with self.assertRaisesRegex(ValueError, 'sdk_case_membership'):
            a.audit(request)
