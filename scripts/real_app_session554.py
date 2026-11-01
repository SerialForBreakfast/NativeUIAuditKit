"""Bounded real-app Simulator sessions for REALAPP554. No settings changes, no retries.

Commands:
  alert-check --udid UUID [--since 'YYYY-MM-DD HH:MM:SS'] [--out DIR]
  scene-trial --udid UUID --app PATH --bundle ID --out DIR [--snapshots N] [ARGS ...]
  session --plan FROZEN_PLAN.json --out NEW_DIR
"""
import argparse
import base64
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
import research_queue as q

TTR = Path('/Users/josephmccraw/Developer/TVTestRig')
AATV = TTR/'.local-work/parallel551/DerivedData/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv'
LOCAL = TTR/'.local-work/realapp554'
OCR = q.ROOT/'scripts/ocr_helper.swift'
ENDPOINT = 'http://127.0.0.1:8097/diagnostics/sdk/probe'
REASONS = re.compile(r"^\[(?P<scene>[^\]]+)\] Setting deactivation reasons to: '(?P<reasons>[^']*)'")
ALERT = 'systemModalAlert'


def deactivation(lines):
    """Return the latest deactivation reasons for each scene from PineBoard ndjson log lines."""
    latest = {}
    for line in lines:
        if not line.startswith('{'):
            continue
        row = json.loads(line)
        match = REASONS.match(row.get('eventMessage', ''))
        if match:
            reasons = [] if match['reasons'] == '(none)' else [r.strip() for r in match['reasons'].split(',')]
            latest[match['scene']] = dict(timestamp=row['timestamp'], reasons=reasons)
    return latest


def alert_state(latest):
    """A scene has an open alert when its latest reasons include systemModalAlert."""
    scenes = sorted(s for s, v in latest.items() if ALERT in v['reasons'])
    return dict(status='alert' if scenes else 'clear', alertScenes=scenes, scenes=latest)


def read_log(udid, since):
    command = ['xcrun', 'simctl', 'spawn', udid, 'log', 'show', '--style', 'ndjson',
               '--predicate', 'process == "PineBoard" AND category == "SceneDeactivation"']
    command += ['--start', since] if since else ['--last', '1d']
    r = subprocess.run(command, capture_output=True, text=True, timeout=120)
    q.require(r.returncode == 0 and r.stdout.rstrip().endswith('"finished":1}'), 'alert_log_unavailable')
    return r.stdout.splitlines()


def alert_text(udid, out):
    """Read visible alert text with Vision OCR. The screenshot stays in the TTR work folder."""
    LOCAL.mkdir(parents=True, exist_ok=True)
    image = LOCAL/f'alert-{udid[:8]}-{int(time.time())}.png'
    subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(image)], capture_output=True, timeout=30, check=True)
    r = subprocess.run(['swift', str(OCR), str(image), '--json'], capture_output=True, text=True, timeout=120)
    return dict(image=str(image), sha256=q.digest(image), text=r.stdout.strip()[:4000], returnCode=r.returncode)


