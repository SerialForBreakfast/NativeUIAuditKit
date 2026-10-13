"""Capture bounded controlled scenes through the existing Fixture interfaces."""
import argparse
import copy
import time
from pathlib import Path
from PIL import Image
import direct_tvos_capture as d
import native343 as n
import research_queue as q
from focus_batch_harness import lock


def clean(recipe):
    value = copy.deepcopy(recipe)
    value.pop('recipe_hash', None)
    value['appearance'].pop('family_id', None)
    return value


def recipes(original):
    result = []
    for position in ('corners', 'center'):
        for effect in ('native', 'growth', 'border', 'combined'):
            value = clean(original)
            composition = value['appearance']['composition']
            q.require(composition['version'] == 5 and len(composition['regions']) == 4, 'unsupported_scene')
            if position == 'center':
                for region, (x, y) in zip(composition['regions'], ((550, 250), (1050, 250), (550, 650), (1050, 650))):
                    region['frame'][:2] = [x, y]
            focus = {'version': 1, 'kind': 'native_image'}
            if effect != 'native':
                focus = {'version': 1, 'kind': 'custom', 'custom': {
                    'scale': 1.08 if effect in ('growth', 'combined') else 1,
                    'borderWidth': 4 if effect in ('border', 'combined') else 0,
                    'borderRGB': 16777215, 'shadowOpacity': 0, 'shadowRGB': 0,
                    'cornerRadius': 12}}
            composition['styles']['image']['focus'] = focus
            result.append({'id': position + '-' + effect, 'recipe': value,
                           'position': position, 'effect': effect})
    return result


def wait_loaded(fixture, current, output, number):
    """Wait for observed focus after reload before sending another focus request."""
    deadline = time.monotonic() + 10
    last = None
    reason = 'no_observation'
    while time.monotonic() < deadline:
        last = fixture.snapshot()
        q.require(n.identity(last) == n.identity(current), 'reload_identity_changed')
        try:
            scene = last['scene']
            observation = scene['focus_observation']
            diagnostics = scene['observation_diagnostics']
            q.require(scene['is_settled'] and observation['verified'], 'reload_unsettled')
            q.require(observation['generation'] == scene['observation_generation'] == diagnostics['sampledGeneration'], 'reload_generation')
            q.require(diagnostics['reason'] == 'ready' and 0 <= diagnostics['sampleAgeMilliseconds'] <= 200, 'reload_stale')
            # Reload can clear requested focus while retaining a measured native view.
            # Endpoint capture still requires the full focus signature after focus/set.
            return last
        except (ValueError, KeyError, RuntimeError) as exc:
            reason = str(exc)
            time.sleep(.1)
    q.save(output / f'reload-{number}-failure.json', dict(reason=reason, observation=last))
    raise ValueError('reload_not_ready:' + reason)


