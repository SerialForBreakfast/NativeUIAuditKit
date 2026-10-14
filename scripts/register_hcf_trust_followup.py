"""Register a bounded review of retained HCF errors. Do not approve or start it."""
import research_queue as q


def register(owner, queue=q.QUEUE):
    source = q.load(queue / 'jobs/hcf371r5-92-decision/spec.json')
    code = q.ROOT / 'scripts/hcf_failure_review.py'
    spec = dict(version='research-spec-v2', id='hcf-trust-c1-errors-v1', task='PROGRAM384-C1', owner=owner,
        kind='screen', jobKind='aggregation', authority='diagnostic',
        hypothesis='Matched retained outcomes show which HCF conditions all methods miss.',
        question='Which retained HCF errors affect every method, and which depend on the method?',
        controlledComparison='Compare the 4 existing methods on identical development and retained cases. Run no new inference.',
        decisionRule='Reject mismatched IDs, pixels, groups, or roles. Count errors by supported conditions. Do not accept a model.',
        nextActionByOutcome={
            'sharedMisses': 'Inspect original geometry for shared misses before selecting a data correction.',
            'methodDifferences': 'Review disagreement cases before proposing a combined detector.',
            'invalidInputs': 'Repair the named comparison input without changing historical results.'},
        adapter=dict(type='python-callable', steps=['hcf_failure_review.run'], outputAttributes=['hcf_failure_review.OUT']),
        inputs=[dict(path=q.relative(code), sha256=q.digest(code))], dependencies=source['dependencies'],
        evidence=dict(citations='sources.json'),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
    folder = q.ROOT / 'Research/ResearchSpecs/TRUST-REPAIR'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (spec['id'] + '.json')
    q.require(not path.exists(), 'immutable_spec_exists')
    q.save(path, spec)
    return q.submit(path, queue)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    print(register(parser.parse_args().owner))
