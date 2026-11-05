"""Preserve detector classification on verified original training anchors."""
import math
from pathlib import Path
import torch
from torch.nn import functional as F
import research_queue as q
from experiment_templates import checked


def validate(config, membership):
    q.require({'model','anchors','weight'}<=set(config)<= {'model','anchors','weight','geometryWeight'}, 'detector_preservation_fields')
    if 'geometryWeight' in config:
        q.require(type(config['geometryWeight']) in (int,float) and math.isfinite(config['geometryWeight']) and config['geometryWeight']>0,'geometry_preservation_weight')
    weight = config['weight']
    q.require(type(weight) in (int, float) and math.isfinite(weight) and weight > 0,
              'detector_preservation_weight')
    checked(config['model'])
    anchors = q.load(checked(config['anchors']))
    q.require(anchors.get('version') == 'detector-preservation-anchors-v1' and
              set(anchors) == {'version', 'rows'}, 'detector_preservation_anchors')
    rows = {r['id']: r for r in membership['rows']}
    ids = [r['id'] for r in anchors['rows']]
    q.require(ids and len(ids) == len(set(ids)), 'detector_preservation_membership')
    for row in anchors['rows']:
        q.require(row == rows.get(row['id']) and row['role'] == 'train' and
                  row['trainingEligible'] is True and row['labelsComplete'] is True,
                  'detector_preservation_training_only')
        checked(row['image'])
    return anchors


def scores(predictions):
    if isinstance(predictions, tuple):
        predictions = predictions[1]
    q.require(isinstance(predictions, dict) and 'scores' in predictions and
              'one2one' not in predictions, 'detector_preservation_output')
    return predictions['scores']


class ClassificationPreservation:
    """Wrap the resident loss without replacing its box or distribution losses."""
    def __init__(self, base, teacher, paths, weight):
        self.base, self.teacher = base, teacher.eval().requires_grad_(False)
        self.paths, self.weight = frozenset(str(Path(p).resolve()) for p in paths), weight
        self.reference = {k: v.detach().cpu().clone() for k, v in teacher.state_dict().items()}
        self.calls = self.anchor_images = 0
        self.loss_sum = 0.0

    def __call__(self, predictions, batch):
        loss, items = self.base(predictions, batch)
        # Validation uses the ordinary criterion. Unknown files never become anchors.
        indices = [i for i, p in enumerate(batch['im_file']) if str(Path(p).resolve()) in self.paths]
        if not indices:
            return loss, items
        student = scores(predictions)[indices]
        with torch.no_grad():
            target = scores(self.teacher(batch['img'][indices])).detach()
        q.require(student.shape == target.shape and torch.isfinite(target).all() and
                  torch.isfinite(student).all(), 'detector_preservation_logits')
        # Average over anchor images and positions; sum over taxonomy channels.
        # Match the resident loss's batch-size scaling without adding updates.
        penalty = F.binary_cross_entropy_with_logits(student.float(), target.float().sigmoid(), reduction='none')
        penalty = penalty.sum(dim=1).mean() * self.weight
        q.require(torch.isfinite(penalty).all(), 'detector_preservation_nonfinite')
        loss = loss.clone()
        q.require(loss.numel() == 3, 'detector_preservation_loss_shape')
        loss[1] = loss[1] + penalty * batch['img'].shape[0]
        items = dict(items)
        items['cls_loss'] = items['cls_loss'] + penalty.detach()
        self.calls += 1
        self.anchor_images += len(indices)
        self.loss_sum += float(penalty.detach())
        return loss, items

    def verify(self):
        q.require(not self.teacher.training and not any(p.requires_grad or p.grad is not None
                  for p in self.teacher.parameters()), 'detector_preservation_teacher_gradient')
        q.require(all(torch.equal(v.detach().cpu(), self.reference[k]) for k, v in
                      self.teacher.state_dict().items()), 'detector_preservation_teacher_changed')


def attach(model, config, membership, dataset, output):
    anchors = validate(config, membership)
    paths = [dataset.parent/'images/train'/(r['id'] + Path(r['image']['path']).suffix) for r in anchors['rows']]
    q.require(all(p.is_file() for p in paths), 'detector_preservation_prepared_anchors')
    state = {}
    def setup(trainer):
        from ultralytics import YOLO
        # Model construction must not change the student's sampler or initialization.
        with torch.random.fork_rng(devices=[]):
            teacher = YOLO(str(checked(config['model']))).model.to(trainer.device).float()
        student = trainer.model
        expected = membership['names']
        q.require([teacher.names[i] for i in range(len(teacher.names))] == expected and
                  [student.names[i] for i in range(len(student.names))] == expected,
                  'detector_preservation_taxonomy')
        q.require(type(teacher.model[-1]).__name__ == 'Detect' and not teacher.model[-1].end2end,
                  'detector_preservation_architecture')
        original = student.init_criterion()
        if 'geometryWeight' in config:
            from detector_geometry570 import GeometryPreservation
            wrapper=GeometryPreservation(original,teacher,paths,config['weight'],config['geometryWeight'])
        else:
            wrapper = ClassificationPreservation(original, teacher, paths, config['weight'])
        student.criterion = wrapper
        state['wrapper'] = wrapper
        state['student'] = student
        state['original'] = original
    def finish(trainer):
        wrapper = state['wrapper']; wrapper.verify()
        q.require(wrapper.calls > 0 and wrapper.anchor_images > 0, 'detector_preservation_unused')
        state['student'].criterion = state['original']
        q.save(output/'preservation.json', dict(version='detector-preservation-result-v1',
            configuration=config, anchorCount=len(paths), calls=wrapper.calls,
            presentedAnchorImages=wrapper.anchor_images, meanPenalty=wrapper.loss_sum/wrapper.calls,
            teacherUnchanged=True, teacherDetached=True, trainingOnly=True,
            boxLossUnchanged='geometryWeight' not in config, originalSupervisedBoxLossUnchanged=True,
            geometryDistributionPenaltyAdded='geometryWeight' in config,
            meanGeometryPenalty=wrapper.geometry_loss_sum/wrapper.calls if 'geometryWeight' in config else None,
            addedOptimizerUpdates=0, modelAccepted=False))
    model.add_callback('on_pretrain_routine_end', setup)
    model.add_callback('on_train_end', finish)
