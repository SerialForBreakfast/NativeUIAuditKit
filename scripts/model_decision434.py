"""Compare matched development evidence and select a bounded reporting action."""
from collections import Counter
import research_queue as q
from experiment_templates import checked, pin
from template_adapters395 import resolve_inputs
from native_selection_comparison import load_source, compare
from consumer_crop_comparison import summarize

OUT = None


def context():
    spec = q.load(OUT.parents[2]/'spec.json')
    queue = OUT.parents[4]
    config = q.load(checked(spec['decisionConfig']))
    resolved = q.dependency_inputs(spec, queue)
    q.require(resolved == q.load(OUT/'dependencies.json'), 'decision_dependency_changed')
    return spec, config, resolved, queue


def source(dependency, queue, name):
    result = checked(dependency['result'])
    spec_path = queue/'jobs'/dependency['job']/'spec.json'
    q.require(q.text_digest(q.load(spec_path)) == dependency['specSHA256'], 'decision_spec_changed')
    matches = [r for r in dependency['outputs'] if checked(r) == result.parent/'out'/name]
    q.require(len(matches) == 1, 'decision_output_missing')
    return dict(report=matches[0], result=dependency['result'], spec=pin(spec_path))


def consumer_source(ref):
    from cached_selection405 import verified_report
    report = verified_report({k:ref[k] for k in ('report','result')})
    spec = q.load(checked(ref['spec'])); result = q.load(checked(ref['result']))
    q.require(result['specSHA256'] == q.text_digest(spec) and spec['template']['id'] == 'T63', 'decision_consumer_spec')
    inputs = resolve_inputs(spec['template'], checked(ref['result']).parent/'out')
    data = q.load(checked(inputs['membership']))
    q.require(data['version'] == 'consumer-crops-v1' and data['trainingEligible'] is False and
              data['rows'] and all(r['role'] == 'development' and r['profile'] == 'standard' for r in data['rows']),
              'decision_consumer_role')
    q.require(report['backend'] == spec['template']['parameters']['backend'], 'decision_backend')
    q.require(report['focusThreshold'] == .85 and report['ambiguityThreshold'] == .7, 'decision_threshold')
    # Recompute decisions instead of trusting summary counts or serialized categories.
    q.require(len(report['crops']) == len(data['rows']), 'decision_crop_count')
    for old, new in zip(data['rows'], report['crops']):
        q.require(all(new.get(k) == v for k,v in old.items()), 'decision_crop_identity')
    derived = summarize(data['rows'], [r['score'] for r in report['crops']])
    q.require(all(report[k] == derived[k] for k in ('rows','crops','counts')), 'decision_consumer_outcomes')
    return report, inputs


def matched_consumer(left, right):
    q.require(left['backend'] == right['backend'], 'decision_backend')
    rows = []
    for field, arm, success, wrong in [('rows','consumer-frame',{'correct'},{'wrong'}),
                                      ('crops','consumer-crop',{'tp','tn'},{'fp'})]:
        a,b = left[field],right[field]
        q.require(a and len(a) == len(b) and len({r['id'] for r in a}) == len(a), 'decision_consumer_membership')
        for old,new in zip(a,b):
            keys = ('id','group','profile','role','family') if field == 'rows' else ('id','frame','group','profile','role','family','label','bounds','image')
            q.require(all(old[k] == new[k] for k in keys), 'decision_consumer_identity')
            x,y = (r['outcome' if field == 'rows' else 'category'] for r in (old,new))
            rows.append(dict(id=old['id'],group=old['group'],profile=old['profile'],noFocus=False,arm=arm,
                baseline=x,candidate=y,gain=x not in success and y in success,loss=x in success and y not in success,
                newWrong=x not in wrong and y in wrong,
                candidateMargin=new['score']-.85 if field == 'crops' else None,
                baselineMargin=old['score']-.85 if field == 'crops' else None))
    return rows


def comparison():
    spec, config, deps, queue = context()
    q.require(config['kind'] == 'pair' and 1<=len(config['pairs'])<=4, 'decision_pair_contract')
    results=[]
    for pair in config['pairs']:
        results.append(compare_pair(pair,deps,queue))
    q.save(OUT/'comparison.json',dict(version='model-comparison-set-v1',comparisons=results,modelAccepted=False))
    receipt()


