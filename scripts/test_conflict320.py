"""Check gradient measurements and the optional authored correction."""
import copy
import unittest
import numpy as np
import torch
import conflict320 as c
import report_authored319 as report
from pathlib import Path
from test_native_adapt152 import Toy


class ConflictTests(unittest.TestCase):
    def test_report_folder(self):
        self.assertEqual(report.report_folder(Path('reports/work')),c.b.ROOT/'reports/work')
        with self.assertRaisesRegex(ValueError,'report_folder'):report.report_folder(c.b.ROOT/'scripts')

    def test_cosine_and_empty_norm(self):
        self.assertAlmostEqual(c.cosine(torch.tensor([1.,0.]),torch.tensor([-1.,0.])),-1.)
        self.assertIsNone(c.cosine(torch.zeros(2),torch.ones(2)))
        with self.assertRaisesRegex(ValueError,'gradient_values'):c.cosine(torch.ones(2),torch.ones(3))

    def test_projection_preserves_original_and_removes_opposition(self):
        first=torch.tensor([1.,2.,3.]);second=torch.tensor([-3.,-2.,1.]);saved=first.clone()
        _,projected,changed=c.b.trainer.project_conflicting_gradients(first,second)
        self.assertTrue(changed);torch.testing.assert_close(first,saved)
        self.assertGreaterEqual(float(torch.dot(first,projected)),-1e-6)
        _,same,changed=c.b.trainer.project_conflicting_gradients(first,first)
        self.assertFalse(changed);torch.testing.assert_close(same,first)

    def test_auxiliary_cap_and_zero_original(self):
        first=torch.tensor([1.,0.]);other=torch.tensor([-10.,100.])
        added,opposes,capped=c.b.trainer.bounded_auxiliary_gradient(first,other)
        self.assertTrue(opposes);self.assertTrue(capped)
        self.assertLessEqual(float(added.norm()),float(first.norm())+1e-6)
        self.assertGreaterEqual(float(torch.dot(first,added)),-1e-6)
        zero,_,capped=c.b.trainer.bounded_auxiliary_gradient(torch.zeros(2),other)
        torch.testing.assert_close(zero,torch.zeros(2));self.assertTrue(capped)
        with self.assertRaisesRegex(ValueError,'projection_inputs'):
            c.b.trainer.bounded_auxiliary_gradient(first,torch.tensor([float('nan'),1.]))

    def test_roles(self):
        with self.assertRaisesRegex(ValueError,'gradient_role'):c.groups([dict(role='test',group='x')],[1])
        self.assertEqual(c.groups([None,dict(role='train',group='x')],[0,1]),
                         {'retained-replay:label-0':[0],'x:label-1':[1]})

    def test_real_detail_projection(self):
        torch.manual_seed(42)
        net=c.r.extend(c.r.s.c.model.extend(c.b.worker.make_model(torch,paired_context=True)),2)
        x=torch.rand(2,6,128,192);detail=c.r.encoded_details(x,2)
        before={k:v.clone() for k,v in net.state_dict().items() if not k.startswith(('change.detail.','change.correction.'))}
        cfg=dict(c.b.trainer.CONFIG,epochs=1,batch=2,detailOnly=True)
        net,h=c.b.trainer.fit(net,x,torch.tensor([0.,1.]),cfg,detail_inputs=detail,
            auxiliary_inputs=1-x,auxiliary_detail=1-detail,auxiliary_weight=.25,auxiliary_projection=True)
        self.assertEqual(h[0]['updates'],1)
        for key,value in before.items():torch.testing.assert_close(value,net.state_dict()[key],rtol=0,atol=0)

    def test_deterministic_projected_fit_and_legacy_path(self):
        torch.manual_seed(9);net=Toy();x=torch.rand(4,6,128,192);y=torch.tensor([0.,1.,0.,1.])
        cfg=dict(c.b.trainer.CONFIG,epochs=2,batch=2)
        args=dict(auxiliary_inputs=1-x,auxiliary_weight=.25)
        first,h=c.b.trainer.fit(copy.deepcopy(net),x,y,cfg,**args,auxiliary_projection=True)
        second,j=c.b.trainer.fit(copy.deepcopy(net),x,y,cfg,**args,auxiliary_projection=True)
        self.assertEqual([v['loss'] for v in h],[v['loss'] for v in j])
        for key,value in first.state_dict().items():torch.testing.assert_close(value,second.state_dict()[key],rtol=0,atol=0)
        for key,value in net.geometry.state_dict().items():torch.testing.assert_close(value,first.geometry.state_dict()[key],rtol=0,atol=0)
        old,_=c.b.trainer.fit(copy.deepcopy(net),x,y,cfg,**args)
        explicit,_=c.b.trainer.fit(copy.deepcopy(net),x,y,cfg,**args,auxiliary_projection=False)
        for key,value in old.state_dict().items():torch.testing.assert_close(value,explicit.state_dict()[key],rtol=0,atol=0)
        self.assertTrue(all(v['updates']==2 for v in h))
        with self.assertRaisesRegex(ValueError,'auxiliary_projection'):
            c.b.trainer.fit(net,x,y,cfg,auxiliary_projection=True)


if __name__=='__main__':unittest.main()
