"""Recover retention after a verified capture. Never execute capture again."""
from pathlib import Path
import shutil
import research_queue as q
from experiment_templates import checked, pin
import ttr_evidence_compaction458 as storage

OUT = None


def verify(plan):
    result_path = checked(plan['result'])
    result = q.load(result_path)
    spec = q.load(checked(plan['spec']))
    q.require(result['status'] == 'failed' and result['reason'] == 'process_failed', 'retention_failure_state')
    q.require(result['job'] == spec['id'] and result['specSHA256'] == q.text_digest(spec), 'retention_spec')
    root = result_path.parent/'out'
    for row in result['outputs']:
        path = q.local_path(root, row['path'])
        q.require(path.stat().st_size == row['bytes'] and q.digest(path) == row['sha256'], 'retention_output_changed')
    outputs = {r['path'] for r in result['outputs']}
    q.require({'artifact.json', 'capture-evidence.json', 'template-result.json'} <= outputs, 'retention_outputs')
    failure = q.load(root/'template-result.json')
    q.require(failure.get('execution') == 'failed' and failure.get('code') in
              ('compaction_input_budget', 'compaction_archive_budget', 'compaction_space'), 'retention_failure_cause')
    evidence = q.load(root/'capture-evidence.json')
    q.require(evidence.get('cleanup') is True and evidence.get('images'), 'retention_cleanup')
    artifact = q.load(root/'artifact.json')
    if Path(artifact['path']).is_absolute():
        source = Path(artifact['path'])
        q.require(source.resolve() == source and source.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'),
                  'retention_source_scope')
        q.require(q.digest(source) == artifact['sha256'], 'retention_source_changed')
    else:
        source = checked(dict(path=artifact['path'], sha256=artifact['sha256']))
    capture = q.load(source)
    q.require(capture.get('complete') is True and capture.get('cleanup') is True, 'retention_capture_incomplete')
    q.require(len(capture['frames']) == len(evidence['images']), 'retention_frame_count')
    for frame, image in zip(capture['frames'], evidence['images']):
        q.require(image['path'] in outputs and frame['sha256'] == image['sha256'], 'retention_image_binding')
        q.require(q.digest(q.local_path(source.parent, frame['path'])) == frame['sha256'], 'retention_source_image')
    return root, evidence


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    plan = q.load(checked(spec['retentionRecovery']))
    source, evidence = verify(plan)
    folder = OUT/'retention'; folder.mkdir()
    storage.local_compact(folder)
    # Recheck before publication. The original failed attempt stays immutable.
    verify(plan)
    for name in ['artifact.json', 'capture-evidence.json', *[r['path'] for r in evidence['images']]]:
        target = q.local_path(OUT, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(q.local_path(source, name), target)
    q.save(OUT/'recovery.json', dict(version='retention-recovery-v1', original=plan,
        captureRepeated=False, retentionComplete=True, modelAccepted=False))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=str(p.relative_to(OUT)), sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))


def specification(ident, plan_path):
    plan = q.load(plan_path)
    return dict(version='research-spec-v2', id=ident, task='RETENTION461', owner='Maximum-mini-NUIAK',
        kind='screen', authority='diagnostic', jobKind='artifact', retentionRecovery=pin(plan_path),
        hypothesis='Verified completed capture can survive a retention-only failure without another capture.',
        question='Can verified retention release the existing native evidence?',
        controlledComparison='Reuse exact capture bytes. Change only retention accounting.',
        decisionRule='Publish only verified completed capture after retention succeeds. Preserve the failed attempt.',
        nextActionByOutcome=dict(supported='Release dependent jobs.', contradicted='Preserve evidence and diagnose retention.'),
        inputs=[pin(plan_path), plan['result'], plan['spec'], pin(Path(__file__)), pin(Path(storage.__file__))],
        evidence=dict(reads=[pin(plan_path)['path'], plan['result']['path'], plan['spec']['path']], artifactReceipt='artifact-receipt.json'),
        adapter=dict(type='python-callable', steps=['retention_recovery461.run'], outputAttributes=['retention_recovery461.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
