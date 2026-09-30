"""Explicit static-human admission and matched auxiliary experiment; no model at preflight."""
import argparse
from collections import Counter
import importlib.metadata
import json
import math
import random
import re
import time

import focus_pretrained_experiment as pretrained
import focus_paired_experiment as paired
import focus_representative_experiment as rep
from focus_dataset_contract import ROOT, digest, local, pixel_digest
from human_corpus_inventory import components, metadata_hashes

a = rep.a
require = rep.require
VERSION = 'focus-human-static-experiment-v1'
SESSION = 'E93B12DA-9358-4FD6-91F2-1B42AD8C9329'
PACKET = ROOT/'reports/work/HUMAN-STATIC-ADMISSION'
INVENTORY = ROOT/'reports/work/HUMAN-CORPUS-INVENTORY-01/final-results'


def read_ref(ref):
    return json.loads(a.checked(ref).read_text())


def sealed(ref, key):
    doc = read_ref(ref)
    content = dict(doc); seal = content.pop(key)
    require(digest(content) == seal, 'changed_seal')
    return doc


def partition(assembly, inventory, proposal):
    frames = inventory['frames']; controls = inventory['controls']
    require(components(frames) == proposal['groups'], 'changed_source_groups')
    train_frames = sorted(f['id'] for f in frames if f['sessionID'] == SESSION)
    require(len(train_frames) == 8 and train_frames in proposal['groups'], 'partial_or_connected_session')
    selected = [r for r in assembly['samples'] if r['use'] == 'representative-selection']
    require(len(selected) == 453 and len({r['id'] for r in selected}) == 453, 'changed_human_membership')
    indexed = {c['id']: c for c in controls}
    human, dev = [], []
    for row in selected:
        c = indexed[row['id']]
        require(c['proposalEligible'] is True and c['priorUse'] == 'representative-selection'
                and c['frameID'] == row['frameID'] and c['crop'] == row['crop']
                and c['bounds'] == row['bounds'] and c['state'] == row['state']
                and row['label'] == {'focused': 1, 'unfocused': 0}[c['state']], 'changed_human_label_or_crop')
        (human if row['frameID'] in train_frames else dev).append(row)
    require(len(human) == 138 and len(dev) == 315 and len(assembly['excludedSelection']) == 64,
            'changed_partition_counts')
    require(Counter(r['label'] for r in human) == {0: 130, 1: 8}, 'changed_human_support')
    require({c['id'] for c in controls if not c['proposalEligible']} ==
            {r['id'] for r in assembly['excludedSelection']}, 'changed_exclusions')
    return human, dev, train_frames


def check_pixels(rows):
    for row in rows:
        frame = row.get('frame', row.get('image'))
        a.checked({k:frame[k] for k in ('path','sha256')})
        crop = dict(row['crop'], pixelSHA256=row.get('pixelSHA256', row['crop'].get('pixelSHA256')))
        rep.checked_pixels(crop)
        if 'pixelSHA256' in frame: rep.checked_pixels(frame)


def leakage(assembly, inventory, human, dev, train_frames):
    protected = read_ref(assembly['protectedMetadata'])
    protected_pixels = metadata_hashes(protected)
    reserved = sealed(assembly['reservedPixels'], 'seal')
    all_reserved = {v for r in reserved['samples'] for v in (r['framePixelSHA256'], r['crop']['pixelSHA256'])}
    frame_pixels = {f['id']: f['pixelSHA256'] for f in inventory['frames']}
    allowed = {frame_pixels[f] for f in train_frames} | {r['pixelSHA256'] for r in human}
    retained = [r for r in assembly['samples'] if r['use'] == 'retention-validation']
    forbidden = protected_pixels | (all_reserved - allowed)
    forbidden |= {r['pixelSHA256'] for r in dev}
    forbidden |= {frame_pixels[r['frameID']] for r in dev}
    forbidden |= {r[k]['pixelSHA256'] for r in retained for k in ('frame', 'crop')}
    require(not (allowed & forbidden), 'protected_or_validation_leakage')
    native = [r for r in assembly['samples'] if r['use'] == 'train-candidate']
    native_pixels = {r[k]['pixelSHA256'] for r in native for k in ('frame', 'crop')}
    require(not (allowed & native_pixels), 'human_baseline_overlap')
    return dict(version='human-session-reservation-amendment-v1', sourceSessionID=SESSION,
        trainingFrames=train_frames, trainingIDs=[r['id'] for r in human],
        developmentIDs=[r['id'] for r in dev], excludedIDs=[r['id'] for r in assembly['excludedSelection']],
        scope='whole-session-and-descendants', labelSource='human-reviewed-static',
        priorRole='development-selection', newRole='training-auxiliary',
        overriddenReservedPixels=sorted(allowed & all_reserved), protectedReference=assembly['protectedMetadata'],
        protectedRolesUnchanged=True, independentTransferEstablished=False)


