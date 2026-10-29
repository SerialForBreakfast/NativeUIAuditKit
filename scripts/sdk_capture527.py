"""Capture one SDK packet through the pinned TTR helper. No navigation or retry."""
import json
import os
import shutil
import stat
import time
import uuid
import subprocess
from pathlib import Path
import research_queue as q
from experiment_templates import checked,pin
from sdk_packet502 import review

OUT=None
TARGET='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
ENDPOINT='http://127.0.0.1:8097/diagnostics/sdk/probe'
TTR=Path('/Users/josephmccraw/Developer/TVTestRig')


def external(ref,root):
    q.require(set(ref)=={'path','sha256'},'sdk_capture_pin')
    p=Path(ref['path'])
    helper_link=(p.name=='aatv' and p.parent.name=='Helpers' and
                 p.resolve()==p.parent.parent/'MacOS/TVTestRig')
    q.require(p.is_absolute() and (p.resolve()==p or helper_link) and p.resolve().is_relative_to(root) and p.is_file(),'sdk_capture_path')
    q.require(q.digest(p)==ref['sha256'],'sdk_capture_source_changed')
    return p


def validate_config(c):
    q.require(set(c)=={'version','id','target','endpoint','helper','enrollment','output','expectedAppID','group','sourceRevision'},'sdk_capture_fields')
    q.require(c['version'] in ('sdk-capture-request-v1','sdk-arrival-departure-request-v1','sdk-removal-restoration-request-v1') and q.ID.fullmatch(c['id']),'sdk_capture_identity')
    q.require(c['target']==TARGET and c['endpoint']==ENDPOINT,'sdk_capture_target')
    helper=external(c['helper'],TTR/'.local-work')
    q.require(helper.name=='aatv' and helper.parent.name=='Helpers','sdk_capture_helper')
    enrollment=external(c['enrollment'],TTR/'.local-work')
    q.require(enrollment.stat().st_size<=8192 and stat.S_IMODE(enrollment.stat().st_mode)==0o600,'sdk_capture_private_enrollment')
    identity=q.load(enrollment)
    q.require(identity.get('appID')==c['expectedAppID']=='example.ttr.navigation.consumer','sdk_capture_app')
    q.require(identity.get('processID') and identity.get('runID'),'sdk_capture_launch_identity')
    out=Path(c['output'])
    q.require(out.is_absolute() and out.resolve()==out and out.is_relative_to(TTR/'.local-work') and out.parent.is_dir(),'sdk_capture_output')
    q.require(q.HASH.fullmatch(c['sourceRevision']+'0'*24) and len(c['sourceRevision'])==40,'sdk_capture_revision')
    q.require(isinstance(c['group'],str) and q.ID.fullmatch(c['group']),'sdk_capture_group')
    return c


