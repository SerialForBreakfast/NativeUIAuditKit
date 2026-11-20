"""Preserve teacher box distributions only on verified original training anchors."""
import torch
from torch.nn import functional as F
from pathlib import Path
import research_queue as q
from detector_preservation551 import ClassificationPreservation


def raw(predictions):
    if isinstance(predictions,tuple):predictions=predictions[1]
    q.require(isinstance(predictions,dict) and {'boxes','scores'}<=set(predictions) and 'one2one' not in predictions,'geometry_preservation_output')
    return predictions


def distribution_loss(student,target,mask=None):
    q.require(student.shape==target.shape and student.ndim==3 and student.shape[1]%4==0 and student.shape[1]>4,'geometry_preservation_shape')
    q.require(torch.isfinite(student).all() and torch.isfinite(target).all(),'geometry_preservation_nonfinite')
    batch,channels,positions=student.shape
    a=student.float().reshape(batch,4,channels//4,positions)
    b=target.detach().float().reshape_as(a)
    divergence=F.kl_div(a.log_softmax(dim=2),b.softmax(dim=2),reduction='none').sum(dim=2)
    if mask is None:return divergence.mean().clamp_min(0)
    values=divergence.mean(dim=1)
    q.require(mask.shape==(batch,positions) and mask.dtype==torch.bool,'geometry_preservation_mask')
    # Empty teacher foreground contributes zero, not a fabricated positive target.
    counts=mask.sum(dim=1);valid=counts>0
    means=(values*mask).sum(dim=1)/counts.clamp_min(1)
    return (means[valid].mean() if valid.any() else values.sum()*0).clamp_min(0)


def classification_loss(student,target,mask=None):
    """Match teacher logits on selected training positions. Never use evaluation labels."""
    q.require(student.shape==target.shape and student.ndim==3,'classification_preservation_shape')
    q.require(torch.isfinite(student).all() and torch.isfinite(target).all(),'classification_preservation_nonfinite')
    values=F.binary_cross_entropy_with_logits(student.float(),target.detach().float().sigmoid(),reduction='none').sum(dim=1)
    if mask is None:return values.mean()
    q.require(mask.shape==values.shape and mask.dtype==torch.bool,'classification_preservation_mask')
    counts=mask.sum(dim=1);valid=counts>0
    means=(values*mask).sum(dim=1)/counts.clamp_min(1)
    return means[valid].mean() if valid.any() else values.sum()*0


class GeometryPreservation(ClassificationPreservation):
    def __init__(self,base,teacher,paths,weight,geometry_weight,geometry_confidence=None,classification_confidence=None):
        super().__init__(base,teacher,paths,weight)
        self.geometry_weight=geometry_weight;self.geometry_loss_sum=0.
        self.classification_confidence=classification_confidence
        self.classification_foreground_positions=0;self.classification_total_positions=0;self.classification_empty_images=0
        self.geometry_confidence=geometry_confidence;self.foreground_positions=0;self.total_positions=0;self.empty_foreground_images=0

    def __call__(self,predictions,batch):
        loss,items=self.base(predictions,batch)
        indices=[i for i,p in enumerate(batch['im_file']) if str(Path(p).resolve()) in self.paths]
        if not indices:return loss,items
        student=raw(predictions)
        with torch.no_grad():target=raw(self.teacher(batch['img'][indices]))
        a,b=student['scores'][indices],target['scores'].detach()
        q.require(a.shape==b.shape and torch.isfinite(a).all() and torch.isfinite(b).all(),'detector_preservation_logits')
        class_mask=None
        if self.classification_confidence is not None:
            class_mask=b.float().sigmoid().amax(dim=1)>=self.classification_confidence
            self.classification_foreground_positions+=int(class_mask.sum());self.classification_total_positions+=class_mask.numel()
            self.classification_empty_images+=int((class_mask.sum(dim=1)==0).sum())
        classification=classification_loss(a,b,class_mask)*self.weight
        mask=None
        if self.geometry_confidence is not None:
            mask=target['scores'].detach().float().sigmoid().amax(dim=1)>=self.geometry_confidence
            self.foreground_positions+=int(mask.sum());self.total_positions+=mask.numel()
            self.empty_foreground_images+=int((mask.sum(dim=1)==0).sum())
        geometry=distribution_loss(student['boxes'][indices],target['boxes'],mask)*self.geometry_weight
        q.require(torch.isfinite(classification) and torch.isfinite(geometry),'geometry_preservation_nonfinite')
        loss=loss.clone();q.require(loss.numel()==3,'detector_preservation_loss_shape')
        loss[1]=loss[1]+classification*batch['img'].shape[0]
        loss[2]=loss[2]+geometry*batch['img'].shape[0]
        items=dict(items);items['cls_loss']=items['cls_loss']+classification.detach();items['dfl_loss']=items['dfl_loss']+geometry.detach()
        self.calls+=1;self.anchor_images+=len(indices);self.loss_sum+=float(classification.detach());self.geometry_loss_sum+=float(geometry.detach())
        return loss,items
