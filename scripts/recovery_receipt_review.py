"""Publish verified recovery evidence after a receipt-read failure. Never recapture."""
import shutil
import research_queue as q
from experiment_templates import checked, pin
from hcf_recovery367 import valid_result
from recovery_capture_gate437 import OUTPUTS

OUT = None


def review(spec, output):
    if 'capture' in spec:
        q.load(checked(spec['capture']['plan']))
    source = checked(spec['reviewResult'])
    result = q.load(source)
    original_spec = q.load(checked(spec['reviewSpec']))
    q.require(result['specSHA256'] == q.text_digest(original_spec), 'review_spec_changed')
    q.require(result.get('status') == 'failed' and result.get('reason') == spec['expectedFailure'], 'review_failure_changed')
    missing = checked(spec['retentionReceipt'])
    q.require(spec['expectedFailure'] == 'evidence_not_read:' + q.relative(missing), 'review_failure_scope')
    q.require(q.outputs_intact(source.parent, result), 'review_outputs_changed')
    retention = q.load(missing)
    q.require(isinstance(retention, dict) and bool(retention), 'review_retention_missing')
    origin = source.parent/'out'
    valid_result(q.load(origin/'qualification/qualification.json'))
    original = q.load(origin/'recovery.json')
    q.require(original.get('complete') is True and original.get('trainingEligible') is False, 'review_recovery_incomplete')
    for name in OUTPUTS:
        path = origin/name
        q.require(any(item['path'] == name and item['sha256'] == q.digest(path) for item in result['outputs']),
                  'review_output_not_recorded:' + name)
    for name in OUTPUTS:
        if name == 'recovery.json':
            continue
        destination = output/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        q.require(not destination.exists(), 'review_collision')
        shutil.copyfile(origin/name, destination)
    for field, name in [('qualification','qualification/qualification.json'), ('fixture','fixture-after.json'),
                        ('previousMarker','previous-marker.json')]:
        q.require(original[field] == pin(origin/name), 'review_original_binding:' + field)
        original[field] = pin(output/name)
    original['reviewedAttempt'] = spec['reviewResult']
    q.save(output/'recovery.json', original)
    q.save(output/'review.json', dict(reusedRecovery=True, newCapture=False, newNavigation=False,
        result=spec['reviewResult'], retention=spec['retentionReceipt'], modelAccepted=False))
    q.save(output/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=str(p.relative_to(output)), sha256=q.digest(p))
        for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'artifact-receipt.json']))


def run():
    review(q.load(OUT.parents[2]/'spec.json'), OUT)