class Client:
    def __init__(self,c,out,prefix='call'):self.config,self.out,self.sequence,self.prefix=c,out,0,prefix
    def call(self,*args):
        self.sequence+=1
        helper=external(self.config['helper'],TTR/'.local-work')
        env=dict(os.environ);env.pop('TVTESTRIG_PROJECT',None)
        # SDK file operations use their explicit repository root. IPC keeps the active app workspace.
        prefix=['--project',str(TTR)] if args and args[0]=='sdk' else []
        r=subprocess.run([str(helper),*prefix,'--json',*args],capture_output=True,text=True,timeout=45,env=env)
        q.require(len(r.stdout.encode())+len(r.stderr.encode())<=8*1048576,'sdk_capture_reply_limit')
        q.save(self.out/f'{self.prefix}-{self.sequence:02}.json',dict(arguments=list(args),returnCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        d=json.loads(r.stdout)
        q.require(r.returncode==0 and d.get('success') is True,'sdk_capture_call_failed:'+str(d.get('error')))
        return next(iter(d['data'].values()))['_0']


def readiness(c,out):
    validate_config(c)
    r=Client(c,out,'readiness').call('simulator','readiness','--simulator-udid',c['target'])
    q.require(r.get('can_run') is True and r.get('ownership') and all(x['state']=='clear' for x in r['ownership']),'sdk_capture_target_busy')
    return r


def build(path):
    c=validate_config(q.load(path))
    spec=dict(version='research-spec-v2',id=c['id'],task='FRICTION526-CAPTURE',owner='Maximum-mini-NUIAK',
        kind='screen',jobKind='capture',authority='capture',dependencies=[],inputs=[pin(path),pin(Path(__file__))],
        capture=dict(target=c['target'],endpoint=c['endpoint'],plan=pin(path),approval='Maintainer authorizes bounded Simulator acquisition; one packet, no input, no settings mutation.'),
        adapter=dict(type='python-callable',steps=['sdk_capture527.run'],outputAttributes=['sdk_capture527.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(reads=[pin(path)['path']],captureReceipt='capture-evidence.json'),
        question='Does the source-built SDK consumer supply usable native focus and frame-aligned registered bounds?',
        hypothesis='A single supported SDK packet removes custom capture handling and supplies actionable missing-evidence reports.',
        controlledComparison='Pin the app enrollment, helper, Simulator, Git revision, and group. Do not navigate or infer unknown labels.',
        decisionRule='Require matching native identity and valid packet geometry. Unknown profile remains unavailable for training.',
        nextActionByOutcome=dict(supported='Prepare registered crops after required profile evidence passes.',contradicted='Use the exact producer failure; preserve incomplete output and do not retry automatically.'))

    if c['version'] in ('sdk-arrival-departure-request-v1','sdk-removal-restoration-request-v1'):
        spec['task']='SDK529'
        spec['capture']['approval']='Maintainer approves sample installation and bounded arrival/departure comparison: at most 6 frames, 800 s, 100 MB. This job uses 3 frames and 2 playPause inputs on the named sample only.'
        spec['question']='Does corrected native history preserve no-focus, focus arrival, and focus departure across exact frames?'
        spec['controlledComparison']='Same source-built sample, enrollment, target, group, and model-free native evidence. Two playPause inputs toggle sample focusability only.'
        spec['decisionRule']='Capture observed endpoints even when the hypothesis fails. Require native no-focus, focused, no-focus and complete history to qualify departure. Missing evidence is inconclusive. Never retry an input.'
    if c['version']=='sdk-removal-restoration-request-v1':
        spec['capture']['approval']='Requires explicit approval for 3 frames and 2 playPause inputs, within 800 s and 100 MB, on the removal sample.'
        spec['question']='Does native removal and restoration produce departure and return with aligned image evidence?'
        spec['controlledComparison']='Same source-built sample and stable control objects. Remove both views, then restore them. Record actual native focus.'
        spec['decisionRule']='Retain every observed endpoint. Qualify departure and return only when native history and image labels agree. Never infer nil focus from removal.'
    return spec


def validate_spec(spec):
    c=validate_config(q.load(checked(spec['capture']['plan'])))
    q.require(spec['id']==c['id'] and spec['capture']['target']==c['target'] and spec['capture']['endpoint']==c['endpoint'],'sdk_capture_spec_identity')
    q.require(spec['limits']['timeoutSeconds']<=800 and spec['limits']['maxOutputBytes']<=100000000 and spec['limits']['maxAttempts']==1,'sdk_capture_budget')


def run():
    spec=q.load(OUT.parents[2]/'spec.json');validate_spec(spec);c=q.load(checked(spec['capture']['plan']))
    if c['version'] in ('sdk-arrival-departure-request-v1','sdk-removal-restoration-request-v1'):
        return run_sequence(c,spec)
    for dep in q.dependency_inputs(spec,OUT.parents[4]):
        for ref in dep['outputs']:
            receipt=q.load(checked(ref))
            q.require(receipt.get('reviewable') is True,'sdk_capture_dependency_not_reviewable')
    q.save(OUT/'readiness.json',readiness(c,OUT))
    destination=Path(c['output']);q.require(not destination.exists(),'sdk_capture_output_exists')
    q.require(shutil.disk_usage(destination.parent).free>=spec['limits']['maxOutputBytes']+100000000,'sdk_capture_storage')
    client=Client(c,OUT)
    result=client.call('sdk','packet','--endpoint',c['endpoint'],'--enrollment',c['enrollment']['path'],
        '--simulator-udid',c['target'],'--output',str(destination))
    q.save(OUT/'producer.json',result)
    q.require(result.get('state') in ('collected','collected_with_issues'),'sdk_capture_not_collected')
    paths=[destination/name for name in ('frame.png','evidence.json')]
    q.require(all(p.is_file() and not p.is_symlink() for p in paths),'sdk_capture_missing_output')
    q.require(sum(p.stat().st_size for p in paths)<=90000000,'sdk_capture_packet_limit')
    for p in paths:
        target=OUT/p.name;shutil.copyfile(p,target);q.require(q.digest(p)==q.digest(target),'sdk_capture_copy_changed')
    e=q.load(OUT/'evidence.json')
    identity=q.load(external(c['enrollment'],TTR/'.local-work'))
    q.require(e['sourceID']==c['target'] and all(e[side][k]==identity[k] for side in ('before','after') for k in ('appID','processID','runID')),'sdk_capture_evidence_identity')
    reviewed=review(e,OUT/'frame.png')
    reviewed.update(group=c['group'],sourceRevision=c['sourceRevision'],profile='unknown',role='review_only',
        missingForTraining=['observed_profile','reviewed_group_membership'],capturesDispatched=1,inputsDispatched=0)
    q.save(OUT/'benchmark_summary.json',reviewed)
    q.save(OUT/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=[dict(path='frame.png',sha256=q.digest(OUT/'frame.png'))],inputsDispatched=0))
    files=[p for p in OUT.iterdir() if p.is_file()]
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=p.name,sha256=q.digest(p)) for p in files]))


