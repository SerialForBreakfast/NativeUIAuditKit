"""Write immutable review specifications and the investigation inventory. Do not submit or approve."""
import research_queue as q

INVESTIGATIONS = [
 ('A1','Paired gains and losses','Which previous failures improve without losing successes?','ready','hcf376-crop-review-v1'),
 ('A2','Profile score margins','Does either profile remain close to competing controls?','ready','hcf376-crop-review-v1'),
 ('A3','Family and group coverage','Does success span supported groups or only repeated frames?','ready','hcf376-crop-review-v1'),
 ('A4','Size and position slices','Which measured control positions and sizes lack support?','ready','hcf376-crop-review-v1'),
 ('A5','Duplicate training exposure','How much crop reuse occurs in each profile and label?','ready','hcf376-crop-review-v1'),
 ('B1','Deployable proposal recall','Does a fixed proposal method find each observed focused control?','blocked','research-host-NUIAK: pin proposal outputs for the 264 exact frame identities.'),
 ('B2','Selection with deployable proposals','Does crop selection work without known control boxes?','blocked','research-host-NUIAK: B1 proposal outputs and production crop inference adapter.'),
 ('B3','Proposal displacement','How much proposal displacement removes the useful focus cue?','blocked','research-host-NUIAK: B2 baseline; freeze offsets and original crop comparison.'),
 ('B4','Proposal size error','How much proposal size error causes a wrong selection?','blocked','research-host-NUIAK: B2 baseline; freeze scale variants and original crop comparison.'),
 ('B5','Overlapping proposals','Does repeated coverage of one control cause false ambiguity?','blocked','research-host-NUIAK: B2 baseline and fixed overlap matching rule.'),
 ('C1','Review wrong rule selections','Which visible features explain the 25 retained wrong selections?','blocked','research-host-NUIAK: case-linked pixel measurements; reuse hcf-trust-c1-errors-v1 outcomes.'),
 ('C2','Outline and body geometry','Which families need an outline-to-body offset?','blocked','research-host-NUIAK: reviewed outline labels distinct from observed body bounds.'),
 ('C3','Border contrast and closure','Do misses lack contrast or a complete outline?','blocked','research-host-NUIAK: C2 outline labels and frozen measurement implementation.'),
 ('C4','Pinned peer rule comparison','Does the peer rule improve the same cases without losses?','blocked','peer-host-TTR: prototype source revision, parameters, and executable interface.'),
 ('C5','Rules-first combination','Can rules and a model add coverage without wrong selections?','blocked','research-host-NUIAK: C4 matched predictions and separate calibration scores.'),
 ('D1','Profile balance alone','Does Standard training explain the recovered selections?','blocked','research-host-NUIAK: matched trainer switch preserving duplicate weighting.'),
 ('D2','Duplicate removal alone','Does duplicate removal improve the HCF-only control?','blocked','research-host-NUIAK: matched trainer switch preserving profile membership.'),
 ('D3','Combined changes','Do profile balance and duplicate removal interact?','blocked','research-host-NUIAK: D1 and D2; reuse HCF375C only after matched settings checks.'),
 ('D4','Second training seed','Does the justified correction repeat with another seed?','blocked','research-host-NUIAK: D3 decision and frozen seed configuration.'),
 ('D5','Third seed and grouped comparison','Are gains consistent across seeds and groups?','blocked','research-host-NUIAK: D4 decision, third seed configuration, grouped comparison.'),
 ('E1','Native no-focus states','Does the method abstain when no control has focus?','blocked','research-host-TTR: qualified no-focus observation recipe; freeze groups before capture.'),
 ('E2','Native decoration decoys','Does white decoration cause wrong focus selections?','blocked','research-host-NUIAK: compiled native decoy recipes and frozen groups; OS HCF remains enabled.'),
 ('E3','Native clipped and corner controls','Does partial visibility cause wrong selections or abstentions?','blocked','research-host-NUIAK: compiled clipping and position recipes with observed bounds.'),
 ('E4','New native control families','Which families show visible HCF cues and usable detection?','blocked','research-host-NUIAK: selected family recipes, qualified focus observations, reserved groups.'),
 ('E5','Native transition sequences','When does the detector decide before focus has settled?','blocked','research-host-TTR: qualified timed sequence producer with capture timestamps and observations.'),
]


def prepare(owner, folder):
    code=q.ROOT/'scripts/hcf_crop_review376.py'
    dependencies=[]
    for job,name in [('hcf371r5-80-crop-evaluate','comparison.json'),('hcf375c-80-crop-evaluate','comparison.json'),
                     ('hcf371r4-50-crops','crops.json'),('hcf371-00-retained','admission.json')]:
        dependencies.append(dict(job=job,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/job/'spec.json')),outputs=[name]))
    spec=dict(version='research-spec-v2',id='hcf376-crop-review-v1',task='HCF376',owner=owner,
        kind='screen',jobKind='aggregation',authority='diagnostic',
        hypothesis='Matched crop predictions separate recovered Standard selections from retained HCF successes.',
        question='What improves, what regresses, and which coverage limits remain after the crop correction?',
        controlledComparison='Compare original and corrected crop predictions on identical pixels, crops, groups, and roles. Run no inference.',
        decisionRule='Reject identity mismatches. Report gains and losses by profile, group, family, and measured geometry. Do not promote.',
        nextActionByOutcome={'gainsWithoutLosses':'Isolate profile balance and duplicate removal with matched training controls.',
                             'losses':'Diagnose lost case margins before training.',
                             'unsupported':'Prepare the named missing coverage without altering final audit roles.'},
        adapter=dict(type='python-callable',steps=['hcf_crop_review376.run'],outputAttributes=['hcf_crop_review376.OUT']),
        inputs=[dict(path=q.relative(code),sha256=q.digest(code))], dependencies=dependencies,
        evidence=dict(citations='sources.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    q.validate(spec)
    inventory=dict(version='hcf-investigations-v1',executionJobs=1,investigations=25,
        note='Five retained-data questions share one report. Blocked investigations are not executable jobs.',
        rows=[dict(id=i,test=t,question=question,state=s,requirement=r) for i,t,question,s,r in INVESTIGATIONS])
    folder.mkdir(parents=True,exist_ok=True)
    for name,value in [('hcf376-crop-review-v1.json',spec),('investigations.json',inventory)]:
        path=folder/name
        q.require(not path.exists(),'immutable_spec_exists')
        q.save(path,value)
    return spec


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner',required=True)
    args=parser.parse_args()
    print(prepare(args.owner,q.ROOT/'Research/ResearchSpecs/HCF376')['id'])
