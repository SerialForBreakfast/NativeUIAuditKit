import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import detector_training_batch478 as batch
import research_queue as q
from experiment_templates import pin
from detector_training_batch478 import assessment


class DecisionTests(unittest.TestCase):
    def report(self, gains=(), losses=()):
        return dict(version='detector-case-match-v1', gains=list(gains),
                    lostPriorSuccesses=list(losses))

    def test_gain_never_promotes(self):
        result=assessment([self.report(['a'])])
        self.assertEqual(result['outcome'],'supported')
        self.assertFalse(result['modelAccepted'])

    def test_one_loss_vetoes_other_gains(self):
        result=assessment([self.report(['a','b']),self.report(losses=['c'])])
        self.assertEqual(result['outcome'],'contradicted')
        self.assertEqual(result['lostPriorSuccesses'],['c'])

    def test_unchanged_is_inconclusive(self):
        self.assertEqual(assessment([self.report()])['outcome'],'inconclusive')

    def test_missing_or_unknown_reports_fail(self):
        for reports in ([],[dict(version='unknown')]):
            with self.assertRaisesRegex(ValueError,'report_version'):
                assessment(reports)


if __name__ == '__main__':
    unittest.main()


class ReportContractTests(unittest.TestCase):
    def exercise(self, version='detector-training-batch-v1', count=1, pinned=True):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as directory:
            root=Path(directory)
            out=root/'jobs/example/attempts/1/out';out.mkdir(parents=True)
            request=root/'request.json'
            q.save(request,dict(version=version,question='Preserve detections?',baselines=['old']*count))
            report=root/'comparison.json'
            q.save(report,dict(version='detector-case-match-v1',gains=['a'],lostPriorSuccesses=['b'],decisions=[]))
            q.save(out.parents[2]/'spec.json',dict(question='Preserve detections?',
                evidence=dict(reads=[q.relative(request)]),inputs=[pin(request)] if pinned else []))
            with patch.object(batch,'OUT',out), patch.object(q,'dependency_inputs',return_value=[dict(job='score',outputs=[pin(report)])]):
                batch.finish()
            import research_graph
            research_graph.check_conditions(dict(dependencies=[dict(job='report',outputs=['decision.json'])],
                conditions=[dict(job='report',output='decision.json',outcome='contradicted')]),
                [dict(job='report',outputs=[dict(pin(out/'decision.json'),name='decision.json')])],q.ROOT)
            return q.load(out/'decision.json')

    def test_report_reads_and_validates_pinned_request(self):
        self.assertEqual(self.exercise()['outcome'],'contradicted')

    def test_unknown_request_fails(self):
        with self.assertRaisesRegex(ValueError,'request_contract'):self.exercise(version='unknown')

    def test_missing_pin_fails(self):
        with self.assertRaisesRegex(ValueError,'request_pin'):self.exercise(pinned=False)

    def test_incomplete_comparisons_fail(self):
        with self.assertRaisesRegex(ValueError,'comparison_count'):self.exercise(count=2)