def observed(client, identity, focused):
    """Require fresh native state before input; never infer it from an input receipt."""
    d=client.call('sdk','snapshot','--endpoint',client.config['endpoint'],'--enrollment',client.config['enrollment']['path'])
    q.require(d.get('state')!='unavailable' and d.get('sourceKind')!='none','sdk_sequence_live_evidence_unavailable')
    q.require(all(d.get(k)==identity[k] for k in ('appID','processID','runID')), 'sdk_sequence_identity')
    q.require(d.get('fresh') is True and d.get('sourceKind')=='authenticated_sdk_challenge' and
              d.get('currentFocusKnown') is True and d.get('controlEventGap') is False,
              'sdk_sequence_observation_unknown')
    control=d.get('control') or {}
    q.require(control.get('ready') is True and control.get('focusSource')=='nativeCallback' and
              not control.get('presentationIDs'), 'sdk_sequence_sample_not_ready')
    q.require(isinstance(control.get('focusObservedAt'),int) and
              0<=control['sampledAt']-control['focusObservedAt']<1000000000, 'sdk_sequence_focus_stale')
    return focused is None or (d.get('currentFocusID') is not None)==focused


def wait_observed(client,identity,focused):
    for attempt in range(12):
        if observed(client,identity,focused):return
        time.sleep(.2)
    raise ValueError('sdk_sequence_focus_timeout')


def remote(client,action,session=None):
    args=['simulator','remote',action,'--simulator-udid',client.config['target']]
    if session:args+=['--session',session]
    if action=='press':args+=['--button','playPause']
    d=client.call(*args)
    q.require(d.get('simulatorID')==client.config['target'],'sdk_sequence_remote_target')
    uuid.UUID(d['operationID'])
    if session:q.require(d['operationID']==session,'sdk_sequence_remote_session')
    return d


def wait_remote(client,session,wanted):
    for attempt in range(30):
        d=remote(client,'status',session)
        if d['state']==wanted:return d
        q.require(d['state'] in ('starting','stopping'),'sdk_sequence_remote_state:'+d['state'])
        time.sleep(.5)
    raise ValueError('sdk_sequence_remote_timeout:'+wanted)


