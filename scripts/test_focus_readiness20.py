"""Real campaign/readiness callers and exact small-batch transition selection."""
import copy
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import human_annotation_review as h
import fixture_campaign_intake as campaign
import focus_structural_readiness as structural
import focus_recorded_readiness as recorded
from test_fixture_campaign_intake import generated
import test_focus_artwork_readiness as fixture
import test_human_recording_review as recording_fixture


class StructuralTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.PipelineTests();self.f.setUp();self.addCleanup(self.f.tearDown)
        root=self.f.root/'campaign';root.mkdir();p,b,protected=generated(root)
        self.output=root/'complete';campaign.run(p,b,protected,self.output)
        self.completion=self.output/'completed.json'

    def test_actual_cli_pair_dedup_mass_and_unchanged_eval(self):
        out=self.f.root/'readiness.json'
        p=subprocess.run([sys.executable,str(h.ROOT/'scripts/focus_structural_readiness.py'),
            '--completion',str(self.completion),'--baseline',str(self.f.path),'--output',str(out)],
            capture_output=True,text=True,timeout=60)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        r=h.sealed(out,'focus-structural-readiness-v1')
        self.assertFalse(r['launchEligible']);self.assertFalse(r['trainingEligible'])
        self.assertEqual(r['counts']['targetPairs'],4)
        self.assertGreater(r['counts']['proposedControls'],0)
        self.assertLess(r['counts']['proposedControls'],8)
        c=r['comparison'];self.assertAlmostEqual(sum(c['hypotheticalAdditionWeights'].values()),1)
        evaluation=[s for s in self.f.base['samples'] if s['split']!='train']
        self.assertEqual(c['evaluationMembershipSHA256'],h.digest(evaluation))
        self.assertFalse(c['executionAuthorized'])
        self.assertTrue(any(pair['aliases'] for pair in r['pairs']))
        self.assertEqual(r['comparison'],structural.prepare(self.completion,self.f.path)['comparison'])

    def test_changed_output_and_baseline_are_rejected(self):
        (self.output/'attempt-001/campaign-review.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed_campaign_outputs'):
            structural.prepare(self.completion,self.f.path)

    def test_changed_baseline_and_completion_reject(self):
        raw=self.f.path.read_text();self.f.path.write_text(raw.replace('0.85','0.86'))
        with self.assertRaisesRegex(ValueError,'baseline'):
            structural.prepare(self.completion,self.f.path)
        self.f.path.write_text(raw)
        d=h.read(self.completion);d['files']=[];self.completion.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'changed_or_unsupported'):
            structural.prepare(self.completion,self.f.path)

    def test_human_editor_edits_are_not_silently_approved(self):
        p=next((self.output/'attempt-001/audit/review/editor').glob('*.json'))
        doc=h.read(p);doc['description']='human work in progress';p.write_text(json.dumps(doc))
        r=structural.prepare(self.completion,self.f.path)
        self.assertIn('human_sample_acceptance_pending',r['blockers'])
        self.assertFalse(r['launchEligible'])

    def test_competitor_label_conflict_cannot_be_hidden_by_target_filter(self):
        original=structural.native.candidates
        def conflicting(*args):
            rows,accounting,links=original(*args)
            target=next(r for r in rows if r['sourceElementID']=='e')
            other=next(r for r in rows if r['sourceElementID']!='e')
            other['crop']=target['crop'];other['label']=1-target['label']
            return rows,accounting,links
        with patch.object(structural.native,'candidates',side_effect=conflicting):
            r=structural.prepare(self.completion,self.f.path)
        self.assertGreater(r['counts']['blockedPairs'],0)
        self.assertTrue(any('conflicting_crop_labels' in p['reasons'] for p in r['pairs']))


class RecordedTests(unittest.TestCase):
    def fixture(self):
        fs=[dict(frameID=str(i),sequenceNumber=i,sha256='hash'+str(i),capturedMonotonicNanoseconds=i) for i in range(4)]
        events=[dict(frame={'_0':f}) for f in fs]
        a=dict(actionID='a',command='down',associationReady=True,reasons=[],preFrames=['0','1'],settledFrames=['3','2'])
        return dict(actions=[a]),events

    def test_closest_pre_first_settled_and_no_inferred_truth(self):
        audit,events=self.fixture();rows,gaps=recorded.endpoints(audit,events,{'hash1':[]},{'hash2':{}})
        r=rows[0];self.assertEqual(r['endpoints']['before']['frameID'],'1')
        self.assertEqual(r['endpoints']['after']['frameID'],'2')
        self.assertEqual(r['missingReview'],['hash2']);self.assertTrue(r['metadataReady'])
        self.assertFalse(r['runtimeContextVerified']);self.assertFalse(r['persistentIdentityVerified'])

    def test_relevant_gaps_block_but_optional_ocr_does_not(self):
        for reason,ready in [('inputOverlap',False),('settlementUnavailable',False),('unknown',False),('advisorySkipped',True)]:
            a,e=self.fixture();e.append(dict(gap={'_0':dict(reason=reason,precedingActionID='a')}))
            rows,_=recorded.endpoints(a,e,{},{});self.assertEqual(rows[0]['metadataReady'],ready)
        a,e=self.fixture();e.append(dict(gap={'_0':dict(reason='unattributed')}))
        _,g=recorded.endpoints(a,e,{},{});self.assertEqual(g,{'unattributed':1})

    def test_exact_frontier_handles_two_endpoint_dependencies_and_ties(self):
        rows=[dict(metadataReady=True,missingReview=['a','b']) for _ in range(3)]
        rows+=[dict(metadataReady=True,missingReview=['c']),dict(metadataReady=False,missingReview=[])]
        f=recorded.review_frontier(rows,['c','b','a'])
        self.assertEqual(f[1]['selected'],['c']);self.assertEqual(f[1]['annotationCompleteActions'],1)
        self.assertEqual(f[2]['selected'],['a','b']);self.assertEqual(f[2]['annotationCompleteActions'],3)
        self.assertEqual(f[3]['annotationCompleteActions'],4)
        self.assertEqual(f,recorded.review_frontier(list(reversed(rows)),['a','b','c']))
        with self.assertRaisesRegex(ValueError,'limit'):recorded.review_frontier(rows,list('123456789'))

    def test_missing_unprepared_endpoint_cannot_be_unlocked(self):
        rows=[dict(metadataReady=True,missingReview=['absent'])]
        self.assertTrue(all(r['annotationCompleteActions']==0 for r in recorded.review_frontier(rows,['a','b'])))

    def test_actual_recorded_cli_keeps_zero_support_unavailable(self):
        f=recording_fixture.RecordingTests();f.setUp();self.addCleanup(f.tearDown)
        b=f.prepare()
        model=fixture.PipelineTests();model.setUp();self.addCleanup(model.tearDown)
        out=f.f.root/'readiness.json'
        cmd=[sys.executable,str(h.ROOT/'scripts/focus_recorded_readiness.py'),
             '--batch',str(b),'--pending',str(b),'--baseline',str(model.path),'--output',str(out)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        r=h.sealed(out,'focus-recorded-readiness-v1')
        self.assertEqual(r['counts']['actions'],0);self.assertIsNone(r['qualifiedTransitionAccuracy'])
        before=out.read_bytes();p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        self.assertNotEqual(p.returncode,0);self.assertEqual(out.read_bytes(),before)


if __name__=='__main__':unittest.main()
