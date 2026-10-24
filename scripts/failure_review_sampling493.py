"""Review verified focus comparisons without changing data or models."""
from collections import Counter
import random
import time

import research_queue as q
from experiment_templates import checked
from cached_selection405 import verified_report
from native_selection_comparison import load_source, compare
from model_decision434 import consumer_source, matched_consumer

OUT = None
SEEDS = (49301, 49302, 49303)
SUCCESS = {'correct', 'correct-abstention', 'tp', 'tn'}


def rebuild(bundle):
    q.require(bundle.get('version') == 'failure-review-input-v1', 'review_input_version')
    report = verified_report(bundle['source'])
    q.require(report.get('version') == 'model-comparison-set-v1', 'review_source_version')
    rows = []
    for pair in report['comparisons']:
        native = pair['rows'][0]['arm'] in ('known-box', 'raw-proposal', 'mapped-proposal')
        loader = load_source if native else consumer_source
        left, a = loader(pair['sources']['baseline'])
        right, b = loader(pair['sources']['candidate'])
        q.require(set(a) == set(b) and all(a[k] == b[k] for k in a if k != 'model'), 'review_unmatched_inputs')
        derived = compare(left, right)['rows'] if native else matched_consumer(left, right)
        q.require(len(derived) == len(pair['rows']), 'review_membership')
        for row, recorded in zip(derived, pair['rows']):
            q.require(all(recorded.get(k) == v for k, v in row.items()), 'review_outcome_changed')
            rows.append(dict(row, comparison=pair['pair']))
    keys = [(r['profile'], r['arm'], r['id']) for r in rows]
    q.require(rows and len(keys) == len(set(keys)), 'review_duplicate_case')
    return rows


def summary(rows):
    result = []
    for profile, arm in sorted({(r['profile'], r['arm']) for r in rows}):
        selected = [r for r in rows if (r['profile'], r['arm']) == (profile, arm)]
        result.append(dict(profile=profile, arm=arm, observations=len(selected),
            groups=len({r['group'] for r in selected}),
            noFocus=sum(r['noFocus'] for r in selected),
            baseline=dict(Counter(r['baseline'] for r in selected)),
            candidate=dict(Counter(r['candidate'] for r in selected)),
            gains=sum(r['gain'] for r in selected), losses=sum(r['loss'] for r in selected),
            newWrong=sum(r['newWrong'] for r in selected)))
    return result


def category(row):
    return row['arm'] + '/' + row['candidate']


def metrics(rows):
    return dict(cases=len(rows), categories=len({category(r) for r in rows}),
        groups=len({r['group'] for r in rows}),
        repeatedGroupCases=len(rows)-len({r['group'] for r in rows}),
        members=[dict(id=r['id'], group=r['group'], arm=r['arm'], category=category(r)) for r in rows])


def sample(rows, profile):
    pool = sorted([r for r in rows if r['profile'] == profile and r['candidate'] not in SUCCESS],
                  key=lambda r: (r['group'], r['id'], r['arm']))
    count = min(20, len({r['group'] for r in pool}))
    selected, groups, categories = [], set(), set()
    start = time.perf_counter()
    while len(selected) < count:
        candidates = [r for r in pool if r['group'] not in groups]
        row = min(candidates, key=lambda r: (category(r) in categories, r['group'], r['id'], r['arm']))
        selected.append(row); groups.add(row['group']); categories.add(category(row))
    diverse = metrics(selected)
    elapsed = time.perf_counter()-start
    random_arms = [dict(seed=seed, **metrics(random.Random(seed).sample(pool, count))) for seed in SEEDS]
    supported = count > 0 and all(diverse['categories'] > r['categories'] and diverse['groups'] >= r['groups'] for r in random_arms)
    return dict(profile=profile, poolCases=len(pool), sampleSize=count, diverse=diverse,
        random=random_arms, selectionSeconds=elapsed, outcome='supported' if supported else 'inconclusive',
        limitation='Category coverage is a selection objective, not model accuracy. Groups are retained ancestry identifiers, not proven independent trials.')


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    bundle = q.load(checked(spec['reviewInput']))
    rows = rebuild(bundle)
    report = dict(version='failure-review-sampling-v1', slices=summary(rows), rows=rows,
        samples=[sample(rows, p) for p in ('standard', 'hcf')], modelAccepted=False,
        productionChanged=False, source=bundle['source'],
        unsupportedConditions=['selected-but-unfocused', 'decorative-border', 'bright-artwork'],
        limitation='No-focus truth is available for native cases. Other negative conditions need observed labels, not names inferred from pixels.')
    q.save(OUT/'review.json', report)
    lines = ['# Retained focus failure review', '', 'No model or data role changes.', '',
             '| Profile | Arm | Cases | Groups | No focus | Gains | Losses | New wrong |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in report['slices']:
        lines.append('| '+' | '.join(str(r[k]) for k in ('profile','arm','observations','groups','noFocus','gains','losses','newWrong'))+' |')
    lines += ['', report['limitation'], '', 'Sampling measures review coverage only. It does not measure model improvement.']
    for r in report['samples']:
        lines.append(f"{r['profile']}: {r['sampleSize']} cases per arm; {r['outcome']}.")
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in ('review.json','report.md')]))
