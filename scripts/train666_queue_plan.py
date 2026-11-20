"""TRAIN666 W1: compile the 2 full-scale D1 baseline fits (T107) for the 10-class legacy-label membership."""
import json
from pathlib import Path

import hcf_templates395 as ht
import research_execution_policy as policy
import research_queue as q
from template_inputs398 import pin

OUT = q.ROOT / 'reports/work/TRAIN666/queue-configs'
MEMBERSHIP = 'reports/work/TRAIN666/membership/d1-10class/membership.json'
EXPECTED = ('Expected scoreboard change: class-agnostic control recall on TVBench development rises from about 24 % (shipped, 103 / 438) '
            'toward the 1-epoch probe level of 86 % (378 / 438) or higher, at both seeds.')


def build(out_dir=OUT, seeds=(371, 372)):
    """The first attempts hit `output_limit`: the trainer hard-links 5.1 GB of images into the output folder.
    Restart them with `research_extensions.py save --max-output-bytes` (EXTENSION408), not with new specifications here."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    init_pin, mem_pin = pin(q.ROOT / 'yolo11n.pt'), pin(q.ROOT / MEMBERSHIP)
    specs = []
    for seed in seeds:
        cfg_path = out_dir / f'cfg-d1-10class-s{seed}.json'
        q.save(cfg_path, dict(initialization=init_pin, epochs=100, imgsz=640, seed=seed, lr0=0.01, batch=8, patience=0, exportCoreML=True), replace=True)
        job_id = f'train666-d1-10class-e100-s{seed}'
        spec = ht.build(dict(
            version='hcf-template-description-v1', id=job_id, task='TRAIN666', owner='Maximum-mini-NUIAK', template='T107',
            question=f'Does 1 detector trained at full scale on the union of existing data (seed {seed}) find more real-app controls than shipped Standard?',
            hypothesis='Pretrained yolo11n trained for 100 epochs on 5,210 rows (10 contract classes, legacy labels) beats shipped phase6b_tvos_v3 on real-app control recall. ' + EXPECTED,
            controlledComparison='Fixed yolo11n.pt initialization, imgsz 640, lr0 0.01, amp off, seeds 371 and 372, identical tvbench Core ML scorer. Baseline, not a release candidate.',
            decision='Score both seeds and shipped Standard on TVBench development with the same scorer. Report class-agnostic recall and precision, role confusion, and lost cases. Do not promote.',
            outcomes=dict(
                supported='Both seeds exceed shipped control recall by more than the seed difference. D1 becomes the baseline for the TRAIN666 recipe grid.',
                contradicted='No repeatable gain over shipped at both seeds. Inspect label and domain defects before another full-scale fit.',
            ),
            inputs=dict(configuration=pin(cfg_path), initialization=init_pin, membership=mem_pin), parameters={}, dependencies=[],
            training=dict(expectedScoreboardChange=EXPECTED, experimentLogRunId=f'TRAIN666-D1-S{seed}', initialization=init_pin, membership=[mem_pin], epochs=100,
                          storageBudgetBytes=2 << 30, acceptanceEvidence='Paired TVBench development Core ML comparison across seeds 371 and 372 against shipped Standard.', resume='restart'),
        ))
        q.require(spec['limits']['timeoutSeconds'] == policy.TRAINING_SECONDS, 'policy_timeout_mismatch')
        q.save(out_dir / f'spec-{job_id}.json', spec, replace=True)
        specs.append(spec)
    return specs


if __name__ == '__main__':
    print(json.dumps([dict(id=s['id'], timeout=s['limits']['timeoutSeconds'], sha256=q.text_digest(s)) for s in build()], indent=2))
