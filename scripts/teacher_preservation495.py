"""Training-only teacher targets for the resident crop trainer.

Use the existing minibatches. Do not add updates, evaluation rows, or teacher gradients.
"""
import math

import torch
from torch import nn


def validate_config(config):
    if not isinstance(config, dict) or set(config) != {'model', 'anchors', 'weight'}:
        raise ValueError('teacher_configuration')
    weight = config['weight']
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
        raise ValueError('teacher_weight')
    for key in ('model', 'anchors'):
        ref = config[key]
        if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
            raise ValueError('teacher_reference')
    return config


def prepare(config, rows, tensors, device):
    import research_queue as q
    from experiment_templates import checked
    from focus_ring_backbone import mobilenetv4_conv_small
    validate_config(config)
    model_path, anchor_path = checked(config['model']), checked(config['anchors'])
    document = q.load(anchor_path)
    if document.get('version') != 'teacher-anchors-v1' or set(document) != {'version', 'rows'}:
        raise ValueError('teacher_anchor_version')
    validate_anchors(rows, document['rows'])
    # Teacher construction must not change the student's sampling sequence.
    with torch.random.fork_rng(devices=[]):
        teacher = mobilenetv4_conv_small(num_classes=1)
    teacher.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True)['state_dict'], strict=True)
    return Preservation(teacher.to(device), rows, document['rows'], tensors, weight=config['weight'])


def validate_anchors(rows, anchors):
    train = {r['id']: r for r in rows if r['role'] == 'train'}
    if not anchors or len({r['id'] for r in anchors}) != len(anchors):
        raise ValueError('teacher_anchor_membership')
    for row in anchors:
        if row.get('role') != 'train' or train.get(row.get('id')) != row:
            raise ValueError('teacher_anchor_not_training_member')
    if {r['label'] for r in anchors} != {0, 1}:
        raise ValueError('teacher_anchor_class_support')
    return anchors


class Preservation:
    def __init__(self, teacher, rows, anchors, tensors, *, weight=1.0, batch=16):
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
            raise ValueError('teacher_weight')
        validate_anchors(rows, anchors)
        self.teacher = teacher.eval().requires_grad_(False)
        self.before = {n: t.detach().clone() for n, t in teacher.state_dict().items()}
        self.weight = float(weight)
        self.targets = {}
        self.presented = 0
        self.updates = 0
        # The cache changes compute only. Repeated membership rows retain their original weight.
        cache = {}
        with torch.no_grad():
            for start in range(0, len(anchors), batch):
                selected = anchors[start:start + batch]
                missing = {r['sha256']: r for r in selected if r['sha256'] not in cache}
                if missing:
                    unique = list(missing.values())
                    x, _ = tensors(unique)
                    values = teacher(x).reshape(-1).sigmoid().detach()
                    if len(values) != len(unique) or not torch.isfinite(values).all():
                        raise ValueError('teacher_nonfinite_targets')
                    cache.update((r['sha256'], v.clone()) for r, v in zip(unique, values))
                for row in selected:
                    self.targets[row['id']] = cache[row['sha256']]
        self.verify()

    def loss(self, logits, selected):
        indices = [i for i, row in enumerate(selected) if row['id'] in self.targets]
        if not indices:
            return logits.sum() * 0
        target = torch.stack([self.targets[selected[i]['id']] for i in indices]).to(logits.device)
        prediction = logits.reshape(-1)[indices]
        cross_entropy = nn.functional.binary_cross_entropy_with_logits(prediction, target, reduction='sum')
        entropy = -(torch.special.xlogy(target, target) + torch.special.xlogy(1-target, 1-target)).sum()
        self.presented += len(indices)
        self.updates += 1
        # Normalize over the original batch. Do not amplify batches with fewer anchors.
        return self.weight * (cross_entropy - entropy) / len(selected)

    def verify(self):
        if self.teacher.training or any(p.requires_grad or p.grad is not None for p in self.teacher.parameters()):
            raise ValueError('teacher_not_detached')
        if any(not torch.equal(self.before[n], t) for n, t in self.teacher.state_dict().items()):
            raise ValueError('teacher_state_changed')

    def report(self):
        self.verify()
        return dict(weight=self.weight, temperature=1, anchorRows=len(self.targets),
                    anchorPresentations=self.presented, anchorUpdates=self.updates,
                    teacherUnchanged=True, teacherDetached=True, trainingOnly=True,
                    loss='Bernoulli KL; sum on anchors divided by original batch size')
