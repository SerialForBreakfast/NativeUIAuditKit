"""Prepare fixed rule diagnostics without submitting or approving them."""
import research_queue as q


def prepare(owner):
    folder=q.ROOT/'Research/ResearchSpecs/HCF376'
    code=[q.ROOT/'scripts'/name for name in ('hcf_rule_review376.py','score_hcf_pilot.py')]
    deps=[dict(job=j,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/j/'spec.json')),outputs=[n]) for j,n in
        [('hcf371r4-60-rules','comparison.json'),('hcf371r4-40-catalog','admission.json'),('hcf371-00-retained','admission.json')]]
    for suffix,step,question,decision in [
        ('proposal-recall','proposals','Do the fixed outline proposals contain the focused control even when selection fails?',
         'Poor proposal recall requires another proposal source. Good recall with missed selections requires selection diagnosis.'),
        ('wrong-selections','wrong_selections','Do the 25 wrong rule selections match unfocused controls or unrelated image regions?',
         'Unfocused matches require decoration negatives. Unmatched outlines require contour and geometry diagnosis.'),
        ('boundary-support','contrast','Do rule misses have less bright-mask support near the observed focused body?',
         'A difference supports an outline-label study. No difference argues against changing brightness thresholds alone.')]:
        spec=dict(version='research-spec-v2',id='hcf376-'+suffix+'-v1',task='HCF376',owner=owner,
            kind='screen',jobKind='aggregation',authority='diagnostic',hypothesis=question,question=question,
            controlledComparison='Compare retained rules on identical development and retained frames. Preserve pixels, labels, and thresholds.',
            decisionRule=decision,nextActionByOutcome={'supported':decision,'unsupported':'Record the missing evidence. Do not change model or rule thresholds.'},
            adapter=dict(type='python-callable',steps=['hcf_rule_review376.'+step],outputAttributes=['hcf_rule_review376.OUT']),
            inputs=[dict(path=q.relative(p),sha256=q.digest(p)) for p in code],dependencies=deps,
            evidence=dict(citations='sources.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        q.validate(spec);path=folder/(spec['id']+'.json');q.require(not path.exists(),'immutable_spec_exists');q.save(path,spec)
        print(spec['id'])


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owner',required=True)
    prepare(parser.parse_args().owner)
