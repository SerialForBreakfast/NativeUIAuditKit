"""Review source-defined SDK packets. Never admit data or operate a target."""
import math
from pathlib import Path
from PIL import Image
from sdk_semantics529 import semantics
import research_queue as q
from experiment_templates import checked, pin

OUT = None


def review(evidence, image):
    q.require(evidence.get('schemaVersion') == 1 and type(evidence['schemaVersion']) is int, 'sdk_packet_version')
    q.require(evidence.get('admission') == 'review_only' and
              evidence.get('labelSource') == 'sdk_reported_focus_and_registered_geometry', 'sdk_packet_role')
    q.require(image.stat().st_size == evidence['imageBytes'] and q.digest(image) == evidence['imageSHA256'], 'sdk_packet_pixels')
    with Image.open(image) as im:
        q.require(im.format == 'PNG' and im.size == (evidence['width'], evidence['height']) and
                  0 < im.width*im.height <= 16777216, 'sdk_packet_dimensions')
        im.verify()
    times = [evidence[k] for k in ('captureStartNS', 'captureEndNS', 'observationEndNS')]
    q.require(all(type(v) is int and v >= 0 for v in times) and times == sorted(times), 'sdk_packet_clock')
    q.require(all(isinstance(evidence.get(k), str) and evidence[k] for k in ('clockID', 'captureID', 'sourceID')), 'sdk_packet_identity')
    issues = evidence['issues']
    q.require(isinstance(issues, list) and all(isinstance(v, str) for v in issues), 'sdk_packet_issues')
    reasons = set(issues)
    if times[-1]-times[0] > 1000000000:
        reasons.add('capture_bracket_too_wide')
    before, after = evidence['before'], evidence['after']
    for key in ('appID', 'processID', 'runID'):
        if not isinstance(before.get(key), str) or not before[key] or before[key] != after.get(key):
            reasons.add('producer_identity_changed_or_missing')
    for snapshot in (before, after):
        q.require(type(snapshot.get('focusKnown')) is bool and type(snapshot.get('interrupted')) is bool, 'sdk_packet_focus_schema')
        if snapshot.get('sourceKind') != 'authenticated_sdk_challenge':
            reasons.add('unauthenticated_observation')
        if not snapshot['focusKnown']:
            reasons.add('focus_unavailable')
        if snapshot['interrupted']:
            reasons.add('interrupted')
        elements = snapshot['elements']
        q.require(isinstance(elements, list), 'sdk_packet_elements')
        ids = [e['identity']['id'] for e in elements]
        q.require(all(isinstance(v, str) and v for v in ids) and len(ids) == len(set(ids)), 'sdk_packet_duplicate_identity')
    if before.get('focusID') != after.get('focusID'):
        reasons.add('focus_changed_during_capture')
    if before['elements'] != after['elements']:
        reasons.add('registered_inventory_changed_during_capture')
    focus = after.get('focusID')
    if focus is not None:
        q.require(isinstance(focus, str) and focus, 'sdk_packet_focus_id')
        if focus not in {e['identity']['id'] for e in after['elements']}:
            reasons.add('focused_element_unavailable')
    rows = []
    for element in after['elements']:
        bounds = element.get('bounds') or {}
        values = [bounds.get(k) for k in ('x', 'y', 'width', 'height')]
        numeric = all(type(v) in (int, float) and math.isfinite(v) for v in values)
        valid = (numeric and element.get('coordinateSpace') == 'screenPixels' and
                 values[0] >= 0 and values[1] >= 0 and values[2] > 0 and values[3] > 0 and
                 values[0]+values[2] <= evidence['width'] and values[1]+values[3] <= evidence['height'])
        state = element.get('observedState') or {}
        alpha = state.get('effectiveAlpha')
        visible = (state.get('source') == 'uikit_ancestor_state' and state.get('hidden') is False and
                   state.get('enabled') is True and type(alpha) in (int, float) and 0 < alpha <= 1)
        rows.append(dict(identity=element['identity'], parentID=element.get('parentID'),
            pixelBounds=values if valid else None, geometryAvailable=bool(valid), observedVisibleEnabled=visible,
            registeredSelected=element.get('selected'), selectionProvenance='registration_not_verified_native_selection',
            className=element.get('className'), taxonomyClass=None,
            semanticEvidence=semantics(element)))
        if element['identity']['id'] == focus and (not valid or not visible or element.get('hidden') is not False or element.get('enabled') is not True):
            reasons.add('focused_geometry_or_visibility_unverified')
    focus_state = 'unknown' if reasons else 'no_focus' if focus is None else 'focused'
    return dict(version='sdk-packet-review-v1', focusState=focus_state,
        reportedFocusID=focus, reviewable=not reasons, reasons=sorted(reasons), elements=rows,
        annotationCompleteness='unknown', trainingEligible=False, modelAccepted=False,
        sourceID=evidence['sourceID'], captureID=evidence['captureID'],
        limitation='Registered elements are not a complete detector inventory. Packet declarations do not independently authenticate provenance. '
                   'No training admission or evaluation-group assignment follows from this review.')


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    refs = {Path(ref['path']).name: checked(ref) for ref in spec['inputs']}
    result = review(q.load(refs['evidence.json']), refs['frame.png'])
    q.save(OUT/'benchmark_summary.json', result)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT/'benchmark_summary.json'))]))


