"""Generated fixtures only; no dependency on retained reports or model weights."""
import copy
import json
import math
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import focus_human_static_experiment as e


class StaticTests(unittest.TestCase):
    def data(self):
        frames = [dict(id=f'f{i}',sessionID=e.SESSION if i<8 else 'dev',
                       family='train' if i<8 else 'dev',pixelSHA256=f'frame{i}') for i in range(40)]
        rows = []; controls = []
        for i in range(453):
            f = i % 8 if i<138 else 8+i%32
            r = dict(id=str(i),frameID=f'f{f}',crop={'path':f'{i}.png','sha256':str(i)},
                bounds=[0,0,20,20],state='focused' if i<8 else 'unfocused',label=int(i<8),
                use='representative-selection',pixelSHA256=f'crop{i}')
            rows.append(r)
            controls.append({**r,'proposalEligible':True,'priorUse':'representative-selection'})
        excluded = [dict(id=f'x{i}',proposalEligible=False) for i in range(64)]
        return dict(samples=rows,excludedSelection=excluded),dict(frames=frames,controls=controls+excluded),dict(groups=e.components(frames))

    def test_whole_session_and_labels(self):
        a,i,p = self.data(); human,dev,frames=e.partition(a,i,p)
        self.assertEqual((len(human),len(dev),len(frames)),(138,315,8))
        self.assertFalse(set(r['id'] for r in human)&set(r['id'] for r in dev))
        for mutation in ('label','member','exclude','connected','session'):
            aa,ii,pp=copy.deepcopy((a,i,p))
            if mutation=='label':aa['samples'][0]['label']=0
            if mutation=='member':aa['samples'].pop()
            if mutation=='exclude':aa['excludedSelection'].pop()
            if mutation=='connected':ii['frames'][8]['family']='train'
            if mutation=='session':ii['frames'][0]['sessionID']='dev'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):e.partition(aa,ii,pp)

    def test_protected_and_development_overlap_rejected(self):
        a,i,p=self.data();human,dev,frames=e.partition(a,i,p)
        a.update(protectedMetadata={},reservedPixels={})
        with patch.object(e,'read_ref',return_value={'pixelSHA256':'crop0'}),patch.object(e,'sealed',return_value={'samples':[]}):
            with self.assertRaisesRegex(ValueError,'leakage'):e.leakage(a,i,human,dev,frames)
        with patch.object(e,'read_ref',return_value={}),patch.object(e,'sealed',return_value={'samples':[]}):
            reservation=e.leakage(a,i,human,dev,frames)
            self.assertEqual(len(reservation['excludedIDs']),64)
            dev[0]['pixelSHA256']='crop0'
            with self.assertRaisesRegex(ValueError,'leakage'):e.leakage(a,i,human,dev,frames)

    def schedule(self):
        human=[dict(id=f'h{i}',frameID=f'f{i%8}') for i in range(138)]
        pairs=[dict(weight=1/395,indices=[2*i,2*i+1]) for i in range(395)]
        train=[dict(id=str(i)) for i in range(790)];weights={r['id']:1/790 for r in train}
        return e.schedules(pairs,human,train,weights),human,pairs

    def test_matching_compute_frame_mass_and_presentations(self):
        schedule,human,_=self.schedule()
        self.assertEqual(schedule,self.schedule()[0]);self.assertEqual(len(schedule),30)
        for steps in schedule:
            self.assertEqual(len(steps),13)
            self.assertEqual(sum(len(s['pairs']) for s in steps),395)
            self.assertEqual(sorted(j for s in steps for j in s['human']),list(range(138)))
            self.assertEqual(sum(len(s['baseline']) for s in steps),138)
            mass={f'f{i}':0 for i in range(8)}
            for s in steps:
                self.assertEqual(len(s['baseline']),len(s['human']))
                for j,w in zip(s['human'],s['auxiliaryWeights']):mass[human[j]['frameID']]+=w
            for value in mass.values():self.assertAlmostEqual(value,1/8)
            self.assertAlmostEqual(sum(.8*len(s['pairs'])/395 for s in steps),.8)
            self.assertAlmostEqual(sum(.2*sum(s['auxiliaryWeights']) for s in steps),.2)

    def test_real_head_update_and_no_pairing_of_human_labels(self):
        import torch
        schedule,human,pairs=self.schedule()
        torch.manual_seed(42);x=torch.randn(928,576)
        y=torch.tensor([[1.],[0.]]*395+[[0.]]*138)
        data=torch.utils.data.TensorDataset(x,y)
        results=[]
        for arm in ('static-baseline','static-human'):
            torch.manual_seed(42);model=torch.nn.Linear(576,1);before=model.weight.detach().clone()
            opt=torch.optim.AdamW(model.parameters(),lr=.0003)
            report=dict(arm=arm,staticHuman=dict(schedule=schedule,pairs=pairs,nativeCount=790))
            value=e.train_epoch(model,data,report,1,'cpu',opt,time.monotonic()+60)
            self.assertTrue(math.isfinite(value));self.assertFalse(torch.equal(before,model.weight))
            results.append(model.weight.detach().clone())
            with self.assertRaisesRegex(ValueError,'deadline'):e.train_epoch(model,data,report,1,'cpu',opt,0)
        self.assertFalse(torch.equal(*results));self.assertFalse(x.requires_grad)

    def test_cli_dispatch_stale_approval_and_hashes(self):
        from focus_learning_experiment import load_protocol
        from focus_training_preflight import preflight
        parent=e.ROOT/'.build/debug-output';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            root=Path(temp);image=root/'crop';image.write_bytes(b'unit')
            doc=dict(version=e.VERSION,inputs={},samples=[dict(id='x',crop=e.a.reference(image))],
                configuration={},selection={},sampling={'weights':{}},counts={},warmCheckpoint=None,
                runtime={},unmetQualificationBlockers=[],representation={},staticHuman={},reservation={})
            doc['protocolSHA256']=e.digest(doc);path=root/'focus_dataset_manifest.json';path.write_text(json.dumps(doc))
            approval=dict(version='focus-human-static-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
                arm='static-human',runName='static-unit',authority='Maintainer: Lets try that experiment. 2026-09-30',
                reservationSHA256=e.digest({}),scope='two-arms-no-export-no-promotion')
            ap=root/'approval.json';ap.write_text(json.dumps(approval))
            with patch.object(e,'assemble',return_value=doc):
                self.assertTrue(load_protocol(path,'static-human','static-unit',ap)[0]['launchEligible'])
                self.assertFalse(load_protocol(path,'static-human','static-unit')[0]['launchEligible'])
                with self.assertRaises(ValueError):load_protocol(path,'paired-stretch','static-unit',ap)
                approval['reservationSHA256']='changed';ap.write_text(json.dumps(approval))
                with self.assertRaisesRegex(ValueError,'stale'):load_protocol(path,'static-human','static-unit',ap)
            ref=e.a.reference(path);path.write_text('{}')
            with self.assertRaises(ValueError):e.sealed(ref,'protocolSHA256')
            path.write_text(json.dumps(doc))
            self.assertFalse(preflight(root,'ordinary-static')['launchEligible'])

    def test_fourteen_frame_guard_is_explicit_legacy_default_unchanged(self):
        from test_focus_representative_experiment import SelectionTests
        test=SelectionTests();test.setUp()
        self.assertTrue(test.metric()['checkpointEligible'])
        test.selection['expectedCompleteFrames']=14
        self.assertFalse(test.metric()['checks']['completeFrames'])


if __name__=='__main__':unittest.main()
