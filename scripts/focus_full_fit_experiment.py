"""Sealed full-corpus weighted fit; integrates with the existing FocusRing trainer."""
import argparse
from collections import defaultdict
import json
import math
import os
import time

import focus_fit_diagnostic as fit
from focus_dataset_contract import ROOT, digest, local

s = fit.static
a = s.a
require = fit.require
VERSION = 'focus-full-fit-v1'
ARM = 'full-corpus-fit'
RUN = 'fdr020-full-corpus-fit'
PROPOSAL = 'ef8001be1109177728ecd35ec8fd473bee31a6bf61782c08737070eb84a44537'
CONFIG = dict(epochs=1000, batch=928, lr=.01, model='mobilenet_v3_small_frozen', seed=42,
              maxSeconds=300, augmentation='none', inputSize=256,
              initialization='fresh-linear-head', testDuringTraining=False,
              selection=s.rep.POLICY)


def training_weights(base):
    native = [r for r in base['samples'] if r['use'] == 'train-candidate']
    human = [r for r in base['samples'] if r['use'] == 'human-static-auxiliary']
    require(len(native) == 790 and len(human) == 138, 'changed_training_support')
    rows = native + human
    require(len({r['id'] for r in rows}) == 928 and all(r['split'] == 'train' for r in rows),
            'changed_training_membership')
    pixels = lambda r: r.get('pixelSHA256', r['crop'].get('pixelSHA256'))
    labels = {}
    for r in rows:
        px = pixels(r)
        require(px is not None and r['label'] in (0, 1), 'invalid_training_label')
        require(px not in labels or labels[px] == r['label'], 'conflicting_duplicate_labels')
        labels[px] = r['label']
    require(not set(labels) & {pixels(r) for r in base['samples'] if r['split'] == 'validation'},
            'development_pixel_overlap')
    weights = {r['id']: .8 * base['sampling']['weights'][r['id']] for r in native}
    groups = defaultdict(lambda: defaultdict(list))
    for r in human:
        require('pairID' not in r, 'fabricated_human_pair')
        groups[r['frameID'], r['label']][pixels(r)].append(r['id'])
    frames = {r['frameID'] for r in human}
    require(len(frames) == 8 and set(groups) == {(f, y) for f in frames for y in (0, 1)},
            'missing_frame_label_bucket')
    for group in groups.values():
        for ids in group.values():
            for sid in ids:
                weights[sid] = .2 / 16 / len(group) / len(ids)
    require(all(math.isfinite(w) and w > 0 for w in weights.values())
            and math.isclose(sum(weights.values()), 1), 'invalid_weight_mass')
    for population, expected in ((native, .4), (human, .1)):
        for label in (0, 1):
            require(math.isclose(sum(weights[r['id']] for r in population if r['label'] == label), expected),
                    'unbalanced_source_label_mass')
    return rows, weights


def assemble(spec):
    require(spec['version'] == 'focus-full-fit-input-v1', 'wrong_input_version')
    proposal = s.sealed(spec['proposal'], 'proposalSHA256')
    require(proposal['proposalSHA256'] == PROPOSAL, 'unapproved_proposal')
    base = s.sealed(spec['base'], 'protocolSHA256')
    require(base['version'] == s.VERSION and proposal['source'] == spec['base'], 'wrong_base')
    rows, weights = training_weights(base)
    validation = [r for r in base['samples'] if r['split'] == 'validation']
    require(weights == proposal['weights'] and [r['id'] for r in rows] == proposal['trainingIDs']
            and [r['id'] for r in validation] == proposal['validationIDs']
            and base['selection'] == proposal['selection'], 'changed_proposed_membership_or_weights')
    require(len(validation) == 333, 'changed_validation_support')
    receipt = s.read_ref(spec['receipt']); preflight = s.read_ref(spec['preflight'])
    require(preflight['protocolSHA256'] == base['protocolSHA256']
            and receipt['representation'] == base['representation'] and receipt['backboneUnchanged'] is True,
            'wrong_cache_provenance')
    a.checked(spec['cache']); a.checked(base['representation']['weights'])
    for ref in s.read_ref(base['inputs']['inventoryInputs']): a.checked(ref)
    s.check_pixels(base['samples'])
    runtime = s.rep.retention.runtime_identity()
    runtime['code'] += [a.reference(ROOT/'scripts'/n) for n in (
        'focus_full_fit_experiment.py', 'focus_fit_diagnostic.py', 'focus_human_static_experiment.py',
        'focus_paired_experiment.py', 'focus_pretrained_experiment.py', 'focus_representative_experiment.py',
        'focus_representative_validation.py', 'human_focus_evaluation.py', 'human_focus_roles.py')]
    doc = dict(version=VERSION, inputs=spec, samples=rows+validation, runtime=runtime,
        configuration=CONFIG, selection=base['selection'], representation=base['representation'], warmCheckpoint=None,
        counts=dict(training=928, development=315, retention=18),
        fullFit=dict(weights=weights, consecutivePasses=5, validationEvery=25, weightDecay=.01),
        releaseEligible=False, unmetQualificationBlockers=base['unmetQualificationBlockers'])
    doc['protocolSHA256'] = digest(doc)
    return doc


