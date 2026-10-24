"""Report SDK corpus capabilities without assigning training roles or labels."""
from collections import Counter
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
from sdk_packet502 import review

OUT = None


def audit(manifest_path):
    manifest=q.load(manifest_path);root=manifest_path.parent
    q.require(manifest.get('schemaVersion')==1 and manifest.get('admission')=='review_only','sdk_dataset_contract')
    members={}
    for row in manifest['members']:
        q.require(row['path'] not in members,'sdk_dataset_duplicate_member')
        path=q.local_path(root,row['path'])
        q.require(path.is_file() and not path.is_symlink() and path.stat().st_size==row['bytes'] and
                  q.digest(path)==row['sha256'],'sdk_dataset_member_changed')
        members[row['path']]=path
    counts=Counter();cases=[];seen=set();groups=set()
    for case in manifest['cases']:
        q.require(case['id'] not in seen,'sdk_dataset_duplicate_case');seen.add(case['id'])
        q.require(all(isinstance(case.get(k),str) and case[k] for k in ('id','group','contentGroup','split')),'sdk_dataset_ancestry')
        groups.add((case['group'],case['contentGroup']))
        frames=[]
        for frame in case['frames']:
            q.require(frame['image'] in members and frame['evidence'] in members,'sdk_dataset_missing_member')
            q.require(frame.get('labelAdmission')=='review_only','sdk_dataset_frame_admission')
            evidence=q.load(members[frame['evidence']])
            q.require(all(evidence[s].get('appID')==manifest['source']['appID'] for s in ('before','after')),'sdk_dataset_app_identity')
            result=review(evidence,members[frame['image']])
            counts['frames']+=1;counts[result['focusState']]+=1
            for element in result['elements']:
                counts['registeredElements']+=1
                counts['pixelGeometry']+=element['geometryAvailable']
                counts['classNames']+=bool(element['className'])
                counts['parentLinks']+=bool(element['parentID'])
            frames.append(dict(role=frame['role'],image=pin(members[frame['image']]),
                evidence=pin(members[frame['evidence']]),focusState=result['focusState'],
                issues=result['reasons'],registeredElements=len(result['elements'])))
        cases.append(dict(id=case['id'],group=case['group'],contentGroup=case['contentGroup'],
            split=case['split'],frames=frames))
    q.require(cases and counts['frames']>0,'sdk_dataset_empty')
    requirements=[]
    if not counts['no_focus']:
        requirements.append(dict(id='observed-no-focus',owner='TTR producer',requirement='Provide a stable native packet with focusKnown true and no focusID. Unknown telemetry is not a negative label.'))
    requirements.append(dict(id='action-linked-transitions',owner='TTR producer',requirement='Provide before and after packets linked to one delivered action and observed outcomes. Screenshot brackets alone are not navigation pairs.'))
    requirements.append(dict(id='detector-label-coverage',owner='TTR producer and Maximum-mini-NUIAK',requirement='Provide registered-to-native class mapping and explicit coverage/exclusions. Review taxonomy before any detector-label admission.'))
    return dict(version='sdk-dataset-audit-v1',manifest=pin(manifest_path),cases=cases,counts=dict(counts),
        ancestryGroups=len(groups),splitAuthority=manifest.get('splitAuthority','unknown'),
        annotationCompleteness='unknown',verifiedNavigationPairs=0,requirements=requirements,
        trainingEligible=False,modelAccepted=False,
        limitation='Registered element counts do not establish complete UI coverage. Preserve producer splits and content ancestry. '
                   'The current packet schema lacks a validated action-pair or class-completeness contract.')


def build(manifest_path,ident):
    refs=[pin(manifest_path),pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2',id=ident,task='SDK505',owner='Maximum-mini-NUIAK',kind='screen',
        jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs,
        adapter=dict(type='python-callable',steps=['sdk_dataset505.run'],outputAttributes=['sdk_dataset505.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json',reads=[refs[0]['path']]),
        question='Which SDK dataset requirements are observed, missing, or unsupported in the delivered native corpus?',
        hypothesis='Delivered metadata supports geometry review but does not yet establish complete detector labels or action-linked focus transitions.',
        controlledComparison='Preserve delivered images, source declarations, cases, roles, groups, and requested test split.',
        decisionRule='Reuse verified observations. Emit exact producer requirements for missing evidence. Never infer training eligibility.',
        nextActionByOutcome=dict(supported='Use observed fields in diagnostics and request only missing data.',
                                 contradicted='Preserve the corpus and report the exact failing evidence check.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');result=audit(checked(spec['inputs'][0]))
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
