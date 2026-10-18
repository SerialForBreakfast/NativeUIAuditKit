"""T47: score ordered before/after focus pairs with 1 pinned transition model.

Movement, content-only, and no-op pairs stay separate. Thresholds 0.15 and 0.85 stay fixed.
Each pair needs both endpoint focus identities and 1 action receipt. Pairs without them are refused.
Scoring reuses the retained PROGRAM384-D1 path (report_additive341.score_rows) and the
reserve346 outcome rules. The adapter never trains, tunes, or accepts a model.

Manifest builders (`manifest d1`, `manifest graph364`) convert retained corpora into pinned
`temporal-pairs-v1` manifests under reports/work/TEMPORAL414.
"""
import argparse
from collections import Counter
from pathlib import Path

import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs

OUT = None
VERSION = 'temporal-pairs-v1'
KINDS = ('movement', 'content-only', 'no-op')
ACTIONS = ('authored-render', 'native-receipt')
ROLES = ('train', 'development')
DIRECTIONS = ('forward', 'reverse')
# `model` scores pairs with pinned weights. `settings-guarded-rule` reads the sealed retained
# Settings rule result (settings_focus_stability.run). Its `model` pin is the rule implementation.
SCORERS = ('model', 'settings-guarded-rule')
RULE_SOURCE = 'scripts/settings_focus_stability.py'
THRESHOLDS = {'stable': 0.15, 'changed': 0.85}
MAX_PAIRS = 4096
SUCCESS = 'correct'
STORE = q.ROOT / 'reports/work/TEMPORAL414'
# Retained condition names. An unknown condition is refused, not guessed.
CONDITION_KINDS = {'movement': 'movement', 'base-movement': 'movement', 'dim-movement': 'movement',
                   'banner-movement': 'movement', 'toast-movement': 'movement',
                   'identical': 'no-op', 'stable-repeat': 'no-op', 'base-identical': 'no-op',
                   'dim-identical': 'no-op', 'banner-identical': 'no-op', 'toast-identical': 'no-op',
                   'artwork-only': 'content-only', 'matched-content': 'content-only',
                   'dim-appearance': 'content-only', 'banner-appearance': 'content-only',
                   'toast-appearance': 'content-only',
                   'settings-row-move': 'movement', 'settings-page-change': 'movement', 'settings-same-row': 'no-op'}
SETTINGS_RULE = 'reports/work/SETTINGS-STABILITY-23/retained-final/result.json'
SETTINGS_SEMANTICS = 'reports/work/FOCUS-RECORDED-STRUCTURAL-22/artifacts/settings-ocr/semantics.json'


def parameters(value):
    """Return the direction. Thresholds are fixed at 0.15 and 0.85. `scorer` is optional (default `model`)."""
    q.require(isinstance(value, dict) and {'direction', 'thresholds'} <= set(value) <=
              {'direction', 'thresholds', 'scorer'}, 'temporal_parameters')
    q.require(value['direction'] in DIRECTIONS, 'temporal_direction')
    q.require(value['thresholds'] == THRESHOLDS, 'temporal_thresholds_fixed')
    q.require(value.get('scorer', 'model') in SCORERS, 'temporal_scorer')
    q.require(value.get('scorer', 'model') == 'model' or value['direction'] == 'forward', 'rule_direction')
    return value['direction']


def decided(value):
    """A model probability, a rule decision dict, or None (no prior)."""
    if value is None:
        return None
    if isinstance(value, dict):
        q.require(set(value) == {'decision', 'reason'} and value['decision'] in (0, 1, None), 'rule_decision')
        return value['decision']
    return decision(value)


def decision(p):
    """Return 1 (changed), 0 (stable), or None (abstention). Same rule as research_campaign340.decision."""
    q.require(type(p) in (int, float) and 0 <= p <= 1, 'probability')
    return 0 if p <= THRESHOLDS['stable'] else 1 if p >= THRESHOLDS['changed'] else None