def run(output, execute=False, prepared=None):
    binding = d.bind_target(n.TARGET, 'http://127.0.0.1:8080')
    fixture = d.Fixture(binding['endpoint'])
    original = fixture.snapshot()
    n.signature(original, original, original['scene']['focused_element_id'])
    cases = recipes(original['scene']['recipe'])
    plan = dict(version='controlled-fixture351-v1', binding=binding, original=original,
                cases=cases, expectedFrames=40, role='development', trainingEligible=False,
                group='fixture351-related-scenes', maxSeconds=800, maxBytes=100_000_000,
                hcf='unchanged_unknown', sourceMatching='unverified',
                limitations=['Custom effects are authored, not OS HCF.',
                             'Early samples do not guarantee animation coverage.',
                             'Capture intervals are not atomic frame identities.'])
    if prepared is not None:
        q.require(prepared['binding'] == binding, 'planned_binding_changed')
        q.require(clean(prepared['original']['scene']['recipe']) == clean(original['scene']['recipe']), 'planned_scene_changed')
        q.require(prepared['original']['scene']['focused_element_id'] == original['scene']['focused_element_id'], 'planned_focus_changed')
        cases = prepared['cases']
        q.require(1 <= len(cases) <= 8 and prepared['expectedFrames'] == 5 * len(cases), 'planned_counts')
        plan = copy.deepcopy(prepared)
    if not execute:
        return plan
    output = d.new_output(output)
    output.mkdir(parents=True)
    q.save(output / 'plan.json', plan)
    started = time.monotonic()
    records = []
    pairs = []
    current = original
    mutated = False
    cleanup = False
    error = None
    action_number = 0

    def action(kind, value):
        nonlocal action_number
        action_number += 1
        q.save(output / f'action-{action_number:03d}-{kind}.json', value)

    def budget():
        q.require(time.monotonic() - started < 760, 'capture_timeout')
        q.require(sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) < 95_000_000, 'output_limit')

    def same_process(snapshot):
        q.require(snapshot['device']['fixture_instance_id'] == original['device']['fixture_instance_id'], 'instance_changed')
        q.require(d.bind_target(n.TARGET, binding['endpoint']) == binding, 'binding_changed')

    def load(recipe):
        nonlocal current, mutated
        budget()
        same_process(fixture.snapshot())
        q.require(n.identity(fixture.snapshot()) == n.identity(current), 'external_scene_change')
        mutated = True
        receipt = fixture.request('/recipe', recipe)
        current = fixture.snapshot()
        action('load', dict(recipe=recipe, receipt=receipt, observation=current))
        q.require(receipt['recipe_hash'] == current['scene']['recipe']['recipe_hash'], 'load_receipt_mismatch')
        if plan.get('reloadPolicy') == 'observe-before-focus-v1':
            wait_loaded(fixture, current, output, action_number)
        return receipt

    def focus(target):
        budget()
        q.require(n.identity(fixture.snapshot()) == n.identity(current), 'external_scene_change')
        start = time.time()
        snapshot = fixture.snapshot()
        observed = False
        if plan.get('reloadPolicy') == 'observe-before-focus-v1':
            try:
                n.signature(snapshot, current, target)
                observed = True
            except (ValueError, KeyError, RuntimeError):
                pass
        reply = dict(notSent='already_observed') if observed else fixture.request('/focus/set', {'element_id': target, 'settle_time_ms': 150})
        result = dict(start=start, end=time.time(), reply=reply, requested=target)
        action('focus', result)
        return result

    def frame(case_id, phase, target, settled=True):
        budget()
        before = n.settle(fixture, current, target) if settled else fixture.snapshot()
        same_process(before)
        q.require(n.identity(before) == n.identity(current), 'external_scene_change')
        path = output / (case_id + '-' + phase + '.png')
        start = time.time()
        d.run(['xcrun', 'simctl', 'io', n.TARGET, 'screenshot', '--type=png', str(path)], timeout=15)
        end = time.time()
        after = fixture.snapshot()
        same_process(after)
        q.require(n.identity(after) == n.identity(current), 'external_scene_change')
        reason = None
        try:
            q.require(n.signature(before, current, target) == n.signature(after, current, target), 'interval_changed')
        except (ValueError, KeyError, RuntimeError) as exc:
            reason = str(exc)
        with Image.open(path) as image:
            image.load()
            q.require(list(image.size) == [after['scene']['scene_width'], after['scene']['scene_height']], 'dimensions')
        record = dict(id=path.stem, phase=phase, path=path.name, sha256=q.digest(path),
                      start=start, end=end, before=before, after=after,
                      verifiedInterval=reason is None, exclusion=reason,
                      observedFocusID=target if reason is None else None)
        q.save(output / (path.stem + '.json'), record)
        records.append(record)
        if plan.get('reloadPolicy'):
            q.save(output.parent.parent/'progress.json', dict(step=f'Capture {case_id}: {phase}',
                completed=len(records), total=plan['expectedFrames'], updatedAt=time.time()), replace=True)
        q.require(not settled or reason is None, reason or 'unverified_settled_capture')
        return record

    with lock():
        try:
            for case in cases:
                cid = case['id']
                source_focus = case.get('sourceFocus', 'item-0')
                target_focus = case.get('targetFocus', 'item-1')
                receipt = load(case['recipe'])
                focus(source_focus)
                before = frame(cid, 'before', source_focus)
                command = focus(target_focus)
                early = frame(cid, 'early', target_focus, False)
                after = frame(cid, 'settled', target_focus)
                repeat = frame(cid, 'repeat', target_focus)
                changed = copy.deepcopy(case['recipe'])
                for content in changed['appearance']['composition']['contents'].values():
                    content['seed'] += 500
                content_receipt = load(changed)
                focus(target_focus)
                content = frame(cid, 'content', target_focus)
                pairs.extend([
                    dict(case=cid, condition='movement', before=before['id'], after=after['id'], changed=True),
                    dict(case=cid, condition='recapture', before=after['id'], after=repeat['id'], changed=False),
                    dict(case=cid, condition='content', before=repeat['id'], after=content['id'], changed=False)])
                q.save(output / (cid + '-sequence.json'), dict(case=case, load=receipt, command=command,
                    frames=[r['id'] for r in (before, early, after, repeat, content)], contentLoad=content_receipt,
                    contentMeaning='Settled endpoint focus identity stays fixed; reload may cause intermediate focus changes.'))
        except Exception as exc:
            error = str(exc)
            try:
                q.save(output / 'failure-observation.json', fixture.snapshot())
            except Exception as diagnostic_error:
                q.save(output / 'failure-observation-error.json', dict(error=str(diagnostic_error)))
        finally:
            try:
                if mutated:
                    same_process(fixture.snapshot())
                    q.require(n.identity(fixture.snapshot()) == n.identity(current), 'cleanup_external_scene_change')
                    fixture.request('/recipe', clean(original['scene']['recipe']))
                    restored = fixture.snapshot()
                    q.require(clean(restored['scene']['recipe']) == clean(original['scene']['recipe']), 'restore_recipe_mismatch')
                    target = original['scene']['focused_element_id']
                    fixture.request('/focus/set', {'element_id': target, 'settle_time_ms': 150})
                    n.settle(fixture, restored, target)
                cleanup = True
            except Exception as exc:
                error = (error or '') + '; cleanup: ' + str(exc)
            q.save(output / 'capture.json', dict(version=plan['version'], complete=error is None and len(records)==plan['expectedFrames'],
                expectedFrames=plan['expectedFrames'], expectedPairs=3*len(cases),
                cleanup=cleanup, error=error, frames=records, pairs=pairs, seconds=time.monotonic()-started,
                trainingEligible=False, role='development', group=plan['group'], planSHA256=q.digest(output/'plan.json')))
    q.require(error is None, error or 'capture_failed')
    return dict(frames=len(records), pairs=len(pairs), cleanup=cleanup)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(run(args.output, args.execute))
