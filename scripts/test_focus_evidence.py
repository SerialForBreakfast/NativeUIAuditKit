import copy
import json
import math
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import focus_evidence as e
import review_focus_evidence as r


def row(i=0,**changes):
    return dict(dict(id=str(i),group='g'+str(i),role='development',condition='focus',
                     truth=True,decision=False,authority='authored'),**changes)


CONTEXT=dict(source='pinned-source',model='pinned-model',preprocessing='pinned-settings',domain='procedural')


class EvidenceTests(unittest.TestCase):
    def test_exact_boundary_and_sample_sizes(self):
        self.assertIsNone(e.upper95(0,0));self.assertEqual(e.upper95(5,5),1)
        for target,n in ((.01,299),(.05,59)):
            self.assertLess(e.upper95(0,n),target);self.assertGreater(e.upper95(0,n-1),target)
        self.assertAlmostEqual(e.upper95(1,2),math.sqrt(.95),12)
        self.assertAlmostEqual(e.upper95(15,300),.07594869829959561,places=12)

    def test_invalid_counts(self):
        for k,n in ((-1,3),(4,3),(True,3),(0,2.2),(0,float('nan'))):
            with self.assertRaises(ValueError):e.upper95(k,n)

    def test_unknown_and_abstention_denominators(self):
        s=e.summary([row(),row(1,decision=None),row(2,truth=False),row(3,truth=None)])
        self.assertEqual(s['missedPositive']['denominator'],2)
        self.assertEqual(s['errorAmongNegativeDecisions']['denominator'],2)
        self.assertEqual(s['counts']['unknownTruthNegativeDecisions'],1)
        self.assertEqual(s['coverage']['value'],.75)

    def test_producer_agreement_never_accuracy(self):
        d=e.report([row(authority='producer-reported')],task='focus-change',context=CONTEXT)
        self.assertIsNone(d['metrics']['missedPositive']['value'])
        self.assertEqual(d['producerAgreement']['missedPositive']['value'],1)
        self.assertIsNone(d['bounds']['upper95'])

    def test_no_support(self):
        d=e.report([],task='focus-change',context=CONTEXT)
        self.assertIsNone(d['metrics']['coverage']['value'])

    def test_duplicates_and_cross_roles(self):
        for rows in ([row(),row()],[row(),row(1,group='g0',role='calibration')],
                     [row(role='final-audit',previouslyExposed=True)]):
            with self.assertRaises(ValueError):e.validate(rows)

    def test_invalid_rows(self):
        for changes in (dict(truth=1),dict(decision=float('nan')),dict(authority='model'),dict(group='')):
            with self.assertRaises(ValueError):e.validate([row(**changes)])

    def test_independence_requires_qualified_final_singletons(self):
        with self.assertRaises(ValueError):e.report([row()],task='focus-change',context=CONTEXT,independent_reference='audit')
        d=e.report([row(authority='qualified',role='final-audit')],task='focus-change',context=CONTEXT,independent_reference='audit')
        self.assertEqual(d['bounds']['upper95'],1)

    def test_unknown_task_domain(self):
        for task,ctx in [('modal',CONTEXT),('focus-change',dict(CONTEXT,domain='real'))]:
            with self.assertRaises(ValueError):e.report([],task=task,context=ctx)

    def test_paired_reproducible_and_no_safety_claim(self):
        a=[row(),row(1)];b=[dict(x,decision=True) for x in a]
        result=e.paired_groups(a,b)
        self.assertEqual(result,e.paired_groups(a,b));self.assertEqual(result['mean'],-1)
        self.assertFalse(result['safetyGuarantee'])
        self.assertIsNone(e.paired_groups([row()],[row()])['interval95'])

    def test_paired_membership_truth_and_reverse_group(self):
        for b in ([row(1)],[row(truth=False)]):
            with self.assertRaises(ValueError):e.paired_groups([row()],b)
        a=[row(),row(1,group='g0')]
        self.assertEqual(e.paired_groups(a,a)['groups'],1)

    def test_ios_review_random_sample_and_missing_scores(self):
        cases=[dict(partition='dev',imageID=str(i),group='g',GT=[],FP=[]) for i in range(11)]
        cases[0]['FP']=[dict(reason='unmatched_FP',stableID='a',score=.9),dict(reason='unmatched_FP',stableID='b')]
        doc=dict(schema='worker218-retention-v1',cases=cases)
        out=r.ios_qa(doc)
        self.assertEqual(len(out['randomCaseSample']),2);self.assertEqual(out['unrankableMissingScore'],1)
        self.assertEqual(out['automaticCorrections'],0)
        self.assertEqual(out['randomCaseSample'],r.ios_qa(dict(doc,cases=list(reversed(cases))))['randomCaseSample'])

    def test_temporal_equal_threshold_and_unknown(self):
        frames=[dict(episode='e',family='f',role='development',condition='tiny',t=i,
            foreground_stable=None if i==0 else False,whole=None if i==0 else .005,
            tile=None if i==0 else .02) for i in range(3)]
        out=r.temporal(dict(frames=frames),'bd27',{'sha256':'test'})
        self.assertEqual(out['reports']['whole:0.005']['metrics']['missedPositive']['value'],1)
        self.assertEqual(out['reports']['tile:0.005']['metrics']['missedPositive']['value'],0)
        self.assertIsNone(out['nativeEfficacy'])

    def test_input_version(self):
        with self.assertRaisesRegex(ValueError,'input_version'):r.load_inputs({'version':'future'})

    def test_json_and_hash_integrity(self):
        base=r.ROOT/'.build/debug-output/evidence223-tests';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            p=Path(folder)/'input.json';p.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(ValueError,'duplicate_key'):r.read(p)
            p.write_text('{"a":NaN}')
            with self.assertRaisesRegex(ValueError,'nonfinite'):r.read(p)
            p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'input_hash'):
                r.load_inputs(dict(version='evidence223-inputs-v1',inputs={'endpoint':dict(
                    path=str(p.relative_to(r.ROOT)),sha256='bad')}))

    def test_output_collision_precedes_work(self):
        with patch('sys.argv',['review','--inputs','absent','--output',str(r.ROOT)]),patch.object(r,'run') as run:
            self.assertEqual(r.main(),2);run.assert_not_called()

    def test_schema4_cached_adaptation_and_probability(self):
        doc=dict(version='schema4-score-diagnostic-v1',inspectionSHA256='inspection',
            artifact={'sha256':'model'},runtime={'helperSHA256':'helper'},preprocessing={'crop':256},
            rows=[dict(id='a',reportedRole='focused',clipped=True,probability=.9)])
        self.assertEqual(e.schema4_report(doc)['producerAgreement']['counts']['total'],1)
        self.assertEqual(e.schema4_report(doc)['metrics']['counts']['total'],0)
        doc['rows'][0]['probability']=float('nan')
        with self.assertRaisesRegex(ValueError,'probability'):e.schema4_report(doc)

    def test_native_missing_source_remains_unresolved(self):
        case=dict(stableID='x',flags=[],reported_focus_change_expectation='change',
                  reported_condition='moved',frames=[],crop_checks=[],dispositions={'m':'change'})
        out=r.native(dict(id='bd12-13-native48-report01',cases=[case],duplicates=[],missing_fields=['source'],models={'m':{'sha256':'test'}}),{})
        self.assertFalse(out['dataEligible']);self.assertEqual(out['cases'][0]['disposition'],'unresolved-source-binding')


if __name__=='__main__':unittest.main()
