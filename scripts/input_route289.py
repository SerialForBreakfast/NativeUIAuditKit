"""Separate original and added difference routes in the fixed trained model."""
import argparse
from pathlib import Path
import time
import types
import numpy as np
import input_use289 as audit

base = audit.base
OUT = audit.OUT/'routes'


def suppress(net, mode):
    base.require(mode in ('absolute','both'), 'mode')
    def inputs(self, images):
        value = audit.model.change_inputs(self, images)
        value[:, :3] = 0
        if mode == 'both':value[:, 9:] = 0
        return value
    net.change_inputs = types.MethodType(inputs, net)
    return net


def run():
    base.require(not OUT.exists(), 'output_collision')
    base.torch.set_num_threads(2)
    manifest = base.worker.read_package(base.PACKAGE)
    membership = base.read(base.PACKAGE/'membership.json')
    report = base.read(audit.OUT/'result.json')
    prior = base.read(audit.OUT/'registration.json')
    base.checked(prior['model'])
    for ref in prior['inputs']:base.checked(ref)
    nets = {mode:suppress(audit.model.load_candidate(base.checked(prior['model'])),mode)
            for mode in ('absolute','both')}
    OUT.mkdir()
    base.write(OUT/'registration.json',dict(version='input-route289-v1',
        runner=base.ref(Path(__file__)), comparison=base.ref(Path(audit.__file__)),
        prior=base.ref(audit.OUT/'result.json'), model=prior['model'], modes=list(nets),
        hypothesis='Original differences may dominate nuisance responses despite useful residual inputs.',
        training=False, dataRolesChanged=False, productionEligible=False))
    started = time.monotonic()
    results = {}
    for name in manifest['evaluation']:
        x = np.load(base.PACKAGE/name,mmap_mode='r',allow_pickle=False)
        labels = np.array([r['changed'] for r in membership['rows']]) if 'native' in name else (
            np.asarray(membership['replayLabels']) if 'replay' in name else np.zeros(len(x)))
        normal = report['conditions'][name]['normalProbabilities']
        results[name] = {}
        for mode,net in nets.items():
            scores = base.worker.score(net,x)
            results[name][mode] = dict(**audit.compare(normal,scores,labels),probabilities=scores.tolist())
        print(name, {k:v['suppressed'] for k,v in results[name].items()},flush=True)
    base.write(OUT/'result.json',dict(version='input-route289-v1',conditions=results,
        seconds=time.monotonic()-started,productionEligible=False,
        limitations=report['limitations']+['RGB frames still permit the network to infer differences.']))
    total = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(total < 64*1024**2,'output_budget')
    base.write(OUT/'completion.json',dict(outputBytes=total,seconds=time.monotonic()-started,
        conditions=len(results),training=False,productionEligible=False))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
