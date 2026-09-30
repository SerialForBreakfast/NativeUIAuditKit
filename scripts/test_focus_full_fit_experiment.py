import copy
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import focus_full_fit_experiment as e


class FullFitTests(unittest.TestCase):
    def base(self):
        native = [dict(id=f'n{i}', label=i%2, split='train', use='train-candidate',
                       crop=dict(pixelSHA256=f'n{i}')) for i in range(790)]
        human = []
        for frame in range(8):
            count = 18 if frame < 2 else 17
            for i in range(count):
                sid = f'h{frame}-{i}'
                human.append(dict(id=sid, label=int(i == 0), split='train', use='human-static-auxiliary',
                                  frameID=str(frame), pixelSHA256=sid, crop=dict(pixelSHA256=sid)))
        return dict(samples=native+human, sampling=dict(weights={r['id']:1/790 for r in native}))

    def test_weight_mass_and_duplicate_pixels(self):
        base = self.base(); rows, weights = e.training_weights(base)
        self.assertEqual(len(rows), 928); self.assertAlmostEqual(sum(weights.values()), 1)
        for label in (0, 1):
            self.assertAlmostEqual(sum(weights[r['id']] for r in rows if r['label'] == label), .5)
        human = base['samples'][790:]
        human[2]['pixelSHA256'] = human[1]['pixelSHA256']
        _, weights = e.training_weights(base)
        self.assertAlmostEqual(weights[human[1]['id']], weights[human[2]['id']])
        self.assertAlmostEqual(weights[human[1]['id']]*2, weights[human[3]['id']])

    def test_invalid_membership_and_leakage(self):
        for mode in ('missing', 'duplicate', 'conflict', 'overlap', 'pair', 'missinglabel', 'weights'):
            base = self.base(); rows = base['samples']
            if mode == 'missing': rows.pop()
            if mode == 'duplicate': rows[-1]['id'] = rows[-2]['id']
            if mode == 'conflict': rows[1]['crop']['pixelSHA256'] = 'n0'
            if mode == 'overlap': rows.append(dict(split='validation',use='representative-selection',crop=dict(pixelSHA256='n0')))
            if mode == 'pair': rows[-1]['pairID'] = 'fake'
            if mode == 'missinglabel': rows[790]['label'] = 0
            if mode == 'weights': base['sampling']['weights']['n0'] = float('nan')
            with self.subTest(mode=mode), self.assertRaises(ValueError): e.training_weights(base)

    def test_metrics_stop_and_invalid_scores(self):
        rows, weights = e.training_weights(self.base())
        ps = [dict(id=r['id'],label=r['label'],probability=.99 if r['label'] else .01) for r in rows]
        result = e.training_metrics(ps, rows, weights)
        self.assertTrue(result['fitPass']); self.assertEqual(result['groups']['human:1']['n'], 8)
        self.assertEqual(result['groups']['overall']['confidentCorrect'],928)
        self.assertAlmostEqual(result['groups']['overall']['weightedBCE'], -.0+0.01005033585350145)
        streak = 0
        for i in range(1,6):
            streak,done,observe=e.schedule(i,True,streak)
            self.assertEqual(done,i==5); self.assertEqual(observe,i==5)
        self.assertEqual(e.schedule(25,False,4),(0,False,True))
        self.assertEqual(e.schedule(1000,False,0),(0,True,True))
        for q in (float('nan'),float('inf'),True,-1,2):
            changed=copy.deepcopy(ps); changed[0]['probability']=q
            with self.assertRaises(ValueError):e.training_metrics(changed,rows,weights)
        with self.assertRaises(ValueError):e.training_metrics(ps[:-1],rows,weights)
        changed=copy.deepcopy(ps); changed[0]['id']='wrong'
        with self.assertRaises(ValueError):e.training_metrics(changed,rows,weights)

    def test_actual_trainer_dispatch_and_approval(self):
        import sys
        from focus_learning_experiment import load_protocol
        from train_focus_ring_detector import main
        root=e.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            doc=dict(version=e.VERSION, inputs={}, samples=[], configuration=e.CONFIG, selection={}, representation={},
                     warmCheckpoint=None,runtime={},counts={},fullFit={},unmetQualificationBlockers=[])
            doc['protocolSHA256']=e.digest(doc)
            path=Path(directory)/'protocol.json';path.write_text(json.dumps(doc))
            ap=Path(directory)/'approval.json';ap.write_text(json.dumps(e.approval(doc)))
            with patch.object(e,'assemble',return_value=doc),patch.object(e,'ROOT',Path(directory)):
                self.assertFalse(load_protocol(path,e.ARM,e.RUN)[0]['launchEligible'])
                self.assertTrue(load_protocol(path,e.ARM,e.RUN,ap)[0]['launchEligible'])
                args=['trainer','--experiment-protocol',str(path),'--experiment-approval',str(ap),
                      '--experiment-arm',e.ARM,'--name',e.RUN,'--preflight']
                with patch.object(sys,'argv',args),patch('builtins.print'):self.assertEqual(main(),0)
                with patch.object(sys,'argv',args+['--batch','64']),patch('builtins.print'):self.assertEqual(main(),2)
                with self.assertRaises(ValueError):load_protocol(path,e.ARM,'wrong',ap)
                changed=e.approval(doc);changed['protocolSHA256']='stale';ap.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):load_protocol(path,e.ARM,e.RUN,ap)
                path.write_text(json.dumps({**doc,'counts':{'changed':1}}))
                with self.assertRaises(ValueError):load_protocol(path,e.ARM,e.RUN,ap)

    def test_actual_loop_no_eligible_and_earliest_tie(self):
        import torch
        root=e.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        rows=[dict(id=str(i),label=i%2,split='train',use='train-candidate' if i<2 else 'human-static-auxiliary') for i in range(4)]
        data=torch.utils.data.TensorDataset(torch.tensor([[0.],[1.],[0.],[1.]]),torch.tensor([[0.],[1.],[0.],[1.]]))
        val=[{**r,'split':'validation'} for r in rows]
        real_require=e.require
        def test_device_check(ok,reason):
            if reason!='full_fit_requires_mps':real_require(ok,reason)
        for eligible in (False,True):
            with self.subTest(eligible=eligible),tempfile.TemporaryDirectory(dir=root) as directory:
                out=Path(directory);(out/'weights').mkdir();torch.manual_seed(42)
                model=torch.nn.Linear(1,1)
                report=dict(fullFit=dict(weights={r['id']:.25 for r in rows},weightDecay=.01),
                    configuration={**e.CONFIG,'epochs':26},representation={},selection={},protocolSHA256='test')
                score=dict(checkpointEligible=eligible,selectionLoss=.1)
                start=time.monotonic()
                with patch.object(e,'require',side_effect=test_device_check),patch.object(e.s.rep,'selection_metrics',return_value=score):
                    self.assertEqual(e.run(model,data,data,report,rows,val,torch.device('cpu'),out,start,start+30,'test'),0)
                result=json.loads((out/'experiment-result.json').read_text())
                self.assertEqual(result['selectedUpdate'],25 if eligible else None)
                self.assertEqual((out/'weights/best.pt').exists(),eligible)
                self.assertEqual(len((out/'training-observations.jsonl').read_text().splitlines()),27)
                self.assertEqual([r['update'] for r in result['history'] if r['validation'] is not None],[25,26])
                self.assertEqual(result['stopReason'],'update_cap')


if __name__=='__main__':unittest.main()
