"""TRAIN666 H2: compile, approve-limit and submit the H2 detector fits (T107) on membership D2.

Arms (Research/Plans/H2Recipe666.md), 2 seeds each, best epoch on the calibration split:
- A: D1 recipe unchanged (YOLO11n, 640, 100 epochs, augmentation `none`).
- B: A + augmentation `mosaic` (mosaic and shuffled square batches; HSV, scale and translate stay at the Ultralytics defaults).
- C: B + YOLO11s. Not compiled while `yolo11s.pt` is missing; a weight download needs Joe's approval.
D2 fits take about 11-13 h (D1: 8.1 h for 5,645 rows). Joe's decision 3 (2026-11-25, "Approve all 3") covers larger limits per
spec hash for H2 fits: each spec gets 86,400 s and 8 GiB counted output, recorded before submission as for H3 arm F.
Usage: h2_queue_plan666.py --membership PATH [--arms A B] [--submit]
"""
import argparse
import json
from pathlib import Path

import hcf_templates395 as ht
import research_approval
import research_execution_policy as policy
import research_extensions as ext
import research_queue as q
from template_inputs398 import pin

OUT = q.ROOT / 'reports/work/TRAIN666/queue-configs'
SECONDS, LIMIT = 86400, 8 << 30
APPROVAL = ('Joe in chat 2026-11-25: "Approve all 3" (H2 decision 3: larger limits per spec hash for H2 fits above 12 h) '
            'and "Yes, train on posters" (poster-grid family in D2). Record: reports/work/user-approvals/train666-h2-*-20261125.json.')
EXPECTED = ('Expected scoreboard change (H2 plan, written before admission): on the 31 layouts, for both seeds of the best arm, '
            'equal-app localization recall at least 0.69 (D1 s372: 0.610); media poster cells at least 50 of 68 and artwork pictures at least 25 of 51; '
            'Plozz recall at least 85 of 137; equal-app precision at least D1 - 0.05; with S0n, focus at least 46 of 58 correct and at most 8 wrong picks. '
            'Arm A is expected to give most of the gain; arms B and C at most 3 points each.')
ARMS = {
    'A': dict(weights='yolo11n.pt', augmentation='none', text='D1 recipe unchanged on D2 (poster-grid and training-app real frames added).'),
    'B': dict(weights='yolo11n.pt', augmentation='mosaic', text='Arm A plus mosaic and shuffled square batches.'),
    'C': dict(weights='yolo11s.pt', augmentation='mosaic', text='Arm B with YOLO11s.'),
}


def build(membership, arms=('A', 'B'), seeds=(371, 372), out_dir=OUT):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    mem_pin = pin(q.ROOT / membership); specs = []
    for arm in arms:
        a = ARMS[arm]; weights = q.ROOT / a['weights']
        q.require(weights.is_file(), f'h2_weights_missing:{a["weights"]}')
        init_pin = pin(weights)
        for seed in seeds:
            cfg_path = out_dir / f'cfg-h2-{arm.lower()}-s{seed}.json'
            q.save(cfg_path, dict(initialization=init_pin, epochs=100, imgsz=640, seed=seed, lr0=0.01, batch=8, patience=0,
                                  exportCoreML=True, augmentation=a['augmentation'], selection='best'), replace=True)
            job_id = f'train666-h2{arm.lower()}-d2-e100-s{seed}'
            spec = ht.build(dict(
                version='hcf-template-description-v1', id=job_id, task='TRAIN666', owner='Maximum-mini-NUIAK', template='T107',
                question=f'H2 arm {arm} (seed {seed}): does D2 data and this recipe find more real-app controls than D1?',
                hypothesis=f'H2 arm {arm}: {a["text"]} ' + EXPECTED,
                controlledComparison=f'Pretrained {a["weights"]}, imgsz 640, lr0 0.01, batch 8, 100 epochs, best epoch on calibration, augmentation {a["augmentation"]}, '
                                     'seeds 371 and 372, identical tvbench Core ML scorer, compared with the same D1 seed.',
                decision='Score both seeds with scripts/tvbench.py eval --roles on manifest-31layouts.json plus S0n focus. '
                         'Report the predicted change beside the measured change, lost cases and unsupported classes. Do not promote.',
                outcomes=dict(
                    supported='The predictions hold for both seeds of 1 arm, and the gain over D1 exceeds the seed difference.',
                    contradicted='Arm A gains less than 2 recall points over D1 at both seeds: data is not the cause. Report before arms B and C.',
                ),
                inputs=dict(configuration=pin(cfg_path), initialization=init_pin, membership=mem_pin), parameters={}, dependencies=[],
                training=dict(expectedScoreboardChange=EXPECTED, experimentLogRunId=f'TRAIN666-H2{arm}-S{seed}', initialization=init_pin,
                              membership=[mem_pin], epochs=100, storageBudgetBytes=LIMIT,
                              acceptanceEvidence='Paired 31-layout Core ML comparison across seeds 371 and 372 against the same D1 seed.', resume='restart'),
            ))
            q.require(spec['limits']['timeoutSeconds'] == policy.TRAINING_SECONDS, 'policy_timeout_mismatch')
            spec['limits'].update(timeoutSeconds=SECONDS, maxOutputBytes=LIMIT)
            q.validate(spec)
            q.save(out_dir / f'spec-{job_id}.json', spec, replace=True)
            specs.append(spec)
    return specs


def submit(specs, queue=q.QUEUE):
    outcomes = []
    for spec in specs:
        q.require(not (queue / 'jobs' / spec['id']).exists(), 'h2_job_exists:' + spec['id'])
        override = ext.record_limits(queue, spec, 'maintainer', APPROVAL)
        q.submit(OUT / f"spec-{spec['id']}.json", queue)
        record = research_approval.approve(queue, spec['id'], 'maintainer', APPROVAL)
        outcomes.append(dict(job=spec['id'], specSHA256=q.text_digest(spec), override=override, approvedSHA256=record['sha256']))
    return outcomes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--membership', required=True); parser.add_argument('--arms', nargs='+', default=['A', 'B'])
    parser.add_argument('--submit', action='store_true')
    args = parser.parse_args()
    specs = build(args.membership, tuple(args.arms))
    print(json.dumps(submit(specs) if args.submit else [dict(id=s['id'], limits=s['limits'], sha256=q.text_digest(s)) for s in specs], indent=2))
