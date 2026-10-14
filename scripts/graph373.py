"""Read pinned predictions and request examples without changing data roles."""
from collections import Counter, defaultdict
import math
import random

import research_queue as q
from focus_evidence import upper95

OUT = None


def decision(value):
    q.require(type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 1, 'invalid_probability')
    return True if value >= .85 else False if value <= .15 else None


def records(doc):
    rows = []
    seen = set()
    for source, part in doc['sets'].items():
        original = part['originalProbabilities']
        predictions = dict(part['probabilities'], original=original)
        q.require(all(len(p) == len(part['rows']) for p in predictions.values()), 'prediction_length')
        for i, row in enumerate(part['rows']):
            q.require(row['id'] not in seen, 'duplicate_prediction'); seen.add(row['id'])
            q.require(row['role'] == 'development' and row['group'], 'development_role_required')
            q.require(type(row['changed']) is int and row['changed'] in (0, 1), 'invalid_label')
            q.require(row.get('sourceDomain') == 'authored', 'unsupported_domain')
            rows.append(dict(row, source=source, predictions={name: decision(p[i]) for name, p in predictions.items()}))
    q.require(rows, 'empty_predictions')
    return rows


def summarize(rows, key):
    groups = defaultdict(list)
    counts = Counter(total=len(rows), correct=0, abstentions=0, wrong=0, changed=0, unchanged=0,
                     falseStable=0, stableDecisions=0, falseChange=0, missedChangeIncludingAbstention=0)
    for row in rows:
        pred = row['predictions'][key]; truth = bool(row['changed'])
        correct = pred is not None and pred == truth
        counts['correct'] += correct
        counts['abstentions'] += pred is None
        counts['wrong'] += pred is not None and pred != truth
        counts['changed' if truth else 'unchanged'] += 1
        counts['stableDecisions'] += pred is False
        counts['falseStable'] += truth and pred is False
        counts['falseChange'] += not truth and pred is True
        counts['missedChangeIncludingAbstention'] += truth and pred is not True
        groups[row['group']].append(int(correct))
    def rate(n, d):
        return dict(numerator=counts[n], denominator=counts[d], value=counts[n]/counts[d] if counts[d] else None)
    return dict(counts=dict(counts), rowAccuracy=rate('correct', 'total'),
                equalGroupAccuracy=sum(sum(g)/len(g) for g in groups.values())/len(groups) if groups else None,
                groups=len(groups), falseStableAmongChanged=rate('falseStable', 'changed'),
                errorAmongStable=rate('falseStable', 'stableDecisions'),
                missedChanges=rate('missedChangeIncludingAbstention', 'changed'),
                coverage=dict(numerator=len(rows)-counts['abstentions'], denominator=len(rows)),
                independentTrials=None, binomialUpper95=None,
                limit='Related authored development cases. Independent deployment risk is not established.')


def compare(rows):
    q.require(len({r['id'] for r in rows}) == len(rows), 'duplicate_case')
    gains, losses, grouped = [], [], defaultdict(list)
    for row in rows:
        truth = bool(row['changed']); p = row['predictions']
        before = p['control'] is not None and p['control'] == truth
        after = p['gamma'] is not None and p['gamma'] == truth
        if before and not after: losses.append(row['id'])
        if after and not before: gains.append(row['id'])
        grouped[row['group']].append(int(after)-int(before))
    effects = [sum(v)/len(v) for v in grouped.values()]
    interval = None
    if len(effects) >= 2:
        rng = random.Random(373)
        draws = sorted(sum(rng.choices(effects, k=len(effects)))/len(effects) for _ in range(1000))
        interval = [draws[25], draws[974]]
    return dict(gains=gains, losses=losses, groupDelta=sum(effects)/len(effects) if effects else None,
                descriptiveGroupInterval95=interval, independentSafetyClaim=False,
                decision='Reject replacement; retained successes are lost.' if losses else
                'Review other retained sets before any advancement.' if gains else 'No measured gain on this membership.')


def load_config():
    cfg = q.load(OUT/'config.json')
    for pin in cfg['pins']:
        q.require(q.digest(q.ROOT/pin['path']) == pin['sha256'], 'input_changed')
    return cfg


def audit():
    cfg = load_config()
    rows = records(q.load(q.ROOT/cfg['comparison']))
    q.save(OUT/'summary.json', dict(rows=rows, reports={name:summarize(rows, name) for name in ('control','gamma','original')},
        comparison=compare(rows), modelAccepted=False, dataRole='development', domain='authored',
        nextAction='Use the aggregate across all parts before selecting a correction.'))


def aggregate():
    cfg = load_config(); rows=[]
    for dep in q.load(OUT/'dependencies.json'):
        for pin in dep['outputs']:
            q.require(q.digest(q.ROOT/pin['path']) == pin['sha256'], 'result_changed')
            rows.extend(q.load(q.ROOT/pin['path'])['rows'])
    q.require(len(rows) == 392, 'incomplete_membership')
    slices={c:{name:summarize([r for r in rows if r['condition']==c],name) for name in ('control','gamma')}
            for c in sorted({r['condition'] for r in rows})}
    q.save(OUT/'summary.json',dict(arm=cfg['arm'],reports={name:summarize(rows,name) for name in ('control','gamma','original')},
        comparison=compare(rows), slices=slices, modelAccepted=False, productionChanged=False,
        nextAction='Prioritize conditions with lost movement and false changes. Do not tune on final audit data.'))


def request_audit():
    cfg = load_config(); reports=[]
    for pin in cfg['requests']:
        d=q.load(q.ROOT/pin['path'])
        count=math.prod(len(d[k]) for k in ('seeds','positions','layouts','backgrounds'))*len(d.get('artwork_styles',[None]))
        q.require(count==d['budget']['max_cases'], 'request_count')
        reports.append(dict(path=pin['path'], cases=count, sourceRole=d['source_role'],
            trainingEligible=False, targetMatchesLocal=d['target']['simulator_udid']==cfg['target'],
            positions=d['positions'], estimateBytes=count*16*1024**2,
            declaredBytes=d['budget']['max_retained_bytes']))
    q.save(OUT/'summary.json',dict(requests=reports,totalCases=sum(r['cases'] for r in reports),
        trainingEligible=False, modelAccepted=False,
        decision='Keep calibration requests for diagnosis. Use separately admitted native training producers; do not rewrite calibration labels.',
        blockers=['Current target differs from supplied examples.','Seed use and live producer qualification need checks after HCF capture.'],
        owner='research-host-NUIAK'))


def risk_plan():
    load_config()
    q.save(OUT/'summary.json',dict(examples=[dict(independentTrials=n, errors=0,upper95=upper95(0,n)) for n in (0,19,30,59,299)],
        modelAccepted=False, measuredModelRisk=None,
        decision='Use 59 independent zero-error changed trials for an illustrative 5% upper bound. Related frames do not meet this requirement.',
        nextAction='Report actual connected groups and withheld decisions separately. Do not change thresholds.'))
