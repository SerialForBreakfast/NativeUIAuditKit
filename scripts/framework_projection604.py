"""RESET604 T2.5: project framework facts to tvOS detector classes (`tvos-framework-projection-v1`).

The contract lives in `Research/Contracts/tvos-framework-projection-v1.{md,json}`.
Each visible object gets 1 disposition: target, owned_metadata, out_of_scope, or unresolved.
Matching uses construction facts only. The id prefix, title, language, tint and Fixture family never take part.
`scripts/roles559.py` stays unchanged for historical results.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import research_queue as q

CONTRACT_PATH = q.ROOT / 'Research/Contracts/tvos-framework-projection-v1.json'
# Evidence failures stay unresolved even when the object is owned by a target.
EVIDENCE_REASONS = {'framework_facts_missing', 'join_mismatch', 'frame_identity_mismatch', 'fact_conflict', 'duplicate_object_id'}


@lru_cache(maxsize=4)
def load_contract(path=CONTRACT_PATH):
    """Load the machine table once. Returns (contract dict, sha256 of the file)."""
    raw = Path(path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def tvos_classes(contract=None):
    contract = contract or load_contract()[0]
    return list(contract['classes'])


STYLE_KEYS = {'style', 'style_source', 'style_required'}


def _failing_keys(rule, c, owned):
    """Return the `match` keys of the rule that do not hold for construction facts `c`."""
    failed = []
    for key, want in rule['match'].items():
        if key == 'primitive_in':
            ok = c.get('primitive') in want
        elif key == 'style_required':
            ok = (c.get('style') is not None) is want
        elif key == 'style_not':
            ok = c.get('style') not in want
        elif key == 'owned':
            ok = owned is want
        else:
            ok = c.get(key) == want
        if not ok:
            failed.append(key)
    return failed


def _rule_matches(rule, c, owned):
    return not _failing_keys(rule, c, owned)


def _fails_only_on_style_evidence(rule, c, owned):
    """A1 item 2: the rule fails only because style evidence is missing or only declared, not because of another style."""
    failed = _failing_keys(rule, c, owned)
    if not failed or not set(failed) <= STYLE_KEYS:
        return False
    if 'style' in failed and c.get('style') is not None:
        return False
    return True


def _unresolved(reason, rule_id=None):
    return dict(disposition='unresolved', cls=None, rule_id=rule_id, reason=reason)


def project_object(obj, contract=None, owned=False):
    """Project 1 object without ownership or frame context. Returns disposition, cls, rule_id, reason."""
    contract = contract or load_contract()[0]
    c, o = obj.get('construction'), obj.get('observation')
    if not isinstance(c, dict) or not c.get('primitive'):
        return _unresolved('framework_facts_missing')
    # A1 item 4: a construction without an observation, or a different instance, is a join failure.
    if o is None or o.get('instance_id') != c.get('instance_id'):
        return _unresolved('join_mismatch')
    if contract['mapping_version'] == 'ttr-settings-toggle-v1.1':
        # This predicate belongs to the settled observation, never to the recipe.
        c = dict(c, visible_disabled=(
            o.get('enabled') is False and o.get('visible_in_capture') is True
            and o.get('focusable') is False
        ))
    hits = [r for r in contract['rules'] if _rule_matches(r, c, owned)]
    if not hits:
        if any(_fails_only_on_style_evidence(r, c, owned) for r in contract['rules']):
            return _unresolved('style_evidence_missing')
        return _unresolved('unprojected_framework_facts')
    top = max(r['specificity'] for r in hits)
    best = [r for r in hits if r['specificity'] == top]
    if len({(r['disposition'], r.get('class')) for r in best}) > 1:
        return _unresolved('conflicting_rules', '+'.join(sorted(r['rule_id'] for r in best)))
    rule = best[0]
    for field, want in (rule.get('expect') or {}).items():
        if o is not None and field in o and o[field] != want:
            return _unresolved('fact_conflict', rule['rule_id'])
    if rule['disposition'] == 'unresolved':
        return _unresolved(rule.get('reason', 'unprojected_framework_facts'), rule['rule_id'])
    if rule.get('requires_affordance'):
        visible = (o or {}).get('affordance_visible')
        if visible is None:
            return _unresolved('affordance_evidence_missing', rule['rule_id'])
        if visible is False:
            return dict(disposition='out_of_scope', cls=None, rule_id=rule['rule_id'], reason='affordance_hidden')
    return dict(disposition=rule['disposition'], cls=rule.get('class'), rule_id=rule['rule_id'],
                reason=rule.get('reason'), focus_destination=bool(rule.get('focus_destination')))


def _box(o, width, height):
    """Half-open integer pixel rect [x0, y0, x1, y1] -> [x, y, w, h], clipped to the frame."""
    b = (o or {}).get('visible_bounds_px')
    if not (isinstance(b, (list, tuple)) and len(b) == 4 and all(type(v) is int for v in b)):
        return None
    x0, y0, x1, y1 = max(b[0], 0), max(b[1], 0), min(b[2], width), min(b[3], height)
    return [x0, y0, x1 - x0, y1 - y0] if x1 > x0 and y1 > y0 else None


def _covered_child_button(child, parent, focus):
    """Require a measured button body wholly clipped out of its visible action owner."""
    if child.get('owner_relation') != 'separate_action' or not parent:
        return False
    obs = child.get('observation') or {}
    visible = obs.get('visible_bounds_px')
    if (obs.get('focusable') is not False or visible != [0, 0, 0, 0]
            or not all(type(v) is int for v in visible)
            or focus.get('state') != 'focused' or focus.get('id') == child['id']):
        return False

    owner = parent.get('observation') or {}
    boxes = (obs.get('full_bounds_px'), owner.get('full_bounds_px'), owner.get('visible_bounds_px'))
    for box in boxes:
        if not (isinstance(box, list) and len(box) == 4 and all(type(v) is int for v in box)
                and box[0] < box[2] and box[1] < box[3]):
            return False
    child_box, owner_box, visible_owner = boxes
    for box in (child_box, visible_owner):
        if not (owner_box[0] <= box[0] and owner_box[1] <= box[1]
                and box[2] <= owner_box[2] and box[3] <= owner_box[3]):
            return False
    return (child_box[2] <= visible_owner[0] or visible_owner[2] <= child_box[0]
            or child_box[3] <= visible_owner[1] or visible_owner[3] <= child_box[1])


def project_frame(frame, contract=None, *, diagnostic_covered_children=False):
    """Project every object of 1 frame and decide full-frame eligibility.

    `frame` holds `scene_revision`, `screenshot_sha256`, `width`, `height`, optional `focus`, and `objects`.
    """
    contract, digest = (contract, None) if contract else load_contract()
    ids = [ob.get('id') for ob in frame['objects']]
    by_id = {ob['id']: ob for ob in frame['objects']}
    results, reasons = [], []
    for ob in frame['objects']:
        parent, relation = ob.get('parent_id'), ob.get('owner_relation')
        res = project_object(ob, contract, owned=parent is not None)
        o = ob.get('observation') or {}
        if (diagnostic_covered_children and res['reason'] == 'fact_conflict'
                and res['rule_id'] == 'button.uikit'
                and _covered_child_button(ob, by_id.get(parent), frame.get('focus') or {})):
            res = dict(disposition='out_of_scope', cls=None, rule_id=res['rule_id'],
                       reason='fully_covered_child')
        if ids.count(ob['id']) > 1:
            res = _unresolved('duplicate_object_id')
        elif o and (o.get('scene_revision') != frame.get('scene_revision') or o.get('screenshot_sha256') != frame.get('screenshot_sha256')):
            res = _unresolved('frame_identity_mismatch', res.get('rule_id'))
        elif parent is not None and res['reason'] not in EVIDENCE_REASONS:
            if parent not in by_id:
                res = _unresolved('missing_parent', res.get('rule_id'))
            elif relation not in ('same_action', 'separate_action'):
                res = _unresolved('ownership_relation_missing', res.get('rule_id'))
            elif relation == 'same_action' and res['disposition'] != 'unresolved':
                # A1 item 5: an unresolved object stays unresolved under same_action ownership.
                res = dict(res, disposition='owned_metadata', cls=None, reason=None)  # the reason belonged to the pre-ownership outcome
        c = ob.get('construction') or {}
        item = dict(id=ob['id'], disposition=res['disposition'], **{'class': res['cls']}, rule_id=res['rule_id'], reason=res['reason'],
                    parent_id=parent, focus_destination=res.get('focus_destination', False),
                    attributes=dict(style=c.get('style'), role=c.get('role'), selected=o.get('selected'), focusable=o.get('focusable')))
        if item['disposition'] == 'target':
            item['box'] = _box(o, frame.get('width', 0), frame.get('height', 0))
            if item['box'] is None and o:
                item.update(disposition='unresolved', reason='target_geometry_missing')
        if item['disposition'] == 'unresolved':
            reasons.append(f"{item['reason']}:{ob['id']}")
        results.append(item)
    focus = frame.get('focus') or {'state': 'unknown'}
    focus_state = focus.get('state', 'unknown')
    if focus_state == 'known_no_focus' and focus.get('source') == 'empty_registry':
        focus_state = 'unknown'
        reasons.append('empty_registry_is_not_no_focus')
    if focus_state == 'focused':
        hit = next((r for r in results if r['id'] == focus.get('id')), None)
        if not hit or not (hit['disposition'] == 'target' or hit['focus_destination']):
            reasons.append(f"focused_item_not_a_target:{focus.get('id')}")
            focus_state = 'unknown'
    unresolved = [r for r in results if r['disposition'] == 'unresolved']
    return dict(
        mapping_version=contract['mapping_version'], contract_sha256=digest,
        eligible=not unresolved, objects=results, reasons=sorted(reasons), focus_state=focus_state,
        focus_id=focus.get('id') if focus_state == 'focused' else None,
        targets=[r for r in results if r['disposition'] == 'target'],
    )
