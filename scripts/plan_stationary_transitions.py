"""Create a frozen development-only no-scroll matrix; never contact a runtime."""
import argparse
import human_annotation_review as h


def catalog():
    cases=[]
    for screen in ('nostalgex_guide','stingray_catalog'):
        for theme in ('dark','light'):
            for artwork in ('city','collage','orbit'):
                for kind in ('boundary_noop','interior_switch'):
                    cases.append(dict(id=f'{screen}-{theme}-{artwork}-{kind}',
                        referenceScreen=screen,theme=theme,artworkStyle=artwork,seed=83,variant=0,
                        partition='development',journeyGroup='fixture-procedural-renderer-v1',
                        relatedSeedPolicy='Keep all variants and prior reference captures development-connected; no independent evaluation claim.',
                        condition=kind,expectedFocusChanged=kind=='interior_switch',expectedScrolled=False,
                        targetSelection=('Native-observed edge control; outward directional press.' if kind=='boundary_noop' else
                            'Two fully visible native-observed adjacent controls within one viewport; one directional press.'),
                        captureCount=2,maxActions=1,maxRecipeSeconds=120,
                        acceptance=['Fresh exact simulator/Fixture instance and matching endpoint.',
                            'Unique verified settled input focus and measured body bounds in both captures.',
                            'Same named scroll containers and equal native offsets across all four scene brackets.',
                            'Observed focus relation equals case expectation; requested focus is not a label.',
                            'Hash-verified distinct observations, action receipt and verified cleanup.',
                            'Any clipping, automatic scroll, external input or uncertain cleanup rejects the case.']))
    return dict(version='stationary-transition-plan-v1',cases=cases,expectedPairs=24,expectedCaptures=48,
        executionEligible=False,trainingEligible=False,independentEvaluationEligible=False,
        requiredAuthority=['Exact currently verified simulator UUID and Fixture launch/storage scope.',
            'Bounded capture assignment and current runtime/endpoint readiness.',
            'Reviewed consumer condition adapter; existing scroll-only admission is not bypassed.'],
        runtime='Use source-matched instrumented reference renderer; historical qualification is not current runtime readiness.',
        stop='No automatic retries or fallback to Office. Preserve partial output and end on failed preflight/cleanup.',
        finalEvaluation='Not allocated from these related seed83 development groups; requires independent journey reservation.')


def validate(doc):
    h.require(doc==catalog(),'stationary_plan_changed')
    h.require(len({v['id'] for v in doc['cases']})==24,'duplicate_case')
    return doc


def campaign(retained):
    """Session-level scheduling only; preserve existing per-case contracts."""
    report=h.read(h.checked(h.ROOT,retained))
    h.require(report.get('version')=='retained-stationary-coverage-v1' and
        report.get('seal')==h.digest({k:v for k,v in report.items() if k!='seal'}),'retained_coverage_changed')
    for ref in report['sources']:h.checked(h.ROOT,ref)
    original=validate(catalog());cases=sorted(original['cases'],key=lambda c:(
        c['referenceScreen'],c['theme'],c['artworkStyle'],c['condition']!='interior_switch'))
    groups={}
    for case in cases:
        key=':'.join(str(case[k]) for k in ('referenceScreen','theme','artworkStyle','seed','variant'))
        groups.setdefault(key,[]).append(case['id'])
    values=list(groups.items());batches=[]
    for i in range(0,len(values),2):
        subset=values[i:i+2]
        batches.append(dict(id=f'batch-{i//2:02}',recipeGroups=[k for k,_ in subset],
            caseIDs=[v for _,ids in subset for v in ids],maxSeconds=600,
            caseSeconds=120,actionLimit=4,completedPublicationOnly=True))
    h.require(len(groups)==12 and len(batches)==6 and sum(len(b['caseIDs']) for b in batches)==24,'campaign_accounting')
    return dict(version='stationary-session-campaign-v1',retainedCoverage=retained,
        retainedStationaryContractCandidates=report['stationaryCandidates'],cases=cases,batches=batches,
        expectedPairs=24,expectedCaptures=48,plannedRuntimeSessions=1,
        executionEligible=False,trainingEligible=False,independentEvaluationEligible=False,
        lifecycle=['Authorize exact target/build/endpoint and session/storage scope before starting.',
            'Qualify runtime once; each case still needs fresh identity, focus, geometry and equal-offset brackets.',
            'Prioritize interior switches within each group; reuse healthy runtime between bounded jobs.',
            'Release job-owned leases after each job; check health. Do not quit/relaunch healthy Fixture between batches.',
            'Seal/export/intake complete batches asynchronously. Resume only missing groups after inspection and authority check.',
            'Stop on changed instance, target, build, external input, unknown cleanup or lost authority; no automatic retry/reset.'],
        requiredCapabilities=['Verify producer supports retaining runtime while releasing each job lease.',
            'Verify actual interior_switch/boundary_noop contracts and full observed offset/geometry metadata.',
            'No assumed ability to preserve a session across producer crash or app update.'],
        rolePolicy='All these seed83 renderer-related cases remain development-connected; new training admission is separate.',
        finalEvaluation='No independent group is allocated from this renderer ancestry. Reserve genuinely separate reviewed journeys before future capture.',
        gaps=['Native high-contrast reference rendering not yet pinned; do not claim palette variation covers it.',
            'Additional control shapes/layouts need a source-supported matrix, not repeated seed variants alone.',
            'Retained eight composite-card negatives are already admitted; do not recapture them.',
            'No new capture or final-evaluation authority is granted by this plan.'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    p.add_argument('--retained-coverage',help='Build session campaign from a verified retained-source inventory')
    a=p.parse_args();out=h.fresh(a.output)
    doc=campaign(h.ref(h.local(a.retained_coverage))) if a.retained_coverage else validate(catalog())
    h.write(out,doc,sealed=True)