def compare_pair(config,deps,queue):
    by_job = {d['job']:d for d in deps}
    refs = {side:source(by_job[config[side]],queue,config['output']) for side in ('baseline','candidate')}
    loader = load_source if config['template'] == 'T37' else consumer_source
    left,a = loader(refs['baseline']);right,b = loader(refs['candidate'])
    q.require(set(a) == set(b) and all(a[k] == b[k] for k in a if k != 'model'), 'decision_matched_inputs')
    if config['template'] == 'T37':
        rows = compare(left,right)['rows']
        l = {r['id']:r for r in left['rows']};r = {r['id']:r for r in right['rows']}
        for row in rows:
            for side,values in [('baseline',l),('candidate',r)]:
                scores=values[row['id']]['arms'][row['arm']]['scores']
                row[side+'Margin'] = max(scores)-.85 if scores else None
                row[side+'Proposals'] = len(scores)
    else:
        q.require(config['template'] == 'T63', 'decision_template')
        rows = matched_consumer(left,right)
    for row in rows:row['comparison'] = config['pair']
    return dict(version='model-pair-decision-v1',pair=config['pair'],rows=rows,
        models=dict(baseline=a['model'],candidate=b['model']),sources=refs,modelAccepted=False,
        executionSeconds={side:q.load(checked(refs[side]['result'])).get('wallSeconds') for side in refs})


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=p.name,sha256=q.digest(p)) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != 'artifact-receipt.json']))


def merge():
    _,config,deps,queue = context()
    q.require(config['kind'] == 'merge', 'decision_merge_contract')
    comparisons=[]
    for dep in deps:
        doc=q.load(checked(source(dep,queue,'comparison.json')['report']))
        if doc['version'] == 'model-pair-decision-v1':comparisons.append(doc)
        else:
            q.require(doc['version'] == 'model-comparison-set-v1','decision_merge_version')
            comparisons.extend(doc['comparisons'])
    q.require(len({c['pair'] for c in comparisons}) == len(comparisons),'decision_duplicate_pair')
    q.save(OUT/'comparison.json',dict(version='model-comparison-set-v1',comparisons=comparisons,modelAccepted=False))
    receipt()


def assess(comparisons, expected):
    q.require(comparisons and {c['pair'] for c in comparisons} == set(expected) and
              len(comparisons) == len(expected), 'decision_incomplete_suite')
    models={side:{c['models'][side]['sha256'] for c in comparisons} for side in ('baseline','candidate')}
    q.require(all(len(v)==1 for v in models.values()), 'decision_model_drift')
    rows=[r for c in comparisons for r in c['rows']]
    keys=[(r['profile'],r['arm'],r['id']) for r in rows]
    q.require(rows and len(set(keys)) == len(keys), 'decision_duplicate_case')
    q.require(any(r['profile']=='standard' and r['arm']=='raw-proposal' for r in rows), 'decision_standard_support')
    # Protect every declared prior success, including the optional HCF and consumer slices.
    losses=[r for r in rows if r['loss']];wrong=[r for r in rows if r['newWrong']]
    target=[r for r in rows if r['profile']=='standard' and r['arm']=='raw-proposal']
    gains=[r for r in target if r['gain']]
    outcome='contradicted' if losses or wrong else 'supported' if gains else 'inconclusive'
    slices=[]
    for profile,arm in sorted({(r['profile'],r['arm']) for r in rows}):
        subset=[r for r in rows if (r['profile'],r['arm'])==(profile,arm)]
        slices.append(dict(profile=profile,arm=arm,observations=len(subset),groups=len({r['group'] for r in subset}),
            noFocusObservations=sum(r['noFocus'] for r in subset),baseline=dict(Counter(r['baseline'] for r in subset)),
            candidate=dict(Counter(r['candidate'] for r in subset)),gains=sum(r['gain'] for r in subset),
            losses=sum(r['loss'] for r in subset),newWrongSelections=sum(r['newWrong'] for r in subset)))
    return dict(version='model-batch-decision-v1',outcome=outcome,modelAccepted=False,models=models_to_json(models),
        target='standard/raw-proposal',targetGains=gains,losses=losses,newWrongSelections=wrong,slices=slices,rows=rows,
        limitation='Inspected development evidence. Arms, crops, paired profiles, and related frames are not independent trials. No automatic promotion.')


