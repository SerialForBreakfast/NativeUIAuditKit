"""Keep runtime changes separate from label and cleanup failures."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import campaign_comparison516 as adapter

class ComparisonTests(unittest.TestCase):
    def run_case(self, matched, same_runtime=False):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as directory:
            job=Path(directory)/'job';out=job/'attempts/1/out';out.mkdir(parents=True)
            q.save(job/'spec.json',dict(runtimeChange=dict(oldHelperSHA256='0'*64,newHelperSHA256=('0' if same_runtime else '1')*64)))
            def compare():
                q.save(out/'comparison.json',dict(matchedLabels=matched,outcome='supported' if matched else 'contradicted',limitation='Test fixture.'))
            with patch.object(adapter,'OUT',out),patch.object(adapter.campaign,'compare',side_effect=compare):
                adapter.run()
            result=q.load(out/'comparison.json')
            receipt=q.load(out/'artifact-receipt.json')
            self.assertEqual(receipt['outputs'][0]['sha256'],q.digest(out/'comparison.json'))
            return result
    def test_changed_runtime_cannot_support_speedup(self):
        result=self.run_case(True)
        self.assertEqual(result['outcome'],'inconclusive')
        self.assertFalse(result['timingCausalClaim'])
    def test_failed_labels_remain_contradicted(self):
        self.assertEqual(self.run_case(False)['outcome'],'contradicted')
    def test_identical_runtime_rejects_wrong_adapter(self):
        with self.assertRaisesRegex(ValueError,'campaign516_runtime_change'):
            self.run_case(True,True)

if __name__=='__main__':unittest.main()