def alert_check(udid, since=None, out=None):
    """Preflight: fail when any scene keeps a system modal alert. A missing log is 'unavailable', not clear."""
    try:
        result = alert_state(deactivation(read_log(udid, since)))
    except (ValueError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        result = dict(status='unavailable', reason=str(error))
    result.update(udid=udid, since=since, checkedAt=time.time())
    if result['status'] == 'alert':
        result['ocr'] = alert_text(udid, out)
    if out:
        Path(out).mkdir(parents=True, exist_ok=True)
        q.save(Path(out)/'alert-check.json', result, replace=True)
    return result


def aatv(*args, out, name):
    env = dict(os.environ); env.pop('TVTESTRIG_PROJECT', None)
    r = subprocess.run([str(AATV), '--project', str(TTR), '--json', *args], capture_output=True, text=True, timeout=45, env=env)
    (out/f'{name}.stdout').write_text(r.stdout); (out/f'{name}.stderr').write_text(r.stderr[-20000:])
    data = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {}
    return r.returncode, data


def scene_trial(udid, app, bundle, out, arguments, snapshots=3):
    """Install, launch with SDK enrollment, read scene state and SDK snapshots, check alerts, then terminate."""
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    code, ready = aatv('simulator', 'readiness', '--simulator-udid', udid, out=out, name='readiness')
    readiness = next(iter(ready.get('data', {}).values()), {}).get('_0', {})
    q.require(code == 0 and readiness.get('can_run') is True, 'target_not_ready')
    install = subprocess.run(['xcrun', 'simctl', 'install', udid, app], capture_output=True, text=True, timeout=120)
    q.require(install.returncode == 0, 'install_failed:'+install.stderr[-300:])
    since = time.strftime('%Y-%m-%d %H:%M:%S')
    key = base64.b64encode(secrets.token_bytes(32)).decode()
    env = dict(os.environ, SIMCTL_CHILD_TTR_SAMPLE_KEY=key, SIMCTL_CHILD_SIMULATOR_UDID=udid)
    console = open(out/'console.stdout', 'w')
    launch = subprocess.Popen(['xcrun', 'simctl', 'launch', '--console-pty', '--terminate-running-process', udid, bundle, *arguments],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    identity, lines, result = None, [], dict(udid=udid, bundle=bundle, arguments=arguments, since=since)
    try:
        deadline = time.monotonic()+60
        while identity is None and time.monotonic() < deadline:
            line = launch.stdout.readline()
            if not line:
                break
            console.write(line); console.flush()
            if line.startswith('REAL543_SDK {'):
                identity = json.loads(line.split(' ', 1)[1])
        q.require(identity is not None, 'sdk_identity_missing')
        LOCAL.mkdir(parents=True, exist_ok=True)
        enrollment = LOCAL/f'{out.name}-enrollment.json'
        fd = os.open(enrollment, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(dict(appID=identity['appID'], processID=identity['processID'], runID=identity['runID'], secretBase64=key), f)
        reader = _Reader(launch, console, lines)
        rows = []
        for index in range(snapshots):
            time.sleep(2)
            code, data = aatv('sdk', 'snapshot', '--endpoint', identity['endpoint'], '--enrollment', str(enrollment), out=out, name=f'snapshot-{index}')
            inquiry = next(iter(data.get('data', {}).values()), {}).get('_0', {})
            rows.append(dict(returnCode=code, success=data.get('success'), state=inquiry.get('state'),
                             currentFocusKnown=inquiry.get('currentFocusKnown'), elements=len(inquiry.get('elements') or []),
                             issues=inquiry.get('issues')))
        time.sleep(0.5); reader.drain()
        scenes = [json.loads(l.split(' ', 1)[1]) for l in lines if l.startswith('REAL543_SCENE ')]
        result.update(identity=identity, snapshots=rows, scenes=scenes)
    finally:
        terminate = subprocess.run(['xcrun', 'simctl', 'terminate', udid, bundle], capture_output=True, text=True, timeout=30)
        launch.terminate(); console.close()
        result['cleanupCode'] = terminate.returncode
    result['alert'] = alert_check(udid, since, out)
    result['elapsedSeconds'] = time.monotonic()-started
    scenes = result.get('scenes', [])
    result['active'] = bool(scenes) and all(s['applicationState'] == 0 and s['windowSceneState'] == 0 and
                                            s['swiftUIScenePhase'] == 'active' for s in scenes)
    q.save(out/'trial.json', result)
    return result


DATA = q.ROOT/'dataset/real_apps/realapp554'
BUTTONS = {'up', 'down', 'left', 'right', 'select', 'back', 'playPause'}


def validate_plan(plan):
    q.require(plan.get('version') == 'realapp554-case-plan-v1' and plan.get('predictionViewed') is False, 'plan_identity')
    q.require(plan.get('dataRole') == 'pilot-evaluation' and plan.get('trainingEligible') is False, 'plan_role')
    ids = [c['id'] for f in plan['flows'] for c in f['cases']]
    q.require(ids and len(ids) == len(set(ids)) and all(q.ID.fullmatch(i) for i in ids), 'plan_case_identity')
    q.require(all(set(c['inputs']) <= BUTTONS for f in plan['flows'] for c in f['cases']), 'plan_input')
    q.require(sum(len(c['inputs']) for f in plan['flows'] for c in f['cases']) <= plan['budget']['inputs'], 'plan_input_budget')
    return plan


def launch_app(udid, bundle, arguments, out, name, sdk):
    """Start 1 fresh app process. With sdk, wait for the SDK identity and write a private enrollment."""
    key = base64.b64encode(secrets.token_bytes(32)).decode()
    env = dict(os.environ, SIMCTL_CHILD_TTR_SAMPLE_KEY=key, SIMCTL_CHILD_SIMULATOR_UDID=udid)
    console = open(out/f'{name}-console.stdout', 'w')
    process = subprocess.Popen(['xcrun', 'simctl', 'launch', '--console-pty', '--terminate-running-process', udid, bundle, *arguments],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    launched = dict(process=process, console=console, lines=[], identity=None, enrollment=None)
    if sdk:
        deadline = time.monotonic()+60
        while launched['identity'] is None and time.monotonic() < deadline:
            line = process.stdout.readline()
            if not line:
                break
            console.write(line); console.flush()
            if line.startswith('REAL543_SDK {'):
                launched['identity'] = json.loads(line.split(' ', 1)[1])
        q.require(launched['identity'] is not None, 'sdk_identity_missing')
        LOCAL.mkdir(parents=True, exist_ok=True)
        enrollment = LOCAL/f'{out.name}-{name}-enrollment.json'
        fd = os.open(enrollment, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            identity = launched['identity']
            json.dump(dict(appID=identity['appID'], processID=identity['processID'], runID=identity['runID'], secretBase64=key), f)
        launched['enrollment'] = enrollment
    launched['reader'] = _Reader(process, console, launched['lines'])
    return launched


def stop_app(udid, bundle, launched):
    r = subprocess.run(['xcrun', 'simctl', 'terminate', udid, bundle], capture_output=True, text=True, timeout=30)
    launched['process'].terminate(); launched['console'].close()
    return r.returncode


def sdk_rows(launched, out, name):
    code, data = aatv('sdk', 'snapshot', '--endpoint', launched['identity']['endpoint'], '--enrollment', str(launched['enrollment']), out=out, name=name)
    inquiry = next(iter(data.get('data', {}).values()), {}).get('_0', {})
    elements = sorted((e['identity']['id'], json.dumps(e['bounds'], sort_keys=True), e.get('selected')) for e in inquiry.get('elements') or [])
    return dict(returnCode=code, success=data.get('success'), state=inquiry.get('state'), focusKnown=inquiry.get('currentFocusKnown'),
                issues=sorted(i['code'] for i in inquiry.get('issues') or []), elements=elements, file=f'{name}.stdout')


def capture_case(plan, launched, out, case, since):
    """Record 1 settled case: SDK before, screenshot, SDK after, and system scene state. No retry."""
    time.sleep(plan['settleSeconds'])
    udid, sdk = plan['udid'], launched['identity'] is not None
    before = sdk_rows(launched, out, f"{case['id']}-sdk-before") if sdk else None
    local = LOCAL/out.name; local.mkdir(parents=True, exist_ok=True)
    image = local/f"{case['id']}.png"
    shot = subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(image)], capture_output=True, text=True, timeout=30)
    after = sdk_rows(launched, out, f"{case['id']}-sdk-after") if sdk else None
    record = dict(id=case['id'], flow=case['flow'], group=case['group'], expectedScreen=case['expectedScreen'], inputs=case['inputs'],
                  focus='unknown', focusSource='none: app hooks and remote observe do not report native focus identity')
    if shot.returncode != 0:
        return dict(record, status='failed', reason='screenshot_failed:'+shot.stderr[-300:])
    target = DATA/out.name/image.name; target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(image, target)
    q.require(q.digest(target) == q.digest(image), 'capture_copy_changed')
    system = alert_check(udid, since)
    app_scene = system.get('scenes', {}).get(plan['bundle']+'-default')
    scenes = [json.loads(l.split(' ', 1)[1]) for l in launched['lines'] if l.startswith('REAL543_SCENE ')]
    record.update(image=str(target), sha256=q.digest(target), ttrCopy=str(image), sdkBefore=before, sdkAfter=after,
                  appScene=scenes[-1] if scenes else None, systemScene=app_scene, alert=system['status'])
    live = lambda r: r['success'] and r['elements'] and 'live_evidence_unavailable' not in r['issues']
    stable = not sdk or (live(before) and live(after) and before['elements'] == after['elements'])
    active = system['status'] == 'clear' and app_scene is not None and app_scene['reasons'] == []
    ids = {e[0] for e in (before or {}).get('elements', [])}
    if active and stable and not set(case.get('expectedSDK', [])) <= ids:
        return dict(record, status='failed', reason='unexpected_screen')
    reason = None if active and stable else ('system_alert' if system['status'] != 'clear' else 'scene_inactive' if not active else
                                             'sdk_unavailable' if not (live(before) and live(after)) else 'sdk_changed_during_capture')
    return dict(record, status='captured' if reason is None else 'failed', reason=reason)


def run_session(plan_path, out):
    """Capture 1 frozen plan in 1 session. Each flow starts from a fresh launch. Inputs are never replayed."""
    plan = validate_plan(q.load(plan_path))
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    code, ready = aatv('simulator', 'readiness', '--simulator-udid', plan['udid'], out=out, name='readiness')
    q.require(code == 0 and next(iter(ready.get('data', {}).values()), {}).get('_0', {}).get('can_run') is True, 'target_not_ready')
    code, reply = aatv('simulator', 'remote', 'connect', '--simulator-udid', plan['udid'], out=out, name='remote-connect')
    q.require(code == 0 and reply.get('success'), 'remote_connect_failed:'+str(reply.get('error')))
    session = next(iter(reply['data'].values()))['_0']['operationID']
    records, inputs = [], 0
    try:
        for _ in range(24):
            code, status = aatv('simulator', 'remote', 'status', '--simulator-udid', plan['udid'], '--session', session, out=out, name='remote-status')
            state = (status.get('data') or {}).get('simulatorRemote', {}).get('_0', {}).get('state')
            if state != 'starting':
                break
            time.sleep(5)
        q.require(state == 'ready', f'remote_not_ready:{state}')
        for flow in plan['flows']:
            since = time.strftime('%Y-%m-%d %H:%M:%S')
            launched = launch_app(plan['udid'], plan['bundle'], plan['arguments'], out, flow['id'], plan['sdk'])
            try:
                time.sleep(plan['launchSettleSeconds'])
                failed = None
                for case in flow['cases']:
                    case = dict(case, flow=flow['id'], group=flow['group'])
                    if failed:
                        records.append(dict(id=case['id'], flow=flow['id'], status='failed', reason='previous_case_failed:'+failed)); continue
                    for button in case['inputs']:
                        q.require(time.monotonic()-started < plan['budget']['seconds'], 'session_time_budget')
                        inputs += 1
                        code, press = aatv('simulator', 'remote', 'press', '--simulator-udid', plan['udid'], '--session', session,
                                           '--button', button, out=out, name=f"{case['id']}-press-{inputs:03}")
                        if code != 0 or not press.get('success'):
                            failed = 'input_uncertain'; break
                        time.sleep(plan['inputSettleSeconds'])
                    if failed:
                        records.append(dict(id=case['id'], flow=flow['id'], status='failed', reason=failed)); continue
                    record = capture_case(plan, launched, out, case, since)
                    records.append(record)
                    if record['status'] == 'failed' and record['reason'] in ('system_alert', 'scene_inactive'):
                        failed = record['reason']
            finally:
                launched['reader'].drain()
                stop_app(plan['udid'], plan['bundle'], launched)
    finally:
        aatv('simulator', 'remote', 'disconnect', '--simulator-udid', plan['udid'], '--session', session, out=out, name='remote-disconnect')
        closed = None
        for _ in range(12):  # The next session needs this one closed. Readiness reports a closing session as active.
            closed = (aatv('simulator', 'remote', 'status', '--simulator-udid', plan['udid'], '--session', session, out=out,
                           name='remote-close')[1].get('data') or {}).get('simulatorRemote', {}).get('_0', {}).get('state')
            if closed == 'closed':
                break
            time.sleep(5)
        result = dict(version='realapp554-session-v1', plan=dict(path=str(Path(plan_path).resolve()), sha256=q.digest(plan_path)),
                      udid=plan['udid'], bundle=plan['bundle'], session=session, sessionClosed=closed == 'closed', inputs=inputs, cases=records,
                      captured=sum(r['status'] == 'captured' for r in records), failed=sum(r['status'] == 'failed' for r in records),
                      elapsedSeconds=time.monotonic()-started, trainingEligible=False, predictionViewed=False)
        q.save(out/'session.json', result)
    return result


def replay_sessions(sessions, out):
    """Replay each distinct captured frame once through `aatv visual replay`. Restore the NUIAK feature state."""
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    frames = {}
    for path in sessions:
        for case in q.load(path)['cases']:
            if case['status'] == 'captured':
                frames.setdefault(case['sha256'], []).append(dict(case=case['id'], session=str(path), ttrCopy=case['ttrCopy']))
    code, status = aatv('status', out=out, name='status-before')
    q.require(code == 0 and next(iter(status['data'].values()))['_0'].get('commandActive') is False, 'ttr_busy')
    code, before = aatv('features', 'status', out=out, name='features-before')
    enabled = next(iter(before['data'].values()))['_0']['enabled']
    work = LOCAL/out.name; work.mkdir(parents=True, exist_ok=False)
    rows = []
    try:
        if not enabled:
            code, reply = aatv('features', 'set', 'nuiak', 'on', out=out, name='features-enabled')
            q.require(code == 0 and reply.get('success'), 'feature_enable_failed')
        for sha256, cases in frames.items():
            name = cases[0]['case']
            source = Path(cases[0]['ttrCopy'])
            q.require(q.digest(source) == sha256, 'replay_source_changed')
            manifest = work/f'{name}-input.json'
            manifest.write_text(json.dumps(dict(source_sha256=sha256), indent=2))
            target = work/name
            code, reply = aatv('visual', 'replay', '--source', str(source.relative_to(TTR)), '--manifest', str(manifest.relative_to(TTR)),
                               '--output', str(target.relative_to(TTR)), out=out, name=f'{name}-response')
            row = dict(sha256=sha256, cases=[c['case'] for c in cases], returnCode=code, success=reply.get('success'), error=reply.get('error'))
            if code == 0 and reply.get('success'):
                shutil.copytree(target, out/name)
                row.update(export=str((out/name).relative_to(q.ROOT)), **{k: v for k, v in next(iter(reply['data'].values()))['_0'].items()
                                                                       if k in ('requestToResultDurableMS', 'selectionStatus', 'resultSHA256')})
            rows.append(row)
    finally:
        restore = None
        if not enabled:
            code, reply = aatv('features', 'set', 'nuiak', 'off', out=out, name='features-restored')
            restore = code == 0 and reply.get('success')
        q.save(out/'replays.json', dict(version='realapp554-replays-v1', sessions=[str(p) for p in sessions], featureWasEnabled=enabled,
                                        featureRestored=restore, frames=rows, trainingEligible=False))
    return rows


class _Reader:
    """Collect console lines without blocking the snapshot loop."""
    def __init__(self, process, console, lines):
        import threading
        self.process, self.console, self.lines = process, console, lines
        self.thread = threading.Thread(target=self.run, daemon=True); self.thread.start()

    def run(self):
        for line in self.process.stdout:
            self.lines.append(line.rstrip('\n'))
            if not self.console.closed:
                self.console.write(line)

    def drain(self):
        self.console.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    a = sub.add_parser('alert-check'); a.add_argument('--udid', required=True); a.add_argument('--since'); a.add_argument('--out', type=Path)
    s = sub.add_parser('scene-trial'); s.add_argument('--udid', required=True); s.add_argument('--app', required=True)
    s.add_argument('--bundle', required=True); s.add_argument('--out', type=Path, required=True)
    s.add_argument('--snapshots', type=int, default=3); s.add_argument('arguments', nargs='*')
    c = sub.add_parser('session'); c.add_argument('--plan', type=Path, required=True); c.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'session':
        result = run_session(args.plan, args.out)
        print(json.dumps(dict(captured=result['captured'], failed=result['failed'], inputs=result['inputs'], seconds=round(result['elapsedSeconds']),
                              cases=[(r['id'], r['status'], r.get('reason')) for r in result['cases']]), indent=1))
        return
    if args.command == 'alert-check':
        result = alert_check(args.udid, args.since, args.out)
        print(json.dumps({k: v for k, v in result.items() if k != 'scenes'}, indent=1))
        sys.exit(0 if result['status'] == 'clear' else 1)
    result = scene_trial(args.udid, args.app, args.bundle, args.out, args.arguments, args.snapshots)
    print(json.dumps(dict(active=result['active'], alert=result['alert']['status'], snapshots=result.get('snapshots'),
                          scenes=result.get('scenes', [])[-1:], cleanupCode=result['cleanupCode']), indent=1))


if __name__ == '__main__':
    main()
