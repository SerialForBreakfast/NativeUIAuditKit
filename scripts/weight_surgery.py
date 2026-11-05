"""Bounded parameter edits. Callers must verify checkpoint ancestry separately."""
import math
import torch


def edit_parameters(model, base, donor, allowed, coefficient, bias_offset=0.0):
    """Return a new state and receipt; preserve every non-target state entry."""
    parameters = set(dict(model.named_parameters()))
    allowed = set(allowed)
    if not allowed or not allowed <= parameters:
        raise ValueError('parameter_allowlist')
    if set(base) != set(model.state_dict()) or set(donor) != set(base):
        raise ValueError('checkpoint_keys')
    if not math.isfinite(coefficient) or not 0 <= coefficient <= 1 or not math.isfinite(bias_offset):
        raise ValueError('edit_coefficient')
    if bias_offset and 'classifier.bias' not in allowed:
        raise ValueError('bias_outside_allowlist')
    for key, reference in model.state_dict().items():
        for state in (base, donor):
            value = state[key]
            if value.shape != reference.shape or value.dtype != reference.dtype:
                raise ValueError('checkpoint_tensor:' + key)
            if value.is_floating_point() and not torch.isfinite(value).all():
                raise ValueError('nonfinite_tensor:' + key)
    out = {key: value.detach().clone() for key, value in base.items()}
    with torch.no_grad():
        for key in allowed:
            source = donor[key].to(base[key].device)
            out[key] = base[key].clone() if coefficient == 0 else base[key] + coefficient * (source - base[key])
        if bias_offset:
            out['classifier.bias'] += bias_offset
    for key in allowed:
        if not torch.isfinite(out[key]).all():
            raise ValueError('nonfinite_result:' + key)
    changed = sorted(key for key in out if not torch.equal(out[key], base[key]))
    if not set(changed) <= allowed:
        raise ValueError('unexpected_edit')
    return out, dict(allowedParameters=sorted(allowed), changedParameters=changed,
                    coefficient=coefficient, biasOffset=bias_offset,
                    ancestryVerified=False, modelAccepted=False)


def main():
    import argparse
    import json
    import hashlib
    from pathlib import Path
    from focus_ring_backbone import mobilenetv4_conv_small
    parser = argparse.ArgumentParser(description='Inspect a bounded FocusRing edit without saving weights or running inference.')
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--donor', required=True, type=Path)
    parser.add_argument('--group', choices=['classifier', 'head'], required=True)
    parser.add_argument('--coefficient', type=float, default=.5)
    args = parser.parse_args()
    model = mobilenetv4_conv_small()
    states = []
    hashes = []
    for path in (args.base, args.donor):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checkpoint = torch.load(path, map_location='cpu', weights_only=True)
        states.append(checkpoint['state_dict'])
        hashes.append(digest)
    prefixes = ('classifier',) if args.group == 'classifier' else ('classifier', 'conv_head')
    allowed = [key for key, _ in model.named_parameters() if key.split('.')[0] in prefixes]
    _, receipt = edit_parameters(model, *states, allowed, args.coefficient)
    receipt.update(baseSHA256=hashes[0], donorSHA256=hashes[1],
                   candidateSaved=False, inferenceExecuted=False)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
