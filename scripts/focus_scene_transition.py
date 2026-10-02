"""Opt-in scene corroboration of attributed control changes; never authorizes input."""
import argparse
import human_annotation_review as h

DECISIONS = {'arrival', 'departure', 'unchanged', 'unknown', 'unavailable'}
CONTEXT = {'sameScene', 'settled', 'fresh', 'completeCoverage'}


def corroborate(request, enabled=False, *, require_resolved=False):
    result = dict(version='focus-scene-transition-v1', diagnosticOnly=True,
                  releaseEligible=False, controlIssued=False,
                  requireResolvedBackground=require_resolved)
    if not enabled:
        return dict(result, status='disabled', decision='unavailable')
    h.require(isinstance(request, dict) and set(request) == {'version', 'context', 'controls'}, 'request_fields')
    h.require(type(request['version']) is int and request['version'] == 1, 'request_version')
    flags = request['context']
    h.require(isinstance(flags, dict) and set(flags) == CONTEXT, 'context_fields')
    h.require(all(type(v) is bool for v in flags.values()), 'context_boolean_required')
    controls = request['controls']
    h.require(isinstance(controls, list) and 1 <= len(controls) <= 256, 'control_limit')
    seen = set()
    for c in controls:
        h.require(isinstance(c, dict) and set(c) == {'id', 'decision', 'identityVerified'}, 'control_fields')
        cid = c['id']
        h.require(isinstance(cid, str) and 0 < len(cid) <= 256 and cid not in seen, 'control_identity')
        seen.add(cid)
        h.require(isinstance(c['decision'], str) and c['decision'] in DECISIONS, 'control_decision')
        h.require(type(c['identityVerified']) is bool, 'identity_boolean_required')
    result.update(controlCount=len(controls), context=flags)
    if not all(flags.values()) or not all(c['identityVerified'] for c in controls):
        return dict(result, status='unavailable', decision='unavailable', reason='context_or_identity_unverified')
    by = {d: [c['id'] for c in controls if c['decision'] == d] for d in DECISIONS}
    result.update(arrivals=by['arrival'], departures=by['departure'],
                  unresolved=by['unknown'] + by['unavailable'])
    if len(by['unchanged']) == len(controls):
        return dict(result, status='available', decision='unchanged', reason='all_controls_unchanged')
    if by['unavailable'] or (require_resolved and by['unknown']):
        return dict(result, status='unavailable', decision='unavailable', reason='unresolved_controls')
    if len(by['arrival']) != 1 or len(by['departure']) != 1:
        return dict(result, status='ambiguous', decision='unknown', reason='requires_one_gain_and_one_loss')
    return dict(result, status='candidate', decision='switch',
                gained=by['arrival'][0], lost=by['departure'][0],
                reason='opposing_visual_changes_not_focus_proof')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--enable-experimental', action='store_true')
    p.add_argument('--require-resolved-background', action='store_true')
    a = p.parse_args()
    out = h.fresh(a.output)
    result = corroborate(h.read(h.local(a.request)), a.enable_experimental,
                         require_resolved=a.require_resolved_background)
    h.write(out, result)
    print(result['status'], result['decision'])


if __name__ == '__main__':
    main()
