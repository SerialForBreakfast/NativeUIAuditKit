"""Prepare a bounded Standard batch. Do not start or restart the runner."""
import argparse
import research_queue as q
import research_approval as approval

FOLDER = q.ROOT / 'Research/ResearchSpecs/STANDARD390'


def pin(path):
    return dict(path=path, sha256=q.digest(q.local_path(q.ROOT, path)))


def dependency(ident, output):
    path = q.QUEUE / 'jobs' / ident / 'spec.json'
    if not path.exists():
        path = FOLDER / (ident + '.json')
    return dict(job=ident, specSHA256=q.text_digest(q.load(path)), outputs=[output])


def save(path, value):
    if path.exists():
        q.require(q.load(path) == value, 'immutable_spec_changed')
    else:
        q.save(path, value)


def make(ident, question, decision, config, deps, extra):
    config_path = FOLDER / (ident + '-config.json')
    save(config_path, config)
    step = 'prepare' if ident.endswith('05-data-priorities') else 'run'
    spec = dict(version='research-spec-v2', id=ident, task='STANDARD390', owner='Maximum-mini-NUIAK',
        kind='screen', authority='diagnostic', jobKind='aggregation', question=question, hypothesis=question,
        controlledComparison='Compare retained predictions on identical rows and fixed thresholds. Keep Standard and HCF work separate.',
        decisionRule=decision,
        nextActionByOutcome=dict(supported='Prepare a matched correction for the named failure while preserving all retained successes.',
            contradicted='Keep the baseline. Resolve unsupported evidence before training or generating more data.'),
        inputs=[pin('scripts/standard390.py'), *extra],
        dependencies=deps, stage=[{'from': pin(q.relative(config_path)), 'to': 'config.json'}],
        evidence=dict(citations='sources.json', reads=[p['path'] for p in extra]),
        adapter=dict(type='python-callable', steps=['standard390.' + step], outputAttributes=['standard390.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
    # Model pins protect identity; the report consumes saved predictions, not weights.
    spec['evidence']['reads'] = [p['path'] for p in extra if p['path'].endswith('.json')]
    q.validate(spec)
    q.verify_pins(spec)
    save(FOLDER / (ident + '.json'), spec)
    return spec


def build():
    FOLDER.mkdir(parents=True, exist_ok=True)
    specs = []
    tests = [
        ('01-retained-appearance', ['01-original'],
         'Which original-view successes does notification training lose, and are those losses shared with its matched control?',
         'List paired gains, losses, margins, and data roles. Preserve the losses in the next correction; do not relax the gate.'),
        ('02-native-transfer', ['02-regression-native', '03-regression-replay'],
         'Does the notification correction preserve retained native and replay movements?',
         'Separate native and replay outcomes. If native movement fails, prioritize native examples rather than authored volume.'),
        ('03-context-regression', ['04-regression-global', '05-regression-left', '06-regression-center'],
         'Which retained context views cause strong errors rather than near-threshold errors?',
         'Use case margins to distinguish lost visual evidence from weak decisions. Do not infer screen position from view names.'),
        ('04-identical-neighbors', ['27-neighbors-0', '28-neighbors-2'],
         'Does the notification correction preserve focus movement between identical neighboring controls?',
         'If identical-neighbor losses occur, prepare matched movement examples with unchanged artwork. Otherwise retain this regression test.')]
    for suffix, names, question, rule in tests:
        pairs = [[f'focus366-control-{name}', f'focus366-notification-{name}'] for name in names]
        deps = [dependency(job, 'comparison.json') for pair in pairs for job in pair]
        specs.append(make('standard390-' + suffix, question, rule,
            dict(pairs=pairs, decision=rule), deps, []))
    scorecard = 'reports/work/REAL-MODEL-SCORECARD-36/scorecard-final/scorecard.json'
    doc = q.load(q.ROOT / scorecard)
    refs = [pin(scorecard), doc['inputs'], *doc['rawPredictions']]
    for ref in refs:
        q.require(pin(ref['path']) == ref, 'retained_scorecard_changed')
    question = 'Which Standard data should we prepare from detector gaps and retained transition losses?'
    rule = 'Rank case-linked capture needs. Keep unknown profile, taxonomy, and label coverage explicit. Do not accept a model.'
    specs.append(make('standard390-05-data-priorities', question, rule,
        dict(scorecard=scorecard, externalEvidence=refs),
        [dependency(s['id'], 'review.json') for s in specs], refs))
    return specs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true')
    args = parser.parse_args()
    specs = build()
    # Validate the entire batch before approving any job.
    for spec in specs:
        q.validate(spec)
        q.verify_pins(spec)
    for spec in specs:
        if args.submit:
            q.submit(FOLDER / (spec['id'] + '.json'))
            approval.approve(q.QUEUE, spec['id'], 'agent:standard390',
                'Maintainer requests ready Standard diagnostics from retained evidence. Preserve current execution and all model gates.')
        print(spec['id'], q.text_digest(spec), flush=True)


if __name__ == '__main__':
    main()
