"""Replay an explicit HCF-only fallback without changing primary decisions."""
import copy
import time
import research_queue as q
from template_adapters395 import document,resolve_inputs
from template_analysis397 import matched

OUT=None


def combine(primary,fallback,enabled):
    q.require(type(enabled) is bool,'fallback_enable_type')
    matched(primary,fallback)
    secondary={r['id']:r for r in fallback['rows']};rows=[];used=[]
    for row in primary['rows']:
        other=secondary[row['id']]
        for candidate in (row,other):
            pred=candidate['prediction']
            q.require(pred['decision'] in ('select','abstain'),'decision_state')
            q.require((pred['box'] is None)==(pred['decision']=='abstain'),'decision_geometry')
        use=enabled and row['profile']=='hcf' and row['prediction']['decision']=='abstain'
        result=copy.deepcopy(other if use else row)
        # Outcomes remain measurements. They never select the branch.
        rows.append(result)
        if use:used.append(row['id'])
    return dict(rows=rows,method='detector-first-explicit-hcf-fallback-v1',fallbackCases=used,
        modelAccepted=False,standardChanged=False,
        limitation='Cached inspected cases. HCF requires verified caller state. Group-excluded geometry is diagnostic, not a deployable fixed mapping.')


def run():
    contract=q.load(OUT.parents[2]/'spec.json')['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(contract,OUT)
        value=combine(document(inputs['primary']),document(inputs['fallback']),contract['parameters']['enabled'])
        q.save(OUT/'comparison.json',value)
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
            dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',code=str(error)[:500],modelAccepted=False));raise
