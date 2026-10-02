"""Retained scene-level experiment; reuses pinned pixel decisions, no model execution."""
import argparse
from collections import Counter, defaultdict
import copy
import os
import subprocess
import sys
import human_annotation_review as h
from focus_scene_transition import corroborate

BASE = h.ROOT/'reports/work/FOCUS-ALIGNMENT-12/artifacts/common-support/result.json'


def run(output):
    out=h.fresh(output); out.mkdir(parents=True)
    ref=h.ref(BASE); source=h.read(BASE,limit=32*1024**2)
    groups=defaultdict(list)
    for r in source['decisions']:
        if r['lane']=='real-development-contrast':groups[(tuple(r['group']),r['kind'])].append(r)
    eligibility={tuple(f['group']):f['eligible'] for f in source['frameComparisons']}
    h.write(out/'protocol.json',dict(input=ref,code=h.ref(h.ROOT/'scripts/focus_scene_transition.py'),
        assumption='Existing offline geometry correspondences, not verified runtime persistent identities.',
        arms=['opposing_changes','resolved_background'],training=False,releaseEligible=False))
    rows=[]; summary=defaultdict(Counter)
    for (group,kind),members in sorted(groups.items()):
        req=dict(version=1,context=dict(sameScene=True,settled=True,fresh=True,completeCoverage=eligibility[group]),
            controls=[dict(id=m['id'],decision=m['arms']['alignedGated'],identityVerified=True) for m in members])
        # Truth is consulted only after requests and all predictions are constructed.
        predictions={name:corroborate(req,True,require_resolved=strict)
                     for name,strict in [('opposing_changes',False),('resolved_background',True)]}
        gains=[m['id'] for m in members if m['truth']=='arrival']
        losses=[m['id'] for m in members if m['truth']=='departure']
        outcomes={}
        for name,p in predictions.items():
            if p['decision'] in ('unknown','unavailable'):outcome='abstained'
            elif p['decision']=='unchanged':outcome='correct' if not gains and not losses else 'wrong'
            else:outcome='correct' if [p['gained']]==gains and [p['lost']]==losses else 'wrong'
            outcomes[name]=outcome
            if eligibility[group]:summary[('identical' if kind.startswith('identical') else 'contrast')+'/'+name][outcome]+=1
        rows.append(dict(group=group,kind=kind,eligible=eligibility[group],request=req,
                         predictions=predictions,outcomes=outcomes))
    # Actual CLI paths include retained examples and explicit aggregation confounds.
    cases=[]
    base=dict(version=1,context=dict(sameScene=True,settled=True,fresh=True,completeCoverage=True),
              controls=[dict(id='a',decision='arrival',identityVerified=True),
                        dict(id='b',decision='departure',identityVerified=True)])
    variants=[('paired-content-confound',base,True,False),('disabled',{},False,False)]
    single=copy.deepcopy(base);single['controls'][1]['decision']='unchanged'
    variants.append(('isolated-content',single,True,False))
    for name in ('completeCoverage','sameScene','fresh','settled'):
        req=copy.deepcopy(base);req['context'][name]=False;variants.append(('false-'+name,req,True,False))
    for name in ('duplicate','wrong-version','extra-truth','nonboolean','empty'):
        req=copy.deepcopy(base)
        if name=='duplicate':req['controls'][1]['id']='a'
        elif name=='wrong-version':req['version']=True
        elif name=='extra-truth':req['truth']='switch'
        elif name=='nonboolean':req['controls'][0]['identityVerified']=1
        else:req['controls']=[]
        variants.append((name,req,True,True))
    for i,r in enumerate(r for r in rows if r['eligible'] and r['kind']=='forward'):
        variants.append((f'retained-{i}',r['request'],True,False))
    for name,req,enabled,invalid in variants:
        path=out/(name+'-request.json');dest=out/(name+'-result.json');h.write(path,req)
        cmd=[sys.executable,str(h.ROOT/'scripts/focus_scene_transition.py'),'--request',str(path),'--output',str(dest)]
        if enabled:cmd.append('--enable-experimental')
        p=subprocess.run(cmd,capture_output=True,text=True,env=os.environ.copy(),timeout=30)
        if invalid:
            h.require(p.returncode!=0 and not dest.exists(),'invalid_cli_accepted')
            cases.append(dict(name=name,exitCode=p.returncode,rejected=True))
        else:
            h.require(p.returncode==0,'CLI_failed:'+p.stderr[-300:])
            actual=h.read(dest);h.require(actual==corroborate(req,enabled),'cli_parity')
            cases.append(dict(name=name,exitCode=0,result=actual))
    h.require(h.ref(BASE)==ref,'source_changed')
    h.write(out/'result.json',dict(input=ref,rows=rows,summary=dict(summary),cli=cases,
        completePairCount=sum(eligibility.values()),releaseEligible=False,
        limitation='Two opposing content-only changes pass; candidate is not proof of focus.'))
    print(dict(summary));print('CLI cases',len(cases))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
