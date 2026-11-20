"""RESET604 T1.1: Blinded tvOS system screen capture for TVBench v1 sealed split.

Follows `tvtestrig` and `tvos-safe-navigation` safety rules:
- Preflights PineBoard system alerts (`real_app_session554.alert_check`).
- Never displays sealed screenshots or records model predictions.
- Checks Vision OCR locally only to enforce the `FORBIDDEN_KEYWORDS` blocklist
  and a narrow read-only Settings submenu allowlist before any `select`.
- Deduplicates captures blindly with 48 x 27 grayscale signatures (`diff_threshold=2.0`).

Usage:
  tvbench_sealed_capture604.py [--target-count 20] [--udid 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA]
"""
import os
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

import real_app_session554 as sess554
import research_queue as q
import tvbench_sealed_prep604 as sp

VERSION = 'tvbench-sealed-capture-v1'
DEFAULT_AATV = Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig')) / '.local-work/artparity595/DerivedData/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv'
DEFAULT_TTR = Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig'))
DEFAULT_UDID = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
DEFAULT_OUT = q.ROOT / 'dataset/real_apps/tvbench-v1/sealed-captures'
OCR_SCRIPT = q.ROOT / 'scripts/ocr_helper.swift'

FORBIDDEN_KEYWORDS = re.compile(
    r'\b(Reset|Erase|Format|Update|Delete|Remove|Sign Out|Add Profile|Add New|'
    r'Purchase|Restore|Terms|Agree|Offload|Restart|Sleep|Calibrate|Check HDMI)\b',
    re.IGNORECASE,
)

SAFE_SUBMENUS = {
    'General',
    'Users and Accounts',
    'Video and Audio',
    'AirPlay and Apple Home',
    'Remotes and Devices',
    'Accessibility',
    'Privacy & Security',
    'Apps',
    'Screensaver',
    'About',
    'Legal & Regulatory',
    'Language & Region',
    'Appearance',
    'Screen Time',
    'Display',
    'Motion',
}


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def text_is_safe(ocr_text):
    """Return False if any forbidden destructive keyword appears in OCR output."""
    return not bool(FORBIDDEN_KEYWORDS.search(ocr_text or ''))


def matching_safe_submenu(ocr_text, exclude=None):
    """Return matched read-only submenu name only when no forbidden keyword is present."""
    if not text_is_safe(ocr_text):
        return None
    skip = set(exclude or ())
    for line in (ocr_text or '').splitlines():
        s = line.strip()
        if s in SAFE_SUBMENUS and s not in skip:
            return s
    return None


def _run_aatv(aatv, ttr, args, timeout=45):
    import os
    env = dict(os.environ)
    env.pop('TVTESTRIG_PROJECT', None)
    cmd = [str(aatv), '--project', str(ttr), '--json', *args]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    payload = {}
    for line in res.stdout.splitlines():
        if line.lstrip().startswith('{'):
            try:
                payload = json.loads(res.stdout[res.stdout.index(line):])
            except Exception:
                pass
            break
    return res.returncode == 0, payload


def _connect_simulator_remote(aatv, ttr, udid):
    ok_ready, ready = _run_aatv(aatv, ttr, ['simulator', 'readiness', '--simulator-udid', udid])
    can_run = ok_ready and next(iter((ready.get('data') or {}).values()), {}).get('_0', {}).get('can_run') is True
    q.require(can_run, f'simulator_not_ready:{ready}')
    ok_conn, reply = _run_aatv(aatv, ttr, ['simulator', 'remote', 'connect', '--simulator-udid', udid])
    q.require(ok_conn and reply.get('success'), f'simulator_remote_connect_failed:{reply}')
    session = next(iter(reply['data'].values()))['_0']['operationID']
    state = None
    for _ in range(24):
        _, status = _run_aatv(aatv, ttr, ['simulator', 'remote', 'status', '--simulator-udid', udid, '--session', session])
        state = (status.get('data') or {}).get('simulatorRemote', {}).get('_0', {}).get('state')
        if state != 'starting':
            break
        time.sleep(5)
    q.require(state == 'ready', f'simulator_remote_not_ready:{state}')
    return session


def _press_button(aatv, ttr, udid, session, button):
    ok, reply = _run_aatv(
        aatv, ttr,
        ['simulator', 'remote', 'press', '--simulator-udid', udid, '--session', session, '--button', button],
    )
    q.require(ok and reply.get('success'), f'simulator_press_failed:{button}:{reply}')


