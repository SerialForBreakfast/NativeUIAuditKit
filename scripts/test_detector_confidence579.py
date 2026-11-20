"""Check the training-only classification support correction."""
import unittest
import torch
from torch.nn import functional as F
from detector_geometry570 import classification_loss,GeometryPreservation
from test_detector_geometry570 import Teacher,base

class ForegroundTests(unittest.TestCase):
    def test_default_is_original_loss(self):
        a=torch.randn(2,3,4);b=torch.randn_like(a)
        old=F.binary_cross_entropy_with_logits(a,b.sigmoid(),reduction='none').sum(dim=1).mean()
        self.assertTrue(torch.equal(classification_loss(a,b),old))
    def test_background_and_empty_images_receive_no_penalty_gradient(self):
        a=torch.zeros(2,2,4,requires_grad=True);b=torch.ones_like(a)
        mask=torch.tensor([[True,False,False,True],[False,False,False,False]])
        classification_loss(a,b,mask).backward()
        self.assertGreater(float(a.grad[0,:,[0,3]].abs().sum()),0)
        self.assertEqual(float(a.grad[0,:,1:3].abs().sum()),0)
        self.assertEqual(float(a.grad[1].abs().sum()),0)
        self.assertEqual(float(classification_loss(a,b,torch.zeros_like(mask)).detach()),0)
        with self.assertRaisesRegex(ValueError,'mask'):classification_loss(a,b,mask.float())
        with self.assertRaisesRegex(ValueError,'nonfinite'):classification_loss(a,torch.full_like(a,float('nan')),mask)
    def test_opt_in_reaches_existing_wrapper_and_preserves_anchor_boundary(self):
        class SpatialTeacher(Teacher):
            def forward(self,x):
                scores=torch.tensor([2.,-10.,-10.,-10.],device=x.device).expand(len(x),2,4)
                return None,dict(scores=scores,boxes=torch.zeros(len(x),8,4,device=x.device))
        wrapper=GeometryPreservation(base,SpatialTeacher(),['/anchor.png'],1.,1.,.25,.25)
        pred=dict(scores=torch.zeros(2,2,4,requires_grad=True),boxes=torch.zeros(2,8,4,requires_grad=True))
        batch=dict(im_file=['/anchor.png','/native.png'],img=torch.zeros(2,3,4,4))
        loss,_=wrapper(pred,batch);loss.sum().backward()
        self.assertGreater(float(pred['scores'].grad[0,:,0].abs().sum()),0)
        self.assertEqual(float(pred['scores'].grad[0,:,1:].abs().sum()),0)
        self.assertEqual(float(pred['scores'].grad[1].abs().sum()),0)
        self.assertEqual(wrapper.classification_foreground_positions,1)
        self.assertEqual(wrapper.classification_total_positions,4);wrapper.verify()
    def test_config_cannot_smuggle_unsupported_threshold(self):
        from unittest.mock import patch
        from detector_preservation551 import validate
        for value in [True,0,1.1,float('nan')]:
            with self.assertRaisesRegex(ValueError,'classification_preservation_confidence'):
                validate(dict(model={},anchors={},weight=1,geometryWeight=1,classificationConfidence=value),{})
        with self.assertRaisesRegex(ValueError,'classification_preservation_confidence'):
            validate(dict(model={},anchors={},weight=1,classificationConfidence=.25),{})

if __name__=='__main__':unittest.main()
