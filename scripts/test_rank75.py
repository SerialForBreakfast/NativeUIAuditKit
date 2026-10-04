import base64
import copy
import io
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from PIL import Image
import focus_candidate_ranker as r
import focus_runtime as runtime


class RankingTests(unittest.TestCase):
    def test_selector_order_ties_missing_and_invalid(self):
        candidates=[dict(id='b',bounds=[0,0,1,1]),dict(id='a',bounds=[1,0,1,1])]
        self.assertEqual(r.choose(candidates,[2,2])['id'],'a')
        self.assertEqual(r.choose(candidates[::-1],[2,2])['id'],'a')
        self.assertEqual(r.choose(candidates,[3,2])['id'],'b')
        self.assertIsNone(r.choose([],[]))
        with self.assertRaises(ValueError):r.choose(candidates,[float('nan'),2])

    def test_loss_multiple_positives(self):
        torch=r.d.torch_runtime();scores=torch.tensor([1.,1.,0.],requires_grad=True)
        one=r.frame_loss(torch,scores,[0]);two=r.frame_loss(torch,scores,[0,1])
        self.assertLess(float(two.detach()),float(one.detach()));two.backward()
        self.assertTrue(torch.isfinite(scores.grad).all())
        with self.assertRaises(ValueError):r.frame_loss(torch,scores,[])

    def test_supervision_rejects_role_and_positive_conflicts(self):
        rows=[dict(id='p',split='train',group='g',images=[dict(sha256='x')]*2,size=[10,10],boxes=[[0,0,5,5]]*2)]
        f=dict(id='x',split='train',size=[10,10],candidates=[dict(id='a',bounds=[0,0,5,5])])
        inputs=dict(frames=[f],pairs=[dict(id='p',split='train',group='g',frames=['x','x'])])
        labels=[dict(pairID='p',endpoint=e,frameID='x',split='train',**r.targets(f['candidates'],[0,0,5,5])) for e in ('before','after')]
        self.assertEqual(r.supervision(inputs,labels,rows),{'x':frozenset(['a'])})
        bad=copy.deepcopy(inputs);bad['frames'][0]['split']='development'
        with self.assertRaises(ValueError):r.supervision(bad,labels,rows)
        bad=copy.deepcopy(rows);bad[0]['boxes'][1]=[5,5,5,5]
        with self.assertRaises(ValueError):r.supervision(inputs,labels,bad)

    def test_shared_batches_and_real_crop_parity(self):
        with tempfile.TemporaryDirectory(dir=r.d.h.ROOT/'.build',prefix='rank75-test-') as td:
            p=Path(td)/'source.png'
            Image.linear_gradient('L').resize((1920,1080)).convert('RGB').save(p)
            item=dict(id='one',path=str(p),sha256=r.d.h.ref(p)['sha256'],bounds=[11.5,21.5,210,60])
            items=[dict(item,id=str(i)) for i in range(129)]
            self.assertEqual([len(b) for b in runtime.bounded_batches(items,shared_images=True)],[128,1])
            self.assertEqual([len(b) for b in runtime.bounded_batches(items)],[16]*8+[1])
            batch=runtime.invoke(items[:59]);single=runtime.invoke([items[0]])
            self.assertEqual([v['id'] for v in batch['results']],[str(i) for i in range(59)])
            raw=base64.b64decode(single['results'][0]['png'])
            self.assertTrue(all(base64.b64decode(v['png'])==raw for v in batch['results']))
            self.assertEqual(Image.open(io.BytesIO(raw)).size,(256,256))
            bad=[item,dict(item,id='two',sha256='0'*64)]
            with self.assertRaises(ValueError):list(runtime.bounded_batches(bad,shared_images=True))
            with self.assertRaises(ValueError):runtime.invoke(bad)
            with self.assertRaises(ValueError):runtime.invoke([item,dict(item,id='two',bounds=[-1,0,10,10])])

    def test_real_bank_and_protocol_reject_changed_evidence(self):
        root=r.d.h.ROOT/'reports/work/RANK-75'
        if not (root/'ready-r2/protocol.json').exists():self.skipTest('retained experimental bank absent')
        with tempfile.TemporaryDirectory(dir=r.d.h.ROOT/'.build',prefix='rank75-contract-') as td:
            td=Path(td);doc=r.d.h.read(root/'ready-r2/protocol.json')
            bad=copy.deepcopy(doc);bad['pins']['dependencies']['torch']='changed'
            bad.pop('protocolSHA256');bad['protocolSHA256']=r.d.h.digest(bad)
            r.d.h.write(td/'protocol.json',bad)
            with self.assertRaisesRegex(ValueError,'code_or_dependencies'):
                r.load_protocol(td/'protocol.json',r.ARM,'rank75-unlaunched')
            manifest=r.d.h.read(root/'ready/bank.json');manifest.pop('seal')
            manifest['encodingDependencies']=r.d.pins()['dependencies']
            tensor=td/'bad.npy';tensor.write_bytes(b'altered')
            manifest['tensor']=dict(path=str(tensor.relative_to(r.d.h.ROOT)),sha256='0'*64)
            r.d.h.write(td/'bank.json',manifest,sealed=True)
            with self.assertRaisesRegex(ValueError,'changed_hash'):r.bank(td/'bank.json')
            manifest.pop('seal');manifest['encodingDependencies']['pillow']='changed'
            r.d.h.write(td/'bad-dependency.json',manifest,sealed=True)
            with self.assertRaisesRegex(ValueError,'encoding_dependencies'):r.bank(td/'bad-dependency.json')
            with self.assertRaises(ValueError):r.d.old.fresh_run('rank75-dtm016')
            with patch.object(r,'pins',return_value={'changed':True}):
                with self.assertRaises(ValueError):r.load_protocol(root/'ready-r2/protocol.json',r.ARM,'rank75-unlaunched')


if __name__=='__main__':unittest.main()
