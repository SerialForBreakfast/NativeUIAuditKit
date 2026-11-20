"""Prepare fresh native evidence through existing SDK checks. Never infer admission."""
from pathlib import Path
import research_queue as q
from template_inputs398 import checked,pin
import sdk_training513 as sdk
OUT=None


def validate(request):
    q.require(set(request)=={'version','id','captures','source','tool','exclusions'},'native587_prepare_fields')
    q.require(request['version']=='native-review-preparation587-v1' and q.ID.fullmatch(request['id']),'native587_prepare_identity')
    q.require(len(request['captures'])==8 and len({r['job'] for r in request['captures']})==8,'native587_prepare_membership')
    for row in request['captures']:
        q.require(set(row)=={'job','specSHA256','group','split'} and row['split'] in ('train','validation'),'native587_prepare_role')
    q.require(sum(r['split']=='train' for r in request['captures'])==6,'native587_prepare_roles')
    checked(request['source']);checked(request['tool'])


def build(path):
    r=q.load(path);validate(r)
    deps=[dict(job=x['job'],specSHA256=x['specSHA256'],outputs=['producer/pair/manifest.json','cleanup.json','benchmark_summary.json']) for x in r['captures']]
    return dict(version='research-spec-v2',id=r['id'],task='NATIVE587',owner='Maximum-mini-NUIAK',kind='screen',jobKind='artifact',authority='diagnostic',
        question='Do all fresh native pairs retain their frozen groups and supply reusable focus labels and production crops?',
        hypothesis='Observed native focus and measured geometry support fresh crop labels while profile admission stays explicit.',
        controlledComparison='Preserve original packets, roles, groups, source identity, crop geometry and observed focus.',
        decisionRule='Reject missing or changed captures, invalid pair evidence, cleanup failures and group drift. Never infer training permission.',
        nextActionByOutcome=dict(supported='Review exact profile evidence and data-use decision before admitted training.',contradicted='Preserve evidence and repair the exact failed boundary.'),
        request=pin(path),inputs=[pin(path),r['source'],r['tool'],pin(Path(__file__))],dependencies=deps,
        adapter=dict(type='python-callable',steps=['native_training587.run'],outputAttributes=['native_training587.OUT']),
        evidence=dict(reads=[q.relative(path)],artifactReceipt='artifact-receipt.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))


def run():
    s=q.load(OUT.parents[2]/'spec.json');r=q.load(checked(s['request']));validate(r)
    deps=q.dependency_inputs(s,OUT.parents[4]);by={d['job']:d for d in deps};pairs=[];profiles=[]
    for item in r['captures']:
        d=by[item['job']];outputs={Path(x['path']).name:x for x in d['outputs']}
        summary=q.load(checked(outputs['benchmark_summary.json']));q.require(summary['cleanupVerified'] is True,'native587_cleanup')
        ref=outputs['manifest.json'];p=checked(ref);m=q.load(p)
        for side in ('before','after'):
            packet=q.load(q.local_path(p.parent,m[side]['packet'])/'manifest.json');case=packet['cases'][0]
            q.require(case['group']==item['group'] and case['contentGroup']==item['group'] and case['split']==item['split'],'native587_capture_role_drift')
        pairs.append(ref);profiles.append(dict(job=item['job'],assessment=m.get('continuityAssessment'),profileEvidence=m.get('focusStyleEvidence')))
    request=dict(version='sdk-preparation-v1',id=r['id'],pairs=pairs,source=r['source'],tool=r['tool'],exclusions=r['exclusions'],admission=None,products=['crops'])
    data=sdk.intake(request);q.save(OUT/'intake-request.json',request);q.save(OUT/'intake.json',data)
    crops=sdk.prepare_crops(data,OUT/'crops',r['tool']);q.save(OUT/'crops.json',crops)
    q.save(OUT/'benchmark_summary.json',dict(resultsProvisional=True,frames=len(data['frames']),cropRows=len(crops['rows']),intendedGroups=r['captures'],
        observedFocus=data['capabilities']['observedFocusStates'],profiles=profiles,gaps=data['gaps'],trainingEligible=False,modelAccepted=False,
        nextAction='Require explicit approval for bounded profile inference or direct applicable profile evidence. Preserve requested roles.'))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in OUT.rglob('*') if p.is_file()]))
