"""Recover one owned capture with current queue evidence. Never retry automatically."""
import os
import signal
from pathlib import Path

import research_queue as q
import qualify_hcf362 as runtime
import native343
from generation352 import MARKER
from focus_batch_harness import lock
from hcf_recovery367 import valid_result
from experiment_templates import pin

OUT = None


def finish(output, marker, expected_hash, report, before, endpoint):
    """Release the guard only after restoration and retained evidence pass."""
    valid_result(report)
    with lock():
        q.require(q.digest(marker) == expected_hash, 'recovery_marker_changed')
        fixture = runtime.d.Fixture(endpoint)
        after = native343.settle(fixture, before, before['scene']['focused_element_id'])
        q.save(output/'fixture-after.json', after)
        image = output/'restored-fixture.png'
        runtime.d.capture_screenshot(native343.TARGET, image, timeout=15)
        from PIL import Image
        with Image.open(image) as decoded:
            decoded.verify()
        q.require(q.live_output_bytes(output) < 100_000_000, 'recovery_output_limit')
        q.save(output/'capture-evidence.json', dict(version='research-capture-evidence-v1',
            images=[dict(path=image.name, sha256=q.digest(image))], cleanup=True,
            modelAccepted=False, trainingEligible=False))
        q.save(output/'recovery.json', dict(complete=True, target=native343.TARGET,
            previousMarker=pin(output/'previous-marker.json'),
            qualification=pin(output/'qualification/qualification.json'),
            fixture=pin(output/'fixture-after.json'), modelAccepted=False, trainingEligible=False))
        q.require(q.digest(marker) == expected_hash, 'recovery_marker_changed')
        # This is the exact failed guard, already preserved in the attempt.
        marker.unlink()


def run():
    output = OUT
    spec = q.load(output.parents[2]/'spec.json')
    contract = spec['capture']
    path = q.local_path(q.ROOT, contract['plan']['path'])
    q.require(q.digest(path) == contract['plan']['sha256'], 'recovery_plan_changed')
    plan = q.load(path)
    q.require(plan.get('version') == 'native-capture-recovery-v2', 'recovery_plan_version')
    stage_ref = plan['staging']
    stage_path = q.local_path(q.ROOT, stage_ref['path'])
    q.require(q.digest(stage_path) == stage_ref['sha256'], 'recovery_staging_changed')
    stage = q.load(stage_path)
    root, folder = Path(stage['projectRoot']), Path(stage['directory'])
    q.require(stage['version'] == 'simulator-staging-v1' and root.is_absolute() and root.name == 'NativeUIAuditKit'
              and root.is_dir() and folder == root/'.build/debug-output/native-screenshots'
              and not any(p.is_symlink() for p in (folder, *folder.parents)), 'recovery_staging_path')
    runtime.d.SCREENSHOT_STAGING = folder
    q.require(contract['target'] == native343.TARGET and
              contract['endpoint'] == 'http://127.0.0.1:8080', 'recovery_target')
    q.require(q.digest(runtime.CLI.resolve()) == plan['helperSHA256'], 'recovery_helper_changed')
    q.require(runtime.d.bind_target(native343.TARGET, contract['endpoint']) == plan['binding'], 'recovery_binding_changed')
    q.require(q.digest(MARKER) == plan['markerSHA256'], 'recovery_marker_changed')
    marker = q.load(MARKER)
    q.require(marker['job'] == plan['failedJob'], 'recovery_owner')
    try:
        os.kill(marker['pid'], 0)
    except ProcessLookupError:
        pass
    else:
        raise ValueError('recovery_previous_process_exists')
    q.save(output/'previous-marker.json', marker)
    before = runtime.d.Fixture(contract['endpoint']).snapshot()
    q.require(before['device']['simulator_udid'] == native343.TARGET, 'recovery_fixture_target')
    q.save(output/'fixture-before.json', before)
    previous = signal.getsignal(signal.SIGTERM)
    def stop(signum, frame):
        raise RuntimeError('recovery_cancelled')
    signal.signal(signal.SIGTERM, stop)
    try:
        mode = plan.get('recoveryMode')
        q.require(mode in (None, 'standard-restoration-v1'), 'recovery_mode_unknown')
        report = runtime.run(output/'qualification', normalize=True, ensure_standard=True,
                             restore_only=mode == 'standard-restoration-v1')
        finish(output, MARKER, plan['markerSHA256'], report, before, contract['endpoint'])
        from ttr_evidence_compaction458 import after_job
        after_job(output)
    finally:
        signal.signal(signal.SIGTERM, previous)


def specification(ident, plan_path):
    """Build an immutable recovery job. This does not register or approve it."""
    ref = pin(Path(plan_path))
    return dict(version='research-spec-v2', id=ident, task='B405-220', owner='Maximum-mini-NUIAK',
        kind='screen', authority='capture', jobKind='capture',
        hypothesis='The corrected TTR route restores Standard and the original Fixture without an uncertain input.',
        question='Can the corrected route verify restoration and release only the exact failed capture guard?',
        controlledComparison='Keep the original failed attempt. Verify Standard restoration, closed ownership, and original Fixture state.',
        decisionRule='Release the guard only after all checks pass. Keep it on failure. Do not accept model or training data.',
        nextActionByOutcome=dict(supported='Review recovery evidence before approving capture successors.',
                                 contradicted='Preserve the guard and send the exact failure to Maximum-mini-TTR.'),
        inputs=[pin(q.ROOT/'scripts/native_capture_recovery.py'), ref],
        evidence=dict(reads=[ref['path']], captureReceipt='capture-evidence.json'),
        capture=dict(target=native343.TARGET, endpoint='http://127.0.0.1:8080', plan=ref,
            approval='The maintainer approves one bounded recovery after route repair. Preserve Standard and failed attempts.'),
        adapter=dict(type='python-callable', steps=['hcf_recovery367.run'], outputAttributes=['hcf_recovery367.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
