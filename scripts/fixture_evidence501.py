"""Audit retained Fixture evidence for SDK dataset requirements. Never capture."""
from collections import Counter
from pathlib import Path

import research_queue as q
from experiment_templates import checked, pin
from focus_corrected_transition_audit import validate_case
from inventory_transition_sources import observed_scroll

OUT = None


def validate_request(request):
    q.require(set(request) == {'version', 'id', 'view', 'export', 'campaign', 'cases'}, 'sdk_request_fields')
    q.require(request['version'] == 'fixture-evidence-request-v1', 'sdk_request_version')
    q.require(q.ID.fullmatch(request['id']) is not None, 'sdk_request_id')
    q.require(request['view'] in ('geometry', 'transitions'), 'sdk_request_view')
    q.require(isinstance(request['cases'], list) and request['cases'] and
              all(isinstance(v, str) for v in request['cases']) and
              len(set(request['cases'])) == len(request['cases']), 'sdk_case_membership')


def audit(request):
    validate_request(request)
    receipt_path = checked(request['export'])
    receipt = q.load(receipt_path)
    root = Path(receipt['exported_path'])
    q.require(root.resolve() == (receipt_path.parent/'corpus').resolve(), 'sdk_export_path')
    members = set()
    for item in receipt['files']:
        path = q.local_path(root, item['path'])
        q.require(item['path'] not in members, 'sdk_duplicate_member')
        members.add(item['path'])
        q.require(not path.is_symlink() and path.is_file() and
                  path.stat().st_size == item['bytes'] and q.digest(path) == item['sha256'], 'sdk_export_changed')
    config = q.load(checked(request['campaign']))
    cases = {c['case_id']: c for c in config['manifest']['cases']}
    q.require(set(request['cases']) <= set(cases), 'sdk_case_unknown')
    q.require(receipt['campaign']['campaign_id'] == config['manifest']['campaign_id'], 'sdk_campaign_identity')
    paths = {}
    for name in members:
        if Path(name).name == 'transition-case.json':
            path = q.local_path(root, name)
            ident = q.load(path)['case_id']
            q.require(ident not in paths, 'sdk_duplicate_case')
            paths[ident] = path
    q.require(set(paths) == set(cases), 'sdk_export_membership')
    frames, pairs = [], []
    for ident in request['cases']:
        path = paths[ident]
        evidence, before, after = validate_case(root, path, cases[ident])
        q.require(evidence.get('cleanup') == 'verified', 'sdk_cleanup')
        for role, endpoint in (('before', before), ('after', after)):
            scene = endpoint['scene']
            elements = scene['elements']
            ids = {e['element_id'] for e in elements}
            q.require(len(ids) == len(elements), 'sdk_duplicate_element')
            focus = endpoint['focus']
            # The current validator qualifies nonempty focus only. Never infer no-focus.
            q.require(isinstance(focus, str) and focus in ids, 'sdk_focus_unavailable')
            items = []
            for element in elements:
                body = element.get('rendered_body_geometry') or {}
                artwork = (element.get('artwork_geometry') or {}).get('presentation') or {}
                items.append(dict(id=element['element_id'], parent=element.get('parent_element_id'),
                    taxonomy=element.get('taxonomy_class'), focused=element.get('is_focused'),
                    layoutBounds=element.get('pixel_bounds'), body=body, artworkPresentation=artwork))
            frames.append(dict(case=ident, endpoint=role, image=endpoint['image'],
                group=cases[ident]['independence_group'], role='calibration', trainingEligible=False,
                focusState='focused', focusedID=focus, generation=scene['focus_observation']['generation'],
                coordinateSpace='image_top_left_pixels', elements=items,
                semanticInventory=scene.get('semantic_inventory'),
                annotationCompleteness='unknown', evidenceSource='fixture_capture_bracket'))
        moved, source = observed_scroll(evidence)
        pairs.append(dict(case=ident, group=cases[ident]['independence_group'],
            beforeFocus=before['focus'], afterFocus=after['focus'],
            observedFocusChanged=before['focus'] != after['focus'],
            observedScrollChanged=moved, scrollEvidence=source,
            requestedCondition=cases[ident]['transition']['condition']))
    counts = Counter()
    for frame in frames:
        counts['frames'] += 1
        for e in frame['elements']:
            counts['elements'] += 1
            counts['parentLinks'] += e['parent'] is not None
            counts['measuredBodies'] += e['body'].get('availability') == 'measured'
            counts['measuredArtwork'] += e['artworkPresentation'].get('availability') == 'measured'
            counts['clippedBodies'] += e['body'].get('clipping') in ('fully_clipped', 'partially_clipped')
    counts.update(pairs=len(pairs), focusChanges=sum(p['observedFocusChanged'] for p in pairs),
                  scrollKnown=sum(p['observedScrollChanged'] is not None for p in pairs),
                  independentGroups=len({p['group'] for p in pairs}))
    return dict(version='fixture-evidence-audit-v1', view=request['view'], counts=dict(counts),
        frames=frames if request['view'] == 'geometry' else [], pairs=pairs,
        modelAccepted=False, trainingEligible=False,
        missingRequirements=['Explicit observed no-focus state', 'Per-class annotation completeness',
                             'Observed selection and decorative-condition tags', 'Independent app qualification'],
        limitation='Retained Fixture evidence, not proof of portable SDK delivery. Related frames share ancestry. '
                   'Scroll offsets do not measure arbitrary background motion. No model accuracy is measured.')


def build(request_path):
    request = q.load(request_path)
    validate_request(request)
    inputs = [pin(request_path), request['export'], request['campaign'], pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2', id=request['id'], task='SDK501', owner='Maximum-mini-NUIAK',
        kind='screen', jobKind='artifact', authority='diagnostic', dependencies=[], inputs=inputs,
        adapter=dict(type='python-callable', steps=['fixture_evidence501.run'], outputAttributes=['fixture_evidence501.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[p['path'] for p in inputs[:3]]),
        question='Which observed geometry and focus fields can retained captures supply for dataset qualification?',
        hypothesis='Existing observed metadata can replace manual geometry and transition annotation for this retained scope.',
        controlledComparison='Same retained bytes and calibration roles. Change only the requested evidence view and case membership.',
        decisionRule='Reuse verified fields. Request missing observations explicitly. Do not admit calibration data for training.',
        nextActionByOutcome=dict(supported='Reuse observed fields for diagnostic labels and a qualified producer contract.',
                                 contradicted='Preserve inputs and report the exact missing or invalid observation.'))


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    request = q.load(checked(spec['inputs'][0]))
    report = audit(request)
    q.save(OUT/'benchmark_summary.json', report)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT/'benchmark_summary.json'))]))