def _disconnect_simulator_remote(aatv, ttr, udid, session):
    _run_aatv(aatv, ttr, ['simulator', 'remote', 'disconnect', '--simulator-udid', udid, '--session', session])
    for _ in range(12):
        _, status = _run_aatv(aatv, ttr, ['simulator', 'remote', 'status', '--simulator-udid', udid, '--session', session])
        if (status.get('data') or {}).get('simulatorRemote', {}).get('_0', {}).get('state') == 'closed':
            break
        time.sleep(2)


def _ocr_text(image_path):
    res = subprocess.run(['swift', str(OCR_SCRIPT), str(image_path), '--json'], capture_output=True, text=True, timeout=60)
    if res.returncode != 0 or not res.stdout.strip().startswith('{'):
        return ''
    doc = json.loads(res.stdout)
    return '\n'.join(r.get('text', '') for r in doc.get('regions', []))


def _capture_if_distinct(udid, tmp_png, accepted_sigs, accepted_shas, diff_threshold=2.0):
    subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
    sha = sha256_file(tmp_png)
    if sha in accepted_shas:
        return None, ''
    sig, dims = sp.grayscale_signature(tmp_png)
    for prev_sig in accepted_sigs:
        if sp.mean_abs_diff(sig, prev_sig) <= diff_threshold:
            return None, ''
    ocr = _ocr_text(tmp_png)
    accepted_sigs.append(sig)
    accepted_shas.add(sha)
    return dict(sha256=sha, dims=dims, ocrSafe=text_is_safe(ocr)), ocr


def is_pineboard_home(ocr_text):
    """Heuristic context-lock check for unexpected escape to PineBoard home screen."""
    text = ocr_text or ''
    return ('App Store' in text and 'Settings' in text and 'Photos' in text) or ('TVTestRigFixture' in text and 'Settings' in text)


def _load_capture_state(out_dir):
    """Load existing sealed captures plus dev + RC561 signatures to prevent duplicate/exposed captures."""
    accepted_shas, accepted_sigs, captured = set(), [], []
    existing_manifest = Path(out_dir) / 'manifest.json'
    if existing_manifest.is_file():
        for c in q.load(existing_manifest).get('cases', []):
            abs_img = q.ROOT / c['image']
            if abs_img.is_file():
                sig, _ = sp.grayscale_signature(abs_img)
                accepted_sigs.append(sig)
                accepted_shas.add(c['sha256'])
                captured.append(c)
    for manifest_name in ('dev-manifest.json', 'dev-manifest-v2.json'):
        mpath = q.ROOT / 'dataset/real_apps/tvbench-v1' / manifest_name
        if mpath.is_file():
            for c in q.load(mpath).get('cases', []):
                accepted_shas.add(c['image']['sha256'])
                abs_img = q.ROOT / c['image']['path']
                if abs_img.is_file():
                    sig, _ = sp.grayscale_signature(abs_img)
                    accepted_sigs.append(sig)
    rc561_path = q.ROOT / 'reports/work/RC561/holdout/manifest.json'
    if rc561_path.is_file():
        for c in q.load(rc561_path).get('cases', []):
            accepted_shas.add(c['sha256'])
            abs_img = q.ROOT / c['image']
            if abs_img.is_file():
                sig, _ = sp.grayscale_signature(abs_img)
                accepted_sigs.append(sig)
    return accepted_shas, accepted_sigs, captured


