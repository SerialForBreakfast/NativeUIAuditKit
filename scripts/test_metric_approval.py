import json
import tempfile
import unittest
from pathlib import Path
import metric_approval as a

class ReviewTests(unittest.TestCase):
    def test_provisional_until_explicit_review(self):
        with tempfile.TemporaryDirectory(dir=a.ROOT/'.build') as temp:
            root=Path(temp);report=root/'report.json';report.write_text('{}')
            self.assertEqual(a.report_status(report,root)['metricsStatus'],'provisional')
            folder=root/a.LEDGER;folder.mkdir(parents=True)
            record=dict(version='user-review-v1',decision='approved',action='publish-metrics',
                userMessage='I approve publishing these metrics.',chatReference='test conversation',reportSHA256=a.digest(report))
            (folder/'review.json').write_text(json.dumps(record))
            self.assertEqual(a.report_status(report,root)['metricsStatus'],'user-approved')
            report.write_text('{"changed":true}')
            self.assertEqual(a.report_status(report,root)['metricsStatus'],'provisional')

    def test_promotion_requires_separate_decision(self):
        with tempfile.TemporaryDirectory(dir=a.ROOT/'.build') as temp:
            root=Path(temp);(root/'review.json').write_text(json.dumps(dict(version='user-review-v1',decision='approved',
                action='publish-metrics',userMessage='Approve these metrics.',chatReference='test')))
            with self.assertRaisesRegex(ValueError,'promotion_approval_required'):
                a.require_promotion(dict(approvalReference='review.json'),root)

if __name__=='__main__':unittest.main()
