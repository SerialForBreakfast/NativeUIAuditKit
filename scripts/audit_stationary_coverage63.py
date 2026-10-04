"""Read-only retained-source compatibility audit; never relabel or admit cases."""
import argparse
from collections import Counter
import human_annotation_review as h
from fixture_owned_pairs import member
from synth05_intake import verify_package
from focus_corrected_transition_audit import validate_case
from inventory_transition_sources import observed_scroll


def classification(raw, valid):
    scroll,reason=observed_scroll(raw)
    condition=raw['specification']['condition']
    return dict(condition=condition,legacyValid=valid,observedScrolled=scroll,offsetEvidence=reason,
        stationaryContractCandidate=valid and scroll is False and raw.get('cleanup')=='verified'
            and condition in ('interior_switch','boundary_noop'),
        cleanupVerified=raw.get('cleanup')=='verified',trainingEligible=False)


def run(sources_path,output):
    out=h.fresh(output);sources=h.read(h.local(sources_path));records=[];source_refs=[]
    for source in sources:
        ref=source['report'];doc=h.read(h.checked(h.ROOT,ref));source_refs.append(ref)
        if doc['version']=='settings-stability-v1':
            records.append(dict(source=ref,kind='settings',reason='no_native_scroll_offset_binding',
                stationaryContractCandidate=False,trainingEligible=False));continue
        h.require(doc['version'] in ('corrected-transition-audit-v1','reference-transition-audit-v1'),'unsupported_retained_report')
        root=h.checked(h.ROOT,doc['manifest']).parent
        campaign=None
        if doc['version']=='corrected-transition-audit-v1':
            verify_package(root/'file-manifest.json');campaign=h.read(root/'campaign-manifest.json')
        for pair in doc['pairs']:
            if campaign is None:
                evidence=h.checked(h.ROOT,pair['inputs'][2]);cp=h.checked(h.ROOT,pair['inputs'][3]);cases=h.read(cp)['cases']
            else:
                cases=campaign['cases'];case=next(c for c in cases if c['case_id']==pair['id'])
                evidence=member(root,f"splits/{case['split_group']}/{case['case_id']}/transition-case.json")
            matching=[c for c in cases if c['case_id']==pair['id']];h.require(len(matching)==1,'retained_case_membership')
            raw=h.read(evidence);failure=None
            try:validate_case(root,evidence,matching[0],stationary=raw['specification']['condition'] in ('interior_switch','boundary_noop'))
            except (ValueError,KeyError,TypeError,OSError) as error:failure=str(error)
            row=dict(id=pair['id'],source=h.ref(evidence),**classification(raw,failure is None),rejection=failure)
            if row['stationaryContractCandidate']:
                # No condition rewriting: only actual supported producer conditions qualify.
                validate_case(root,evidence,matching[0],stationary=True)
            records.append(row)
    counts=Counter((r.get('condition','settings'),str(r.get('observedScrolled')),r.get('legacyValid')) for r in records)
    report=dict(version='retained-stationary-coverage-v1',sources=source_refs,records=records,
        counts=[dict(condition=k[0],scrolled=k[1],legacyValid=k[2],count=v) for k,v in counts.items()],
        stationaryCandidates=sum(r['stationaryContractCandidate'] for r in records),newAdmission=False,
        scope='Exact three-source retained inventory from REFERENCE-TRANSITION-50; not all unreceived peer artifacts.',
        limitations=['Boundary intent is not observed no-scroll; absent offsets stay unknown.',
                    'No historical condition translation, training-role change or independent-evaluation claim.'])
    out.parent.mkdir(parents=True,exist_ok=True);h.write(out,report,sealed=True)
    print(report['counts']);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.sources,a.output)
