"""Register 20 bounded investigations and reuse retained measurements."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics
import research_queue as q

OUT = None
PLAN = q.ROOT / 'Research/ResearchSpecs/RESEARCH340'
TESTS = [
 ('A1','Artwork exchange','Keep focus and geometry fixed while exchanging artwork.','Matched artwork-only pairs with reviewed constant focus'),
 ('A2','Effect components','Separate growth, border, shadow, and tint contributions.','Renderer controls for independent effect components'),
 ('A3','Equal change, different cause','Match pixel-change magnitude for focus and content changes.','Matched magnitude strata with reviewed change labels'),
 ('A4','Competing decoration','Add focus-like decoration to unfocused controls.','Independent decorative borders and observed focus labels'),
 ('A5','No-focus scenes','Compare no focus with one focused control.','Verified settled no-focus examples; authored null is not native truth'),
 ('B1','Position exchange','Move matched controls across a 3 by 3 screen grid.','Position-controlled matched pairs with unchanged artwork'),
 ('B2','Clipping progression','Vary visible body fraction without changing focus identity.','Clipping controls and full/visible body measurements'),
 ('B3','Subpixel alignment','Move rendering origins by 0, 0.25, 0.5, and 0.75 pixels.','Fractional-origin renderer and unchanged-focus paired receipts'),
 ('B4','Boundary visibility','Compare retained original windows with boundary-ranked windows.',''),
 ('B5','Identical neighbors','Move focus among controls with identical artwork.','Matched neighboring focus transitions with identical artwork'),
 ('C1','Scroll versus focus','Separate fixed-focus scrolling from stationary focus movement.','Observed scroll offsets, focus IDs, and timed frame pairs'),
 ('C2','Animation phase','Measure change and readiness across animation phases.','Timestamped native sequences with independently verified settlement'),
 ('C3','Reversal consistency','Compare forward and reversed decisions from cached predictions.',''),
 ('C4','Interruption sequences','Insert a rendered modal, loading state, or overlay.','Rendered interruptions with frame-linked state evidence'),
 ('C5','Capture disruption','Replay missing, repeated, delayed, and mismatched frames.','Pinned temporal consumer contract and genuine ordered frame trace'),
 ('D1','Exaggerated-effect curriculum','Compare exaggerated-to-native and native-strength-only training.','Qualified effect-strength corpus and equal-budget frozen training arms'),
 ('D2','Synthetic/native residuals','Compare matched authored and native effect rendering.','Matched native/authored pairs with aligned bodies and effect settings'),
 ('D3','Unseen effect combinations','Reserve combinations of growth, shadow, tint, and border.','Independent effect controls and frozen combination exclusions'),
 ('D4','Factor interactions','Cover pairwise size, contrast, spacing, theme, and artwork factors.','Verified factor controls; measured outputs for all requested factors'),
 ('D5','Data selection','Compare uniform and failure-targeted selection at equal budgets.','Eligible candidate pool, group exclusions, and fixed equal-budget arms'),
]


def pin(path):
    return dict(path=q.relative(path), sha256=q.digest(path))


def register(queue=q.QUEUE):
    PLAN.mkdir(parents=True, exist_ok=True)
    for code, title, hypothesis, missing in TESTS:
        id = 'measured340-' + code.lower()
        existing = queue / 'jobs' / id / 'spec.json'
        if existing.exists():
            print(id, 'already_registered'); continue
        inputs = [pin(Path(__file__))]
        if code == 'B4':
            inputs += [pin(q.ROOT/'reports/work/FOCUS-331/audit.json')]
        if code == 'C3':
            inputs += [pin(q.ROOT/'reports/work/FOCUS-329/run/evaluation.json'),
                       pin(q.ROOT/'reports/work/TRANSITION-249/artifacts/package/membership.json')]
        config = dict(code=code, inputs=inputs[1:], title=title)
        config_path = PLAN / (id + '-config.json')
        q.save(config_path, config)
        spec = dict(version=q.SPEC_VERSION, id=id, task='RESEARCH340-'+code, owner='Maximum-mini-NUIAK',
            kind='screen', authority='diagnostic', batch=code[0], hypothesis=hypothesis,
            decisionRule='Report group-level differences. Do not train unless target errors improve without lost retained successes.',
            requirements=[missing] if missing else [],
            adapter=dict(type='python-callable', steps=['research_campaign340.run'], outputAttributes=['research_campaign340.OUT']),
            inputs=inputs, stage=[dict(**{'from':pin(config_path)},to='config.json')],
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=2))
        path=PLAN/(id+'.json');q.save(path,spec);print(id,q.submit(path,queue))


def decision(p):
    q.require(type(p) in (int,float) and 0 <= p <= 1,'probability')
    return 0 if p <= .15 else 1 if p >= .85 else None


def reversal(evaluation, membership):
    output={}
    for name, labels in [('native.npy',[r['changed'] for r in membership['rows']]),('replay.npy',membership['replayLabels'])]:
        forward=evaluation['conditions'][name]['probabilities']
        reverse=evaluation['conditions']['reverse_'+name]['probabilities']
        q.require(len(forward)==len(reverse)==len(labels),'score_membership_length')
        groups=defaultdict(lambda:dict(count=0,disagreements=0,lostCorrect=0,gainedCorrect=0))
        cases=[]
        for i,(a,b,label) in enumerate(zip(forward,reverse,labels)):
            x,y=decision(a),decision(b)
            group=membership['rows'][i]['group'] if name=='native.npy' else 'encoded-replay-ancestry-unavailable'
            row=groups[group];row['count']+=1;row['disagreements']+=x!=y
            row['lostCorrect']+=x==label and y!=label;row['gainedCorrect']+=x!=label and y==label
            if x!=y:cases.append(dict(index=i,group=group,forward=a,reverse=b,label=label))
        output[name]=dict(groups=dict(groups),cases=cases,
            disagreements=sum(g['disagreements'] for g in groups.values()),
            lostCorrect=sum(g['lostCorrect'] for g in groups.values()),
            gainedCorrect=sum(g['gainedCorrect'] for g in groups.values()))
    return dict(comparisons=output,nextAction='Test reversal consistency on training groups before changing any threshold.',
        limitations=['Cached FOCUS329 predictions; no new inference.',
                    'Box exchange is unavailable in these cached predictions.',
                    'Previously inspected groups are not final evaluation.'])


def boundaries(audit):
    groups=defaultdict(list)
    for row in audit['rows']:
        if all(row['measurements'][p]['coverage'] is not None and row['measurements'][p]['purity'] is not None
               for p in ('old','boundary','retain_first')):
            groups[row['group']].append(row)
    values={}
    for group,rows in groups.items():
        values[group]={policy:dict(coverage=statistics.mean(r['measurements'][policy]['coverage'] for r in rows),
                                   purity=statistics.mean(r['measurements'][policy]['purity'] for r in rows))
            for policy in ('old','boundary','retain_first')}
    harmed={policy:[g for g,v in values.items() if v[policy]['coverage']<v['old']['coverage']]
            for policy in ('boundary','retain_first')}
    return dict(groups=values,harmedGroups=harmed,measuredRows=sum(map(len,groups.values())),
        unavailableRows=len(audit['rows'])-sum(map(len,groups.values())),
        nextAction='Preserve original windows. Do not train a replacement-window candidate from these results.',
        limitations=['Retained training-only measurements; no new rendering.',
                    'Neighbor and padding interventions still need controlled renders.',
                    'Coverage is not model accuracy.'])


def run():
    config=q.load(OUT/'config.json')
    docs=[]
    for ref in config['inputs']:
        path=q.local_path(q.ROOT,ref['path']);q.require(q.digest(path)==ref['sha256'],'input_hash')
        docs.append(q.load(path))
    if config['code']=='B4':result=boundaries(docs[0])
    elif config['code']=='C3':result=reversal(*docs)
    else:raise ValueError('missing_controlled_inputs')
    q.save(OUT/'diagnostic.json',dict(version='research-diagnostic-v1',code=config['code'],
        evidenceKind='cached-diagnostic',inputs=config['inputs'],candidateJustified=False,**result))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--register',action='store_true',required=True)
    parser.parse_args();register()
