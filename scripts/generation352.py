"""Run a frozen Fixture plan as a queue producer. Preserve failed cleanup evidence."""
import signal
import os
import dataset351 as capture
import compare351
import research_queue as q

OUT = None
MARKER = q.ROOT / '.build/fixture-generation-recovery.json'


def run():
    spec = q.load(OUT.parent.parent.parent / 'spec.json')
    contract = spec['capture']
    ref = contract['plan']
    path = q.local_path(q.ROOT, ref['path'])
    q.require(q.digest(path) == ref['sha256'], 'capture_plan_changed')
    plan = q.load(path)
    study = plan.get('version') in ('native-hcf371-v1', 'native-hcf402-v1', 'native-controls-t45-v1')
    q.require(plan['role'] == ('study-pending' if study else 'development') and plan['trainingEligible'] is False, 'capture_role')
    q.require(plan['binding']['endpoint'] == contract['endpoint'], 'capture_endpoint')
    q.require(plan['binding']['simulatorUDID'] == contract['target'], 'capture_target')
    # Exclusive creation also blocks capture after an interrupted cleanup.
    with MARKER.open('x') as stream:
        import json
        json.dump(dict(job=spec['id'], output=q.relative(OUT), plan=ref, pid=os.getpid()), stream)
    previous = signal.getsignal(signal.SIGTERM)

    def stop(signum, frame):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        raise RuntimeError('capture_cancelled')

    signal.signal(signal.SIGTERM, stop)
    try:
        if study:
            import hcf_study371
            hcf_study371.capture(OUT, plan)
        elif plan.get('version') == 'native-hcf362-v1':
            import hcf_capture362
            hcf_capture362.capture(OUT / 'capture', plan)
        else:
            capture.run(OUT / 'capture', execute=True, prepared=plan)
            compare351.validate_capture(q.load(OUT / 'capture/capture.json'), OUT / 'capture')
    finally:
        signal.signal(signal.SIGTERM, previous)
        receipt = OUT / 'capture/capture.json'
        if receipt.is_file() and q.load(receipt).get('cleanup') is True:
            MARKER.unlink()


def inspect():
    """Verify producer output before a dependent analysis uses it."""
    dependencies = q.load(OUT / 'dependencies.json')
    q.require(len(dependencies) == 1, 'capture_dependency_count')
    dep = dependencies[0]
    for ref in [dep['result'], *dep['outputs']]:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'dependency_changed')
    q.require(len(dep['outputs']) == 1, 'capture_manifest_count')
    path = q.local_path(q.ROOT, dep['outputs'][0]['path'])
    doc = q.load(path)
    plan_path = path.parent / 'plan.json'
    q.require(q.digest(plan_path) == doc['planSHA256'], 'capture_plan_hash')
    q.require(q.load(plan_path)['expectedFrames'] == doc.get('expectedFrames', 40), 'capture_plan_counts')
    frames = compare351.validate_capture(doc, path.parent)
    q.save(OUT / 'dataset-check.json', dict(frames=len(frames), pairs=len(doc['pairs']),
        source=dep, trainingEligible=False, modelAccepted=False,
        limitation='Capture validation does not establish model accuracy or real-app transfer.'))
    return dep['outputs'][0]


def compare():
    ref = inspect()
    config = q.load(OUT / 'comparison.json')
    config.update(capture=ref, inputs=[ref, *config['models'].values()])
    q.save(OUT / 'config.json', config)
    compare351.OUT = OUT
    compare351.run()
