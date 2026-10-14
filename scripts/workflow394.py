"""Isolated DVC comparison using the same real crop functions as the queue."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time

import research_queue as q
import experiment_templates as templates

OUT = None


def environment(output):
    cache = output / 'cache'
    cache.mkdir(exist_ok=True)
    return dict(os.environ, DVC_NO_ANALYTICS='true', DVC_STUDIO_OFFLINE='true', DO_NOT_TRACK='1',
        XDG_CONFIG_HOME=str(cache/'config'), XDG_CACHE_HOME=str(cache), TMPDIR=str(cache),
        MPLCONFIGDIR=str(cache), TORCH_HOME=str(cache), PYTHONDONTWRITEBYTECODE='1',
        PYTHONPATH=str(q.MODULES))


def command(argv, workspace, env, name):
    start = time.monotonic()
    proc = subprocess.run(argv, cwd=workspace, env=env, capture_output=True, text=True, timeout=180)
    q.save(workspace/(name+'.json'), dict(command=argv, returnCode=proc.returncode,
        stdout=proc.stdout[-12000:], stderr=proc.stderr[-12000:], seconds=time.monotonic()-start))
    q.require(proc.returncode == 0, 'dvc_command_failed:'+name)
    return time.monotonic()-start


def dvc_pipeline(config, output):
    templates.validate(config)
    workspace = output / 'pipeline'
    workspace.mkdir()
    env = environment(output)
    dvc = str(q.ROOT / '.venv-workflow394/bin/dvc')
    interpreter = str(q.ROOT / '.venv-yolo/bin/python')
    command([dvc, 'init', '--no-scm'], workspace, env, 'init')
    command([dvc, 'config', 'core.analytics', 'false'], workspace, env, 'analytics')
    command([dvc, 'config', 'cache.type', 'copy'], workspace, env, 'cache-copy')
    q.save(workspace/'config.json', config)
    script = q.MODULES/'experiment_steps393.py'
    base = [interpreter, str(script)]
    shared = [str(script), str(q.MODULES/'focus_ring_backbone.py'), str(q.MODULES/'train_focus_ring_detector.py'), 'config.json']
    manifest = q.load(templates.checked(config['manifest']))
    inputs = [str(templates.checked(p)) for p in [config['manifest'], config['model']] + [r['image'] for r in manifest['rows']]]
    stages = {}
    for step, deps, outputs in [
        ('prepare', inputs, ['prepare/prepared.json', 'prepare/tensors.npy']),
        ('score', ['prepare/prepared.json', 'prepare/tensors.npy', str(templates.checked(config['model']))], ['score/predictions.json']),
        ('report', ['score/predictions.json'], ['report/report.json']),
    ]:
        stages[step] = dict(cmd=shlex.join(base+[step, str(workspace/'config.json'), str(workspace)]),
                            deps=list(dict.fromkeys(shared+deps)), outs=outputs)
    # JSON is a YAML subset. No arbitrary command comes from an experiment description.
    q.save(workspace/'dvc.yaml', dict(stages=stages))
    cold = command([dvc, 'repro'], workspace, env, 'first-run')
    before = q.digest(workspace/'report/report.json')
    warm = command([dvc, 'repro'], workspace, env, 'reuse-run')
    q.require(before == q.digest(workspace/'report/report.json'), 'dvc_reuse_changed')
    q.save(output/'dvc-result.json', dict(version=1, firstSeconds=cold, reuseSeconds=warm,
        reportSHA256=before, modelAccepted=False, qualificationOnly=True, cache='OS cache uncontrolled'))


def run_dvc():
    config = q.load(OUT.parents[2]/'spec.json')['templateConfig']
    start = time.monotonic()
    try:
        dvc_pipeline(config, OUT)
    except Exception as error:
        q.save(OUT/'template-result.json', dict(execution='failed', code=str(error),
            modelAccepted=False, qualificationOnly=True, seconds=time.monotonic()-start))
        raise


def freeze_inputs(folder):
    """Copy a bounded retained sample. Preserve source membership and original bytes."""
    source = q.ROOT/'reports/work/research-queue/jobs/hcf371r4-50-crops/attempts/1/out/crops.json'
    document = q.load(source)
    rows = sorted((r for r in document['rows'] if r['role'] == 'development'), key=lambda r:r['id'])[:16]
    q.require(len(rows) == 16, 'pilot_membership_missing')
    folder.mkdir(parents=True, exist_ok=True)
    images = folder/'images'; images.mkdir(exist_ok=True)
    members = []
    for index, row in enumerate(rows):
        path = Path(row['path'])
        q.require(path.resolve() == path and path.is_relative_to('/Volumes/training-drive/data/NUIAK'), 'source_scope')
        q.require(q.digest(path) == row['sha256'], 'source_image_changed')
        target = images / (str(index)+'.png')
        if not target.exists(): shutil.copyfile(path, target)
        q.require(q.digest(target) == row['sha256'], 'copy_changed')
        members.append(dict(id=row['id'], group=row['group'], role=row['role'], label=row['label'], profile=row['profile'],
                            image=templates.pin(target)))
    manifest = dict(version='prepared-crop-membership-v1', preprocessing='production-crops-rgb256-v1', rows=members,
                    source=templates.pin(source), originalPreprocessing=document['preprocessing'])
    dest = folder/'membership.json'
    if dest.exists(): q.require(q.load(dest) == manifest, 'frozen_membership_changed')
    else: q.save(dest, manifest)
    model = q.ROOT/'reports/work/research-queue/jobs/hcf375c-70-crop-train/attempts/1/out/final.pt'
    q.require(q.digest(model) == 'dc0a8449523c545820b6ff5c04577fb1d0f31d6c7bcd2715b94beabc8a6a5b05', 'pilot_model_changed')
    return dict(version=templates.VERSION, id='workflow394-pilot', owner='research-host-NUIAK',
        question='Does the workflow preserve measured crop predictions and recover completed steps?',
        decision='Require matching membership and decisions. Report overhead without accepting a model.',
        manifest=templates.pin(dest), model=templates.pin(model), batchSize=4)


def register_pilot(folder, queue):
    description = freeze_inputs(folder/'inputs')
    records = []
    for index in range(3):
        config = dict(description, id=f'workflow394-q{index}')
        templates.register(config, queue)
        records.extend(s['id'] for s in templates.build(config))
        spec = templates.build(dict(description, id=f'workflow394-d{index}'))[0]
        spec.update(id=f'workflow394-d{index}', stage=[], dependencies=[],
            adapter=dict(type='python-callable', steps=['workflow394.run_dvc'], outputAttributes=['workflow394.OUT']))
        spec['inputs'].append(templates.pin(Path(__file__)))
        spec['evidence']['predictions'] = 'pipeline/score/predictions.json'
        spec['templateConfig'] = dict(description, id=f'workflow394-d{index}')
        path=folder/(spec['id']+'.json')
        if path.exists(): q.require(q.load(path)==spec, 'pilot_spec_changed')
        else: q.save(path,spec)
        q.submit(path,queue)
        # Alternate arms between repetitions.
        if index % 2: records.insert(len(records)-3, spec['id'])
        else: records.append(spec['id'])
    q.save(folder/'dispatch.json', dict(jobs=records, queue=q.relative(queue), modelAccepted=False), replace=True)
    return records


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--queue',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(register_pilot(args.folder.absolute(),args.queue.absolute()),indent=2))
