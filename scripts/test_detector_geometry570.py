import copy
import unittest
import torch
from torch import nn
from detector_geometry570 import GeometryPreservation,distribution_loss

class Teacher(nn.Module):
    def __init__(self):super().__init__();self.weight=nn.Parameter(torch.tensor(.3))
    def forward(self,x):return None,dict(scores=self.weight.expand(len(x),2,4),boxes=torch.zeros(len(x),8,4))

def base(pred,batch):
    z=pred['boxes'].sum()*0+pred['scores'].sum()*0
    return torch.stack([z+1,z+2,z+3]),dict(box_loss=z.detach()+1,cls_loss=z.detach()+2,dfl_loss=z.detach()+3)

class GeometryTests(unittest.TestCase):
    def test_anchor_only_gradients_teacher_and_original_loss(self):
        wrapper=GeometryPreservation(base,Teacher(),['/anchor.png'],1.,1.)
        boxes=torch.zeros(2,8,4);boxes[:,0]=1.;boxes.requires_grad_()
        scores=torch.full((2,2,4),.3,requires_grad=True)
        batch=dict(im_file=['/anchor.png','/native.png'],img=torch.zeros(2,3,4,4))
        loss,items=wrapper(dict(boxes=boxes,scores=scores),batch)
        self.assertEqual(float(loss[0].detach()),1.);self.assertGreater(float(loss[2].detach()),3.)
        loss.sum().backward();self.assertGreater(float(boxes.grad[0].abs().sum()),0.)
        self.assertEqual(float(boxes.grad[1].abs().sum()),0.);wrapper.verify();self.assertIsNone(wrapper.teacher.weight.grad)

    def test_non_anchor_and_distribution_identity(self):
        boxes=torch.zeros(1,8,4,requires_grad=True);scores=torch.zeros(1,2,4,requires_grad=True)
        batch=dict(im_file=['/native.png'],img=torch.zeros(1,3,4,4));pred=dict(boxes=boxes,scores=scores)
        wrapper=GeometryPreservation(base,Teacher(),['/anchor.png'],1.,1.)
        self.assertTrue(torch.equal(wrapper(pred,batch)[0],base(pred,batch)[0]))
        self.assertEqual(float(distribution_loss(boxes,boxes).detach()),0.)
        with self.assertRaisesRegex(ValueError,'shape'):distribution_loss(torch.zeros(1,4,2),torch.zeros(1,4,2))

    def test_resident_yolo_loss_and_gradients(self):
        from ultralytics.nn.tasks import DetectionModel
        from ultralytics.cfg import get_cfg
        torch.set_num_threads(2)
        with torch.random.fork_rng():
            torch.manual_seed(570);model=DetectionModel('yolo11n.yaml',nc=2,verbose=False)
        model.args=get_cfg();model.train();teacher=copy.deepcopy(model).eval()
        images=torch.rand(2,3,64,64)
        batch=dict(img=images,im_file=['/anchor.png','/native.png'],batch_idx=torch.tensor([0.,1.]),cls=torch.tensor([[0.],[1.]]),bboxes=torch.tensor([[.5,.5,.3,.3],[.5,.5,.2,.2]]))
        wrapper=GeometryPreservation(model.init_criterion(),teacher,['/anchor.png'],1.,1.)
        loss,items=wrapper(model(images),batch);self.assertTrue(torch.isfinite(loss).all());loss.sum().backward()
        self.assertTrue(all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None))
        wrapper.verify();self.assertEqual(wrapper.anchor_images,1);self.assertGreater(wrapper.geometry_loss_sum,0.)

    def test_mps_execution_when_available(self):
        if not torch.backends.mps.is_available():self.skipTest('MPS is unavailable')
        teacher=Teacher().to('mps');wrapper=GeometryPreservation(base,teacher,['/anchor.png'],1.,1.)
        boxes=torch.randn(2,8,4,device='mps',requires_grad=True);scores=torch.zeros(2,2,4,device='mps',requires_grad=True)
        batch=dict(im_file=['/anchor.png','/native.png'],img=torch.zeros(2,3,4,4,device='mps'))
        # This teacher returns CPU boxes; copy both outputs to the observed image device.
        original=teacher.forward
        def forward(x):
            value=original(x)[1];return None,{k:v.to(x.device) for k,v in value.items()}
        teacher.forward=forward
        loss,items=wrapper(dict(boxes=boxes,scores=scores),batch);loss.sum().backward()
        self.assertTrue(torch.isfinite(boxes.grad).all());wrapper.verify()
