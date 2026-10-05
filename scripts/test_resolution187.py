import copy
import unittest
from unittest.mock import patch
import resolution187 as g


class Tests(unittest.TestCase):
    def fixture(self):
        c=dict(rows=[dict(id=str(i),split='train') for i in range(432)],initializer={},membership={},metadata={},schedule=g.r.schedule(54,10,.25),args=dict(imgsz=640,box=7.5,batch=8,epochs=10,data='data',name='old',project='old'))
        d=copy.deepcopy(c);d['args'].update(imgsz=1280,name=g.RUN.name,project=str(g.RUN.parent));return d,c

    def test_exact_resolution_treatment(self):
        d,c=self.fixture();g.compatible(d,c)
        for key in ('rows','initializer','membership','metadata','schedule'):
            d,c=self.fixture();d[key]='bad'
            with self.subTest(key=key),self.assertRaises(Exception):g.compatible(d,c)
        for key,value in [('imgsz',960),('box',15),('batch',4),('epochs',20)]:
            d,c=self.fixture();d['args'][key]=value
            with self.subTest(key=key),self.assertRaises(Exception):g.compatible(d,c)
        d,c=self.fixture();d['rows'][0]['split']='test'
        with self.assertRaises(Exception):g.compatible(d,c)

    def test_output_collision(self):
        with patch.object(g,'BASE',g.h.ROOT),patch.object(g.p,'sealed') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):g.prepare()
            read.assert_not_called()

    def test_memory_admission(self):
        for probe in [dict(passed=False,protocol={}),dict(passed=True,protocol={})]:
            with patch.object(g,'verify'),patch.object(g.p,'sealed',return_value=probe),patch.object(g.h,'ref',return_value={'sha':'expected'}):
                with self.assertRaisesRegex(Exception,'memory_preflight'):g.admission()

    def test_export_declares_resolution(self):
        with patch.object(g,'admission'),patch.object(g.r,'ready',return_value='checkpoint'),patch.object(g,'manifests',return_value=[('fit','manifest')]),patch.object(g.e,'export_predictions') as export:
            g.infer();self.assertEqual(export.call_args.kwargs,dict(imgsz=1280,discard_degenerate=True))
        self.assertEqual(g.SETTINGS,dict(g.r.f.d.completed.SETTINGS,imgsz=1280))

    def test_loaded_frozen_checkpoint_gradients(self):
        import torch
        net=torch.nn.Module();net.model=torch.nn.Module();net.model.dfl=torch.nn.Linear(1,1);net.model.conv=torch.nn.Linear(1,1)
        for p in net.parameters():p.requires_grad_(False)
        g.enable_training_gradients(net)
        self.assertFalse(net.model.dfl.weight.requires_grad)
        self.assertTrue(net.model.conv.weight.requires_grad)

    def test_loss_evidence(self):
        import torch
        self.assertEqual(g.loss_evidence({'one2many':torch.tensor([1.,2.])}),{'one2many':[1.,2.]})
        self.assertEqual(g.loss_evidence(torch.tensor([3.])),[3.])


if __name__=='__main__':unittest.main()
