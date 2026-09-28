"""Retention selection and real caller preflight, never an extra model run."""
import copy
import json
import math
import sys
import unittest
from unittest.mock import patch

import focus_retention_experiment as e
import focus_training_extension as extension
import focus_mixed_assembly as a
from focus_dataset_contract import ROOT, digest, FocusDataError
import test_focus_appearance_experiment as fixtures


class RetentionTests(unittest.TestCase):
    save = fixtures.AppearanceTests.save
    row = fixtures.AppearanceTests.row
    complete = fixtures.AppearanceTests.complete

    def setUp(self):
        fixtures.AppearanceTests.setUp(self)
        self.complete()
        self.spec['evaluation'] = []
        base = e.appearance.assemble(self.spec)
        self.source = {**base, 'version': extension.VERSION}
        self.source['protocolSHA256'] = digest({k:v for k,v in self.source.items() if k != 'protocolSHA256'})
        self.input = {'version': e.INPUT_VERSION, 'extension': self.save('extension.json', self.source)}
        p=patch.object(e.extension, 'assemble', side_effect=lambda spec:copy.deepcopy(self.source)); p.start(); self.addCleanup(p.stop)
        p=patch.object(e, 'runtime_identity', return_value={'testOnly':True}); p.start(); self.addCleanup(p.stop)
        self.doc=e.assemble(self.input)
        self.path=ROOT/self.save('retention.json',self.doc)['path']
        self.approval={'version':'focus-retention-approval-v1','approved':True,'protocolSHA256':self.doc['protocolSHA256'],
                       'runName':self.root.name,'arm':'warm-stretch','reviewer':'test-only','reviewReference':'synthetic'}
        self.approval_path=ROOT/self.save('approval.json',self.approval)['path']

    def test_actual_dispatch_trainer_preflight_no_training_or_gate_relaxation(self):
        from focus_learning_experiment import load_protocol
        from train_focus_ring_detector import main
        report,rows=load_protocol(self.path,'warm-stretch',self.root.name,self.approval_path)
        self.assertTrue(report['launchEligible']); self.assertFalse(report['executionAuthorized'])
        self.assertEqual(len(report['unmetQualificationBlockers']),10)
        self.assertEqual(self.doc['samples'],self.source['samples'])
        self.assertEqual(self.doc['sampling'],self.source['sampling'])
        self.assertEqual(self.doc['warmCheckpoint'],self.source['warmCheckpoint'])
        self.assertEqual(self.doc['selection']['reference'],self.source['selection']['reference'])
        self.assertEqual(a.assemble(self.input),self.doc)
        args=['trainer','--experiment-protocol',str(self.path),'--experiment-arm','warm-stretch',
              '--name',self.root.name,'--experiment-approval',str(self.approval_path)]
        before=set(self.root.rglob('*')); imported='torch' in sys.modules
        for suffix,code in ((['--preflight'],0),(['--dry-run','--epochs','31'],2),(['--execute'],2)):
            with patch.object(sys,'argv',args+suffix),patch('builtins.print'): self.assertEqual(main(),code)
        self.assertEqual(before,set(self.root.rglob('*'))); self.assertEqual(imported,'torch' in sys.modules)
        from focus_training_preflight import preflight
        directory=self.root/'ordinary'; directory.mkdir()
        (directory/'focus_dataset_manifest.json').write_text(json.dumps(self.doc))
        self.assertIn('development_protocol_requires_explicit_experiment_mode',preflight(directory,self.root.name)['blockers'])
        self.assertEqual(len(self.source['readinessBlockers']),10)

    def test_missing_stale_approval_or_wrong_scope(self):
        self.assertFalse(e.load_protocol(self.path,'warm-stretch',self.root.name)[0]['launchEligible'])
        for field,value in (('protocolSHA256','changed'),('approved',False),('runName','other'),('arm','scratch-stretch'),('version','focus-appearance-approval-v1')):
            self.approval_path.write_text(json.dumps({**self.approval,field:value}))
            self.assertFalse(e.load_protocol(self.path,'warm-stretch',self.root.name,self.approval_path)[0]['launchEligible'])
        with self.assertRaisesRegex(FocusDataError,'unsupported_retention_arm'):
            e.load_protocol(self.path,'scratch-stretch',self.root.name)

    def test_runtime_changed_extension_and_protocol_rejected(self):
        with patch.object(e,'runtime_identity',return_value={'changed':True}):
            with self.assertRaisesRegex(FocusDataError,'changed_retention_protocol_or_runtime'):
                e.load_protocol(self.path,'warm-stretch',self.root.name)
        with patch.object(e.extension,'assemble',return_value={}):
            with self.assertRaisesRegex(FocusDataError,'changed_retention_extension'):
                e.load_protocol(self.path,'warm-stretch',self.root.name)
        changed=copy.deepcopy(self.doc); changed['configuration']['epochs']=31
        changed['protocolSHA256']=digest({k:v for k,v in changed.items() if k!='protocolSHA256'})
        self.path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(FocusDataError,'changed_retention_protocol_or_runtime'):
            e.load_protocol(self.path,'warm-stretch',self.root.name)

    def test_changed_inputs_unexpected_blockers_and_extra_partitions_rejected(self):
        original=copy.deepcopy(self.source)
        cases=[lambda d:d['samples'][0].update(use='final-challenge',split='test'),
               lambda d:d['readinessBlockers'].append('unknown_labels'),
               lambda d:d['configuration'].update(epochs=31),
               lambda d:d['sampling']['sourceMass'].update(native=.1),
               lambda d:d['counts'].update(**{'train-candidate':0}),
               lambda d:d['selection'].update(nativeRetentionFloor=.5)]
        for change in cases:
            changed=copy.deepcopy(original);change(changed)
            changed['protocolSHA256']=digest({k:v for k,v in changed.items() if k!='protocolSHA256'})
            spec={**self.input,'extension':self.save('changed-extension.json',changed)}
            with self.assertRaises(ValueError): e.assemble(spec)
        (ROOT/self.input['extension']['path']).write_text('{}')
        with self.assertRaisesRegex(FocusDataError,'changed_assembly_input'):e.assemble(self.input)

    def metrics(self, probabilities):
        rows=[r for r in self.doc['samples'] if r['use']=='retention-validation']
        predictions=[dict(id=r['id'],label=r['label'],probability=p) for r,p in zip(rows,probabilities)]
        return rows,predictions

    def test_floor_selection_loss_threshold_and_earliest_tie(self):
        from train_focus_ring_detector import checkpoint_improved
        rows,predictions=self.metrics([.1,.9])
        # Fixture ordering follows sample IDs, not labels.
        for p in predictions: p['probability']=.9 if p['label'] else .1
        result=e.selection_metrics(predictions,rows,self.doc['selection'])
        self.assertTrue(result['checkpointEligible']); self.assertAlmostEqual(result['selectionLoss'],-math.log(.9))
        self.assertFalse(checkpoint_improved(.1,.1,self.doc['configuration']))
        self.assertTrue(checkpoint_improved(.09,.1,self.doc['configuration']))
        for p in predictions: p['probability']=.85 if p['label'] else .849
        self.assertTrue(e.selection_metrics(predictions,rows,self.doc['selection'])['checkpointEligible'])
        for p in predictions: p['probability']=.85
        self.assertFalse(e.selection_metrics(predictions,rows,self.doc['selection'])['checkpointEligible'])
        # Every epoch below the floor leaves the initial best=inf unchanged.
        best=float('inf')
        for p in (.1,.8,.849):
            for prediction in predictions: prediction['probability']=p if prediction['label'] else .1
            metric=e.selection_metrics(predictions,rows,self.doc['selection'])
            if metric['checkpointEligible'] and checkpoint_improved(metric['selectionLoss'],best,self.doc['configuration']): best=metric['selectionLoss']
        self.assertEqual(best,float('inf'))

    def test_scores_membership_missing_duplicates_and_nonretention_rejected(self):
        rows,predictions=self.metrics([.1,.9])
        for value in (float('nan'),float('inf'),-1,1.1,True):
            changed=copy.deepcopy(predictions);changed[0]['probability']=value
            with self.assertRaisesRegex(FocusDataError,'invalid_validation_prediction'):
                e.selection_metrics(changed,rows,self.doc['selection'])
        for preds,rs in (([],[]),(predictions[:1],rows),(predictions[::-1],rows),
                         (predictions*2,rows*2),(predictions,[{**r,'use':'appearance-validation'} for r in rows])):
            with self.assertRaises(ValueError):e.selection_metrics(preds,rs,self.doc['selection'])


if __name__=='__main__': unittest.main()
