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


def prepare(artifact, out):
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
