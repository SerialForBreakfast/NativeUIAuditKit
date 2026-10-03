"""Compare pinned transition replays without admitting data or tuning thresholds."""
import argparse
from collections import Counter
import human_annotation_review as h


def rows(doc):
    reference=doc['version']=='reference-transition-audit-v1'
    h.require(reference or doc['version']=='settings-stability-v1','comparison_version')
    result={}
    for action in doc['pairs'] if reference else doc['actions']:
        key=action['id'] if reference else action['actionID']
        controls=action.get('controls',[]) if reference else action.get('guardedControls',[])
        for c in controls:
            ident=(key,c['id']);h.require(ident not in result,'duplicate_comparison_control')
            result[ident]=c
    return result


def metrics(items):
    counts=Counter();states={}
    for c in items:
        t=c['prediction']['tracking'];label=c['expected'] or 'unmatched'
        state=states.setdefault(label,Counter());state['controls']+=1
        matched=t['status'] in ('matched','identical')
        correct=c['trackingAgreesWithSemanticTarget']
        outcome='correct' if correct else 'wrong' if matched and c['expected'] is not None else 'unscored' if matched else 'abstained'
        counts[outcome]+=1;state[outcome]+=1
        counts['reason:'+t.get('reason',t['status'])]+=1
    return dict(counts=dict(counts),states={k:dict(v) for k,v in states.items()})


def compare(baseline,candidate):
    h.require(baseline['version']==candidate['version'],'comparison_version_mismatch')
    reference=baseline['version']=='reference-transition-audit-v1'
    actions='pairs' if reference else 'actions';ident='id' if reference else 'actionID'
    evidence='inputs' if reference else 'endpoints'
    b_inputs={a[ident]:a.get(evidence) for a in baseline[actions]}
    c_inputs={a[ident]:a.get(evidence) for a in candidate[actions]}
    h.require(b_inputs==c_inputs,'comparison_input_changed')
    b,c=rows(baseline),rows(candidate)
    h.require(set(b)==set(c) and b,'comparison_membership')
    # State/identity targets must be frozen, never adjusted to candidate predictions.
    for key in b:
        h.require(all(b[key][f]==c[key][f] for f in ('expected','afterControl')),'comparison_truth_changed')
    for field in ('partition','trainingEligible','independentEvaluationEligible'):
        h.require(baseline[field]==candidate[field],'comparison_role_changed')
    h.require(not candidate['trainingEligible'],'calibration_not_training')
    result=dict(baseline=metrics(b.values()),candidate=metrics(c.values()),controls=len(b),
                candidateAdopted=False,fullSceneQualification=False)
    result['identityDelta']={k:result['candidate']['counts'].get(k,0)-result['baseline']['counts'].get(k,0)
                             for k in ('correct','wrong','abstained','unscored')}
    result['classification']=dict(baseline=baseline['summaries'],candidate=candidate['summaries'])
    result['elapsedSeconds']={k:d.get('elapsedSeconds') for k,d in [('baseline',baseline),('candidate',candidate)]}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();out=h.fresh(a.output);paths=[h.local(a.baseline),h.local(a.candidate)]
    docs=[h.sealed(path,h.read(path)['version']) for path in paths]
    result=dict(version='focus-correspondence-comparison-v1',**h.FLAGS,
                inputs=[h.ref(path) for path in paths],**compare(*docs),
                implementation=h.ref(h.ROOT/'scripts/focus_correspondence_comparison.py'))
    h.write(out,result,sealed=True);print(result['identityDelta'])


if __name__=='__main__':main()
