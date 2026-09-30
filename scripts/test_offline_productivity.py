"""Offline regression tests for annotation, score reports and training audit."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import annotation_proposal_filter as f
import focus_decision_report as d
import training_efficiency_audit as a
from focus_dataset_contract import ROOT, digest
from ohem_callback import OHEMCallback
from test_focus_representative_experiment import SelectionTests


class FilterTests(unittest.TestCase):
    def test_deterministic_no_mutation(self):
        boxes=[[0,0,50,50],[1,1,50,50],[100,100,1,1]];old=copy.deepcopy(boxes)
        self.assertEqual(f.select(boxes,200,200)[0],[0,2])
        self.assertEqual(f.select(boxes,200,200,'compact')[0],[0])
        self.assertEqual(boxes,old)
        self.assertEqual(f.select([],200,200),([],[]))

    def test_nested_controls_not_deduplicated(self):
        self.assertEqual(f.select([[0,0,100,100],[10,10,30,30]],200,200)[0],[0,1])

    def test_invalid_boxes_and_policy(self):
        for box in ([0,0,0,1],[0,0,float('nan'),1],[-1,0,2,2],[0,0,201,20]):
            with self.assertRaises(ValueError):f.select([box],200,200)
        with self.assertRaises(ValueError):f.select([],200,200,'unknown')


class DecisionTests(unittest.TestCase):
    def setUp(self):
        fixture=SelectionTests();fixture.setUp()
        self.p=dict(samples=fixture.rows,selection=fixture.selection)
        self.p['protocolSHA256']=digest(self.p)
        metrics=d.selection_metrics(fixture.pred,fixture.rows,fixture.selection)
        snapshot=dict(**metrics,predictions=fixture.pred)
        self.r=dict(protocolSHA256=self.p['protocolSHA256'],initial=snapshot,
            history=[dict(update=1,validation=copy.deepcopy(snapshot))])
        self.c=dict(schema_version=1,budget=dict(max_targets_per_case=1),cases=[dict(case_id=str(i),
            split_group='validation',recipe=dict(recipe_hash='hash')) for i in range(3)])

    def call(self):
        with patch.object(d,'recipe_hash',return_value='hash'):return d.report(self.p,self.r,self.c)

    def reseal(self):
        self.p.pop('protocolSHA256');self.p['protocolSHA256']=digest(self.p)
        self.r['protocolSHA256']=self.p['protocolSHA256']

    def test_replay_and_pending_distinct(self):
        result=self.call()
        self.assertEqual(result['reports']['terminal']['real']['metrics']['completeFrameSelection']['supported'],13)
        self.assertTrue(all(x['pairedMetrics'] is None for x in result['pendingCases']))
        self.assertFalse(result['modelExecution'])

    def test_changed_seal_protocol_and_challenge(self):
        self.p['samples'][0]['label']=1
        with self.assertRaisesRegex(ValueError,'seal'):self.call()
        self.setUp();self.r['protocolSHA256']='bad'
        with self.assertRaisesRegex(ValueError,'incompatible'):self.call()
        self.setUp();self.p['samples'][0]['originSplit']='test';self.reseal()
        with self.assertRaisesRegex(ValueError,'protected'):self.call()

    def test_missing_duplicate_nonfinite_and_metric_tampering(self):
        for kind in ('missing','duplicate','nan','tampered'):
            self.setUp();v=self.r['history'][0]['validation']
            if kind=='missing':v['predictions'].pop()
            if kind=='duplicate':v['predictions'].append(v['predictions'][0])
            if kind=='nan':v['predictions'][0]['probability']=float('nan')
            if kind=='tampered':v['selectionLoss']=123
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.call()

    def test_missing_cases_wrong_roles(self):
        self.c['cases'].pop()
        with self.assertRaises(ValueError):self.call()
        self.setUp();self.c['cases'][0]['split_group']='test'
        with self.assertRaises(ValueError):self.call()

    def test_existing_pair_score_envelope_adapter(self):
        pair=dict(pair_id='pair',fixture_scene='grid',theme='dark',element_type='collectionItem',
            focused_crop='f.png',unfocused_crop='u.png',observationBinding={k:dict(recipe={}) for k in ('focusedScene','baselineScene')})
        manifest=dict(pairs=[pair],preprocessing={'test':'isolated'})
        proto=dict(formatVersion='focus-baseline-protocol-v1',manifestSHA256=digest(manifest),partition='development',
            threshold=.85,preprocessing=manifest['preprocessing'],samples=d.pair_rows(manifest),
            artifact=dict(sha256='model'),evidenceKind='test-only',sourceKind='simulatorFixture')
        proto['protocolSHA256']=digest(proto)
        scores=dict(formatVersion='focus-baseline-scores-v1',protocolSHA256=proto['protocolSHA256'],
            artifactSHA256='model',inferenceKind='test-only',scores={'pair:1':.99,'pair:0':.01})
        delivery=dict(version='focus-decision-pairs-v1',cases=[dict(caseID='0',manifest=dict(path='manifest',sha256='m'),
            models=[dict(name='fixture',protocol=dict(path='protocol',sha256='p'),scores=dict(path='scores',sha256='s'))])])
        docs={'manifest':manifest,'protocol':proto,'scores':scores}
        validated=[dict(split='development',pairID='pair',theme='dark',**{'class':'collectionItem'})]
        with patch.object(d,'read',side_effect=lambda path,h:docs[Path(path).name]),patch.object(d,'validate_manifest',return_value=validated),patch.object(d,'recipe_hash',return_value='hash'):
            result=d.paired_delivery(delivery,self.c)
            self.assertEqual(result[0]['models'][0]['report']['evaluation']['groups']['overall']['tp'],1)
            self.assertIsNone(result[0]['frameSelection'])
            scores['scores'].pop('pair:0')
            with self.assertRaises(ValueError):d.paired_delivery(delivery,self.c)
            scores['scores']['pair:0']=.01
            validated[0]['split']='test'
            with self.assertRaisesRegex(ValueError,'role'):d.paired_delivery(delivery,self.c)


class EfficiencyTests(unittest.TestCase):
    def test_requested_effective_unknown(self):
        cfg=a.configuration(dict(device='mps',batch=8,nbs=64,workers=4,amp=True,rect=True,mosaic=1))
        self.assertEqual(cfg['sourceDerived']['workers'],0)
        self.assertFalse(cfg['sourceDerived']['amp']);self.assertEqual(cfg['sourceDerived']['mosaic'],0)
        self.assertEqual(cfg['sourceDerived']['steadyEffectiveBatch'],64)
        self.assertIsNone(cfg['runtimeConfirmed']['batchTensorShapes'])
        self.assertIsNone(a.configuration({})['sourceDerived']['steadyAccumulation'])

    def test_times_and_truncated(self):
        header='epoch,time,metrics/mAP50-95(B)\n'
        out=a.epoch_times(header+'1,10,.2\n2,22,.4\n')
        self.assertEqual(out['medianEpochSeconds'],11)
        self.assertEqual(out['bestRecordedFitnessEpoch'],2)
        for text in ('',header,header+'1,nan,.2\n',header+'1,10,.2\n2,9,.3\n','epoch\n1\n'):
            with self.assertRaises(ValueError):a.epoch_times(text)
        self.assertEqual(a.log_evidence(None)['status'],'unavailable')

    def test_real_callback_proxy_cache_alignment_and_rect_repair(self):
        class Loss:
            def detach(self):return self
            def cpu(self):return self
            def __float__(self):return 8.
        ds=SimpleNamespace(im_files=['a','b','c','d'],labels=[{'id':i} for i in range(4)],
            rect=True,batch_size=2,batch=[0,0,1,1],batch_shapes=[[64,128],[128,64]])
        loader=SimpleNamespace(dataset=ds,reset=lambda:None)
        trainer=SimpleNamespace(train_loader=loader,preprocess_batch=lambda b:b,loss=Loss())
        cb=OHEMCallback(fraction=.5);cb.on_pretrain_routine_end(trainer)
        trainer.preprocess_batch(dict(im_file=['c','d']));cb.on_train_batch_end(trainer)
        self.assertEqual(cb._epoch_loss['c'],[4.]);self.assertEqual(cb._epoch_loss['d'],[4.])
        cb.on_train_epoch_end(trainer)
        self.assertEqual(ds.im_files,['a','b','c','c']);self.assertEqual(ds.labels[3],{'id':2})
        self.assertEqual(ds.ims,[None]*4);self.assertFalse(cb._epoch_loss)
        self.assertEqual(ds.batch_shapes,[[64,128],[128,64]]) # equal-shape replacement preserves padding

    def test_imports_never_load_models(self):
        code="import sys; import annotation_proposal_filter,focus_decision_report,training_efficiency_audit; assert not any(x in sys.modules for x in ('torch','ultralytics','coremltools'))"
        r=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_hash_and_output_collision(self):
        root=ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            path=Path(tmp)/'x.json';path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'changed_input'):d.read(path,'bad')
            self.assertEqual(d.read(path,hashlib.sha256(b'{}').hexdigest()),{})
            with self.assertRaisesRegex(ValueError,'output_collision'):d.run(path,'',path,'',path,'',Path(tmp))


if __name__=='__main__':unittest.main()
