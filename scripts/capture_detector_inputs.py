"""Prepare detector inputs from settled development captures, including no-focus scenes."""
import shutil
from pathlib import Path
from PIL import Image
import research_queue as q
import native343
from detector_native_inputs import VERSION, bounds
from coverage_reports402 import rectangle
from template_adapters395 import document, resolve_inputs
from template_inputs398 import pin

OUT = None


def unique_rows(rows):
    """Reuse identical pixels only when geometry, labels, and groups agree."""
    unique = {}
    for row in rows:
        old = unique.get(row['sha256'])
        if old:
            q.require(old['group'] == row['group'] and old['controls'] == row['controls'], 'capture_duplicate_conflict')
            old['events'].extend(row['events'])
        else:
            unique[row['sha256']] = row
    q.require(0 < len(unique) <= 64, 'capture_frame_count')
    return list(unique.values())


FIXTURE_BATCH = 'fixture-batch-capture-v1'
BATCH_ROOT = q.ROOT/'dataset/tvos_captures'
BATCH_UNAVAILABLE = ['fixture_instance_id', 'wall_clock_snapshot_bounds']


def bracket(capture, png_sha256, expected, run_id, recipe_hash):
    """Check 1 fixture batch capture bracket on the host monotonic clock. Return the scene before the frame."""
    before, after = capture['before_scene'], capture['after_scene']
    q.require(capture['correlation'] == 'validated_capture_bracket' and capture['frame_png_sha256'] == png_sha256, 'batch_frame_identity')
    q.require(capture['before_scene_received_host_ns'] <= capture['frame_received_host_ns'] <= capture['after_scene_received_host_ns'], 'batch_frame_outside_bracket')
    for scene in (before, after):
        q.require(scene['fixture_run_id'] == run_id and scene['recipe']['recipe_hash'] == recipe_hash, 'batch_runtime_or_recipe_changed')
    q.require(native343.scene_signature(before, expected, None) == native343.scene_signature(after, expected, None), 'batch_interval_changed')
    q.require([capture['frame_width'], capture['frame_height']] == [before['scene_width'], before['scene_height']], 'capture_dimensions')
    return before


def batch_row(frame_id, scene, image, sha256, case, expected, out):
    width, height = scene['scene_width'], scene['scene_height']
    with Image.open(image) as pixels:
        q.require(pixels.size == (width, height), 'capture_dimensions')
    controls = []
    for element in scene['elements']:
        if element['element_id'] not in scene['focus_observation']['plannedFocusIDs']:
            continue
        body = rectangle(element['rendered_body_geometry']['visible_pixel_bounds'])
        name = element.get('taxonomy_class')
        q.require(isinstance(name, str) and bool(name), 'capture_taxonomy_missing')
        controls.append(dict(id=element['element_id'], **{'class': name},
                             bounds=bounds([body[k] for k in ('x','y','width','height')],width,height),
                             state='focused' if element['is_focused'] else 'unfocused'))
    target = out/'images'/(sha256+'.png')
    target.parent.mkdir(exist_ok=True)
    if not target.exists():
        shutil.copyfile(image, target)
    q.require(q.digest(target) == sha256, 'capture_copy_changed')
    return dict(id=frame_id, image=pin(target), sha256=sha256, width=width, height=height,
                group=case['group'], screen=case['family'], appearance='standard', controls=controls,
                events=[dict(id=frame_id, profile='standard', noFocus=expected is None)])


def prepare_batch(artifact, out):
    """Prepare detector inputs from a completed `fixture batch` output. Producer splits stay advisory."""
    source = Path(artifact['path'])
    q.require(source.resolve() == source and source.name == 'manifest.json' and source.is_relative_to(BATCH_ROOT), 'capture_source_scope')
    q.require(q.digest(source) == artifact['sha256'], 'capture_changed')
    plan = artifact['plan']
    q.require(plan.get('trainingEligible') is False and plan['cases'] and
              all(c['role'] == 'development' for c in plan['cases']), 'capture_role')
    cases = {c['recipe']: c for c in plan['cases']}
    q.require(len(cases) == len(plan['cases']), 'capture_case_identity')
    receipt = q.load(source.parent/'harvest-receipt.json')
    manifest = q.load(source)
    q.require(receipt['outcome'] == 'completed' and receipt['rejections'] == [] and
              receipt['acceptedRowCount'] == len(manifest), 'capture_incomplete')
    q.require({r['metadata']['recipeFile'] for r in manifest} >= set(cases), 'capture_membership')
    rows, baselines = [], set()
    for row in manifest:
        meta = row['metadata']
        case = cases.get(meta['recipeFile'])
        if case is None:
            continue
        sidecar = q.load(q.local_path(source.parent, meta['metadataPath']))
        expected = row['expectedFocus']
        q.require(sidecar['focused_element_id'] == expected, 'wrong_focus')
        run_id, recipe_hash = sidecar['focused_capture']['before_scene']['fixture_run_id'], meta['recipeHash']
        # The producer names the reference frame "unfocused", but some reference scenes observe a focused control.
        # Label it from the observed scene; the bracket check still requires both scenes to agree.
        observed = sidecar['reference_capture']['before_scene'].get('focused_element_id')
        frames = [(row['id'], sidecar['focused_capture'], sidecar['focused_provenance'], sidecar['focused_sha256'], meta['focusedPath'], expected),
                  (row['id']+'-baseline', sidecar['reference_capture'], sidecar['unfocused_provenance'], sidecar['unfocused_sha256'], meta['unfocusedPath'], observed)]
        for frame_id, capture, provenance, sha256, name, focus in frames:
            image = q.local_path(source.parent, name)
            q.require(q.digest(image) == sha256 == provenance['pngSHA256'], 'capture_pixels_changed')
            q.require(provenance['sourceDeviceID'] == plan['target'] and
                      provenance['providerID'] == 'simctl-screenshot-companion', 'capture_target')
            scene = bracket(capture, sha256, focus, run_id, recipe_hash)
            if frame_id.endswith('-baseline'):
                if sha256 in baselines:
                    continue  # The producer repeats 1 baseline frame for each focused row.
                baselines.add(sha256)
            else:
                q.require(q.digest(image) == row['sha256'], 'capture_manifest_hash')
            rows.append(batch_row(frame_id, scene, image, sha256, case, focus, out))
    q.require(all(any(r['group'] == c['group'] for r in rows) for c in plan['cases']), 'capture_membership')
    return dict(version=VERSION, platform='tvOS',role='development',trainingEligible=False,
                labelReview='unknown',labelSource='native-observation',labelsComplete=False,frames=unique_rows(rows),
                source=dict(kind=FIXTURE_BATCH, target=plan['target'], unavailable=BATCH_UNAVAILABLE),
                limitation='Observed Fixture controls only. Decorations may be unlabelled. Host monotonic capture brackets replace '
                           'wall-clock snapshot bounds; fixture_instance_id is unavailable. No physical-device qualification.')