def validate_request(request):
    q.require(isinstance(request, dict) and set(request) ==
              {'version', 'id', 'evidence', 'image', 'expectedAppID', 'expectedSourceID', 'group', 'role'}, 'sdk_request_fields')
    q.require(request['version'] == 'sdk-packet-request-v1', 'sdk_request_version')
    q.require(isinstance(request['id'], str) and q.ID.fullmatch(request['id']), 'sdk_request_id')
    q.require(request['role'] in ('review_only', 'calibration'), 'sdk_request_role')
    for key in ('expectedAppID', 'expectedSourceID', 'group'):
        q.require(isinstance(request[key], str) and 0 < len(request[key]) <= 512, 'sdk_request_'+key)
    for key in ('evidence', 'image'):
        checked(request[key])


def review_request(request):
    validate_request(request)
    evidence = q.load(checked(request['evidence']))
    q.require(evidence.get('sourceID') == request['expectedSourceID'], 'sdk_request_source_mismatch')
    q.require(all(evidence.get(side, {}).get('appID') == request['expectedAppID'] for side in ('before', 'after')),
              'sdk_request_app_mismatch')
    result = review(evidence, checked(request['image']))
    result.update(group=request['group'], role=request['role'], inputPins={k:request[k] for k in ('evidence','image')})
    return result


def build(request_path):
    request = q.load(request_path)
    validate_request(request)
    inputs = [pin(request_path), request['evidence'], request['image'], pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2', id=request['id'], task='SDK502', owner='Maximum-mini-NUIAK',
        kind='screen', jobKind='artifact', authority='diagnostic', dependencies=[], inputs=inputs,
        adapter=dict(type='python-callable', steps=['sdk_packet502.run_request'], outputAttributes=['sdk_packet502.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[p['path'] for p in inputs[:3]]),
        question='Does the retained SDK packet supply stable observed focus and registered geometry for the expected app and source?',
        hypothesis='A source-defined packet permits deterministic review without another capture or custom script.',
        controlledComparison='Preserve packet bytes, expected app, source identity, group and role. Distinguish valid observations from unavailable labels.',
        decisionRule='Reject mismatched identity or bytes. Keep unavailable observations unknown and preserve review-only admission.',
        nextActionByOutcome=dict(supported='Use reviewed evidence for diagnostics; qualify taxonomy and coverage separately.',
                                 contradicted='Preserve evidence and request the exact missing producer observation.'))


def run_request():
    spec = q.load(OUT.parents[2]/'spec.json')
    result = review_request(q.load(checked(spec['inputs'][0])))
    q.save(OUT/'benchmark_summary.json', result)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT/'benchmark_summary.json'))]))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Compile an SDK review request. Does not register, approve, or execute jobs.')
    parser.add_argument('--request', required=True)
    parser.add_argument('--spec', required=True)
    args = parser.parse_args()
    request_path = q.local_path(q.ROOT, args.request)
    spec_path = q.local_path(q.ROOT, args.spec)
    q.save(spec_path, build(request_path))
