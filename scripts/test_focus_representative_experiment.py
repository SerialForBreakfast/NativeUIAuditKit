"""Offline selector and actual trainer boundary tests; synthetic fixtures, no model."""
import copy
import json
import math
import sys
import tempfile
import unittest
from unittest.mock import patch

import focus_representative_experiment as e
from focus_dataset_contract import ROOT, digest
from train_focus_ring_detector import experiment_selection, checkpoint_improved, main


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(id=f'retention:{i}',label=i%2,split='validation',use='retention-validation') for i in range(18)]
        self.frames = []
        for i in range(13):
            lane = e.LANES[i%4]
            self.frames.append(dict(id=f'f{i}',coverage='complete',settlement='settled'))
            for label in (0,1):
                sid = f'f{i}:{label}'
                self.rows.append(dict(id=sid,label=label,split='validation',use='representative-selection',
                    stratum=lane, family=f'family{i%3}',control='collectionItem',theme='dark',hard=False,
                    frameID=f'f{i}',population='candidate',settlement='settled',pixelSHA256=sid))
        for label in (0,1):
            self.rows.append(dict(id=f'other:{label}',label=label,split='validation',use='representative-selection',
                stratum='other',family='other',control='label',theme='dark',hard=False,
                frameID='other',population='candidate',settlement='settled',pixelSHA256=f'other:{label}'))
        real=self.rows[18:]
        self.selection=dict(policy=e.POLICY,threshold=.85,weights=e.objective_weights(real),
            framePolicy=dict(populations=dict(candidate=[r['id'] for r in real],auxiliary=[],unresolved=[]),
                             frames=self.frames+[dict(id='other',coverage='unknown',settlement='settled')]))
        self.pred=[dict(id=r['id'],label=r['label'],probability=.95 if r['label'] else .05) for r in self.rows]

    def metric(self):
        return experiment_selection(self.pred,self.rows,dict(formatVersion=e.FORMAT,selection=self.selection))

    def test_actual_epoch_dispatch_and_earliest_tie(self):
        result=self.metric()
        self.assertTrue(result['checkpointEligible']); self.assertAlmostEqual(result['selectionLoss'],-math.log(.95))
        self.assertEqual(result['real']['metrics']['completeFrameSelection']['supported'],13)
        self.assertFalse(checkpoint_improved(.2,.2,dict(selection=e.POLICY)))
        self.assertTrue(checkpoint_improved(.1,.2,dict(selection=e.POLICY)))

    def test_no_eligible_epoch_and_each_guard(self):
        for target in ('retention:1','f0:0','f1:0','f2:0','other:0'):
            old=copy.deepcopy(self.pred)
            p=next(p for p in self.pred if p['id']==target)
            p['probability']=.1 if p['label'] else .95
            self.assertFalse(self.metric()['checkpointEligible'])
            self.pred=old
        for p in self.pred[18:]: p['probability']=.1
        best=math.inf
        for _ in range(3):
            result=self.metric()
            if result['checkpointEligible'] and checkpoint_improved(result['selectionLoss'],best,dict(selection=e.POLICY)):
                best=result['selectionLoss']
        self.assertEqual(best,math.inf)

    def test_missing_duplicate_invalid_predictions(self):
        original=copy.deepcopy(self.pred)
        for invalid in (original[:-1], original+[original[0]], list(reversed(original))):
            self.pred=invalid
            with self.assertRaises(ValueError):self.metric()
        for probability in (float('nan'),float('inf'),-.01,1.01,True):
            self.pred=copy.deepcopy(original);self.pred[0]['probability']=probability
            with self.assertRaises(ValueError):self.metric()
        self.pred=copy.deepcopy(original);self.pred[0]['label']=1
        with self.assertRaises(ValueError):self.metric()

    def test_weights_duplicate_pixels_and_missing_buckets(self):
        rows=copy.deepcopy(self.rows[18:]); original=e.objective_weights(rows)
        duplicate={**rows[0],'id':'duplicate'}; rows.append(duplicate)
        weights=e.objective_weights(rows)
        self.assertAlmostEqual(weights[rows[0]['id']]+weights['duplicate'],original[rows[0]['id']])
        self.assertAlmostEqual(sum(weights.values()),1)
        for lane in e.LANES:
            self.assertAlmostEqual(sum(weights[r['id']] for r in rows if r['stratum']==lane),.25)
        duplicate['label']=1
        with self.assertRaisesRegex(ValueError,'conflicting_pixel_labels'):e.objective_weights(rows)
        for invalid in ([], [r for r in self.rows[18:] if r['stratum']!='tabs']):
            with self.assertRaises(ValueError):e.objective_weights(invalid)

    def test_unsupported_strata_challenge_and_incomplete_frames(self):
        self.rows[-1]['stratum']='unknown-new'
        with self.assertRaisesRegex(ValueError,'unsupported_stratum'):self.metric()
        self.rows[-1]['stratum']='other';self.rows[-1]['use']='final-challenge'
        with self.assertRaisesRegex(ValueError,'invalid_selection_role'):self.metric()
        self.rows[-1]['use']='representative-selection';self.frames[0]['coverage']='unknown'
        self.assertFalse(self.metric()['checkpointEligible'])

    def test_threshold_ties_multiple_not_arbitrary_winner(self):
        for p in self.pred:
            if p['id'].startswith('f0:'):p['probability']=.85
        result=self.metric()
        self.assertFalse(result['checkpointEligible'])
        self.assertEqual(result['real']['metrics']['completeFrameSelection']['counts']['multiple_focus'],1)

    def test_actual_trainer_preflight_does_not_import_torch(self):
        directory=ROOT/'.build/debug-output';directory.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as tmp:
            from pathlib import Path
            path=Path(tmp)/'protocol.json'
            doc=dict(version=e.VERSION,inputs={},configuration=dict(epochs=30,batch=64,lr=.0003,model='mobilenetv4_conv_small',selection=e.POLICY),
                selection=self.selection,sampling=dict(weights={}),counts={},warmCheckpoint={},runtime={},
                unmetQualificationBlockers=['still_open'],samples=[])
            doc['protocolSHA256']=digest(doc);path.write_text(json.dumps(doc))
            before=set(Path(tmp).rglob('*')); torch_loaded='torch' in sys.modules
            with patch.object(e,'assemble',return_value=doc),patch('builtins.print'):
                args=['trainer','--experiment-protocol',str(path),'--experiment-arm','warm-stretch','--name',Path(tmp).name]
                for flags in (['--preflight'],['--execute'],['--dry-run','--epochs','31']):
                    with patch.object(sys,'argv',args+flags):self.assertEqual(main(),2)
                report,rows=e.load_protocol(path,'warm-stretch',Path(tmp).name)
                self.assertTrue(report['configurationValid']);self.assertEqual(report['blockers'],['missing_experiment_approval'])
            self.assertEqual(before,set(Path(tmp).rglob('*')));self.assertEqual(torch_loaded,'torch' in sys.modules)

    def test_changed_hash_seal_runtime_approval_and_ordinary_admission(self):
        from pathlib import Path
        from focus_training_preflight import preflight
        directory=ROOT/'.build/debug-output';directory.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as tmp:
            path=Path(tmp)/'focus_dataset_manifest.json'
            doc=dict(version=e.VERSION,inputs={},configuration={},selection={},sampling={},counts={},
                     warmCheckpoint={},runtime={},unmetQualificationBlockers=['still_open'],samples=[])
            doc['protocolSHA256']=digest(doc);path.write_text(json.dumps(doc))
            ref=e.a.reference(path)
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'changed_assembly_input'):e.a.checked(ref)
            path.write_text(json.dumps({**doc,'runtime':{'changed':True}}))
            with self.assertRaisesRegex(ValueError,'changed_appearance_contract'):
                e.load_protocol(path,'warm-stretch',Path(tmp).name)
            path.write_text(json.dumps(doc))
            with patch.object(e,'assemble',return_value={**doc,'runtime':{'changed':True}}):
                with self.assertRaisesRegex(ValueError,'changed_representative_protocol_or_runtime'):
                    e.load_protocol(path,'warm-stretch',Path(tmp).name)
            approval=Path(tmp)/'approval.json'
            approval.write_text(json.dumps(dict(version='focus-representative-approval-v1',approved=True,
                protocolSHA256='stale',runName=Path(tmp).name,arm='warm-stretch',reviewer='test',reviewReference='test')))
            with patch.object(e,'assemble',return_value=doc):
                with self.assertRaisesRegex(ValueError,'stale_representative_approval'):
                    e.load_protocol(path,'warm-stretch',Path(tmp).name,approval)
            self.assertIn('development_protocol_requires_explicit_experiment_mode',preflight(Path(tmp),Path(tmp).name)['blockers'])

    def test_review_missing_duplicate_or_reclassified_members_rejected(self):
        from pathlib import Path
        directory=ROOT/'.build/debug-output';directory.mkdir(parents=True,exist_ok=True)
        pairs=[dict(corpusID='test',pairID=str(i),disposition=
                    'eligible-development-candidate' if i<38 else 'geometry-blocked' if i<41 else 'duplicate-excluded') for i in range(44)]
        with tempfile.TemporaryDirectory(dir=directory) as tmp:
            path=Path(tmp)/'review.json'
            variants=[pairs[:-1],pairs[:-1]+[pairs[0]], [{**p,'disposition':'eligible-development-candidate'} for p in pairs]]
            for members in variants:
                path.write_text(json.dumps(dict(version='qualified44-final-review-v1',pairs=members)))
                with self.assertRaises(ValueError):e.reviewed_additions(e.a.reference(path))


if __name__=='__main__':unittest.main()