def outcome(value, label):
    if value is None:
        return 'abstention'
    if value == label:
        return SUCCESS
    return 'false-change' if value == 1 else 'missed-change'


def check_pair(row):
    """Validate 1 pair. Endpoint identities and the action receipt are required."""
    fields = {'id', 'group', 'role', 'kind', 'changed', 'condition', 'sourceDomain', 'images', 'endpoints', 'action'}
    q.require(isinstance(row, dict) and fields <= set(row) <= fields | {'layout'}, 'pair_fields')
    q.require(isinstance(row['id'], str) and row['id'] and isinstance(row['group'], str) and row['group'], 'pair_identity')
    ends = row['endpoints']
    q.require(isinstance(ends, dict) and set(ends) == {'before', 'after'} and
              all(isinstance(v, str) and v.strip() for v in ends.values()), 'pair_endpoint_identity_missing')
    q.require(row['role'] in ROLES, 'pair_role')
    q.require(row['kind'] in KINDS, 'pair_kind')
    moved = ends['before'] != ends['after']
    q.require(row['changed'] == int(row['kind'] == 'movement') and moved == (row['kind'] == 'movement'),
              'pair_label_endpoint_conflict')
    images = row['images']
    q.require(isinstance(images, list) and len(images) == 2, 'pair_images')
    for pin in images:
        q.check_pin(pin)
    q.require(row['kind'] != 'content-only' or images[0]['sha256'] != images[1]['sha256'], 'pair_content_unchanged')
    action = row['action']
    q.require(isinstance(action, dict) and set(action) == {'source', 'evidence'} and action['source'] in ACTIONS,
              'pair_action_receipt')
    q.check_pin(action['evidence'])
    return row


def manifest(doc):
    """Validate a temporal-pairs-v1 document and return its rows in order."""
    q.require(isinstance(doc, dict) and set(doc) == {'version', 'description', 'sources', 'rows'}, 'manifest_fields')
    q.require(doc['version'] == VERSION, 'manifest_version')
    rows = [check_pair(r) for r in doc['rows']]
    q.require(1 <= len(rows) <= MAX_PAIRS, 'manifest_scope')
    q.require(len({r['id'] for r in rows}) == len(rows), 'pair_duplicate')
    for pin in doc['sources']:
        q.check_pin(pin)
    return rows


def oriented(row, direction):
    """Return the pair in the requested temporal order. Reverse swaps images and endpoints; labels stay."""
    if direction == 'forward':
        return row
    ends = row['endpoints']
    return dict(row, images=row['images'][::-1], endpoints=dict(before=ends['after'], after=ends['before']))


def prior_values(doc, rows):
    """Prior predictions by pair ID. The prior must cover every pair."""
    q.require(isinstance(doc, dict) and isinstance(doc.get('rows'), list), 'prior_format')
    values = {}
    for r in doc['rows']:
        q.require(isinstance(r, dict) and isinstance(r.get('id'), str) and r['id'] not in values, 'prior_format')
        values[r['id']] = r['probability'] if r.get('probability') is not None else \
            dict(decision=r['decision'], reason=r['reason'])
        decided(values[r['id']])
    q.require(all(r['id'] in values for r in rows), 'prior_membership')
    return values


def case(row, probability, prior):
    """Build 1 per-case row. `prior` is None when no prior exists."""
    label = row['changed']
    result = outcome(decided(probability), label)
    old = None if prior is None else outcome(decided(prior), label)
    return dict(id=row['id'], group=row['group'], layout=row.get('layout'), role=row['role'], kind=row['kind'],
                condition=row['condition'], sourceDomain=row['sourceDomain'], actionSource=row['action']['source'],
                endpoints=row['endpoints'], changed=label,
                probability=None if isinstance(probability, dict) else probability, decision=decided(probability),
                reason=probability['reason'] if isinstance(probability, dict) else None,
                outcome=result, priorProbability=None if isinstance(prior, dict) else prior, priorOutcome=old,
                gain=old is not None and old != SUCCESS and result == SUCCESS,
                lost=old is not None and old == SUCCESS and result != SUCCESS)