def models_to_json(models):return {side:sorted(values) for side,values in models.items()}


def decision():
    _,config,deps,queue=context()
    q.require(config['kind']=='decision','decision_contract')
    comparisons=[];evidence=[]
    for dep in deps:
        name='comparison.json' if dep['job']!=config['training'] else 'fit.json'
        ref=source(dep,queue,name)['report'];doc=q.load(checked(ref));evidence += [dep['result'],ref]
        if name=='comparison.json':comparisons.extend(doc['comparisons'])
        else:
            q.require(doc.get('epochs')==30 and doc.get('selection')=='fixed-last' and
                      doc.get('boundaryStopped') is False and doc.get('earlyStopped') is False,'decision_incomplete_training')
            train_ref=source(dep,queue,'final.pt')['report']
    report=assess(comparisons,config['pairs'])
    q.require(report['models']['candidate']==[train_ref['sha256']],'decision_training_model_mismatch')
    report['training']=train_ref;report['question']=config['question']
    train_dep=next(d for d in deps if d['job']==config['training'])
    report['trainingSeconds']=q.load(checked(train_dep['result'])).get('wallSeconds')
    report['scoreExecutionSeconds']=[dict(pair=c['pair'],**c.get('executionSeconds',{})) for c in comparisons]
    q.save(OUT/'decision.json',report)
    reason={'contradicted':'The candidate loses prior successes or adds wrong selections.',
            'supported':'Standard proposal selection gains successes without losses in the declared suite.',
            'inconclusive':'The declared suite has no regression, but no Standard proposal-selection gain.'}[report['outcome']]
    q.save(OUT/'gate.json',dict(version='research-condition-v1',outcome=report['outcome'],reason=reason,evidence=evidence))
    target=next(s for s in report['slices'] if s['profile']=='standard' and s['arm']=='raw-proposal')
    lines=['# '+config['question'],'',reason,'',
        f"Standard fixed-proposal selection gains {target['gains']} successes and loses {target['losses']}.",
        f"It adds {target['newWrongSelections']} wrong selections.",'','Model acceptance: not granted.','',
        '| Profile | Arm | Observations | Groups | Gains | Losses | New wrong |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for s in report['slices']:
        lines.append(f"| {s['profile']} | {s['arm']} | {s['observations']} | {s['groups']} | {s['gains']} | {s['losses']} | {s['newWrongSelections']} |")
    lines += ['',report['limitation'],'','Case identities and source receipts are in decision.json.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    receipt()


def followup():
    _,config,deps,queue=context()
    q.require(config['kind']=='followup' and len(deps)==1,'decision_followup_contract')
    doc=q.load(checked(source(deps[0],queue,'decision.json')['report']))
    q.require(doc['version']=='model-batch-decision-v1' and doc['modelAccepted'] is False,'decision_followup_version')
    outcome=doc['outcome'];q.require(outcome in ('supported','contradicted','inconclusive'),'decision_followup_outcome')
    failures=[r for r in doc['rows'] if r['loss'] or r['newWrong']]
    by_group=[]
    for group in sorted({r['group'] for r in failures}):
        selected=[r for r in failures if r['group']==group]
        by_group.append(dict(group=group,cases=selected,profiles=sorted({r['profile'] for r in selected}),
            observedErrors=dict(Counter(r['candidate'] for r in selected))))
    by_group.sort(key=lambda g:(-sum(r['profile']=='standard' for r in g['cases']),-len(g['cases']),g['group']))
    action={'contradicted':'Diagnose the listed lost successes before any new training. Preserve the retained model.',
            'supported':'Qualify the fixed candidate on independent native groups and the consumer path. Do not promote.',
            'inconclusive':'Inspect missing proposals and coverage before choosing another correction. Do not repeat training.'}[outcome]
    q.save(OUT/'followup.json',dict(version='model-batch-followup-v1',outcome=outcome,action=action,
        failureGroups=by_group,coverage=doc['slices'],modelAccepted=False,newTrainingAuthorized=False,
        unavailable=['independent final audit','physical-device accuracy'],
        sources=[deps[0]['result']],executionStarted=False))
    (OUT/'followup.md').write_text('# Next decision\n\n'+action+'\n\n'+
        '\n'.join('- '+g['group']+': '+str(len(g['cases']))+' affected case/arm observations.' for g in by_group)+'\n')
    receipt()