def prepare(artifact, out):
    if artifact.get('version') == FIXTURE_BATCH:
        return prepare_batch(artifact, out)
    source = Path(artifact['path'])
    q.require(source.resolve() == source and source.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'), 'capture_source_scope')
    q.require(q.digest(source) == artifact['sha256'], 'capture_changed')
    plan = artifact['plan']
    q.require(plan.get('trainingEligible') is False and plan['cases'] and
              all(c['role'] == 'development' for c in plan['cases']), 'capture_role')
    cases = {c['id']: c for c in plan['cases']}
    q.require(len(cases) == len(plan['cases']), 'capture_case_identity')
    capture = q.load(source)
    q.require(capture['complete'] and capture['cleanup'], 'capture_incomplete')
    frames = capture['frames']
    q.require(0 < len(frames) <= 64 and len({f['id'] for f in frames}) == len(frames), 'capture_membership')
    rows = []
    for frame in frames:
        native343.signature(frame['before'], frame['before'], frame['focus'])
        native343.signature(frame['after'], frame['before'], frame['focus'])
        scene = frame['before']['scene']
        width, height = scene['scene_width'], scene['scene_height']
        image = q.local_path(source.parent, frame['path'])
        q.require(q.digest(image) == frame['sha256'], 'capture_pixels_changed')
        with Image.open(image) as pixels:
            q.require(pixels.size == (width, height), 'capture_dimensions')
        controls = []
        for element in scene['elements']:
            if element['element_id'] not in scene['focus_observation']['plannedFocusIDs']:
                continue
            body = rectangle(element['rendered_body_geometry']['visible_pixel_bounds'])
            name = element.get('taxonomy_class')
            q.require(isinstance(name, str) and bool(name), 'capture_taxonomy_missing')
            controls.append(dict(id=element['element_id'], **{'class': name},
                                 bounds=bounds([body[k] for k in ('x','y','width','height')],width,height),
                                 state='focused' if element['is_focused'] else 'unfocused'))
        target = out/'images'/(frame['sha256']+'.png')
        target.parent.mkdir(exist_ok=True)
        if not target.exists():
            shutil.copyfile(image, target)
        q.require(q.digest(target) == frame['sha256'], 'capture_copy_changed')
        case = cases[frame['case']]
        rows.append(dict(id=frame['id'], image=pin(target), sha256=frame['sha256'], width=width,height=height,
                         group=case['group'],screen=case['family'],appearance=frame['profile'],controls=controls,
                         events=[dict(id=frame['id'],profile=frame['profile'],noFocus=frame['focus'] is None)]))
    return dict(version=VERSION, platform='tvOS',role='development',trainingEligible=False,
                labelReview='unknown',labelSource='native-observation',labelsComplete=False,frames=unique_rows(rows),
                limitation='Observed Fixture controls only. Decorations may be unlabelled. Duplicate events remain recorded. No physical-device qualification.')


def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    refs=resolve_inputs(cfg,OUT)
    labels=prepare(document(refs['capture']),OUT)
    q.save(OUT/'labels.json',labels)
    q.save(OUT/'benchmark_summary.json',dict(frames=len(labels['frames']),
        events=sum(len(r['events']) for r in labels['frames']),groups=len({r['group'] for r in labels['frames']}),
        noFocusEvents=sum(e['noFocus'] for r in labels['frames'] for e in r['events']),modelAccepted=False,inputs=refs))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=name,sha256=q.digest(OUT/name)) for name in ('labels.json','benchmark_summary.json')]))
