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


def distribution_loss(student,target):
    q.require(student.shape==target.shape and student.ndim==3 and student.shape[1]%4==0 and student.shape[1]>4,'geometry_preservation_shape')
    q.require(torch.isfinite(student).all() and torch.isfinite(target).all(),'geometry_preservation_nonfinite')
    batch,channels,positions=student.shape
    a=student.float().reshape(batch,4,channels//4,positions)
    b=target.detach().float().reshape_as(a)
    return F.kl_div(a.log_softmax(dim=2),b.softmax(dim=2),reduction='none').sum(dim=2).mean().clamp_min(0)


class GeometryPreservation(ClassificationPreservation):
    def __init__(self,base,teacher,paths,weight,geometry_weight):
        super().__init__(base,teacher,paths,weight)
        self.geometry_weight=geometry_weight;self.geometry_loss_sum=0.

    def __call__(self,predictions,batch):
        loss,items=self.base(predictions,batch)
        indices=[i for i,p in enumerate(batch['im_file']) if str(Path(p).resolve()) in self.paths]
        if not indices:return loss,items
        student=raw(predictions)
        with torch.no_grad():target=raw(self.teacher(batch['img'][indices]))
        a,b=student['scores'][indices],target['scores'].detach()
        q.require(a.shape==b.shape and torch.isfinite(a).all() and torch.isfinite(b).all(),'detector_preservation_logits')
        classification=F.binary_cross_entropy_with_logits(a.float(),b.float().sigmoid(),reduction='none').sum(dim=1).mean()*self.weight
        geometry=distribution_loss(student['boxes'][indices],target['boxes'])*self.geometry_weight
        q.require(torch.isfinite(classification) and torch.isfinite(geometry),'geometry_preservation_nonfinite')
        loss=loss.clone();q.require(loss.numel()==3,'detector_preservation_loss_shape')
        loss[1]=loss[1]+classification*batch['img'].shape[0]
        loss[2]=loss[2]+geometry*batch['img'].shape[0]
        items=dict(items);items['cls_loss']=items['cls_loss']+classification.detach();items['dfl_loss']=items['dfl_loss']+geometry.detach()
        self.calls+=1;self.anchor_images+=len(indices);self.loss_sum+=float(classification.detach());self.geometry_loss_sum+=float(geometry.detach())
        return loss,items