def capture_tvos_system_screens(
    out_dir=DEFAULT_OUT,
    target_count=20,
    udid=DEFAULT_UDID,
    aatv=DEFAULT_AATV,
    ttr=DEFAULT_TTR,
    diff_threshold=2.0,
):
    """Safely capture distinct tvOS Settings + PineBoard system screens without inspecting pixels."""
    out_dir = Path(out_dir)
    sys_dir = out_dir / 'tvos-system'
    sys_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(ttr) / '.local-work/reset604/tvbench-sealed-tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_png = tmp_dir / 'probe.png'

    # Preflight alert check
    alert = sess554.alert_check(udid, out=tmp_dir)
    q.require(alert['status'] == 'clear', f"sealed_capture_blocked_by_alert:{alert['status']}")

    # Load existing dev + prior sealed captures so reruns append instead of overwriting
    accepted_shas, accepted_sigs, captured = _load_capture_state(out_dir)

    session = _connect_simulator_remote(aatv, ttr, udid)
    print(f'[sealed-capture] connected session={session} existing={len(captured)}', flush=True)

    def try_save(app_bundle, flow_tag):
        if len(captured) >= target_count:
            return None, ''
        rec, ocr = _capture_if_distinct(udid, tmp_png, accepted_sigs, accepted_shas, diff_threshold=diff_threshold)
        if rec is None:
            return None, ocr
        idx = len(captured)
        dst = sys_dir / f'system-{idx:03d}.png'
        shutil.copy2(tmp_png, dst)
        captured.append(dict(
            id=f'tvos-system-{idx:03d}',
            app=app_bundle,
            flow=flow_tag,
            image=str(dst.relative_to(q.ROOT)),
            sha256=rec['sha256'],
            width=rec['dims'][0],
            height=rec['dims'][1],
            capturedAt=time.time(),
        ))
        print(f'[sealed-capture] saved {len(captured)}/{target_count} ({app_bundle}:{flow_tag})', flush=True)
        return captured[-1], ocr

    try:
        # 1. PineBoard home screen(s) via termination + directional shelf/grid moves
        subprocess.run(['xcrun', 'simctl', 'terminate', udid, 'com.apple.TVSettings'], capture_output=True)
        time.sleep(1.5)
        try_save('com.apple.PineBoard', 'pineboard-home')
        for btn in ('right', 'right', 'down', 'right', 'down', 'left', 'down'):
            if len(captured) >= target_count:
                break
            _press_button(aatv, ttr, udid, session, btn)
            time.sleep(0.8)
            try_save('com.apple.PineBoard', 'pineboard-browse')

        # 2. TVSettings: crawl root + safe read-only submenus using strict FORBIDDEN_KEYWORDS gate
        subprocess.run(['xcrun', 'simctl', 'launch', udid, 'com.apple.TVSettings'], capture_output=True, check=True)
        time.sleep(1.8)
        _, root_ocr = try_save('com.apple.TVSettings', 'settings-root')

        # Enter top read-only Settings rows one at a time, only scrolling/backtracking if a submenu actually opened
        for row_idx in range(9):
            if len(captured) >= target_count:
                break
            if text_is_safe(root_ocr):
                subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
                before_sig, _ = sp.grayscale_signature(tmp_png)
                _press_button(aatv, ttr, udid, session, 'select')
                time.sleep(1.0)
                subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
                after_sig, _ = sp.grayscale_signature(tmp_png)
                entered_sub = sp.mean_abs_diff(before_sig, after_sig) > 2.0
                if entered_sub:
                    sub_text = _ocr_text(tmp_png)
                    if text_is_safe(sub_text):
                        sub_slug = 'settings-sub'
                        matched_sub = matching_safe_submenu(sub_text)
                        if matched_sub:
                            sub_slug = 'settings-' + re.sub(r'[^a-z0-9]+', '-', matched_sub.lower()).strip('-')
                        _, sub_ocr = try_save('com.apple.TVSettings', sub_slug)
                        for _ in range(5):
                            if len(captured) >= target_count or not text_is_safe(sub_ocr):
                                break
                            # Optionally drill into safe level-2 subviews (e.g. About, Display, Motion)
                            subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
                            b2_sig, _ = sp.grayscale_signature(tmp_png)
                            _press_button(aatv, ttr, udid, session, 'select')
                            time.sleep(0.9)
                            subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
                            a2_sig, _ = sp.grayscale_signature(tmp_png)
                            if sp.mean_abs_diff(b2_sig, a2_sig) > 2.0:
                                s2_ocr = _ocr_text(tmp_png)
                                if text_is_safe(s2_ocr) and not is_pineboard_home(s2_ocr):
                                    _, s2_ocr = try_save('com.apple.TVSettings', f'{sub_slug}-l2')
                                    for _ in range(3):
                                        if len(captured) >= target_count or not text_is_safe(s2_ocr):
                                            break
                                        _press_button(aatv, ttr, udid, session, 'down')
                                        time.sleep(0.6)
                                        _, s2_ocr = try_save('com.apple.TVSettings', f'{sub_slug}-l2')
                                _press_button(aatv, ttr, udid, session, 'back')
                                time.sleep(0.7)
                            _press_button(aatv, ttr, udid, session, 'down')
                            time.sleep(0.7)
                            _, sub_ocr = try_save('com.apple.TVSettings', sub_slug)
                    _press_button(aatv, ttr, udid, session, 'back')
                    time.sleep(0.8)
            _press_button(aatv, ttr, udid, session, 'down')
            time.sleep(0.7)
            _, root_ocr = try_save('com.apple.TVSettings', 'settings-root')
    finally:
        subprocess.run(['xcrun', 'simctl', 'terminate', udid, 'com.apple.TVSettings'], capture_output=True)
        _disconnect_simulator_remote(aatv, ttr, udid, session)
        if tmp_png.exists():
            tmp_png.unlink()

    manifest = dict(version=VERSION, count=len(captured), cases=captured)
    q.save(out_dir / 'manifest.json', manifest, replace=True)
    return dict(version=VERSION, capturedCount=len(captured), outDir=str(out_dir))


