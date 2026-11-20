"""Build and validate RESET604 T107 matched detector experiment queue descriptions."""
import json
from pathlib import Path

import hcf_templates395 as ht
import research_execution_policy as policy
import research_queue as q
from template_inputs398 import pin

DEFAULT_CONFIG_DIR = q.ROOT / 'reports/work/RESET604/queue-configs'


def build_matched_specs(out_dir=DEFAULT_CONFIG_DIR, seeds=(371, 372)):
    """Compile matched T107 queue specs for v2-d1 (12 roles) and v2-f1-arma (12 roles + focused)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    init_pin = pin(q.ROOT / 'yolo11n.pt')
    arms = [
        ('v2d1', 'reports/work/RESET604/membership/v2-d1/membership.json', '12-role detector on complete scenes'),
        ('v2f1', 'reports/work/RESET604/membership/v2-f1-arma/membership.json', '12-role + focused Arm A on single-focus scenes'),
    ]
    specs = []
    for arm_id, mem_rel, desc in arms:
        mem_pin = pin(q.ROOT / mem_rel)
        for seed in seeds:
            cfg_path = out_dir / f'cfg-{arm_id}-s{seed}.json'
            q.save(cfg_path, dict(
                initialization=init_pin,
                epochs=100,
                imgsz=640,
                seed=seed,
                lr0=0.01,
                batch=8,
                patience=0,
                exportCoreML=True,
            ), replace=True)
            cfg_pin = pin(cfg_path)
            job_id = f'reset604-{arm_id}-e100-s{seed}'
            spec = ht.build(dict(
                version='hcf-template-description-v1',
                id=job_id,
                task='RESET604',
                owner='Maximum-mini-NUIAK',
                template='T107',
                question=f'Does {desc} (seed {seed}) improve TVBench v2 real-app control recall and AP50?',
                hypothesis=f'Pretrained yolo11n trained for 100 epochs (lr0=0.01) on {mem_rel} outperforms shipped phase6b_tvos_v3 on TVBench v2.',
                controlledComparison='Fixed yolo11n.pt init, imgsz=640, lr0=0.01, amp=False, seed pair (371, 372), identical tvbench CoreGraphics scorer.',
                decision='Compare dev-manifest-v2 control recall, officialAP50, lost controls, and focus metrics vs matched baseline; do not promote automatically.',
                outcomes=dict(
                    supported='Both seeds improve dev-manifest-v2 control recall/AP50 across multiple apps with bounded regressions; queue sealed evaluation once Joe approves Gate 2.',
                    contradicted='No repeatable gain beyond noise floor or regressions only on real apps; diagnose membership/labels before another run.',
                ),
                inputs=dict(configuration=cfg_pin, initialization=init_pin, membership=mem_pin),
                parameters={},
                dependencies=[],
                training=dict(
                    expectedScoreboardChange='Both seeds improve class-agnostic localization recall on frozen TVBench development beyond the measured noise floor against shipped Standard.',
                    experimentLogRunId=f'RESET604-{arm_id.upper()}-S{seed}',
                    initialization=init_pin,
                    membership=[mem_pin],
                    epochs=100,
                    storageBudgetBytes=2 << 30,
                    acceptanceEvidence='Paired TVBench dev-manifest-v2 Core ML comparison across seeds 371 and 372.',
                    resume='restart',
                ),
            ))
            q.require(spec['limits']['timeoutSeconds'] == policy.TRAINING_SECONDS, 'policy_timeout_mismatch')
            q.save(out_dir / f'spec-{job_id}.json', spec, replace=True)
            specs.append(spec)
    return specs


if __name__ == '__main__':
    built = build_matched_specs()
    print(json.dumps([dict(id=s['id'], timeout=s['limits']['timeoutSeconds'], step=s['adapter']['steps']) for s in built], indent=2))
