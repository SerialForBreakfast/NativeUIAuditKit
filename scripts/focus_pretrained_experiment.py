"""Explicit frozen-feature baseline adapter; imports no model until execution."""
import argparse
import hashlib
import importlib.metadata
import json
import re
import time

import focus_sampler_experiment as sampler
from focus_dataset_contract import ROOT, digest, local

VERSION = 'focus-pretrained-experiment-v1'
INPUT = 'focus-pretrained-input-v1'
WEIGHTS_SHA = '047dcff4addef86ea5bc2eff13c9614dc11f47ab1160d0a71a25e7db994f4e1f'
MODEL = 'mobilenet_v3_small_frozen'
require = sampler.require
REPRESENTATION = dict(kind=MODEL, features=576, normalization=dict(
    mean=[.485, .456, .406], std=[.229, .224, .225]), inputSize=[256, 256],
    centerCrop=False, backboneFrozen=True, batchNormFrozen=True, featureCache=True)


def assemble(spec):
    require(spec.get('version') == INPUT, 'unsupported_pretrained_input')
    base = sampler.rep.appearance.sealed(spec['base'], sampler.VERSION, 'protocolSHA256')
    current = sampler.assemble(base['inputs'])
    stable = lambda d: {k:v for k,v in d.items() if k not in ('runtime', 'protocolSHA256')}
    require(stable(base) == stable(current), 'changed_pretrained_baseline')
    require(spec['weights']['sha256'] == WEIGHTS_SHA, 'wrong_pretrained_weights')
    sampler.rep.a.checked(spec['weights'])
    runtime = current['runtime']
    runtime['packages']['torchvision'] = importlib.metadata.version('torchvision')
    runtime['code'].append(sampler.rep.a.reference(ROOT/'scripts/focus_pretrained_experiment.py'))
    doc = {**current, 'version':VERSION, 'inputs':spec,
           'representation':{**REPRESENTATION, 'weights':spec['weights']},
           'warmCheckpoint':None, 'priorWarmCheckpoint':base['warmCheckpoint'],
           'configuration':{**current['configuration'], 'model':MODEL,
                            'initialization':'imagenet-frozen-features-fresh-linear-head'},
           'comparisonLimitations':['different torchvision/torch runtime', 'different architecture and normalization',
                                    'frozen features versus full-backbone optimization']}
    doc.pop('protocolSHA256', None);doc['protocolSHA256'] = digest(doc)
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path)
    doc = sampler.rep.appearance.sealed(sampler.rep.a.reference(path), VERSION, 'protocolSHA256')
    require(doc == assemble(doc['inputs']), 'changed_pretrained_protocol_or_runtime')
    require(arm == 'pretrained-stretch' and isinstance(run_name, str)
            and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', run_name), 'invalid_pretrained_arm_or_run')
    out = ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), 'output_collision')
    blockers=[];approval_ref=None
    if approval_path is None: blockers.append('missing_experiment_approval')
    else:
        approval_ref = sampler.rep.a.reference(local(approval_path))
        approval = sampler.rep.a.object_json(sampler.rep.a.checked(approval_ref))
        require(approval.get('version') == 'focus-pretrained-approval-v1' and approval.get('approved') is True
                and approval.get('protocolSHA256') == doc['protocolSHA256'] and approval.get('arm') == arm
                and approval.get('runName') == run_name and approval.get('reviewer')
                and approval.get('reviewReference'), 'stale_pretrained_approval')
    rows = [{**r, 'path':sampler.rep.a.checked({k:r['crop'][k] for k in ('path','sha256')}),
             'samplingWeight':doc['sampling']['weights'].get(r['id'],0.)} for r in doc['samples']]
    return dict(formatVersion=sampler.rep.FORMAT, protocolVersion=VERSION, configurationValid=True,
        launchEligible=not blockers, executionAuthorized=False, releaseEligible=False, blockers=blockers,
        **{k:doc[k] for k in ('configuration','selection','sampling','counts','warmCheckpoint','runtime',
                            'protocolSHA256','unmetQualificationBlockers','representation')},
        protocolFile=sampler.rep.a.reference(path), approval=approval_ref, arm=arm,
        output=str(out.relative_to(ROOT))), rows


def state_digest(module):
    h = hashlib.sha256()
    for key, value in sorted(module.state_dict().items()):
        h.update(key.encode()); h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def encode(features, dataset, device, deadline, expected_features=576):
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    features.eval()
    for parameter in features.parameters(): parameter.requires_grad_(False)
    before = state_digest(features)
    mean = torch.tensor(REPRESENTATION['normalization']['mean'], device=device).view(1,3,1,1)
    std = torch.tensor(REPRESENTATION['normalization']['std'], device=device).view(1,3,1,1)
    vectors=[];labels=[]
    with torch.no_grad():
        for x,y in DataLoader(dataset,batch_size=32,shuffle=False,num_workers=0):
            require(time.monotonic() < deadline, 'pretrained_feature_deadline')
            z = features((x.to(device)-mean)/std).flatten(1)
            require(z.shape == (len(x),expected_features) and bool(torch.isfinite(z).all()), 'invalid_pretrained_features')
            vectors.append(z.cpu());labels.append(y.cpu())
    require(vectors and state_digest(features) == before and not features.training
            and not any(p.requires_grad for p in features.parameters()), 'backbone_mutation_or_empty_data')
    return TensorDataset(torch.cat(vectors),torch.cat(labels)), before


def prepare_features(report, train_dataset, val_dataset, device, deadline, output):
    import torch
    from torch import nn
    from torchvision.models import mobilenet_v3_small
    rep = report['representation']
    require({k:v for k,v in rep.items() if k != 'weights'} == REPRESENTATION, 'unsupported_representation')
    path = sampler.rep.a.checked(rep['weights'])
    require(rep['weights']['sha256'] == WEIGHTS_SHA, 'wrong_pretrained_weights')
    network = mobilenet_v3_small(weights=None)
    network.load_state_dict(torch.load(path,map_location='cpu',weights_only=True),strict=True)
    features = nn.Sequential(network.features,network.avgpool).to(device)
    train, before = encode(features,train_dataset,device,deadline)
    val, after = encode(features,val_dataset,device,deadline)
    require(before == after, 'backbone_changed_between_partitions')
    # Do not carry initialization RNG consumption from unused ImageNet classifier.
    torch.manual_seed(42)
    head = nn.Linear(REPRESENTATION['features'],1).to(device)
    receipt = dict(representation=rep,featureStateSHA256=before,backboneUnchanged=True,
        trainCount=len(train),validationCount=len(val),device=str(device),
        headParameters=sum(p.numel() for p in head.parameters()),
        trainFeatureSHA256=hashlib.sha256(train.tensors[0].numpy().tobytes()).hexdigest(),
        validationFeatureSHA256=hashlib.sha256(val.tensors[0].numpy().tobytes()).hexdigest())
    with (output/'pretrained-features.json').open('x') as f:json.dump(receipt,f,indent=2)
    torch.save(dict(train=train.tensors,validation=val.tensors,receipt=receipt),output/'features.pt')
    return head,train,val


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',required=True,type=local)
    parser.add_argument('--output',required=True,type=local)
    args=parser.parse_args();require(not args.output.exists(),'output_collision')
    doc=assemble(sampler.rep.a.object_json(args.inputs))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(doc,f,indent=2,allow_nan=False)
    print(json.dumps(dict(protocolSHA256=doc['protocolSHA256'],counts=doc['counts'])))


if __name__ == '__main__':main()
