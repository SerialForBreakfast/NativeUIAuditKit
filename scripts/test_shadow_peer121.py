import copy
import tempfile
from pathlib import Path
import unittest
import yaml
import shadow_feedback_contract as c

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'reports/work/SHADOW-FEEDBACK-121'


class PeerTests(unittest.TestCase):
    def inspect(self,doc=None,raw=None):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as tmp:
            p=Path(tmp)/'report.yaml';p.write_text(raw if raw is not None else yaml.safe_dump(doc))
            return c.inspect_peer_report(p)

    def source(self):
        return yaml.safe_load((SOURCE/'tvtestrig-20261004-dtm030-survey26-feedback.yaml').read_text())

    def test_actual_published_reports_do_not_become_accuracy(self):
        for name in ('tvtestrig-20261004-dtm030-feedback-receipt.yaml','tvtestrig-20261004-dtm030-survey26-feedback.yaml'):
            r=c.inspect_peer_report(SOURCE/name)
            self.assertTrue(r['internalMetadataChecksPassed']);self.assertIsNone(r['reviewedAccuracy'])
            self.assertFalse(r['imagesVerified'] or r['trainingEligible'] or r['independentEvaluation'])
        self.assertEqual(len(r['differingDecisionIDs']),3)
        self.assertEqual(r['models']['dtm030']['nativeHintAvailable'],6)

    def test_incompatible_or_unknown_models(self):
        for field,value in [('model_id',c.MODEL),('compiled_tree_sha256','0'*64),('contract_sha256','0'*64),
                            ('source_survey_sha256','0'*64),('source_manifest_sha256','0'*64),('navigation_authority',True)]:
            d=self.source();d['dtm030'][field]=value
            with self.assertRaises(ValueError):self.inspect(d)

    def test_count_membership_and_case_corruption(self):
        for value in (-1,True,130):
            d=self.source();d['dtm030']['counts']['native_hint_agreement']=value
            with self.assertRaises(ValueError):self.inspect(d)
        d=self.source();d['cases'].pop()
        with self.assertRaisesRegex(ValueError,'peer_case_accounting'):self.inspect(d)
        for key,value in [('id',self.source()['cases'][0]['id']),('dtm030','success'),('before_sha256','bad')]:
            d=self.source();d['cases'][1][key]=value
            with self.assertRaises(ValueError):self.inspect(d)

    def test_unsafe_yaml_and_scope(self):
        for raw in ('schema_version: 1\nschema_version: 1\n','a: &x [1]\nb: *x\n', '['*40+'1'+']'*40,'a: ['):
            with self.assertRaises(ValueError):self.inspect(raw=raw)
        d=self.source();d['schema_version']=2
        with self.assertRaises(ValueError):self.inspect(d)


if __name__=='__main__':unittest.main()