def schedules(pairs, human, train, weights, epochs=30):
    """Separate RNGs ensure auxiliary sampling cannot change the genuine-pair draws."""
    prng = random.Random(42); arng = random.Random(43); hrng = random.Random(44)
    counts = Counter(r['frameID'] for r in human)
    require(len(counts) == 8 and len(human) == 138, 'changed_auxiliary_support')
    frame_weights = [1 / (8 * counts[r['frameID']]) for r in human]
    result = []
    for _ in range(epochs):
        draws = prng.choices(range(len(pairs)), weights=[p['weight'] for p in pairs], k=len(pairs))
        order = list(range(len(human))); hrng.shuffle(order)
        baseline = arng.choices(range(len(train)), weights=[weights[r['id']] for r in train], k=len(human))
        updates = math.ceil(len(draws) / 32)
        steps = []
        for i in range(updates):
            start = i * len(human) // updates; end = (i+1) * len(human) // updates
            steps.append(dict(pairs=draws[i*32:(i+1)*32], human=order[start:end],
                baseline=baseline[start:end], auxiliaryWeights=[frame_weights[j] for j in order[start:end]]))
        result.append(steps)
    return result


def assemble(spec):
    require(spec['version'] == 'focus-human-static-input-v1', 'unsupported_static_inputs')
    assembly = sealed(spec['assembly'], 'assemblySHA256')
    inventory = read_ref(spec['inventory']); proposal = read_ref(spec['proposal'])
    require(assembly['version'] == 'focus-control32-data-assembly-v1', 'wrong_assembly')
    # Includes all original annotations/observations, not only the derived crops.
    for ref in read_ref(spec['inventoryInputs']): a.checked(ref)
    for ref in (assembly['base'], assembly['proposal']): a.checked(ref)
    human, dev, frames = partition(assembly, inventory, proposal)
    check_pixels(assembly['samples'])
    for f in inventory['frames']:
        require(pixel_digest(ROOT, f['image']) == f['pixelSHA256'], 'changed_frame_pixels')
    reservation = leakage(assembly, inventory, human, dev, frames)
    amendment = sealed(spec['frameAmendment'], 'amendmentSHA256')
    a.checked(amendment['confirmation'])
    require(amendment['priorSupported'] == 13 and amendment['amendedSupported'] == 14, 'wrong_frame_amendment')
    policy = dict(populations=dict(candidate=[r['id'] for r in dev], auxiliary=[], unresolved=[]),
                  frames=[f for f in amendment['framePolicy']['frames'] if f['id'] not in frames])
    require(len(policy['frames']) == 32 and sum(f['coverage'] == 'complete' and f['settlement'] == 'settled'
            for f in policy['frames']) == 14, 'changed_complete_frame_support')
    native = [r for r in assembly['samples'] if r['use'] == 'train-candidate']
    retention = [r for r in assembly['samples'] if r['use'] == 'retention-validation']
    require(len(native) == 790 and len(retention) == 18, 'changed_native_support')
    pair_index = paired.pairs(native, assembly['sampling']['weights'])
    aux = [{**r, 'split': 'train', 'use': 'human-static-auxiliary', 'labelSource': 'human-reviewed-static',
            'sourceSessionID': SESSION, 'pairedTransitionEligible': False} for r in human]
    require(all('pairID' not in r for r in aux), 'fabricated_human_pair')
    a.checked(spec['weights']); require(spec['weights']['sha256'] == pretrained.WEIGHTS_SHA, 'wrong_weights')
    runtime = rep.retention.runtime_identity()
    runtime['packages']['torchvision'] = importlib.metadata.version('torchvision')
    runtime['code'] += [a.reference(ROOT/'scripts'/name) for name in (
        'focus_human_static_experiment.py', 'focus_pretrained_experiment.py', 'focus_paired_experiment.py',
        'focus_representative_experiment.py', 'focus_representative_validation.py', 'human_focus_evaluation.py')]
    doc = dict(version=VERSION, inputs=spec, runtime=runtime, reservation=reservation,
        samples=native+aux+retention+dev, excludedSelection=assembly['excludedSelection'],
        sampling=assembly['sampling'], counts=dict(nativeTraining=790,humanAuxiliary=138,retention=18,development=315),
        staticHuman=dict(pairs=pair_index, nativeCount=790, auxiliaryCount=138,
                         schedule=schedules(pair_index,human,native,assembly['sampling']['weights'])),
        representation={**pretrained.REPRESENTATION, 'weights':spec['weights']}, warmCheckpoint=None,
        configuration={**assembly['priorConfiguration'], 'model':pretrained.MODEL,
                       'initialization':'imagenet-frozen-features-fresh-linear-head'},
        selection={**assembly['selection'], 'weights':rep.objective_weights(dev), 'framePolicy':policy,
                   'expectedCompleteFrames':14},
        unmetQualificationBlockers=assembly['qualificationBlockers'], releaseEligible=False)
    doc['protocolSHA256'] = digest(doc)
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path); doc = sealed(a.reference(path), 'protocolSHA256')
    require(doc['version'] == VERSION and doc == assemble(doc['inputs']), 'changed_static_protocol_or_runtime')
    require(arm in ('static-baseline','static-human') and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name),
            'invalid_static_arm')
    out = ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), 'output_collision')
    blockers = []; approval_ref = None
    if approval_path is None: blockers.append('missing_static_approval')
    else:
        approval_ref = a.reference(local(approval_path)); approval = read_ref(approval_ref)
        require(approval == dict(version='focus-human-static-approval-v1', approved=True,
            protocolSHA256=doc['protocolSHA256'], arm=arm, runName=run_name,
            authority='Maintainer: Lets try that experiment. 2026-09-30',
            reservationSHA256=digest(doc['reservation']), scope='two-arms-no-export-no-promotion'), 'stale_static_approval')
    rows = [{**r, 'path':a.checked({k:r['crop'][k] for k in ('path','sha256')}), 'samplingWeight':doc['sampling']['weights'].get(r['id'],0)}
            for r in doc['samples']]
    return dict(formatVersion=rep.FORMAT, protocolVersion=VERSION, configurationValid=True,
        launchEligible=not blockers, executionAuthorized=False, releaseEligible=False, blockers=blockers,
        **{k:doc[k] for k in ('configuration','selection','sampling','counts','warmCheckpoint','runtime',
                            'protocolSHA256','unmetQualificationBlockers','representation','staticHuman')},
        protocolFile=a.reference(path),approval=approval_ref,arm=arm,output=str(out.relative_to(ROOT))), rows


