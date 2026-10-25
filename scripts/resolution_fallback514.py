"""Evaluate a fixed resolution fallback from completed reports without new inference."""
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
from supplemental_proposals427 import load
from proposal_tier_policy import compare

OUT = None


def evaluate(baseline, fallback):
    cards=[q.load(checked(r['inputs']['scorecard'])) for r in (baseline,fallback)]
    settings=[dict(c['settings']) for c in cards]
    sizes=[s.pop('imageSize') for s in settings]
    q.require(sizes==[1280,960] and settings[0]==settings[1], 'resolution514_settings')
    identities=[dict(c['identity']['detector']) for c in cards]
    for ident,size in zip(identities,sizes):
        q.require(ident.pop('imageSize')==size and ident.get('engine')=='pytorch', 'resolution514_engine')
    q.require(identities[0]==identities[1] and identities[0].get('weightsSHA256'), 'resolution514_weights')
    q.require(cards[0]['frames']==cards[1]['frames'] and cards[0]['inputs']==cards[1]['inputs'], 'resolution514_membership')
    capture=q.load(checked(baseline['inputs']['capture']))
    q.require(capture['plan'].get('trainingEligible') is False and capture['plan']['cases'] and
              all(c['role']=='development' for c in capture['plan']['cases']), 'resolution514_role')
    result=compare(baseline,fallback,'high-first')
    result['policy']='1280-single-selection-else-960'
    result['version']='resolution-fallback-v1'
    result['limitation']+=' Fixed score-only fallback. No model promotion or runtime change. Latency is not measured by cached scoring.'
    return result


def summarize(results):
    rows=[r for result in results for r in result['rows']]
    keys=[(r['id'],r['profile'],r['arm'],r['model']) for r in rows]
    q.require(len(keys)==len(set(keys)), 'resolution514_duplicate_case')
    selected=[r for r in rows if (r['profile'],r['arm'],r['model'])==('standard','detector','candidate')]
    q.require(selected, 'resolution514_standard_missing')
    losses=[r['id'] for r in selected if r['loss']];wrong=[r['id'] for r in selected if r['newWrong']]
    gains=[r['id'] for r in selected if r['gain']]
    supported=len({r['group'] for r in selected})>=3 and any(r['noFocus'] for r in selected)
    return dict(version='resolution-fallback-decision-v1',outcome='contradicted' if losses or wrong else
                'supported' if gains and supported else 'inconclusive',modelAccepted=False,
                gains=gains,losses=losses,newWrong=wrong,rows=rows,
                groups=len({r['group'] for r in selected}),noFocus=sum(r['noFocus'] for r in selected),
                nextAction='Reject runtime replacement after any Standard loss or new wrong selection. Otherwise require independent consumer and latency qualification.')


def run():
    spec=q.load(OUT.parents[2]/'spec.json')
    plan=q.load(checked(spec['plan']))
    q.require(plan['version']=='resolution-fallback-plan-v1' and spec['id'].startswith(plan['id']+'-'), 'resolution514_runtime_plan')
    if spec['preparationStep']=='compare':
        pair=q.load(checked(spec['comparison']))
        result=evaluate(load(pair['baseline']),load(pair['fallback']))
    else:
        deps=q.dependency_inputs(spec,OUT.parents[4])
        result=summarize([q.load(checked(d['outputs'][0])) for d in deps])
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))


def compile_plan(path,destination,queue=q.QUEUE):
    plan=q.load(path);q.require(set(plan)=={'version','id','pairs'} and plan['version']=='resolution-fallback-plan-v1','resolution514_plan')
    q.require(q.ID.fullmatch(plan['id']) and 1<=len(plan['pairs'])<=16,'resolution514_size')
    destination.mkdir(parents=True,exist_ok=True);specs=[]
    for index,pair in enumerate(plan['pairs']):
        refs={}
        for name,ident in pair.items():
            q.require(name in ('baseline','fallback') and q.ID.fullmatch(ident),'resolution514_pair')
            p=queue/'jobs'/ident;sp=q.load(p/'spec.json');aa=q.attempts_of(p)
            q.require(aa and q.load(aa[-1]/'result.json')['status']=='complete','resolution514_incomplete')
            report=aa[-1]/'out'/'benchmark_summary.json'
            refs[name]=dict(report=pin(report),result=pin(aa[-1]/'result.json'),spec=pin(p/'spec.json'))
        q.require(set(refs)=={'baseline','fallback'},'resolution514_pair_fields')
        evaluate(load(refs['baseline']),load(refs['fallback']))
        ref=destination/f'pair-{index+1:02}.json';q.save(ref,refs)
        specs.append(make(plan['id']+f'-compare-{index+1:02}',path,ref,[]))
    deps=[dict(job=s['id'],specSHA256=q.text_digest(s),outputs=['benchmark_summary.json']) for s in specs]
    specs.append(make(plan['id']+'-decision',path,None,deps))
    jobs=[]
    for spec in specs:
        q.validate(spec);p=destination/(spec['id']+'.json');q.save(p,spec)
        jobs.append(dict(job=spec['id'],spec=pin(p),specSHA256=q.text_digest(spec)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(path),existing=[],jobs=jobs)
    q.save(destination/'compiled.json',manifest);return manifest


def make(ident,plan,comparison,deps):
    return dict(version='research-spec-v2',id=ident,task='STREAM514',owner='Maximum-mini-NUIAK',authority='diagnostic',kind='screen',jobKind='artifact',
        question='Does a 1280-first, 960-on-abstention rule recover focus without losing retained successes?',
        hypothesis='Keep unique baseline selections and consult the smaller resolution only on abstention.',
        controlledComparison='Reuse identical captures, weights, crop models, thresholds, and completed scores. Change only the selection rule.',
        decisionRule='Reject Standard losses or new wrong selections. Preserve no-focus and separate HCF.',
        nextActionByOutcome=dict(supported='Qualify independent consumer behavior and actual latency.',contradicted='Preserve current runtime and record failures.',inconclusive='Record missing coverage.'),
        inputs=[pin(plan),pin(Path(__file__))]+([pin(comparison)] if comparison else []),
        plan=pin(plan),comparison=pin(comparison) if comparison else None,preparationStep='compare' if comparison else 'decision',dependencies=deps,
        adapter=dict(type='python-callable',steps=['resolution_fallback514.run'],outputAttributes=['resolution_fallback514.OUT']),
        evidence=dict(reads=[q.relative(plan)],artifactReceipt='artifact-receipt.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
