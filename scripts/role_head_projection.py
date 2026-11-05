"""Paired random and mean-projected YOLO output heads; no training or probability-union claim."""
import copy
import torch
from torch import nn


def initialize_pair(source, names, roles, mapping, seed=42):
    if sorted(names) != list(range(len(names))) or len(set(names.values())) != len(names):
        raise ValueError('source_class_order')
    if not roles or len(set(roles)) != len(roles):
        raise ValueError('target_class_order')
    random_model, projected = copy.deepcopy(source), copy.deepcopy(source)
    head = source.model[-1]
    if len(head.cv3) != 3:
        raise ValueError('detector_scale_count')
    counts = {role: sum(mapping.get(name) == role for name in names.values()) for role in roles}
    changed = []
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        for i, branch in enumerate(head.cv3):
            conv = branch[-1]
            if not isinstance(conv, nn.Conv2d) or conv.out_channels != len(names) or conv.groups != 1:
                raise ValueError('classification_output_layer')
            new = nn.Conv2d(conv.in_channels, len(roles), conv.kernel_size, stride=conv.stride,
                            padding=conv.padding, dilation=conv.dilation, bias=conv.bias is not None)
            new = new.to(device=conv.weight.device, dtype=conv.weight.dtype)
            new.train(conv.training)
            random_model.model[-1].cv3[i][-1] = copy.deepcopy(new)
            for j, role in enumerate(roles):
                ids = [k for k, name in names.items() if mapping.get(name) == role]
                if ids:
                    with torch.no_grad():
                        new.weight[j].copy_(conv.weight[ids].mean(dim=0))
                        if new.bias is not None: new.bias[j].copy_(conv.bias[ids].mean())
            projected.model[-1].cv3[i][-1] = new
            prefix = next(k for k, module in source.named_modules() if module is conv)
            changed.extend(prefix+'.'+key for key in conv.state_dict())
    for model in (random_model, projected):
        target = model.model[-1]; target.nc = len(roles); target.no = len(roles) + target.reg_max * 4
        model.names = dict(enumerate(roles));model.nc = len(roles)
        if hasattr(model, 'yaml'): model.yaml['nc'] = len(roles)
        state = model.state_dict()
        for key, value in source.state_dict().items():
            if key not in changed and not torch.equal(value, state[key]):
                raise ValueError('non_head_tensor_changed:' + key)
        if any(t.is_floating_point() and not torch.isfinite(t).all() for t in state.values()):
            raise ValueError('nonfinite_projection')
    return random_model, projected, dict(seed=seed, mode='mean', targetRoles=roles, sourceClasses=names,
        projectedChannels=counts, randomFallbackRoles=[r for r in roles if not counts[r]],
        changedTensors=changed, nonOutputStatePreserved=True, modelAccepted=False,
        limitation='Mean logits are not max or union probabilities; taxonomy context rules remain in the label converter.')