def counts(cases):
    """Counts with the reserve346.count field names, plus an outcome histogram."""
    return dict(frames=len(cases), groups=len({c['group'] for c in cases}),
                correct=sum(c['outcome'] == SUCCESS for c in cases),
                falseChange=sum(c['outcome'] == 'false-change' for c in cases),
                missedChange=sum(c['outcome'] == 'missed-change' for c in cases),
                abstentions=sum(c['outcome'] == 'abstention' for c in cases),
                priorCorrect=sum(c['priorOutcome'] == SUCCESS for c in cases),
                gained=sum(c['gain'] for c in cases), lost=sum(c['lost'] for c in cases),
                outcomes=dict(Counter(c['outcome'] for c in cases)))


def summarize(cases, direction, prior_source):
    q.require(cases, 'empty_comparison')
    slices = {}
    for field, name in (('kind', 'kind'), ('role', 'role'), ('group', 'group'), ('layout', 'layout'),
                        ('actionSource', 'action'), ('sourceDomain', 'domain')):
        for value in sorted({str(c[field]) for c in cases}):
            slices[name + ':' + value] = counts([c for c in cases if str(c[field]) == value])
    # Same keys as reserve346.count (sourceDomain/condition/group). This allows exact comparison with FOCUS366.
    legacy = {}
    for c in cases:
        legacy.setdefault(c['sourceDomain'] + '/' + c['condition'] + '/' + c['group'], []).append(c)
    legacy = {k: {f: v for f, v in counts(rows).items() if f in
                  ('correct', 'falseChange', 'missedChange', 'abstentions', 'gained', 'lost')} | dict(count=len(rows))
              for k, rows in sorted(legacy.items())}
    total = counts(cases)
    lost = [c['id'] for c in cases if c['lost']]
    gains = [c['id'] for c in cases if c['gain']]
    return dict(version='temporal-summary-v1', direction=direction, thresholds=THRESHOLDS, prior=prior_source,
                totals=total, slices=slices, legacyCounts=legacy, gains=gains, lostPriorSuccesses=lost,
                falseChanges=[c['id'] for c in cases if c['outcome'] == 'false-change'],
                decisions=dict(zeroLostPriorSuccesses=not lost if prior_source else None,
                               gainWithoutLoss=bool(gains) and not lost if prior_source else None,
                               trainingRolePresent=any(c['role'] == 'train' for c in cases)),
                modelAccepted=False,
                limitation='Train-role pairs are not independent evaluation. Related pairs are not independent trials. '
                           'Authored focus identities are not OS observations.')


def rule_decisions(result, rows):
    """Pair decisions of the guarded Settings rule, from its sealed retained result.

    The rule is an action-level decision: switch (1), unchanged (0), or abstention (None).
    Pairs outside the rule's same-screen Settings context are abstentions with reason unsupported_context.
    """
    import human_annotation_review as h
    from settings_focus_stability import action_outcome
    doc = h.sealed(checked(result), 'settings-stability-v1')
    actions = {}
    for action in doc['actions']:
        key = (action['endpoints']['before']['sha256'], action['endpoints']['after']['sha256'])
        q.require(key not in actions, 'rule_duplicate_action')
        guarded = [c['arms']['combined'] for c in action['guardedControls']]
        state = action_outcome(guarded, all(c['scorable'] for c in guarded))
        actions[key] = dict(decision={'switch': 1, 'unchanged': 0}.get(state), reason='rule_' + state)
    values = [actions.get((r['images'][0]['sha256'], r['images'][1]['sha256']),
                          dict(decision=None, reason='unsupported_context')) for r in rows]
    q.require(sum(v['reason'] != 'unsupported_context' for v in values) == len(actions), 'rule_membership')
    return values, doc['summaries']['guarded']


