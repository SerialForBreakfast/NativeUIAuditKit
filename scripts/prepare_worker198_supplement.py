"""Verified Run028 checkpoint-only supplement for retained WORKER-198 inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

from prepare_worker198_eval import check_limits, digest

ROOT = Path(__file__).resolve().parents[1]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def verified_parent(parent, expected):
    require(parent.is_absolute() and parent.resolve() == parent, 'parent_boundary')
    require(digest(parent) == expected, 'parent_changed')
    doc = json.loads(parent.read_text())
    require(doc['version'] == 'worker198-eval-v1' and
            doc['purpose'] == 'frozen_inference_only' and doc['trainingEligible'] is False,
            'parent_role')
    require(doc['settings'] == dict(device='0', imgsz=640, discard_degenerate=True), 'settings')
    require({k: v['count'] for k, v in doc['plans'].items()} ==
            {'fit': 135, 'page': 37, 'combined': 413}, 'membership')
    require(all(v['trainingEligible'] is False for v in doc['plans'].values()), 'plan_role')
    check_limits(doc['files'])
    indexed = {}
    for entry in doc['files']:
        path = parent.parent / entry['path']
        require(path.resolve() == path and path.is_file() and
                path.stat().st_size == entry['bytes'] and digest(path) == entry['sha256'],
                'parent_input_changed')
        indexed[entry['path']] = entry
    require(all(v['path'] in indexed for v in doc['plans'].values()), 'unbound_plan')
    return doc


def package(output, parent, parent_sha, checkpoint, checkpoint_sha, completion, schedule,
            evidence, *, root=ROOT):
    """Packaging only; production CLI obtains completion from the existing sealed runner."""
    output = output.absolute()
    require(output.is_relative_to(root) and output.resolve() == output and not output.exists(),
            'output_boundary_collision')
    require(completion.get('exitCode') == 0 and
            completion.get('optimizerAt') == schedule.get('optimizerAt') and
            bool(schedule.get('optimizerAt')), 'incomplete_or_wrong_schedule')
    require(checkpoint.is_absolute() and checkpoint.resolve() == checkpoint and
            checkpoint.is_file() and digest(checkpoint) == checkpoint_sha and
            completion['checkpoint']['sha256'] == checkpoint_sha, 'checkpoint_changed')
    original = verified_parent(parent, parent_sha)
    require(shutil.disk_usage(root).free > 8 * 1024**3, 'space')
    entry = dict(path='treatment028.pt', bytes=checkpoint.stat().st_size, sha256=checkpoint_sha)
    check_limits([entry])
    manifest = dict(version='worker198-checkpoint-supplement-v1',
        requestID='nuiak-20261006-worker198-eval028', run='Run028',
        purpose='frozen_inference_only', trainingEligible=False,
        parentManifestSHA256=parent_sha, plans=original['plans'], settings=original['settings'],
        checkpoint=entry, completionEvidence=evidence,
        requiredResidentRuntime=dict(ultralytics='8.4.173', matmulTF32=False, cudnnTF32=True),
        limits=dict(seconds=1800, outputBytes=1024**3),
        outputNames={key: f'eval028-{key}-01.json' for key in original['plans']})
    output.mkdir(parents=True)
    copied = output / entry['path']
    shutil.copyfile(checkpoint, copied)
    require(digest(copied) == checkpoint_sha and digest(checkpoint) == checkpoint_sha,
            'checkpoint_copy_changed')
    metadata = output / 'supplement.json'
    metadata.write_text(json.dumps(manifest, indent=2) + '\n')
    entries = [entry, dict(path=metadata.name, bytes=metadata.stat().st_size, sha256=digest(metadata))]
    check_limits(entries)
    archive = output / 'nuiak-worker198-eval028-v1.tar.gz'
    with tarfile.open(archive, 'w:gz') as stream:
        for item in entries:
            stream.add(output / item['path'], arcname=item['path'], recursive=False)
    with tarfile.open(archive) as stream:
        members = stream.getmembers()
        require(len(members) == 2 and all(m.isfile() for m in members), 'archive_members')
        for item in entries:
            data = stream.extractfile(item['path']).read()
            require(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'],
                    'archive_replay')
    require(digest(parent) == parent_sha, 'parent_changed_during_copy')
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--parent-manifest', type=Path, required=True)
    parser.add_argument('--parent-sha256', required=True)
    args = parser.parse_args()
    import train_style210 as training
    training.configure('treatment')
    checkpoint, _ = training.previous.runner.ready()
    runner = training.previous.runner
    completion_path = runner.OUT / 'completion.json'
    protocol_path = runner.OUT / 'protocol.json'
    completion = training.p.sealed(completion_path)
    protocol = training.p.sealed(protocol_path)
    archive = package(args.output, args.parent_manifest.absolute(), args.parent_sha256,
        checkpoint, completion['checkpoint']['sha256'], completion, protocol['schedule'],
        dict(completion=training.h.ref(completion_path), protocol=training.h.ref(protocol_path)))
    print(json.dumps(dict(path=str(archive), bytes=archive.stat().st_size, sha256=digest(archive))))


if __name__ == '__main__':
    main()
