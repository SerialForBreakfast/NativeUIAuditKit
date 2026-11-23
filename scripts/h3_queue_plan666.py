"""TRAIN666 H3 arm F: compile, approve-limit and submit the 2 `focused`-class detector fits (T107).

Recipe is D1's, unchanged (scripts/train666_queue_plan.py). Only the membership differs:
reports/work/TRAIN666/membership/d1-focused-11class (D1 plus 1 `focused` box, rows of unknown focus dropped).
The trainer hard-links about 5 GB of images into the output folder, so each fit gets an 8 GiB counted-output limit.
Joe approved the membership and the 8 GiB limits in chat on 2026-11-22: "Approve both, start".
The limit is recorded as a maintainer override for each exact spec hash before submission, so no attempt
has to fail on `output_limit` first. Plan: Research/Plans/H3Focus666.md.
Usage: h3_queue_plan666.py [--submit]
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
MEMBERSHIP = 'reports/work/TRAIN666/membership/d1-focused-11class/membership.json'
LIMIT = 8 << 30
APPROVAL = 'Joe in chat 2026-11-22: "Approve both, start" (H3 arm F membership of 5,063 rows and 8 GiB counted output for the 2 fits).'
EXPECTED = ('Expected scoreboard change: on dev42, Kanopy and AX-dev, focus top-1 from the `focused` class matches or beats the comparative '
            'selector refit on D1 boxes (arm S) on the equal-app mean at both seeds; no-focus false selections are no higher than arm S; '
            'class-agnostic localization recall stays within 1 point of the same D1 seed.')


def build(out_dir=OUT, seeds=(371, 372)):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    init_pin, mem_pin = pin(q.ROOT / 'yolo11n.pt'), pin(q.ROOT / MEMBERSHIP)
    specs = []
    for seed in seeds:
        cfg_path = out_dir / f'cfg-h3-focused-11class-s{seed}.json'
        q.save(cfg_path, dict(initialization=init_pin, epochs=100, imgsz=640, seed=seed, lr0=0.01, batch=8, patience=0, exportCoreML=True), replace=True)
        job_id = f'train666-h3f-11class-e100-s{seed}'
        spec = ht.build(dict(
            version='hcf-template-description-v1', id=job_id, task='TRAIN666', owner='Maximum-mini-NUIAK', template='T107',
            question=f'Does a `focused` detector class (seed {seed}) select the focused control on real apps better than a selector over D1 boxes?',
            hypothesis='H3 arm F: pretrained yolo11n, 100 epochs, D1 10 classes plus `focused` on 4,689 train rows. ' + EXPECTED,
            controlledComparison='D1 recipe unchanged: yolo11n.pt initialization, imgsz 640, lr0 0.01, batch 8, augmentation off, seeds 371 and 372, identical tvbench Core ML scorer. Only the membership adds `focused` and drops rows of unknown focus.',
            decision='Score both seeds against D1 seeds with the comparative selector (current and refit) on dev42, Kanopy and AX-dev with scripts/tvbench.py. Report focus top-1, no-focus false selections, localization and lost cases. Not decision-eligible until the benchmark has 30 independent layouts. Do not promote.',
            outcomes=dict(
                supported='Both seeds match or beat arm S on focus without a localization loss beyond 1 point. Focus-in-detector becomes the H3 lead.',
                contradicted='Both seeds fall below arm S on focus. Keep the comparative selector as the H3 lead.',
            ),
            inputs=dict(configuration=pin(cfg_path), initialization=init_pin, membership=mem_pin), parameters={}, dependencies=[],
            training=dict(expectedScoreboardChange=EXPECTED, experimentLogRunId=f'TRAIN666-H3F-S{seed}', initialization=init_pin, membership=[mem_pin], epochs=100,
                          storageBudgetBytes=LIMIT, acceptanceEvidence='Paired development Core ML comparison across seeds 371 and 372 against D1 with the comparative selector.', resume='restart'),
        ))
        q.require(spec['limits']['timeoutSeconds'] == policy.TRAINING_SECONDS, 'policy_timeout_mismatch')
        spec['limits']['maxOutputBytes'] = LIMIT
        q.validate(spec)
        q.save(out_dir / f'spec-{job_id}.json', spec, replace=True)
        specs.append(spec)
    return specs


def submit(specs, queue=q.QUEUE):
    outcomes = []
    for spec in specs:
        q.require(not (queue / 'jobs' / spec['id']).exists(), 'h3_job_exists:' + spec['id'])
        override = ext.record_limits(queue, spec, 'maintainer', APPROVAL)
        q.submit(OUT / f"spec-{spec['id']}.json", queue)
        record = research_approval.approve(queue, spec['id'], 'maintainer', APPROVAL)
        outcomes.append(dict(job=spec['id'], specSHA256=q.text_digest(spec), override=override, approvedSHA256=record['sha256']))
    return outcomes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--submit', action='store_true')
    specs = build()
    print(json.dumps(submit(specs) if parser.parse_args().submit else
                     [dict(id=s['id'], limits=s['limits'], sha256=q.text_digest(s)) for s in specs], indent=2))
