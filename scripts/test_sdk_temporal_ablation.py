"""Check retained identity, observed labels, and intervention accounting without model execution."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
from experiment_templates import pin
import sdk_temporal_ablation as m

class AblationTests(unittest.TestCase):
    def request(self, condition='movement'):
        job=q.QUEUE/'jobs'/('temporal544-'+condition)
        return dict(version='sdk-temporal-ablation-v1', id='ablation-test-'+condition,
            sourceSpec=pin(job/'spec.json'), sourceResult=pin(job/'attempts/1/result.json'),
            sourceSummary=pin(job/'attempts/1/out/benchmark_summary.json'))
    def test_both_descriptions_reuse_compiler(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            for condition in ('movement','unchanged'):
                path=Path(folder)/(condition+'.json'); q.save(path,self.request(condition))
                spec=m.build(path); q.validate(spec); q.verify_pins(spec)
                sp=path.with_name(condition+'-spec.json'); q.save(sp,spec)
                self.assertEqual(q.submit(sp,Path(folder)/'queue'),'submitted')
                self.assertEqual(spec['adapter']['steps'],['sdk_temporal_ablation.run'])
    def test_changed_membership_rejected(self):
        original=m.rows
        def changed(source):
            data=original(source); data[0]['group']='wrong-group'; return data
        with patch.object(m,'rows',side_effect=changed),self.assertRaisesRegex(ValueError,'ablation_row_identity'):
            m.prepare(self.request())
    def test_unknown_identity_rejected(self):
        original=m.pair
        def unknown(ref):
            value=original(ref); value['temporalEligible']=False; return value
        with patch.object(m,'pair',side_effect=unknown),self.assertRaisesRegex(ValueError,'ablation_unknown_identity'):
            m.prepare(self.request())
    def test_unknown_fields_rejected(self):
        req=self.request();req['threshold']=.5
        with self.assertRaisesRegex(ValueError,'ablation_fields'):m.prepare(req)
    def test_source_hash_rejected(self):
        req=self.request();req['sourceSummary']['sha256']='0'*64
        with self.assertRaises(ValueError):m.prepare(req)
    def test_removal_losses_and_no_change_preservation(self):
        for condition in ('movement','unchanged'):
            _,_,data,report=m.prepare(self.request(condition))
            result=m.compare(data,report,{n:[.01] for n in report['results']})
            self.assertEqual(result['lostWithRemoval']['baseline'],int(condition=='movement'))
            self.assertFalse(result['modelAccepted']);self.assertFalse(result['trainingEligible'])
    def test_abstention_counts_as_lost_success(self):
        _,_,data,report=m.prepare(self.request())
        result=m.compare(data,report,{n:[.5] for n in report['results']})
        self.assertEqual(result['counts']['baseline'],{'abstention':1})
        self.assertEqual(result['lostWithRemoval']['baseline'],1)
    def test_invalid_probabilities_and_missing_scores(self):
        _,_,data,report=m.prepare(self.request())
        for value in (float('nan'),-1,2):
            with self.assertRaises(ValueError):m.compare(data,report,{n:[value] for n in report['results']})
        with self.assertRaisesRegex(ValueError,'ablation_score_count'):
            m.compare(data,report,{n:[] for n in report['results']})
    def test_model_membership(self):
        _,_,data,report=m.prepare(self.request())
        with self.assertRaisesRegex(ValueError,'ablation_score_models'):m.compare(data,report,{'baseline':[.01]})

if __name__=='__main__':unittest.main()
