"""Verify matched detector reuse and isolated queue rejection paths."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import research_approval as approval
from template_inputs398 import pin
from proposal_tier_policy import compare
from test_proposal_tier_policy import report
import supplemental_proposals427 as adapter


class SupplementalTests(unittest.TestCase):
    def test_fixed_rule_preserves_and_exposes_failures(self):
        self.assertFalse(compare(report(), report(.1, 'miss'), 'high-first')['lostPriorSuccesses'])
        self.assertFalse(compare(report(.9, 'wrong'), report(), 'high-first')['gains'])
        result = compare(report(.1, 'correct-abstention', True), report(.9, 'false-selection', True), 'high-first')
        self.assertTrue(result['newWrongSelections'])

    def test_real_reports_through_queue(self):
        original = q.load(q.ROOT / 'reports/work/SUPPLEMENTAL427/button-spec.json')
        bundle = q.load(q.ROOT / 'reports/work/SUPPLEMENTAL427/button-bundle.json')
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='supplemental427-') as folder:
            root = Path(folder); queue = root / 'queue'
            for name in ('valid', 'bad-receipt', 'wrong-template'):
                doc = copy.deepcopy(bundle)
                if name == 'bad-receipt':doc['supplemental']['report']['sha256'] = '0' * 64
                if name == 'wrong-template':doc['supplemental']['spec'] = doc['baseline']['spec']
                path = root / (name + '.json'); q.save(path, doc); ref = pin(path)
                spec = copy.deepcopy(original); spec['id'] = 'supplemental-test-' + name
                spec['inputs'] = [pin(q.MODULES / 'supplemental_proposals427.py'), ref]
                spec['stage'] = [{'from': ref, 'to': 'bundle.json'}]; spec['evidence']['reads'] = [ref['path']]
                sp = root / (name + '-spec.json'); q.save(sp, spec); q.submit(sp, queue)
                approval.approve(queue, spec['id'], 'test', 'Isolated supplemental comparison qualification.')
                result = q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[spec['id']])
                attempt = queue / 'jobs' / spec['id'] / 'attempts/1'
                self.assertEqual(result, [(spec['id'], 'complete' if name == 'valid' else 'failed')],
                                 (attempt / 'result.json').read_text() + (attempt / 'stderr.log').read_text())
                if name == 'valid':self.assertFalse(q.load(attempt / 'out/benchmark_summary.json')['modelAccepted'])

    def test_changed_settings_rejected(self):
        from unittest.mock import patch
        a = report(); b = report(); a['inputs']['scorecard'] = 'a'; b['inputs']['scorecard'] = 'b'
        cards = [dict(inputs='labels', settings={'confidence': .5}), dict(inputs='labels', settings={'confidence': .25})]
        with patch.object(adapter, 'checked', side_effect=lambda x:x), patch.object(adapter.q, 'load', side_effect=cards):
            with self.assertRaisesRegex(ValueError, 'supplemental_settings'):adapter.evaluate(a,b)


if __name__ == '__main__':unittest.main()
