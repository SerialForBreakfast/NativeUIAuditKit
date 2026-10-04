"""Explicit no-scroll consumer entrypoint; inspection only, never admission."""
import argparse
import human_annotation_review as h
from fixture_owned_pairs import member
from focus_corrected_transition_audit import validate_case,stationary_condition


def run(root,case_path,evidence_path,output):
    root=h.local(root);out=h.fresh(output)
    case_path=member(root,case_path);evidence_path=member(root,evidence_path)
    refs=[h.ref(case_path),h.ref(evidence_path)]
    refs.extend(h.ref(member(root,str((evidence_path.parent/(role+'.json')).relative_to(root))))
                for role in ('before','after'))
    raw,b,a=validate_case(root,evidence_path,h.read(case_path),stationary=True)
    refs.extend([b['image'],a['image']])
    for ref in refs:h.checked(h.ROOT,ref)
    result=dict(version='stationary-transition-intake-v1',inputs=refs,
        caseID=raw['case_id'],condition=raw['specification']['condition'],
        normalizedCondition=stationary_condition(raw['specification']['condition']),
        observedFocus=[b['focus'],a['focus']],observedScrolled=False,
        cleanupVerified=True,inspectionEligible=True,trainingEligible=False,
        independentEvaluationEligible=False,
        limitation='Native observations and hashed capture brackets; not authenticated frame identity or data admission.')
    h.write(out,result,sealed=True);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('root','case','evidence','output'):p.add_argument('--'+k,required=True)
    a=p.parse_args();print(run(a.root,a.case,a.evidence,a.output))
