"""Paired head experiment: immutable cached features only, never encoder inference."""
import hashlib
import json
import re
from collections import defaultdict

import focus_pretrained_experiment as base
from focus_dataset_contract import ROOT, digest, local

VERSION = 'focus-paired-experiment-v1'
require = base.require
a = base.sampler.rep.a


def pairs(rows, weights):
    groups = defaultdict(list)
    ids = set()
    for i, row in enumerate(rows):
        require(row['id'] not in ids and row['split'] == 'train', 'invalid_pair_membership')
        ids.add(row['id'])
        groups[(row['sourceID'], row['pairID'])].append((i, row))
    result = []
    for key, members in sorted(groups.items()):
        require(len(members) == 2 and sorted(r['label'] for _, r in members) == [0, 1], 'incomplete_pair')
        members.sort(key=lambda item: -item[1]['label'])
        positive, negative = [r for _, r in members]
        for field in ('control', 'relatedGroup', 'proposedRole'):
            require(positive.get(field) == negative.get(field), 'conflicting_pair_metadata')
        require(weights[positive['id']] == weights[negative['id']] > 0, 'conflicting_pair_weight')
        result.append(dict(sourceID=key[0], pairID=key[1], indices=[i for i, _ in members],
                           ids=[r['id'] for _, r in members], weight=2*weights[positive['id']]))
    require(bool(result), 'empty_pairs')
    return result


def assemble(spec):
    require(spec.get('version') == 'focus-paired-input-v1', 'unsupported_paired_input')
    previous = base.sampler.rep.appearance.sealed(spec['base'], base.VERSION, 'protocolSHA256')
    current = base.assemble(previous['inputs'])
    stable = lambda d: {k:v for k,v in d.items() if k not in ('runtime', 'protocolSHA256')}
    require(stable(previous) == stable(current), 'changed_paired_corpus')
    for field in ('cache', 'receipt', 'preflight'): a.checked(spec[field])
    preflight = a.object_json(a.checked(spec['preflight']))
    receipt = a.object_json(a.checked(spec['receipt']))
    require(preflight['protocolSHA256'] == previous['protocolSHA256']
            and receipt['representation'] == previous['representation']
            and receipt['backboneUnchanged'] is True, 'incompatible_feature_provenance')
    train = [r for r in current['samples'] if r['split'] == 'train']
    pair_index = pairs(train, current['sampling']['weights'])
    current['runtime']['code'].append(a.reference(ROOT/'scripts/focus_paired_experiment.py'))
    doc = {**current, 'version': VERSION, 'inputs': spec,
           'pairedTraining': dict(loss='bce-plus-softplus-negative-pair-margin', coefficient=1,
                                 pairs=pair_index, pairBatch=32, draws=len(pair_index)),
           'comparisonLimitations': ['paired batches versus independently sampled crops',
                                    'fixed cached encoder; no new data or encoder optimization']}
    doc.pop('protocolSHA256', None)
    doc['protocolSHA256'] = digest(doc)
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path)
    doc = base.sampler.rep.appearance.sealed(a.reference(path), VERSION, 'protocolSHA256')
    require(doc == assemble(doc['inputs']), 'changed_paired_protocol_or_runtime')
    require(arm == 'paired-stretch' and isinstance(run_name, str)
            and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', run_name), 'invalid_paired_arm_or_run')
    out = ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), 'output_collision')
    blockers = []; approval_ref = None
    if approval_path is None: blockers.append('missing_experiment_approval')
    else:
        approval_ref = a.reference(local(approval_path)); approval = a.object_json(a.checked(approval_ref))
        require(approval.get('version') == 'focus-paired-approval-v1' and approval.get('approved') is True
                and approval.get('protocolSHA256') == doc['protocolSHA256'] and approval.get('arm') == arm
                and approval.get('runName') == run_name and approval.get('reviewer')
                and approval.get('reviewReference'), 'stale_paired_approval')
    rows = [{**r, 'path': a.checked({k:r['crop'][k] for k in ('path','sha256')}),
             'samplingWeight':doc['sampling']['weights'].get(r['id'],0.)} for r in doc['samples']]
    return dict(formatVersion=base.sampler.rep.FORMAT, protocolVersion=VERSION,
        configurationValid=True, launchEligible=not blockers, executionAuthorized=False,
        releaseEligible=False, blockers=blockers,
        **{k:doc[k] for k in ('configuration','selection','sampling','counts','warmCheckpoint','runtime',
                            'protocolSHA256','unmetQualificationBlockers','representation','pairedTraining')},
        cachedInputs=doc['inputs'], protocolFile=a.reference(path), approval=approval_ref,
        arm=arm, output=str(out.relative_to(ROOT))), rows


def validate_tensors(cache, receipt, train, validation):
    import torch
    require(cache['receipt'] == receipt, 'changed_feature_receipt')
    for key, rows, hash_key in (('train', train, 'trainFeatureSHA256'),
                                ('validation', validation, 'validationFeatureSHA256')):
        x, y = cache[key]
        require(x.shape == (len(rows),576) and y.shape == (len(rows),1)
                and x.dtype == torch.float32 and y.dtype == torch.float32
                and bool(torch.isfinite(x).all()) and bool(torch.isfinite(y).all()), 'invalid_cached_tensor')
        require(torch.equal(y, torch.tensor([[r['label']] for r in rows],dtype=torch.float32)), 'changed_cached_label_order')
        require(hashlib.sha256(x.contiguous().numpy().tobytes()).hexdigest() == receipt[hash_key], 'changed_feature_order_or_pixels')
    require(receipt['trainCount'] == len(train) and receipt['validationCount'] == len(validation), 'changed_feature_counts')


def prepare_features(report, train, validation, device, output):
    import torch
    spec = report['cachedInputs']
    cache = torch.load(a.checked(spec['cache']), map_location='cpu', weights_only=True)
    receipt = a.object_json(a.checked(spec['receipt']))
    validate_tensors(cache, receipt, train, validation)
    index = torch.tensor([p['indices'] for p in report['pairedTraining']['pairs']])
    x, y = cache['train']
    paired = torch.utils.data.TensorDataset(x[index], y[index])
    val = torch.utils.data.TensorDataset(*cache['validation'])
    torch.manual_seed(42)
    head = torch.nn.Linear(576,1).to(device)
    with (output/'cached-feature-receipt.json').open('x') as f:
        json.dump(dict(source=spec, originalReceipt=receipt, pairs=len(paired),
                       encoderLoaded=False, headParameters=577),f,indent=2)
    return head, paired, val


def paired_loss(logits, labels):
    import torch
    require(logits.ndim == 3 and logits.shape[1:] == (2,1) and logits.shape == labels.shape,
            'invalid_paired_logits')
    require(bool((labels[:,0] == 1).all()) and bool((labels[:,1] == 0).all()), 'invalid_pair_label_order')
    return (torch.nn.functional.binary_cross_entropy_with_logits(logits,labels)
            + torch.nn.functional.softplus(-(logits[:,0]-logits[:,1])).mean())
