import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import focus_fit_diagnostic as e


class FitTests(unittest.TestCase):
    def rows(self):
        return [dict(id=str(i),label=i%2,split='train',use='train-candidate',
                     crop=dict(pixelSHA256=str(i))) for i in range(48)]

    def test_balanced_admitted_membership(self):
        rows=self.rows();e.validate_subset(rows,rows)
        for mode in ('missing','duplicate','unbalanced','role','pixels','overlap'):
            changed=copy.deepcopy(rows);base=copy.deepcopy(rows)
            if mode=='missing':changed.pop()
            if mode=='duplicate':changed[-1]=changed[0]
            if mode=='unbalanced':changed[0]['label']=1
            if mode=='role':changed[0]['split']='validation'
            if mode=='pixels':changed[0]['crop']['pixelSHA256']='1';base=changed
            if mode=='overlap':base.append(dict(id='dev',label=0,split='validation',crop=dict(pixelSHA256='0')))
            with self.subTest(mode=mode),self.assertRaises(ValueError):e.validate_subset(changed,base)

    def test_fit_criterion_has_no_development_dependency(self):
        rows=self.rows();pred=[dict(id=r['id'],label=r['label'],probability=.99 if r['label'] else .01) for r in rows]
        self.assertTrue(e.fit_metrics(pred,rows,.011)['fitPass'])
        self.assertFalse(e.fit_metrics(pred,rows,.1)['fitPass'])
        pred[1]['probability']=.8
        m=e.fit_metrics(pred,rows,.04);self.assertFalse(m['fitPass']);self.assertEqual(m['classificationCorrect'],48)
        for q in (True,float('nan'),-1,2):
            pred[1]['probability']=q
            with self.assertRaises(ValueError):e.fit_metrics(pred,rows,.01)
        with self.assertRaises(ValueError):e.fit_metrics(pred[:-1],rows,.01)

    def test_actual_dispatch_preflight_and_approval(self):
        from focus_learning_experiment import load_protocol
        from train_focus_ring_detector import main
        import sys
        root=e.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            path=Path(directory)/'protocol.json'
            doc=dict(version=e.VERSION,inputs={},samples=[],configuration=e.CONFIG,selection={},representation={},
                warmCheckpoint=None,runtime={},counts={},fitDiagnostic={},unmetQualificationBlockers=[])
            doc['protocolSHA256']=e.digest(doc);path.write_text(json.dumps(doc))
            approval=dict(version='focus-fit-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
                authority='Maintainer approved small balanced learning diagnostic, 2026-09-30',
                arm='fit-diagnostic',runName='fdr019-balanced-fit',scope='one-diagnostic-no-export-no-promotion')
            ap=Path(directory)/'approval.json';ap.write_text(json.dumps(approval))
            with patch.object(e,'assemble',return_value=doc),patch.object(e,'ROOT',Path(directory)):
                self.assertTrue(load_protocol(path,'fit-diagnostic','fdr019-balanced-fit',ap)[0]['launchEligible'])
                self.assertFalse(load_protocol(path,'fit-diagnostic','fdr019-balanced-fit')[0]['launchEligible'])
                args=['trainer','--experiment-protocol',str(path),'--experiment-approval',str(ap),
                      '--experiment-arm','fit-diagnostic','--name','fdr019-balanced-fit','--preflight']
                with patch.object(sys,'argv',args),patch('builtins.print'):self.assertEqual(main(),0)
                with patch.object(sys,'argv',args+['--lr','.1']),patch('builtins.print'):self.assertEqual(main(),2)
                approval['scope']='promotion';ap.write_text(json.dumps(approval))
                with self.assertRaises(ValueError):load_protocol(path,'fit-diagnostic','fdr019-balanced-fit',ap)

    def test_deterministic_stratified_selection(self):
        native=[];mapping={};human=[]
        for lane in ('buttons','tabs','artwork','rows'):
            for j in range(5):
                for label in (0,1):
                    sid=f'{lane}-{j}-{label}'
                    native.append(dict(id=sid,label=label,split='train',use='train-candidate',sourceID=lane,
                        pairID=str(j),control=lane,relatedGroup=lane,proposedRole='train-candidate',crop=dict(pixelSHA256=sid)))
                    mapping[sid]=dict(stratum=lane)
        for f in range(8):
            for label in (0,1):
                sid=f'h{f}-{label}';human.append(dict(id=sid,label=label,split='train',use='human-static-auxiliary',
                    frameID=str(f),pixelSHA256=sid,crop=dict(pixelSHA256=sid)))
        base=dict(inputs={'assembly':{}},samples=native+human,sampling={'weights':{r['id']:1/40 for r in native}})
        with patch.object(e.static,'sealed',return_value=dict(trainingAppearance=mapping)):
            first=e.select(base);self.assertEqual(first,e.select(base));self.assertEqual(len(first),48)
            self.assertEqual(sum(r['use']=='human-static-auxiliary' for r in first),16)
            base['samples'].pop()
            with self.assertRaises(ValueError):e.select(base)


if __name__=='__main__':unittest.main()