def run():
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    direction = parameters(cfg['parameters'])
    scorer = cfg['parameters'].get('scorer', 'model')
    refs = resolve_inputs(cfg, OUT)
    q.require(not (direction == 'reverse' and 'prior' in refs), 'reverse_prior_internal')
    q.require(('rule' in refs) == (scorer == 'settings-guarded-rule'), 'rule_input')
    doc = document(refs['pairs'])
    rows = manifest(doc)
    for pin in {p['path']: p for r in rows for p in [r['action']['evidence']]}.values():
        checked(pin)  # Every action receipt must exist with its pinned hash.
    if scorer == 'settings-guarded-rule':
        q.require(refs['model']['path'] == RULE_SOURCE, 'rule_scorer_pin')
        checked(refs['model'])
        values, controls = rule_decisions(refs['rule'], rows)
        prior, source = None, None
        if 'prior' in refs:
            found = prior_values(document(refs['prior']), rows)
            prior, source = [found[r['id']] for r in rows], dict(kind='pinned-predictions', ref=refs['prior'])
        cases = [case(r, v, p) for r, v, p in zip(rows, values, prior or [None] * len(rows))]
        report = summarize(cases, direction, source)
        report.update(model=refs['model'], rule=refs['rule'], ruleControls=controls, scorer=scorer,
                      pairs=refs['pairs'], description=doc['description'])
        write(report, cases, direction, refs['model'],
              [dict(id=r['id'], probability=None, **v) for r, v in zip(rows, values)])
        return
    score_model(refs['model'], refs['pairs'], refs.get('prior'), direction, doc, rows, scorer)


def score_model(model, pairs, prior_ref, direction='forward', doc=None, rows=None, scorer='model'):
    """Score pinned weights on a pinned manifest and write the T47 outputs to OUT. T49 reuses this after training."""
    import additive341 as a
    import report_additive341 as scoring
    if doc is None:
        doc = document(pairs)
        rows = manifest(doc)
    a.t.set_num_threads(2)
    network = a.e.load_candidate(checked(model))
    network.eval()

    def scores(direction_):
        with a.t.inference_mode():
            values = scoring.score_rows(network, [oriented(r, direction_) for r in rows], False).tolist()
        q.require(len(values) == len(rows), 'score_count')
        return [float(v) for v in values]

    values = scores(direction)
    if direction == 'reverse':
        # The matched control is the same model on the same pairs in forward order.
        prior, source = scores('forward'), dict(kind='same-model-forward')
    elif prior_ref:
        found = prior_values(document(prior_ref), rows)
        prior, source = [found[r['id']] for r in rows], dict(kind='pinned-predictions', ref=prior_ref)
    else:
        prior, source = [None] * len(rows), None
    cases = [case(oriented(r, direction), v, p) for r, v, p in zip(rows, values, prior)]
    report = summarize(cases, direction, source)
    report.update(model=model, scorer=scorer, pairs=pairs, description=doc['description'])
    write(report, cases, direction, model, [dict(id=r['id'], probability=v) for r, v in zip(rows, values)])


def write(report, cases, direction, model, predictions):
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'cases.json', dict(version='temporal-cases-v1', rows=cases, modelAccepted=False))
    q.save(OUT / 'predictions.json', dict(version='temporal-predictions-v1', direction=direction, model=model,
                                          rows=predictions))
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT / name)) for name in ('benchmark_summary.json', 'cases.json', 'predictions.json')]))


# Manifest builders. They read retained corpora only and write pinned manifests.

def pin(path):
    path = Path(path)
    return dict(path=q.relative(path), sha256=q.digest(path))


def authored_endpoint(image):
    """Focused node of an authored render. The annotation must name the same image hash."""
    found = sorted((q.ROOT / image['path']).parent.glob('*_annotations.json'))
    q.require(len(found) == 1, 'annotation_missing:' + image['path'])
    note = q.load(found[0])
    q.require(note['focusedImageSHA256'] == image['sha256'] and note['focusedNodeID'], 'annotation_image_mismatch')
    return note['focusedNodeID'], pin(found[0])