def run_sequence(c,spec):
    from sdk_episode529 import episode
    for dependency in q.dependency_inputs(spec,OUT.parents[4]):
        for ref in dependency['outputs']:checked(ref)
    q.save(OUT/'readiness.json',readiness(c,OUT))
    destination=Path(c['output']);q.require(not destination.exists(),'sdk_capture_output_exists')
    q.require(shutil.disk_usage(destination.parent).free>=spec['limits']['maxOutputBytes']+100000000,'sdk_capture_storage')
    destination.mkdir();identity=q.load(external(c['enrollment'],TTR/'.local-work'))
    client=Client(c,OUT);session=None;frames=[];native_states=[];disabled_focus=[];inputs=0;started=time.monotonic()
    def budget():
        size=sum(p.stat().st_size for root in (destination,OUT) for p in root.rglob('*') if p.is_file())
        q.require(size<=spec['limits']['maxOutputBytes'],'sdk_sequence_storage_budget')
        q.require(time.monotonic()-started<650,'sdk_sequence_time_budget')
    removal=c['version']=='sdk-removal-restoration-request-v1'
    initial=True if removal else False
    try:
        wait_observed(client,identity,initial)
        receipt=remote(client,'connect');session=receipt['operationID']
        q.save(OUT/'remote-session.json',receipt)
        if receipt['state']!='ready':wait_remote(client,session,'ready')
        for index in range(3):
            budget();wait_observed(client,identity,initial if index==0 else None)
            folder=destination/('frame-'+str(index));result=client.call('sdk','packet','--endpoint',c['endpoint'],
                '--enrollment',c['enrollment']['path'],'--simulator-udid',c['target'],'--output',str(folder))
            q.require(result.get('state') in ('collected','collected_with_issues'),'sdk_sequence_capture_failed')
            copied={};local=OUT/('frame-'+str(index));local.mkdir()
            for name in ('frame.png','evidence.json'):
                source=folder/name;q.require(source.is_file() and not source.is_symlink(),'sdk_sequence_missing_packet')
                q.require(source.stat().st_size<30000000,'sdk_sequence_packet_size')
                shutil.copyfile(source,local/name);q.require(q.digest(source)==q.digest(local/name),'sdk_sequence_copy')
                copied['image' if name=='frame.png' else 'evidence']=pin(local/name)
            e=q.load(local/'evidence.json')
            q.require(e['sourceID']==c['target'] and all(e[side][k]==identity[k] for side in ('before','after') for k in ('appID','processID','runID')),'sdk_sequence_packet_identity')
            r=review(e,local/'frame.png');frames.append(copied);q.save(OUT/('partial-frames-'+str(index)+'.json'),frames)
            # Expected outcomes are hypotheses, not prerequisites for retaining observations.
            before,after=e['before'],e['after']
            agreed=all(v.get('focusKnown') is True and v.get('interrupted') is False for v in (before,after)) and before.get('focusID')==after.get('focusID')
            native_states.append(('focused' if after.get('focusID') is not None else 'no_focus') if agreed else 'unknown')
            disabled_focus.append(any(v['identity']['id']==after.get('focusID') and (v.get('observedState') or {}).get('enabled') is False for v in after['elements']))
            budget()
            if index<2:
                wait_observed(client,identity,None)
                # Persist intent before dispatch. An uncertain response must never cause a retry.
                q.save(OUT/('input-'+str(index)+'.json'),dict(state='intent',session=session,button='playPause'))
                inputs+=1;reply=remote(client,'press',session)
                q.save(OUT/('input-'+str(index)+'.receipt.json'),dict(state='received',receipt=reply))
                q.require(reply['state']=='delivered','sdk_sequence_input_unconfirmed')
        row=dict(id=c['id'],scenario='native-removal-restoration' if removal else 'native-arrival-departure',group=c['group'],role='review_only',frames=frames)
        result=episode(row)
        q.save(OUT/'episode-request.json',dict(version='sdk-episode-request-v1',id=c['id'],episodes=[row]))
        expected=['focused','no_focus','focused'] if removal else ['no_focus','focused','no_focus']
        outcome=('inconclusive' if 'unknown' in native_states or not result['eligibility']['temporalReview'] else
                 'supported' if native_states==expected else 'contradicted')
        q.save(OUT/'benchmark_summary.json',dict(version='sdk-native-sequence-v1',episode=result,frames=len(frames),inputsDispatched=inputs,
            expectedNativeStates=expected,observedNativeStates=native_states,nativeFocusOnDisabledControl=disabled_focus,
            hypothesisOutcome=outcome,departureQualified=outcome=='supported',
            imageSequenceQualified=outcome=='supported' and result['eligibility']['allFramesAligned'],
            alignedImageStates=[f['frameFocusState'] for f in result['frames']],trainingAdmitted=False,modelAccepted=False))
    finally:
        if session:
            cleanup=remote(client,'disconnect',session)
            if cleanup['state']!='closed':cleanup=wait_remote(client,session,'closed')
            q.save(OUT/'remote-cleanup.json',cleanup)
    q.save(OUT/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=[dict(path='frame-'+str(i)+'/frame.png',sha256=f['image']['sha256']) for i,f in enumerate(frames)],inputsDispatched=inputs))
    files=[p for p in OUT.rglob('*') if p.is_file()]
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in files]))