def approval(doc):
    return dict(version='focus-full-fit-approval-v1', approved=True, protocolSHA256=doc['protocolSHA256'],
                proposalSHA256=PROPOSAL, arm=ARM, runName=RUN,
                authority='Maintainer approved full-corpus implementation and one bounded run, 2026-09-30',
                scope='one-run-no-export-no-promotion')


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path); doc = s.sealed(a.reference(path), 'protocolSHA256')
    require(doc['version'] == VERSION and doc == assemble(doc['inputs']), 'changed_full_fit_protocol')
    require(arm == ARM and run_name == RUN, 'wrong_full_fit_run')
    out = ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out, *out.parents)), 'output_collision')
    ref = None
    if approval_path is not None:
        ref = a.reference(local(approval_path))
        require(s.read_ref(ref) == approval(doc), 'stale_full_fit_approval')
    rows = [{**r, 'path': a.checked({k:r['crop'][k] for k in ('path', 'sha256')})} for r in doc['samples']]
    return dict(formatVersion=s.rep.FORMAT, protocolVersion=VERSION, launchEligible=ref is not None,
        configurationValid=True, executionAuthorized=False, blockers=[] if ref else ['missing_full_fit_approval'],
        releaseEligible=False, **{k:doc[k] for k in ('configuration', 'selection', 'representation', 'warmCheckpoint',
          'runtime', 'counts', 'fullFit', 'protocolSHA256', 'unmetQualificationBlockers')},
        cachedInputs=doc['inputs'], protocolFile=a.reference(path), approval=ref, arm=arm), rows


def training_metrics(predictions, rows, weights):
    require(len(predictions) == len(rows) and len({r['id'] for r in rows}) == len(rows)
            and set(weights) == {r['id'] for r in rows}, 'training_prediction_membership')
    groups = defaultdict(lambda: dict(n=0, mass=0., bceSum=0., weightedSum=0., correct05=0,
                                      confidentCorrect=0, tp=0, fp=0, tn=0, fn=0))
    for p, r in zip(predictions, rows):
        q = p['probability']; w = weights[r['id']]; y = r['label']
        require(p['id'] == r['id'] and p['label'] == y and r['split'] == 'train'
                and type(q) in (int, float) and math.isfinite(q) and 0 <= q <= 1
                and math.isfinite(w) and w > 0, 'invalid_training_prediction')
        source = 'human' if r['use'] == 'human-static-auxiliary' else 'native'
        require(r['use'] in ('human-static-auxiliary', 'train-candidate'), 'invalid_training_role')
        bce = -math.log(max(1e-12, q if y else 1-q))
        decision = 'tp' if y and q >= .85 else 'fn' if y else 'fp' if q >= .85 else 'tn'
        for key in ('overall', source, f'{source}:{y}'):
            g = groups[key]; g['n'] += 1; g['mass'] += w; g['bceSum'] += bce; g['weightedSum'] += w*bce
            g['correct05'] += int(q >= .5) == y
            g['confidentCorrect'] += q >= .85 if y else q <= .15
            g[decision] += 1
    require(math.isclose(groups['overall']['mass'], 1), 'invalid_training_weight_sum')
    for g in groups.values():
        g['bce'] = g.pop('bceSum')/g['n']; g['weightedBCE'] = g.pop('weightedSum')/g['mass']
        g['recall'] = g['tp']/(g['tp']+g['fn']) if g['tp']+g['fn'] else None
        g['fpr'] = g['fp']/(g['fp']+g['tn']) if g['fp']+g['tn'] else None
    return dict(groups=dict(groups), fitPass=groups['overall']['confidentCorrect'] == len(rows)
                and all(groups[k]['weightedBCE'] <= .05 for k in ('native', 'human')))


