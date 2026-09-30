import copy
import hashlib
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import focus_paired_experiment as p


class PairTests(unittest.TestCase):
    def test_cli_dispatch_approval_and_ordinary_admission(self):
        from focus_learning_experiment import load_protocol
        from focus_training_preflight import preflight
        parent=p.ROOT/'.build/debug-output/paired-tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            root=Path(temp);crop=root/'crop';crop.write_bytes(b'unit')
            doc=dict(version=p.VERSION,inputs={},samples=[dict(id='a',crop=p.a.reference(crop))],
                configuration={},selection={},sampling=dict(weights={'a':1}),counts={},warmCheckpoint=None,
                runtime={},unmetQualificationBlockers=[],representation={},pairedTraining={})
            doc['protocolSHA256']=p.digest(doc)
            path=root/'focus_dataset_manifest.json';path.write_text(json.dumps(doc))
            approval=root/'approval.json';value=dict(version='focus-paired-approval-v1',approved=True,
                protocolSHA256=doc['protocolSHA256'],arm='paired-stretch',runName='paired-unit',
                reviewer='test',reviewReference='unit')
            approval.write_text(json.dumps(value))
            with patch.object(p,'assemble',return_value=doc):
                self.assertTrue(load_protocol(path,'paired-stretch','paired-unit',approval)[0]['launchEligible'])
                self.assertFalse(load_protocol(path,'paired-stretch','paired-unit')[0]['launchEligible'])
                with self.assertRaises(ValueError):load_protocol(path,'warm-stretch','paired-unit',approval)
                value['protocolSHA256']='changed';approval.write_text(json.dumps(value))
                with self.assertRaises(ValueError):load_protocol(path,'paired-stretch','paired-unit',approval)
            with patch.object(p,'assemble',return_value={**doc,'runtime':{'changed':True}}):
                with self.assertRaises(ValueError):load_protocol(path,'paired-stretch','paired-unit',approval)
            self.assertFalse(preflight(root,'ordinary-paired',30,64,.0003,'mobilenetv4_conv_small')['launchEligible'])

    def rows(self):
        return [dict(id=str(i),sourceID='s',pairID='p',label=i,split='train',control='button',
                     proposedRole='train-candidate',relatedGroup='g') for i in (0,1)]

    def test_pair_order_mass_and_rejections(self):
        rows=self.rows(); weights={'0':.5,'1':.5}
        pair=p.pairs(rows,weights)[0]
        self.assertEqual(pair['indices'],[1,0]);self.assertEqual(pair['weight'],1)
        for broken in (rows[:1],rows+rows, [{**rows[0],'split':'validation'},rows[1]],
                       [rows[0],{**rows[1],'control':'other'}]):
            with self.assertRaises(ValueError):p.pairs(broken,weights)
        with self.assertRaises(ValueError):p.pairs(rows,{'0':.2,'1':.8})

    def test_loss_direction_and_head_update(self):
        import torch
        labels=torch.tensor([[[1.],[0.]]])
        good=torch.tensor([[[2.],[-2.]]]);bad=-good
        self.assertLess(p.paired_loss(good,labels),p.paired_loss(bad,labels))
        with self.assertRaises(ValueError):p.paired_loss(good,1-labels)
        torch.manual_seed(42);head=torch.nn.Linear(576,1)
        before=head.weight.detach().clone();features=torch.randn(3,2,576)
        loss=p.paired_loss(head(features),labels.repeat(3,1,1));loss.backward()
        opt=torch.optim.AdamW(head.parameters(),lr=.0003);opt.step()
        self.assertFalse(torch.equal(before,head.weight));self.assertFalse(features.requires_grad)

    def test_cache_order_corruption_and_counts(self):
        import torch
        rows=self.rows();x=torch.randn(2,576);y=torch.tensor([[0.],[1.]])
        h=hashlib.sha256(x.numpy().tobytes()).hexdigest()
        receipt=dict(trainCount=2,validationCount=2,trainFeatureSHA256=h,validationFeatureSHA256=h)
        cache=dict(train=(x,y),validation=(x,y),receipt=receipt)
        p.validate_tensors(cache,receipt,rows,rows)
        with self.assertRaises(ValueError):p.validate_tensors(cache,receipt,rows[::-1],rows)
        bad=copy.deepcopy(cache);bad['train'][0][0,0]=float('nan')
        with self.assertRaises(ValueError):p.validate_tensors(bad,receipt,rows,rows)
        bad=copy.deepcopy(cache);bad['train'][0][0,0]+=1
        with self.assertRaises(ValueError):p.validate_tensors(bad,receipt,rows,rows)
        with self.assertRaises(ValueError):p.validate_tensors(cache,{**receipt,'trainCount':3},rows,rows)


if __name__=='__main__':unittest.main()
