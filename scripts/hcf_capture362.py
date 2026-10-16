"""Capture native OS profiles through the existing queue and qualified TTR caller."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import uuid
import time

from PIL import Image
import research_queue as q
import direct_tvos_capture as d
import native343 as n
import dataset351
from focus_batch_harness import lock
from qualify_hcf362 import Client, TTR, CLI

OUT = None


def save_native_screenshot(path):
    """Stage one screenshot locally. Verify the copy before removing the staging file."""
    d.capture_screenshot(n.TARGET, path, timeout=15)


def verified_profile(value, desired):
    row = value.get('hcf', {})
    q.require(row.get('status') == 'completed' and row.get('desiredVerified') is True,
              'os_profile_unverified')
    q.require(row.get('requested') == row.get('observed') == desired, 'os_profile_wrong')
    q.require(row.get('original') in ('standard', 'hcf') and row.get('mode') == 'ensure', 'os_profile_original')
    q.require(row.get('policy') == 'hcf-setting-en-us-23L470-v1', 'os_profile_policy')
    return row


def validate_plan(plan):
    if plan.get('version') in ('native-hcf371-v1', 'native-hcf402-v1', 'native-controls-t45-v1'):
        from hcf_study371 import validate_capture_plan
        return validate_capture_plan(plan)
    q.require(plan['version'] == 'native-hcf362-v1', 'plan_version')
    q.require(plan['binding']['simulatorUDID'] == n.TARGET and
              plan['binding']['endpoint'] == 'http://127.0.0.1:8080', 'target')
    q.require(plan['role'] == 'development' and plan['trainingEligible'] is False, 'pilot_role')
    q.require(plan['profiles'] == ['standard', 'hcf'] and len(plan['targets']) == 2 and
              len(set(plan['targets'])) == 2 and plan['expectedFrames'] == 8, 'pilot_counts')
    styles = plan['recipe']['appearance']['composition']['styles']
    q.require(styles and all(s.get('focus', {}).get('kind') in ('native_image', 'native_button')
              for s in styles.values()), 'authored_focus_forbidden')
    q.require(plan['qualification']['complete'] and plan['qualification']['restoration'] == 'verified',
              'caller_unqualified')


def capture(output, plan):
    validate_plan(plan)
    q.require(q.digest(CLI.resolve()) == plan['helperSHA256'], 'helper_changed')
    q.require(d.bind_target(n.TARGET, plan['binding']['endpoint']) == plan['binding'], 'fixture_changed')
    output.mkdir()
    q.save(output/'plan.json', plan)
    f = d.Fixture(plan['binding']['endpoint'])
    if plan.get('normalizeSettings'):
        from hcf_settings368 import Client as NavigationClient
        c = NavigationClient(output)
    else:
        c = Client(output)
    session = None
    original_profile = None
    changed_profile = False
    original = f.snapshot()
    frames = []
    profiles = []
    error = None
    cleanup = False
    started = time.monotonic()
    current = original
    cases = plan.get('cases', [dict(id='', recipe=plan.get('recipe'), targets=plan.get('targets'))])
    repeats = plan.get('repeats', 2)
    expected = plan['expectedFrames']
    progress_path = Path(plan['progressPath']) if plan.get('progressPath') else output.parent.parent/'progress.json'
    activated = False
    closed = False
    runtime = TTR/'Diagnostics/Runtime'
    runtime_start = q.live_output_bytes(runtime)
    map_root = TTR/'.local-work/nuiak-hcf362/hcf-map'
    map_start = q.live_output_bytes(map_root)

    def budget():
        q.require(time.monotonic()-started < 580, 'capture_deadline')
        q.require(q.live_output_bytes(output) < plan.get('captureBudgetBytes', 90_000_000), 'capture_output_limit')
        if plan.get('storage'):
            from hcf_study371 import verify_storage
            verify_storage(plan['storage'])
        q.require(shutil.disk_usage(TTR).free > 3*(1<<30), 'native_storage_reserve')
        retained = q.live_output_bytes(runtime)-runtime_start + q.live_output_bytes(map_root)-map_start
        q.require(retained < 700_000_000, 'native_receipt_budget')

    def setting(desired):
        nonlocal activated
        activated = True
        d.run(['xcrun', 'simctl', 'launch', n.TARGET, 'com.apple.TVSettings'])
        value = c.call('profile-'+desired, 'route', 'hcf', '--desired', desired, '--mode', 'ensure',
                       '--map-dir', str(TTR/'.local-work/nuiak-hcf362/hcf-map'),
                       '--simulator-udid', n.TARGET, '--session', session)
        row = verified_profile(value, desired)
        profiles.append(dict(profile=desired, time=time.time(), receipt=value))
        return row

    with lock():
        try:
            ready = c.call('readiness', 'simulator', 'readiness', '--simulator-udid', n.TARGET)
            q.require(ready['can_run'] and all(x['state'] == 'clear' for x in ready['ownership']), 'target_busy')
            receipt = c.remote('connect'); session = receipt['operationID']
            c.terminal(receipt, 'ready')
            for profile in plan['profiles']:
                budget()
                # Record the original before any change. A Standard ensure can itself change HCF.
                if original_profile is None:
                    q.require(plan['originalProfile'] == 'standard', 'original_profile_not_qualified')
                    # The first request verifies Standard without trusting the saved value.
                    value = setting('standard')
                    original_profile = value['original']
                    q.save(output/'original-profile.json', dict(value=original_profile, receipt=profiles[-1]))
                else:
                    changed_profile = True
                    setting(profile)
                d.run(['xcrun', 'simctl', 'launch', n.TARGET, d.BUNDLE])
                q.require(n.identity(f.snapshot())[:3] == n.identity(original)[:3], 'fixture_process_changed')
                for case_index, case in enumerate(cases):
                    f.request('/recipe', case['recipe'])
                    current = f.snapshot()
                    dataset351.wait_loaded(f, current, output, len(profiles)*100+case_index)
                    for target in case['targets']:
                      f.request('/focus/set', {'element_id': target, 'settle_time_ms': 150})
                      for repeat in range(repeats):
                        budget()
                        before = n.settle(f, current, target)
                        signature = n.signature(before, current, target)
                        prefix = case['id']+'-' if case['id'] else ''
                        name = f'{prefix}{profile}-{target}-{repeat}.png'
                        path = output/name
                        begin = time.time()
                        d.capture_screenshot(n.TARGET, path, timeout=15)
                        end = time.time()
                        after = f.snapshot()
                        q.require(n.signature(after, current, target) == signature, 'capture_bracket_changed')
                        with Image.open(path) as image:
                            image.load()
                            q.require(list(image.size) == signature[2], 'image_dimensions')
                        frames.append(dict(id=path.stem, path=name, sha256=q.digest(path), profile=profile,
                            focus=target, repeat=repeat, before=before, after=after, start=begin, end=end,
                            profileReceipt=copy.deepcopy(profiles[-1]), case=case['id']))
                        q.save(progress_path, dict(step='Native HCF capture: '+path.stem,
                            completed=len(frames), total=expected, updatedAt=time.time()), replace=True)
            # Recheck HCF after the block. A stale profile receipt is not sufficient.
            setting('hcf')
        except Exception as exc:
            error = str(exc)
            try:
                q.save(output/'failure-scene.json', f.snapshot())
            except Exception as snapshot_error:
                q.save(output/'failure-observation-error.json', dict(error=str(snapshot_error)[:500]))
        finally:
            failures = []
            if session:
                try:
                    if original_profile is not None:
                        setting(original_profile)
                    elif changed_profile:
                        raise ValueError('original_profile_unknown')
                except Exception as exc:
                    failures.append('profile_restore:'+str(exc))
                try:
                    c.terminal(c.remote('disconnect', session), 'closed')
                    closed = True
                except Exception as exc:
                    failures.append('disconnect:'+str(exc))
            try:
                if activated and closed:
                    d.run(['xcrun', 'simctl', 'launch', n.TARGET, d.BUNDLE])
                    q.require(n.identity(f.snapshot())[:3] == n.identity(original)[:3], 'restore_process_changed')
                    f.request('/recipe', dataset351.clean(original['scene']['recipe']))
                    restored = f.snapshot()
                    target = original['scene']['focused_element_id']
                    f.request('/focus/set', {'element_id': target, 'settle_time_ms': 150})
                    n.settle(f, restored, target)
                ready = c.call('postflight', 'simulator', 'readiness', '--simulator-udid', n.TARGET)
                q.require(ready['can_run'] and all(x['state'] == 'clear' for x in ready['ownership']), 'postflight_not_clear')
            except Exception as exc:
                failures.append('fixture_restore:'+str(exc))
            cleanup = not failures and original_profile is not None
            q.save(output/'capture.json', dict(version=plan['version'], complete=not error and cleanup and len(frames)==expected,
                cleanup=cleanup, error=error, cleanupErrors=failures, frames=frames, profileReceipts=profiles,
                originalProfile=original_profile, group=plan['group'], role=plan['role'], trainingEligible=False,
                modelAccepted=False, seconds=time.monotonic()-started,
                nativeReceiptBytes=q.live_output_bytes(runtime)-runtime_start + q.live_output_bytes(map_root)-map_start,
                nativeReceiptBudgetBytes=1<<30))
    q.require(not error and cleanup and len(frames)==expected, error or str(failures))


def compare():
    import numpy as np
    from hcf361 import measure
    deps = q.load(OUT/'dependencies.json')
    q.require(len(deps) == 1, 'dependency_count')
    ref = deps[0]['outputs'][0]
    path = q.ROOT/ref['path']
    q.require(q.digest(path) == ref['sha256'], 'capture_changed')
    doc = q.load(path)
    q.require(doc['complete'] and doc['cleanup'] and len(doc['frames']) == 8, 'capture_incomplete')
    images = {}
    for frame in doc['frames']:
        p = path.parent/frame['path']
        q.require(q.digest(p) == frame['sha256'], 'image_changed')
        with Image.open(p) as image:
            images[frame['profile'], frame['focus'], frame['repeat']] = np.asarray(image.convert('RGB'))
    rows = []
    for target in sorted({key[1] for key in images}):
        row = dict(target=target, standardRepeat=measure(images['standard', target, 0], images['standard', target, 1]),
            hcfRepeat=measure(images['hcf', target, 0], images['hcf', target, 1]),
            profileDifference=measure(images['standard', target, 0], images['hcf', target, 0]))
        rows.append(row)
    q.save(OUT/'summary.json', dict(rows=rows, trainingEligible=False, modelAccepted=False,
        decision='Review whether profile changes follow the focused control before scaling.',
        limitation='Whole-frame pixel changes are not proof of an HCF cue or Office transfer.'))