def train_epoch(model, dataset, report, epoch, device, optimizer, deadline):
    import torch
    config = report['staticHuman']; steps = config['schedule'][epoch-1]
    x, y = dataset.tensors
    running = 0.
    for step in steps:
        require(time.monotonic() < deadline, 'static_training_deadline')
        indices = torch.tensor([config['pairs'][i]['indices'] for i in step['pairs']])
        aux_indices = step['baseline'] if report['arm'] == 'static-baseline' else [config['nativeCount']+i for i in step['human']]
        optimizer.zero_grad()
        main = paired.paired_loss(model(x[indices].to(device)), y[indices].to(device))
        aux_logits = model(x[aux_indices].to(device))
        aux = torch.nn.functional.binary_cross_entropy_with_logits(aux_logits,y[aux_indices].to(device),reduction='none').flatten()
        aux_weights = torch.tensor(step['auxiliaryWeights'],device=device)
        loss = len(steps) * (.8 * len(step['pairs'])/len(config['pairs']) * main + .2 * (aux*aux_weights).sum())
        require(bool(torch.isfinite(loss)), 'nonfinite_static_loss')
        loss.backward(); optimizer.step(); running += loss.item()/len(steps)
    return running


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=local,required=True)
    args = parser.parse_args(); require(not args.output.exists(),'output_collision')
    spec = dict(version='focus-human-static-input-v1',
        assembly=a.reference(ROOT/'reports/work/FOCUS-CONTROL32-ADMIT-01/assembly.json'),
        inventory=a.reference(INVENTORY/'inventory.json'),proposal=a.reference(INVENTORY/'membership-proposal.json'),
        inventoryInputs=a.reference(INVENTORY/'inputs.json'),
        frameAmendment=a.reference(ROOT/'reports/work/FOCUS-INTEGRATION-03/policy-amendment.json'),
        weights=a.reference(ROOT/'NativeUITrainer/pretrained/mobilenet_v3_small-047dcff4.pth'))
    doc = assemble(spec)
    args.output.mkdir(parents=True)
    outputs = [('protocol.json',doc),('reservation.json',doc['reservation'])]
    for num,arm in ((17,'static-baseline'),(18,'static-human')):
        outputs.append((f'approval-{num}.json',dict(version='focus-human-static-approval-v1',approved=True,
            protocolSHA256=doc['protocolSHA256'],arm=arm,runName=f'fdr{num:03d}-{arm}',
            authority='Maintainer: Lets try that experiment. 2026-09-30',
            reservationSHA256=digest(doc['reservation']),scope='two-arms-no-export-no-promotion')))
    for name,value in outputs:
        with (args.output/name).open('x') as f: json.dump(value,f,indent=2,allow_nan=False)
    print(json.dumps(dict(protocolSHA256=doc['protocolSHA256'],counts=doc['counts'])))


if __name__ == '__main__': main()