def schedule(update, fit_pass, streak, maximum=1000):
    streak = streak+1 if fit_pass else 0
    done = streak >= 5 or update == maximum
    return streak, done, done or update % 25 == 0


def weighted_backward(model, x, y, weights, microbatch, deadline):
    """Accumulate the same weighted sum, not per-microbatch mean losses."""
    import torch
    total=0.
    for offset in range(0,len(y),microbatch):
        if time.monotonic()>=deadline:
            model.zero_grad(set_to_none=True)
            return None
        sl=slice(offset,offset+microbatch)
        loss=(torch.nn.functional.binary_cross_entropy_with_logits(model(x[sl]).view_as(y[sl]),
              y[sl],reduction='none')*weights[sl]).sum()
        require(bool(torch.isfinite(loss)),'nonfinite_training_loss')
        loss.backward();total+=float(loss.detach().item())
    return total


def run(model, train_data, val_data, report, train, val, device, out, started, deadline, experiment_id):
    import torch
    from train_focus_ring_detector import checkpoint_improved
    require(str(device) == 'mps', 'full_fit_requires_mps')
    cfg = report['fullFit']; weights = cfg['weights']
    x, y = (t.to(device) for t in train_data.tensors)
    w = torch.tensor([weights[r['id']] for r in train], dtype=torch.float32, device=device).reshape(-1, 1)
    visual=report.get('visualTraining',False)
    parameters=model.optimizer_groups(report['configuration']['lr'],cfg['tailLR']) if visual else model.parameters()
    opt = torch.optim.AdamW(parameters, lr=report['configuration']['lr'], weight_decay=cfg['weightDecay'])
    def predictions(data, rows):
        model.eval(); result = []
        with torch.no_grad():
            for start in range(0, len(rows), 32):
                q = torch.sigmoid(model(data.tensors[0][start:start+32].to(device))).flatten().cpu().tolist()
                result.extend(dict(id=r['id'], label=r['label'], probability=p)
                              for r, p in zip(rows[start:start+32], q))
        return result
    def observe_train():
        ps = predictions(train_data, train)
        return dict(predictions=ps, **training_metrics(ps, train, weights))
    def observe_val():
        ps = predictions(val_data, val)
        return dict(predictions=ps, **s.rep.selection_metrics(ps, val, report['selection']))
    best_loss = float('inf'); selected = None; history = []; streak = 0; stop = 'update_cap'
    initial = observe_val(); initial_train = observe_train()
    def checkpoint(update, kind):
        if visual:
            return dict(epoch=update,model_name=report['configuration']['model'],state_dict=model.state_dict(),
                        checkpointKind='visual-partial-candidate-v1' if kind=='frozen-pretrained-linear-head-v1'
                        else 'visual-partial-diagnostic-v1',representation=report['representation'],
                        protocolSHA256=report['protocolSHA256'],arm=report['arm'],features=report['features'])
        if report.get('protocolVersion') == 'focus-context-experiment-v1':
            return dict(epoch=update,model_name=report['configuration']['model'],state_dict=model.state_dict(),
                        checkpointKind='context-mlp-head-v1' if kind=='frozen-pretrained-linear-head-v1'
                        else 'context-mlp-diagnostic-last-v1',representation=report['representation'],
                        protocolSHA256=report['protocolSHA256'],contextArm=report['arm'],
                        contextFeatures=report['contextFeatures'],inputWidth=1736,hiddenWidth=64)
        return dict(epoch=update, model_name=report['configuration']['model'], state_dict=model.state_dict(),
                    checkpointKind=kind, representation=report['representation'], protocolSHA256=report['protocolSHA256'])
    with (out/'training-observations.jsonl').open('x') as observations:
        observations.write(json.dumps(dict(update=0, **initial_train), allow_nan=False)+'\n')
        for update in range(1, report['configuration']['epochs']+1):
            if time.monotonic() >= deadline:
                stop = 'time_cap'; break
            model.train(); opt.zero_grad()
            loss = weighted_backward(model,x,y,w,cfg.get('microbatch',len(train)),deadline)
            if loss is None:
                stop='time_cap';break
            grad = sum(float(p.grad.detach().norm().item()) for p in model.parameters() if p.grad is not None)
            require(math.isfinite(grad), 'nonfinite_training_gradient'); opt.step()
            obs = observe_train(); observations.write(json.dumps(dict(update=update, **obs), allow_nan=False)+'\n')
            if visual:
                streak=streak+1 if obs['fitPass'] else 0
                done=update==report['configuration']['epochs']
                evaluate=done or update%cfg['validationEvery']==0
            else:
                streak, done, evaluate = schedule(update, obs['fitPass'], streak, report['configuration']['epochs'])
            timed = time.monotonic() >= deadline
            evaluate = evaluate or timed
            validation = observe_val() if evaluate else None
            history.append(dict(update=update, optimizedLoss=loss, gradientNorm=grad,
                                training={k:v for k,v in obs.items() if k != 'predictions'}, validation=validation))
            if evaluate:
                torch.save(checkpoint(update, 'full-fit-diagnostic-last'), out/'weights/last.pt')
                if validation['checkpointEligible'] and checkpoint_improved(validation['selectionLoss'], best_loss, report['configuration']):
                    best_loss = validation['selectionLoss']; selected = update
                    torch.save(checkpoint(update, 'frozen-pretrained-linear-head-v1'), out/'weights/best.pt')
                observations.flush()
                (out/'progress.json').write_text(json.dumps(dict(history=history, selectedUpdate=selected), allow_nan=False))
                print(f"update {update}: trainingBCE={obs['groups']['overall']['weightedBCE']:.5f} confident={obs['groups']['overall']['confidentCorrect']}/{len(train)} eligible={validation['checkpointEligible']}", flush=True)
            if done or timed:
                stop = 'training_fit' if streak >= 5 and not visual else 'time_cap' if timed else 'update_cap'; break
    # Preserve last completed step even when deadline was reached between updates.
    if history and history[-1]['validation'] is None:
        history[-1]['validation'] = observe_val()
        v = history[-1]['validation']; update = history[-1]['update']
        if v['checkpointEligible'] and checkpoint_improved(v['selectionLoss'], best_loss, report['configuration']):
            selected = update; torch.save(checkpoint(update, 'frozen-pretrained-linear-head-v1'), out/'weights/best.pt')
    torch.save(checkpoint(history[-1]['update'] if history else 0, 'full-fit-diagnostic-last'), out/'weights/last.pt')
    result = dict(status='completed' if history else 'time_cap_before_update', releaseEligible=False,
        checkpointEligible=selected is not None, selectedUpdate=selected, fitPassed=streak >= 5,
        protocolSHA256=report['protocolSHA256'], history=history, initial=initial, initialTraining=initial_train,
        experimentID=experiment_id, device=str(device), pid=os.getpid(), stopReason=stop,
        elapsedSeconds=time.monotonic()-started, torchVersion=str(torch.__version__),
        finalHeadSHA256=fit.paired.base.state_digest(model))
    if visual:
        tail=fit.paired.base.state_digest(model.tail)
        bn=fit.paired.base.state_digest(torch.nn.ModuleList([m for m in model.tail.modules()
            if isinstance(m,torch.nn.modules.batchnorm._BatchNorm)]))
        require(bn==report['initialBNSHA256'],'visual_batchnorm_changed')
        if report['arm'].endswith('frozen'):require(tail==report['initialTailSHA256'],'visual_frozen_tail_changed')
        result['visualState']=dict(initialTail=report['initialTailSHA256'],finalTail=tail,
                                  tailChanged=tail!=report['initialTailSHA256'],batchNormUnchanged=True)
    (out/'experiment-result.json').write_text(json.dumps(result, indent=2, allow_nan=False))
    print(f"Completed: fitPassed={result['fitPassed']}, selectedUpdate={selected}; no export/promotion", flush=True)
    return 0


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=local, required=True); args = p.parse_args()
    require(not args.output.exists(), 'output_collision')
    prior = ROOT/'NativeUITrainer/focus_ring_runs/fdr017-static-baseline'
    spec = dict(version='focus-full-fit-input-v1',
        proposal=a.reference(ROOT/'reports/work/FOCUS-FIT-PREP-02/full-corpus-proposal.json'),
        base=a.reference(ROOT/'reports/work/HUMAN-STATIC-ADMISSION/frozen-ready/protocol.json'),
        cache=a.reference(prior/'features.pt'), receipt=a.reference(prior/'pretrained-features.json'),
        preflight=a.reference(prior/'preflight.json'))
    doc = assemble(spec); args.output.mkdir(parents=True)
    for name, value in [('protocol.json', doc), ('approval.json', approval(doc))]:
        with (args.output/name).open('x') as f: json.dump(value, f, indent=2, allow_nan=False)
    print(json.dumps(dict(protocolSHA256=doc['protocolSHA256'], counts=doc['counts'])))


if __name__ == '__main__': main()