def native_endpoint(image):
    """Observed native focus. The before and after scene brackets must agree with the requested target.

    The action receipt is the complete capture record, which lists each frame and its requested target.
    """
    path = q.ROOT / image['path']
    record = q.load(path.with_suffix('.json'))
    q.require(record['image'] == image, 'native_record_image')
    before, after = record['before']['scene']['activeFocusId'], record['after']['scene']['activeFocusId']
    q.require(before and before == after, 'endpoint_focus_unsettled')
    receipt = path.parent / 'capture.json'
    capture = q.load(receipt)
    q.require(capture['complete'] and capture['cleanup'] and capture['error'] is None, 'native_capture_incomplete')
    frame, = [f for f in capture['frames'] if f['image'] == image]
    q.require(frame['target'] == after, 'native_target_not_observed')
    return after, pin(receipt)


def pair_row(row, endpoints, evidence, source, role=None):
    kind = CONDITION_KINDS.get(row['condition'])
    q.require(kind is not None, 'condition_unknown:' + str(row['condition']))
    value = dict(id=row['id'], group=row['group'], role=role or row['role'], kind=kind, changed=row['changed'],
                 condition=row['condition'], sourceDomain=row['sourceDomain'], images=row['images'],
                 endpoints=dict(before=endpoints[0], after=endpoints[1]), action=dict(source=source, evidence=evidence))
    if row.get('layout'):
        value['layout'] = row['layout']
    return check_pair(value)


def build_d1():
    """PROGRAM384-D1 membership: the 1,408 FOCUS-346 rows in their original order."""
    inputs = q.ROOT / 'reports/work/FOCUS-346/inputs.json'
    data = q.load(inputs)
    sources = {s['path']: s for s in data['sources']}
    for s in sources.values():
        checked(s)
    out = []
    for row in data['rows']:
        if row['sourceDomain'] == 'native-fixture':
            (b, _), (a_, receipt) = native_endpoint(row['images'][0]), native_endpoint(row['images'][1])
            out.append(pair_row(row, (b, a_), receipt, 'native-receipt'))
        elif row.get('endpoints'):
            ends = [e['focusID'] for e in row['endpoints']]
            source = 'reports/work/FOCUS-341/negatives.json' if row['condition'] == 'matched-content' \
                else 'reports/work/FOCUS-326/corpus.json'
            out.append(pair_row(row, ends, sources[source], 'authored-render'))
        else:
            (b, _), (a_, note) = authored_endpoint(row['images'][0]), authored_endpoint(row['images'][1])
            out.append(pair_row(row, (b, a_), note, 'authored-render'))
    return dict(version=VERSION, description='PROGRAM384-D1 retained membership (FOCUS-346 order).',
                sources=[pin(inputs)] + list(sources.values()), rows=out)


GRAPH364 = ['focus364-11-grid', 'focus364-13-top_nav_shelf', 'focus364-r2-10-shelf-artwork-s0',
            'focus364-r2-10-shelf-artwork-s1', 'focus364-r2-12-hero_detail-artwork-s0',
            'focus364-r2-12-hero_detail-artwork-s1', 'focus365-0-settings_list-artwork-s0',
            'focus365-0-settings_list-artwork-s1', 'focus365-1-action_dialog-artwork-s0',
            'focus365-1-action_dialog-artwork-s1', 'focus365-2-focus_maze-artwork-s0', 'focus365-2-focus_maze-artwork-s1']