DEFAULT_SEALED_APPS = (
    ('com.example.apple-samplecode.TVCatalog', 'tvcatalog'),
    ('com.thatcube.Plozz', 'plozz'),
    ('org.nuiak.rc561.strimr', 'strimr'),
)


def capture_tvos_app_screens(
    out_dir=DEFAULT_OUT,
    apps=DEFAULT_SEALED_APPS,
    per_app_target=25,
    max_total=100,
    udid=DEFAULT_UDID,
    aatv=DEFAULT_AATV,
    ttr=DEFAULT_TTR,
    diff_threshold=2.0,
):
    """Safely capture distinct blinded screens across installed sealed tvOS apps."""
    out_dir = Path(out_dir)
    apps_dir = out_dir / 'apps'
    apps_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(ttr) / '.local-work/reset604/tvbench-sealed-app-tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_png = tmp_dir / 'probe.png'

    alert = sess554.alert_check(udid, out=tmp_dir)
    q.require(alert['status'] == 'clear', f"sealed_capture_blocked_by_alert:{alert['status']}")

    accepted_shas, accepted_sigs, captured = _load_capture_state(out_dir)
    session = _connect_simulator_remote(aatv, ttr, udid)
    added_by_app = {}

    def _try_save(bundle_id, slug, flow_tag, app_added):
        if len(captured) >= max_total or app_added >= per_app_target:
            return False, ''
        rec, ocr = _capture_if_distinct(udid, tmp_png, accepted_sigs, accepted_shas, diff_threshold=diff_threshold)
        if rec is None or is_pineboard_home(ocr):
            return False, ocr
        idx = len(captured)
        dst = apps_dir / f'{slug}-{idx:03d}.png'
        shutil.copy2(tmp_png, dst)
        captured.append(dict(
            id=f'{slug}-{idx:03d}',
            app=bundle_id,
            flow=flow_tag,
            image=str(dst.relative_to(q.ROOT)),
            sha256=rec['sha256'],
            width=rec['dims'][0],
            height=rec['dims'][1],
            capturedAt=time.time(),
        ))
        print(f'[sealed-app-capture] saved {len(captured)}/{max_total} ({bundle_id}:{flow_tag})', flush=True)
        return True, ocr

    moves = (
        'down', 'right', 'right', 'down', 'left', 'up', 'up', 'up',
        'left', 'down', 'down', 'right', 'down', 'left', 'up', 'right', 'right', 'right', 'down',
    )
    try:
        for bundle_id, slug in apps:
            if len(captured) >= max_total:
                break
            app_added = 0
            launch = subprocess.run(['xcrun', 'simctl', 'launch', udid, bundle_id], capture_output=True, text=True)
            if launch.returncode != 0:
                print(f'[sealed-app-capture] skip {bundle_id}: launch failed', flush=True)
                continue
            time.sleep(2.5)
            try:
                saved, cur_ocr = _try_save(bundle_id, slug, f'{slug}-launch', app_added)
                app_added += int(saved)
                # Walk top TabBar tabs systematically first (up to 4 tabs)
                for tab_idx in range(4):
                    if len(captured) >= max_total or app_added >= per_app_target:
                        break
                    for _ in range(4):
                        _press_button(aatv, ttr, udid, session, 'up')
                        time.sleep(0.35)
                    for _ in range(tab_idx):
                        _press_button(aatv, ttr, udid, session, 'right')
                        time.sleep(0.4)
                    saved_tab, cur_ocr = _try_save(bundle_id, slug, f'{slug}-tab-{tab_idx}', app_added)
                    app_added += int(saved_tab)
                    if is_pineboard_home(cur_ocr):
                        subprocess.run(['xcrun', 'simctl', 'launch', udid, bundle_id], capture_output=True)
                        time.sleep(1.5)
                        break
                    for _ in range(4):
                        if len(captured) >= max_total or app_added >= per_app_target:
                            break
                        _press_button(aatv, ttr, udid, session, 'down')
                        time.sleep(0.7)
                        s_dn, cur_ocr = _try_save(bundle_id, slug, f'{slug}-tab-{tab_idx}-down', app_added)
                        app_added += int(s_dn)
                    for _ in range(3):
                        if len(captured) >= max_total or app_added >= per_app_target:
                            break
                        _press_button(aatv, ttr, udid, session, 'right')
                        time.sleep(0.7)
                        s_rt, cur_ocr = _try_save(bundle_id, slug, f'{slug}-tab-{tab_idx}-right', app_added)
                        app_added += int(s_rt)

                # Bounded directional exploration + safe select drill-ins
                for step_i, btn in enumerate(moves):
                    if len(captured) >= max_total or app_added >= per_app_target:
                        break
                    _press_button(aatv, ttr, udid, session, btn)
                    time.sleep(0.9)
                    saved, cur_ocr = _try_save(bundle_id, slug, f'{slug}-nav-{btn}', app_added)
                    app_added += int(saved)
                    if is_pineboard_home(cur_ocr):
                        subprocess.run(['xcrun', 'simctl', 'launch', udid, bundle_id], capture_output=True)
                        time.sleep(1.5)
                        continue
                    if text_is_safe(cur_ocr) and (step_i % 2 == 0) and app_added < per_app_target and len(captured) < max_total:
                        subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
                        before_sig, _ = sp.grayscale_signature(tmp_png)
                        _press_button(aatv, ttr, udid, session, 'select')
                        time.sleep(1.1)
                        subprocess.run(['xcrun', 'simctl', 'io', udid, 'screenshot', str(tmp_png)], capture_output=True, timeout=30, check=True)
                        after_sig, _ = sp.grayscale_signature(tmp_png)
                        if sp.mean_abs_diff(before_sig, after_sig) > diff_threshold:
                            sub_ocr = _ocr_text(tmp_png)
                            if not is_pineboard_home(sub_ocr) and text_is_safe(sub_ocr):
                                s_sub, _ = _try_save(bundle_id, slug, f'{slug}-detail', app_added)
                                app_added += int(s_sub)
                                for sub_btn in ('right', 'down'):
                                    if len(captured) >= max_total or app_added >= per_app_target:
                                        break
                                    _press_button(aatv, ttr, udid, session, sub_btn)
                                    time.sleep(0.8)
                                    s_d, sub_ocr = _try_save(bundle_id, slug, f'{slug}-detail-{sub_btn}', app_added)
                                    app_added += int(s_d)
                            _press_button(aatv, ttr, udid, session, 'back')
                            time.sleep(0.9)
            finally:
                subprocess.run(['xcrun', 'simctl', 'terminate', udid, bundle_id], capture_output=True)
                time.sleep(0.6)
            added_by_app[bundle_id] = app_added
    finally:
        _disconnect_simulator_remote(aatv, ttr, udid, session)
        if tmp_png.exists():
            tmp_png.unlink()

    manifest = dict(version=VERSION, count=len(captured), cases=captured)
    q.save(out_dir / 'manifest.json', manifest, replace=True)
    return dict(version=VERSION, capturedCount=len(captured), addedByApp=added_by_app, outDir=str(out_dir))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('system', 'apps'), default='system')
    parser.add_argument('--target-count', type=int, default=20)
    parser.add_argument('--per-app-target', type=int, default=25)
    parser.add_argument('--udid', default=DEFAULT_UDID)
    parser.add_argument('--diff-threshold', type=float, default=2.0)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if args.mode == 'apps':
        res = capture_tvos_app_screens(
            out_dir=args.out, per_app_target=args.per_app_target, max_total=args.target_count,
            udid=args.udid, diff_threshold=args.diff_threshold,
        )
    else:
        res = capture_tvos_system_screens(
            out_dir=args.out, target_count=args.target_count, udid=args.udid, diff_threshold=args.diff_threshold,
        )
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()
