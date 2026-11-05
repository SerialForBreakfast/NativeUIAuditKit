"""Verify preservation against resident detector loss, without training a candidate."""
import copy
import tempfile
import unittest
from pathlib import Path
import torch
from torch import nn
import research_queue as q
from experiment_templates import pin
from detector_preservation551 import ClassificationPreservation, validate


class Teacher(nn.Module):
    def __init__(self):
        super().__init__(); self.weight = nn.Parameter(torch.tensor(0.3))
    def forward(self, x):
        return None, {'scores': self.weight.expand(len(x), 2, 4)}


def base(pred, batch):
    logits=pred['scores']; zero=logits.sum()*0
    return torch.stack([zero+1,zero+2,zero+3]), {'box_loss':zero.detach()+1,'cls_loss':zero.detach()+2,'dfl_loss':zero.detach()+3}


class PreservationTests(unittest.TestCase):
    def test_anchor_only_and_unchanged_localization(self):
        teacher=Teacher(); w=ClassificationPreservation(base,teacher,['/anchor.png'],1.0)
        logits=torch.zeros(2,2,4,requires_grad=True)
        batch={'im_file':['/anchor.png','/native.png'],'img':torch.zeros(2,3,4,4)}
        loss,items=w({'scores':logits},batch)
        self.assertEqual(float(loss[0].detach()),1);self.assertEqual(float(loss[2].detach()),3)
        loss.sum().backward();self.assertGreater(float(logits.grad[0].abs().sum()),0)
        self.assertEqual(float(logits.grad[1].abs().sum()),0);w.verify()
        self.assertEqual(w.anchor_images,1);self.assertIsNone(teacher.weight.grad)

    def test_non_anchor_is_exact_original_loss(self):
        w=ClassificationPreservation(base,Teacher(),['/anchor.png'],1)
        p={'scores':torch.zeros(1,2,4,requires_grad=True)};b={'im_file':['/native.png'],'img':torch.zeros(1,3,4,4)}
        original=base(p,b);actual=w(p,b)
        self.assertTrue(torch.equal(original[0],actual[0]));self.assertEqual(w.calls,0)

    def test_changed_teacher_rejected(self):
        w=ClassificationPreservation(base,Teacher(),['/anchor.png'],1)
        with torch.no_grad():w.teacher.weight.add_(1)
        with self.assertRaisesRegex(ValueError,'teacher_changed'):w.verify()

    def test_roles_and_changed_membership_rejected(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder);model=root/'model';model.write_bytes(b'model');image=root/'image';image.write_bytes(b'image')
            row=dict(id='a',role='train',trainingEligible=True,labelsComplete=True,image=pin(image))
            path=root/'anchors.json';q.save(path,dict(version='detector-preservation-anchors-v1',rows=[row]))
            cfg=dict(model=pin(model),anchors=pin(path),weight=1.0)
            validate(cfg,dict(rows=[row]))
            for change in ({'role':'evaluation'},{'trainingEligible':False},{'labelsComplete':False}):
                bad=dict(row,**change)
                with self.assertRaisesRegex(ValueError,'training_only'):validate(cfg,dict(rows=[bad]))
            for weight in (0,float('nan'),True):
                with self.assertRaisesRegex(ValueError,'weight'):validate(dict(cfg,weight=weight),dict(rows=[row]))

    def test_resident_yolo_loss_and_second_configuration(self):
        from ultralytics.nn.tasks import DetectionModel
        from ultralytics.cfg import get_cfg
        torch.set_num_threads(2)
        with torch.random.fork_rng():
            torch.manual_seed(551)
            model=DetectionModel('yolo11n.yaml',nc=2,verbose=False)
        model.args=get_cfg();model.train()
        teacher=copy.deepcopy(model).eval()
        images=torch.rand(2,3,64,64)
        batch=dict(img=images,im_file=['/anchor.png','/native.png'],batch_idx=torch.tensor([0.,1.]),
                   cls=torch.tensor([[0.],[1.]]),bboxes=torch.tensor([[.5,.5,.3,.3],[.5,.5,.2,.2]]))
        for weight in (1.0,0.5):
            wrapper=ClassificationPreservation(model.init_criterion(),copy.deepcopy(teacher),['/anchor.png'],weight)
            model.zero_grad(set_to_none=True)
            loss,items=wrapper(model(images),batch)
            self.assertTrue(torch.isfinite(loss).all());loss.sum().backward()
            self.assertTrue(all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None))
            wrapper.verify();self.assertEqual(wrapper.anchor_images,1)

    def test_callback_lifecycle_preserves_rng_and_checkpoint(self):
        self.exercise_callback(False)

    def test_geometry_callback_lifecycle_preserves_rng_and_checkpoint(self):
        self.exercise_callback(True)

    def exercise_callback(self, geometry):
        from types import SimpleNamespace
        from unittest.mock import patch
        from ultralytics.nn.tasks import DetectionModel
        from ultralytics.cfg import get_cfg
        from ultralytics.utils.torch_utils import ModelEMA
        from detector_preservation551 import attach
        torch.set_num_threads(2)
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            root=Path(folder); image=root/'anchor.png';image.write_bytes(b'contract')
            modelpath=root/'teacher.pt';modelpath.write_bytes(b'loader mocked below')
            row=dict(id='anchor',image=pin(image),role='train',trainingEligible=True,labelsComplete=True)
            anchors=root/'anchors.json';q.save(anchors,dict(version='detector-preservation-anchors-v1',rows=[row]))
            prepared=root/'images/train';prepared.mkdir(parents=True);(prepared/'anchor.png').write_bytes(b'contract')
            student=DetectionModel('yolo11n.yaml',nc=2,verbose=False);student.args=get_cfg();student.names={0:'a',1:'b'}
            teacher=copy.deepcopy(student);ema=ModelEMA(student)
            callbacks={};host=SimpleNamespace(add_callback=lambda name,fn:callbacks.update({name:fn}))
            config=dict(model=pin(modelpath),anchors=pin(anchors),weight=1.0)
            if geometry:config['geometryWeight']=1.0
            attach(host,config,dict(rows=[row],names=['a','b']),root/'dataset.yaml',root)
            trainer=SimpleNamespace(model=student,device=torch.device('cpu'))
            rng=torch.random.get_rng_state().clone()
            def loader(path):
                torch.rand(3)
                return SimpleNamespace(model=teacher)
            with patch('ultralytics.YOLO',side_effect=loader):callbacks['on_pretrain_routine_end'](trainer)
            self.assertTrue(torch.equal(rng,torch.random.get_rng_state()))
            student.train();imgs=torch.rand(2,3,64,64)
            batch=dict(img=imgs,im_file=[str(prepared/'anchor.png'),str(root/'native.png')],batch_idx=torch.tensor([0.,1.]),cls=torch.tensor([[0.],[1.]]),bboxes=torch.tensor([[.5,.5,.3,.3],[.5,.5,.2,.2]]))
            student.criterion(student(imgs),batch)[0].sum().backward()
            ema.update(student)
            checkpoint=root/'ema.pt';torch.save({'ema':copy.deepcopy(ema.ema)},checkpoint)
            loaded=torch.load(checkpoint,weights_only=False)['ema']
            self.assertFalse(isinstance(getattr(loaded,'criterion',None),ClassificationPreservation))
            callbacks['on_train_end'](trainer)
            self.assertFalse(isinstance(student.criterion,ClassificationPreservation))
            report=q.load(root/'preservation.json');self.assertTrue(report['teacherUnchanged'])
            self.assertEqual(report['geometryDistributionPenaltyAdded'],geometry)
            if geometry:self.assertGreater(report['meanGeometryPenalty'],0.)

if __name__=='__main__':unittest.main()