def build_graph364(native=True):
    """FOCUS366/373 development membership: 392 authored pairs, plus the 16 native FOCUS-343 pairs if requested."""
    out, sources = [], []
    for job in GRAPH364:
        path = q.QUEUE / 'jobs' / job / 'attempts/1/out/corpus.json'
        doc = q.load(path)
        q.require(doc['role'] == 'development' and doc['trainingEligible'] is False, 'graph364_role')
        sources.append(pin(path))
        frames = {f['image']['path']: f for f in doc['frames']}
        for i, row in enumerate(doc['rows']):
            ends, notes = [], []
            for image in row['images']:
                frame = frames[image['path']]
                q.require(frame['image'] == image, 'graph364_frame_image')
                ends.append(frame['target']); notes.append(frame['annotation'])
            # retained348 names rows without an ID by corpus path and index. Keep that identity.
            value = dict(row, id=row.get('id', q.relative(path) + ':' + str(i)), sourceDomain='authored')
            out.append(pair_row(value, ends, notes[1], 'authored-render'))
    if native:
        d1 = q.load(q.ROOT / 'reports/work/FOCUS-346/inputs.json')
        for row in d1['rows']:
            if row['sourceDomain'] == 'native-fixture':
                (b, _), (a_, receipt) = native_endpoint(row['images'][0]), native_endpoint(row['images'][1])
                out.append(pair_row(row, (b, a_), receipt, 'native-receipt'))
        sources.append(pin(q.ROOT / 'reports/work/FOCUS-346/inputs.json'))
    return dict(version=VERSION, description='FOCUS366/373 development pairs' + (' plus FOCUS-343 native pairs.' if native else '.'),
                sources=sources, rows=out)


def build_settings():
    """The 7 reviewed native Settings actions (5 same-screen, 2 page changes). Development role only.

    Endpoint identity is the screen title and the text of the 1 reviewed focused row.
    """
    import human_annotation_review as h
    import focus_recorded_readiness as readiness
    semantics = h.sealed(h.local(SETTINGS_SEMANTICS), 'focus-recorded-semantics-v1')
    i = {k: v['path'] for k, v in semantics['inputs'].items()}
    _, truth = readiness.run_with_frames(i['batch'], i['baseline'], i['pending'], i['revision'], i['completeness'])
    rule = pin(q.ROOT / SETTINGS_RULE)
    h.sealed(q.ROOT / SETTINGS_RULE, 'settings-stability-v1')
    out = []
    for action in semantics['actions']:
        ends, images = [], []
        for side in ('before', 'after'):
            sha = action['endpoints'][side]['sha256']
            frame, described = truth[sha], semantics['descriptions'][sha]
            focused = [c['id'] for c in frame['controls'] if c['state'] == 'focused']
            q.require(len(focused) == 1, 'settings_focus_not_unique')
            text = {r['id']: r['text'] for r in described['rows']}
            q.require(focused[0] in text and frame['image']['sha256'] == sha, 'settings_endpoint_row')
            ends.append(described['title'] + ':' + text[focused[0]])
            images.append(dict(path=frame['image']['path'], sha256=sha))
        condition = ('settings-page-change' if not action['sameTitle'] else
                     'settings-row-move' if ends[0] != ends[1] else 'settings-same-row')
        row = dict(id='settings-' + action['actionID'], group='settings-journey', role='development',
                   changed=int(ends[0] != ends[1]), condition=condition, sourceDomain='native-settings',
                   images=images, layout='settings')
        out.append(pair_row(row, ends, rule, 'native-receipt'))
    return dict(version=VERSION, description='Reviewed native Settings actions (SETTINGS-STABILITY-23 membership plus 2 page changes).',
                sources=[pin(q.ROOT / SETTINGS_RULE), semantics['inputs']['completeness']], rows=out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['manifest'])
    parser.add_argument('name', choices=['d1', 'graph364', 'graph364-authored', 'settings'])
    args = parser.parse_args()
    doc = {'d1': build_d1, 'graph364': build_graph364, 'graph364-authored': lambda: build_graph364(False),
           'settings': build_settings}[args.name]()
    manifest(doc)
    STORE.mkdir(parents=True, exist_ok=True)
    target = STORE / ('pairs-' + args.name + '.json')
    if target.exists():
        q.require(q.load(target) == doc, 'manifest_changed')  # Pinned manifests stay immutable.
    else:
        q.save(target, doc)
    print(q.relative(target), q.digest(target), len(doc['rows']), dict(Counter(r['kind'] for r in doc['rows'])))
