"""Sampler ablation tests; no model execution or retained dataset dependency."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import focus_sampler_experiment as e
from focus_dataset_contract import ROOT,digest


class SamplerTests(unittest.TestCase):
    def setUp(self):
        self.rows=[];self.mapping={}
        for n,s in enumerate(e.rep.LANES,1):
            for pair in range(n):
                for label in (0,1):
                    sid=f'{s}:{pair}:{label}'
                    self.rows.append(dict(id=sid,label=label,split='train',use='train-candidate',sourceID=s,
                        pairID=str(pair),sourceKind='simulatorFixture'))
                    self.mapping[sid]=dict(stratum=s)

    def test_equal_appearance_label_not_raw_count(self):
        result=e.weights(self.rows,self.mapping)
        self.assertAlmostEqual(sum(result['weights'].values()),1)
        for s in e.rep.LANES:
            self.assertAlmostEqual(result['stratumMass'][s],.25)
            for label in (0,1):
                self.assertAlmostEqual(sum(result['weights'][r['id']] for r in self.rows
                    if self.mapping[r['id']]['stratum']==s and r['label']==label),.125)
        self.assertGreater(result['weights']['buttons:0:0'],result['weights']['rows:0:0'])

    def test_reject_evaluation_unknown_missing_or_changed_members(self):
        for role in ('retention-validation','representative-selection','final-challenge'):
            rows=copy.deepcopy(self.rows);rows[0]['use']=role
            with self.assertRaisesRegex(ValueError,'evaluation_in_sampler'):e.weights(rows,self.mapping)
        for mutation in ('missing','unknown','pair'):
            m=copy.deepcopy(self.mapping)
            if mutation=='missing':m.pop(next(iter(m)))
            elif mutation=='unknown':m[next(iter(m))]['stratum']='unknown'
            else:m[next(iter(m))]['stratum']='tabs'
            with self.assertRaises(ValueError):e.weights(self.rows,m)
        rows=[r for r in self.rows if r['sourceID']!='tabs'];m={r['id']:self.mapping[r['id']] for r in rows}
        with self.assertRaisesRegex(ValueError,'missing_training_bucket'):e.weights(rows,m)

    def test_tab_recipe_overrides_generic_button_nested_children_do_not(self):
        row=dict(control='primaryButton',sourceKind='simulatorFixture',scene='gridMatrix')
        self.assertEqual(e.lane(row,'tabs'),'tabs')
        self.assertEqual(e.lane(row,'nested_tabs_v1'),'tabs')
        self.assertEqual(e.lane(row,'nested_tabs_v1','parent'),'buttons')
        self.assertEqual(e.lane(row),'buttons')
        self.assertEqual(e.lane(row,'settings_rows'),'rows')
        self.assertEqual(e.lane({**row,'control':'collectionItem'}),'artwork')
        with self.assertRaises(ValueError):e.lane({**row,'control':'unrecognized'})
        with self.assertRaises(ValueError):e.lane({**row,'sourceKind':'tvos_simulator_os','scene':'unknown'})

    def test_inputs_unmodified_and_deterministic(self):
        before=copy.deepcopy((self.rows,self.mapping))
        a=e.weights(self.rows,self.mapping);b=e.weights(list(reversed(self.rows)),self.mapping)
        self.assertEqual(a['weights'],b['weights']);self.assertEqual(before,(self.rows,self.mapping))

    def test_actual_dispatch_approval_preflight_and_no_ordinary_admission(self):
        from focus_learning_experiment import load_protocol
        from focus_training_preflight import preflight
        from train_focus_ring_detector import main
        out=ROOT/'.build/debug-output';out.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=out) as name:
            directory=Path(name);path=directory/'focus_dataset_manifest.json'
            doc=dict(version=e.VERSION,inputs={},samples=[],configuration=dict(epochs=30,batch=64,lr=.0003,model='mobilenetv4_conv_small'),
                selection={},sampling={},counts={},warmCheckpoint={},runtime={},unmetQualificationBlockers=['unchanged'])
            doc['protocolSHA256']=digest(doc);path.write_text(json.dumps(doc))
            approval=directory/'approval.json'
            ap=dict(version='focus-sampler-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
                    arm='warm-stretch',runName=directory.name,reviewer='test',reviewReference='test')
            approval.write_text(json.dumps(ap))
            with patch.object(e,'assemble',return_value=doc),patch('builtins.print'):
                report,rows=load_protocol(path,'warm-stretch',directory.name,approval)
                self.assertTrue(report['launchEligible']);self.assertFalse(report['executionAuthorized'])
                imported='torch' in sys.modules
                args=['trainer','--experiment-protocol',str(path),'--experiment-approval',str(approval),
                    '--experiment-arm','warm-stretch','--name',directory.name]
                for flags,result in ((['--preflight'],0),(['--execute'],2),(['--dry-run','--epochs','31'],2)):
                    with patch.object(sys,'argv',args+flags):self.assertEqual(main(),result)
                self.assertEqual(imported,'torch' in sys.modules)
                approval.write_text(json.dumps({**ap,'protocolSHA256':'stale'}))
                with self.assertRaisesRegex(ValueError,'stale_sampler_approval'):load_protocol(path,'warm-stretch',directory.name,approval)
            self.assertIn('development_protocol_requires_explicit_experiment_mode',preflight(directory,directory.name)['blockers'])
            with patch.object(e,'assemble',return_value={**doc,'runtime':{'changed':True}}):
                with self.assertRaisesRegex(ValueError,'changed_sampler_protocol_or_runtime'):load_protocol(path,'warm-stretch',directory.name)


if __name__=='__main__':unittest.main()
