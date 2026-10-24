"""Join completed SDK campaigns and emit bounded research decisions."""
from collections import Counter
import research_queue as q
from experiment_templates import pin

OUT=None

def summarize(reports):
    q.require(len(reports)>=2,'sdk508_report_scope')
    rows=[r for report in reports for r in report['rows']]
    q.require(len({r['id'] for r in rows})==len(rows),'sdk508_report_duplicate')
    comparisons=[r for report in reports for r in report['comparisons']]
    gates={}
    for model in ('hcf','mixed','fallback'):
        subset=[r for r in comparisons if r['model']==model]
        gains=[r['id'] for r in subset if r['gain']];losses=[r['id'] for r in subset if r['loss']];wrong=[r['id'] for r in subset if r['newWrong']]
        gates[model]=dict(gains=gains,losses=losses,newWrong=wrong,
            decision='reject_union' if losses or wrong else 'broader_regression_required' if gains else 'no_measured_benefit')
    counts={arm:{model:dict(Counter(r['arms'][arm]['models'][model]['outcome'] for r in rows)) for model in gates} for arm in ('known','scoped','general','union')}
    nofocus=[r for r in rows if r['truth'] is None]
    return dict(version='sdk508-decision-v1',frames=len(rows),uniqueImages=len({r['sha256'] for r in rows}),
        groups=len({r['group'] for r in rows}),counts=counts,gates=gates,
        noFocus={arm:{model:dict(Counter(r['arms'][arm]['models'][model]['outcome'] for r in nofocus)) for model in gates} for arm in counts},
        modelAccepted=False,trainingEligible=False,
        nextAction='Keep deployed models. Diagnose known-box failures first; otherwise investigate missed or mislocalized proposals. Reject union branches with losses.',
        limitation='Related native endpoints, unknown HCF mode, partial registered annotations. No complete-path TTR or independent accuracy claim.')

def build(specs):
    return dict(version='research-spec-v2',id='sdk508-combined-report',task='SDK508',owner='Maximum-mini-NUIAK',kind='screen',
        jobKind='artifact',authority='diagnostic',inputs=[],
        dependencies=[dict(job=s['id'],specSHA256=q.text_digest(s),outputs=['benchmark_summary.json']) for s in specs],
        adapter=dict(type='python-callable',steps=['sdk_report508.run'],outputAttributes=['sdk_report508.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json',reads=[]),
        question='Which proposal or crop correction survives native focus and no-focus comparisons?',
        hypothesis='Case-linked outcomes support rejecting regressions without another manual aggregation step.',
        controlledComparison='Aggregate only completed matched SDK508 arms with unchanged models and settings.',
        decisionRule='Reject union with any lost success or new wrong selection. Retain missing coverage as a blocker to promotion.',
        nextActionByOutcome=dict(supported='Review the bounded correction indicated by the combined report.',contradicted='Preserve evidence and reject failing branches.'))

def run():
    spec=q.load(OUT.parents[2]/'spec.json');reports=[];requests=[];sources=[]
    for dep in spec['dependencies']:
        job=OUT.parents[4]/'jobs'/dep['job'];state,attempts=q.state(job)
        q.require(state=='complete','sdk508_dependency_incomplete')
        p=attempts[-1];receipt=q.load(p/'result.json');q.require(receipt['specSHA256']==dep['specSHA256'],'sdk508_dependency_spec')
        output=p/'out/benchmark_summary.json';entry=next(r for r in receipt['outputs'] if r['path']=='benchmark_summary.json')
        q.require(q.digest(output)==entry['sha256'],'sdk508_dependency_output')
        report=q.load(output);request=q.load(q.ROOT/report['request']['path'])
        q.require(q.digest(q.ROOT/report['request']['path'])==report['request']['sha256'],'sdk508_request_changed')
        reports.append(report);requests.append(request);sources.append(pin(output))
    q.require(all(all(r[k]==requests[0][k] for k in ('crops','detectors','tool')) for r in requests),'sdk508_comparison_models')
    report=summarize(reports);report['sources']=sources
    q.save(OUT/'benchmark_summary.json',report)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
