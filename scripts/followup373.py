"""Diagnose fixed development predictions without fitting or moving data."""
from collections import Counter, defaultdict
import research_queue as q
from graph373 import decision

OUT = None


def load(ref):
    path = q.local_path(q.ROOT, ref['path'])
    q.require(q.digest(path) == ref['sha256'], 'changed_input')
    return q.load(path)


def merge(previous, comparisons):
    rows = {}
    models = {}
    for doc in previous:
        for name, scores in doc['scores'].items():
            q.require(len(scores['probabilities']) == len(doc['rows']), 'prediction_length')
            q.require(name not in models or models[name] == scores['model'], 'model_identity')
            models[name] = scores['model']
        for i, row in enumerate(doc['rows']):
            q.require(row['id'] not in rows, 'duplicate_case')
            q.require(row['role'] == 'development' and row['group'], 'development_role')
            q.require(type(row['changed']) is int and row['changed'] in (0, 1), 'invalid_label')
            rows[row['id']] = dict(row, scores={k: v['probabilities'][i] for k, v in doc['scores'].items()})
    for arm, documents in comparisons.items():
        seen = set()
        for doc in documents:
            model = doc['configuration']['models']['gamma']
            q.require(arm not in models or models[arm] == model, 'model_identity')
            models[arm] = model
            for part in doc['sets'].values():
                q.require(len(part['rows']) == len(part['probabilities']['gamma']), 'prediction_length')
                for row, probability in zip(part['rows'], part['probabilities']['gamma']):
                    ident = row['id']; q.require(ident in rows and ident not in seen, 'comparison_membership')
                    seen.add(ident)
                    for key in ('changed', 'role', 'group', 'images', 'layout', 'condition'):
                        q.require(row[key] == rows[ident][key], 'case_identity:' + key)
                    rows[ident]['scores'][arm] = probability
        q.require(seen == set(rows), 'comparison_membership')
    for row in rows.values():
        for value in row['scores'].values(): decision(value)
    return list(rows.values()), models


def correct(row, name):
    value = decision(row['scores'][name])
    return value is not None and value == bool(row['changed'])


def margin(row, name):
    p = row['scores'][name]
    return p - .85 if row['changed'] else .15 - p


def analyze(rows, mode, training):
    prior = ('FOCUS329', 'gamma348', 'movement349')
    losses = [r for r in rows if any(correct(r, n) for n in prior) and not correct(r, 'notification')]
    def case(row):
        return {k: row[k] for k in ('id', 'group', 'layout', 'condition', 'changed', 'scores')}
    if mode == 'losses':
        return dict(lostSuccesses=[dict(case(r), previousCorrect=[n for n in prior if correct(r, n)],
                    controlCorrect=correct(r, 'control')) for r in losses],
                    nextDecision='Separate losses shared with control from losses introduced by notification training. Do not repeat the same correction.')
    if mode == 'margins':
        ranked = sorted(losses, key=lambda r: margin(r, 'notification'))
        return dict(lossMargins=[dict(case(r), margins={n: margin(r,n) for n in r['scores']}) for r in ranked],
                    thresholds=dict(stable=.15, changed=.85), thresholdsChanged=False,
                    nextDecision='Use strongly wrong cases for representation diagnosis. Use near-boundary cases for a fixed-margin training comparison, not threshold tuning.')
    if mode in ('conditions', 'groups'):
        keys = ('layout', 'condition') if mode == 'conditions' else ('group',)
        groups = defaultdict(list)
        for r in rows: groups[tuple(r[k] for k in keys)].append(r)
        slices = []
        for key, members in sorted(groups.items()):
            scores = {}
            for name in members[0]['scores']:
                scores[name] = dict(correct=sum(correct(r,name) for r in members),
                    abstentions=sum(decision(r['scores'][name]) is None for r in members),
                    falseChanges=sum(not r['changed'] and decision(r['scores'][name]) is True for r in members),
                    missedChanges=sum(bool(r['changed']) and decision(r['scores'][name]) is not True for r in members))
            slices.append(dict(slice=dict(zip(keys,key)), count=len(members), scores=scores,
                               lostCaseIDs=[r['id'] for r in members if r in losses]))
        return dict(slices=slices, independentTrials=None,
                    nextDecision='Target conditions with repeatable losses across recorded groups. These related groups do not support deployment risk claims.')
    q.require(mode == 'ancestry', 'unknown_test')
    q.require(training['trainingEligible'] and all(r['role']=='train' for r in training['rows']), 'training_role')
    train = training['rows']
    train_hashes = {p['sha256'] for r in train for p in r['images']}
    dev_hashes = {p['sha256'] for r in rows for p in r['images']}
    return dict(trainingPairs=len(train), developmentPairs=len(rows),
        sharedEncodedImageHashes=sorted(train_hashes & dev_hashes),
        sharedLayouts=sorted({r['layout'] for r in train} & {r['layout'] for r in rows}),
        developmentAncestryRoles=dict(Counter(r.get('ancestryRole','unknown') for r in rows)),
        pixelDisjointProducerClaim=training['pixelDisjoint'], decodedPixelsRechecked=False,
        producerLimitation=training['limitation'], finalAuditEligible=False,
        nextDecision='Keep these cases for development. Reserve different native families and ancestry before making generalization claims.')


def run():
    cfg=q.load(OUT/'config.json')
    rows, models = merge([load(p) for p in cfg['previous']],
                         {k:[load(p) for p in refs] for k,refs in cfg['comparisons'].items()})
    q.require(len(rows)==392, 'expected_membership')
    for model in models.values():
        q.require(q.digest(q.local_path(q.ROOT,model['path']))==model['sha256'], 'model_changed')
    report=analyze(rows,cfg['mode'],load(cfg['training']))
    q.save(OUT/'summary.json',dict(version='focus373-followup-v1',test=cfg['mode'],models=models,
        membership=392, dataRole='development', sourceDomain='authored', modelAccepted=False,
        productionChanged=False, result=report))
