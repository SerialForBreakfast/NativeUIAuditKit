"""Measurement-only shared reports; no inference, admission or threshold fitting."""
import hashlib
import json
import math
import random
from collections import Counter, defaultdict


def require(ok, reason):
    if not ok: raise ValueError(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def upper95(errors, trials):
    """One-sided Clopper-Pearson. Caller must justify independent trials."""
    require(type(errors) is int and type(trials) is int and 0<=errors<=trials<=100000,
            'invalid_binomial_counts')
    if not trials: return None
    if errors==trials: return 1.
    if errors==0: return -math.expm1(math.log(.05)/trials)
    coefficients=[math.lgamma(trials+1)-math.lgamma(k+1)-math.lgamma(trials-k+1)
                  for k in range(errors+1)]
    lo,hi=0.,1.
    for _ in range(60):
        p=(lo+hi)/2
        terms=[v+k*math.log(p)+(trials-k)*math.log1p(-p) for k,v in enumerate(coefficients)]
        peak=max(terms); cdf=math.exp(peak)*sum(math.exp(v-peak) for v in terms)
        if cdf>.05: lo=p
        else: hi=p
    return hi


def validate(rows):
    ids,roles=set(),{}
    for r in rows:
        require(isinstance(r,dict),'row_type')
        for k in ('id','group','role','condition'):
            require(isinstance(r.get(k),str) and r[k],'missing_'+k)
        require(r['id'] not in ids,'duplicate_case');ids.add(r['id'])
        require(roles.setdefault(r['group'],r['role'])==r['role'],'cross_role_group')
        for k in ('truth','decision'):
            require(k in r and (r[k] is None or type(r[k]) is bool),'invalid_'+k)
        require(r.get('authority') in ('authored','qualified','producer-reported','unknown'),'label_authority')
        require(not(r['role']=='final-audit' and r.get('previouslyExposed',False)),'exposed_final_audit')


def summary(rows):
    c=Counter(total=len(rows))
    for r in rows:
        t,d=r['truth'],r['decision'];c['abstentions' if d is None else 'decisions']+=1
        if t is None:
            c['unknownTruth']+=1
            if d is False:c['unknownTruthNegativeDecisions']+=1
            continue
        c['positiveSupport' if t else 'negativeSupport']+=1
        if d is None:continue
        c['scoredDecisions']+=1
        if d is False:
            c['scoredNegativeDecisions']+=1
            if t:c['falseNegative']+=1
        elif not t:c['falsePositive']+=1
    def rate(n,d):return dict(numerator=c[n],denominator=c[d],value=c[n]/c[d] if c[d] else None)
    return dict(counts=dict(c),missedPositive=rate('falseNegative','positiveSupport'),
        errorAmongNegativeDecisions=rate('falseNegative','scoredNegativeDecisions'),
        falsePositive=rate('falsePositive','negativeSupport'),coverage=rate('decisions','total'),
        abstention=rate('abstentions','total'))


def report(rows, *, task, context, independent_reference=None):
    require(task in ('visual-focus','focus-change','temporal-instability'),'unknown_task')
    validate(rows)
    require(isinstance(context,dict) and all(context.get(k) is not None for k in
            ('source','model','preprocessing')),'missing_context')
    require(context.get('domain') in ('procedural','native-fixture','real-app-simulator',
            'physical-capture','unknown'),'unknown_domain')
    qualified=[r for r in rows if r['authority'] in ('qualified','authored')]
    agreement=[r for r in rows if r['authority']=='producer-reported']
    groups={r['group'] for r in rows}
    bounds=dict(upper95=None,reason='independence_not_established')
    if independent_reference is not None:
        require(isinstance(independent_reference,str) and independent_reference,'independence_reference')
        require(len(groups)==len(rows) and all(r['authority']=='qualified' and
                r['role']=='final-audit' for r in rows),'ineligible_independent_trials')
        totals=summary(rows);s=totals['missedPositive']
        bounds=dict(upper95=upper95(s['numerator'],s['denominator']),reference=independent_reference,
                    trials=s['denominator'],scope='missedPositive; conditional on sampling assumptions',
                    metrics={k:dict(upper95=upper95(totals[k]['numerator'],totals[k]['denominator']),
                                   trials=totals[k]['denominator']) for k in
                             ('missedPositive','errorAmongNegativeDecisions','falsePositive')})
    return dict(version='focus-evidence-v1',task=task,context=context,membershipSHA256=digest(rows),
        cases=len(rows),connectedGroups=len(groups),independentGroups=len(groups) if independent_reference else None,
        metrics=summary(qualified),producerAgreement=summary(agreement),
        slices={k:{v:summary([r for r in qualified if r[k]==v]) for v in sorted({r[k] for r in rows})}
                for k in ('condition','role')},
        producerAgreementByCondition={v:summary([r for r in agreement if r['condition']==v])
                                     for v in sorted({r['condition'] for r in agreement})},
        roleConditionSlices={role:{condition:summary([r for r in qualified if
            r['role']==role and r['condition']==condition]) for condition in
            sorted({r['condition'] for r in rows if r['role']==role})}
            for role in sorted({r['role'] for r in rows})},
        bounds=bounds,illustrativeTargets=[dict(target=t,zeroErrorIndependentTrials=n,
            availableIndependentTrials=bounds.get('trials'),deploymentGate=False) for t,n in ((.01,299),(.05,59))],
        unknownAuthority=sum(r['authority']=='unknown' for r in rows),
        accuracyScope='authored software truth or qualified labels only; domain-specific',
        productionDecisionChanged=False,modelGatePassed=None)


def paired_groups(left,right,draws=1000,seed=223):
    validate(left);validate(right)
    require(type(draws) is int and 100<=draws<=10000,'bootstrap_budget')
    a,b=({r['id']:r for r in items} for items in (left,right))
    require(a.keys()==b.keys(),'paired_membership');grouped=defaultdict(list)
    for key in sorted(a):
        x,y=a[key],b[key]
        require(all(x.get(k)==y.get(k) for k in ('truth','authority','group','role','condition')),'paired_labels_or_ancestry')
        if x['authority']=='unknown' or x['truth'] is None or x['decision'] is None or y['decision'] is None:continue
        grouped[x['group']].append(int(y['decision']!=y['truth'])-int(x['decision']!=x['truth']))
    effects=[sum(v)/len(v) for _,v in sorted(grouped.items())]
    result=dict(groups=len(effects),pairs=sum(map(len,grouped.values())),seed=seed,
        estimand='equal-group mean candidate-minus-reference error on common decided cases',
        safetyGuarantee=False,mean=sum(effects)/len(effects) if effects else None,interval95=None)
    if len(effects)<2:return result
    rng=random.Random(seed)
    values=sorted(sum(rng.choices(effects,k=len(effects)))/len(effects) for _ in range(draws))
    result['interval95']=[values[int(draws*.025)],values[min(draws-1,int(draws*.975))]]
    return result


def schema4_report(doc):
    require(doc.get('version')=='schema4-score-diagnostic-v1','score_version');rows=[]
    for r in doc['rows']:
        p=r['probability']
        require(type(p) in (int,float) and math.isfinite(p) and 0<=p<=1,'invalid_probability')
        require(r['reportedRole'] in ('focused','unfocused'),'reported_role')
        rows.append(dict(id=r['id'],group='ART191-unresolved-ancestry',role='inspection',
            condition='clipped' if r['clipped'] else 'unclipped',truth=r['reportedRole']=='focused',
            decision=p>=.85,authority='producer-reported'))
    return report(rows,task='visual-focus',context=dict(domain='native-fixture',
        source=doc['inspectionSHA256'],model=doc['artifact'],preprocessing=dict(runtime=doc['runtime'],
        crop=doc['preprocessing'],geometry=doc.get('diagnosticGeometry','endpoint'),diagnosticThreshold=.85)))
