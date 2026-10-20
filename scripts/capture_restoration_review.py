"""Publish a derived capture receipt after separately verified restoration.

Never change the failed capture or execute navigation. Training admission stays separate.
"""
import copy
import shutil
from pathlib import Path

import research_queue as q
from experiment_templates import checked, pin
import recovery_capture_gate437 as gate
import native_control_admission as admission

OUT = None


def validate_failure(capture, plan):
    q.require(capture.get('complete') is False and capture.get('cleanup') is False,
              'capture_review_failure_state')
    q.require(capture.get('error') is None and capture.get('originalProfile') == 'standard',
              'capture_review_original_state')
    q.require(capture.get('cleanupErrors') == ['profile_restore:profile-standard:None'],
              'capture_review_failure_scope')
    expected = {(c['id'], p, target) for c in plan['cases']
                for p in plan['profiles'] for target in c['targets']}
    frames = capture['frames']
    actual = [(f['case'], f['profile'], f['focus']) for f in frames]
    q.require(len(actual) == len(set(actual)) == plan['expectedFrames'] and set(actual) == expected,
              'capture_review_membership')
    q.require(all(f['repeat'] == 0 for f in frames), 'capture_review_repeat')


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    plan = q.load(checked(spec['reviewPlan']))
    recovery, _ = gate.verify_recovery(spec, OUT.parents[4], plan)
    result_path = checked(plan['failedResult'])
    result = q.load(result_path)
    failed_spec = q.load(checked(plan['failedSpec']))
    q.require(result.get('status') == 'failed' and result.get('reason') == 'process_failed'
              and result['job'] == failed_spec['id'] == recovery['failedJob']
              and result['specSHA256'] == q.text_digest(failed_spec), 'capture_review_identity')
    q.require(q.outputs_intact(result_path.parent, result), 'capture_review_outputs_changed')
    source = result_path.parent/'out'
    artifact = q.load(source/'artifact.json')
    capture_path = Path(artifact['path'])
    import hcf_study371 as study
    root = study.verify_storage(artifact['storage'])
    q.require(capture_path.resolve() == capture_path and capture_path.is_relative_to(root),
              'capture_review_path')
    q.require(q.digest(capture_path) == artifact['sha256'], 'capture_review_changed')
    capture = q.load(capture_path)
    validate_failure(capture, artifact['plan'])
    # Bind the review to the exact native storage failure, not an arbitrary route failure.
    native = q.load(checked(plan['nativeFailure']))
    failure = native['data']['navigationRoute']['_0']['hcf']
    q.require(failure['requested'] == 'standard' and failure['status'] == 'stopped'
              and 'HCF evidence budget exhausted' in failure['reason'], 'capture_review_native_cause')
    destination = root/spec['id']
    q.require(not destination.exists(), 'capture_review_collision')
    destination.mkdir()
    derived = copy.deepcopy(capture)
    for frame in derived['frames']:
        image = q.local_path(capture_path.parent, frame['path'])
        q.require(q.digest(image) == frame['sha256'], 'capture_review_image_changed')
        target = q.local_path(destination, frame['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(image, target)
        q.require(q.digest(target) == frame['sha256'], 'capture_review_copy_changed')
    derived.update(complete=True, cleanup=True, cleanupErrors=[],
                   restorationReview=dict(originalCapture=str(capture_path),
                       originalSHA256=artifact['sha256'], recovery=plan['recovery'],
                       captureRepeated=False, originalFailurePreserved=True))
    q.save(destination/'capture.json', derived)
    published = copy.deepcopy(artifact)
    published.update(path=str(destination/'capture.json'), sha256=q.digest(destination/'capture.json'))
    # Reuse native validation, but keep every group in development for this check.
    # The role decision is made later by the separate admission job.
    roles = {c['group']: 'development' for c in artifact['plan']['cases']}
    rows = admission.admit_artifact(published, roles, root, spec['id'])
    q.save(OUT/'artifact.json', published)
    q.save(OUT/'review.json', dict(original=plan['failedResult'], recovery=plan['recovery'],
        frames=len(rows), captureRepeated=False, trainingAdmitted=False, modelAccepted=False))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=n, sha256=q.digest(OUT/n)) for n in ('artifact.json', 'review.json')]))
