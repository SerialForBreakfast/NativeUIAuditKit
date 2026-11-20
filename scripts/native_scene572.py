"""Own one source-built native scene and collect fixed SDK packets without input."""
from pathlib import Path
import base64
import json
import os
import shutil
import subprocess
import time
import research_queue as q
from experiment_templates import checked, pin
import real_app_sdk572 as metadata
from sdk_packet502 import review
import sdk_capture527 as capture
OUT = None
WORKSPACE = Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig'))
TARGET = metadata.TARGET
ENDPOINT = 'http://127.0.0.1:8097/diagnostics/sdk/probe'


def validate_config(c):
    q.require(set(c)=={'version','id','target','workspace','style','moving','noFocus','construction','scene','partition','offsets','helper','helperSHA256','sources','app'},'scene572_fields')
    q.require(c['version']=='native-scene572-v1' and q.ID.fullmatch(c['id']),'scene572_identity')
    q.require(c['target']==TARGET and c['workspace']==str(WORKSPACE),'scene572_scope')
    q.require(c['style'] in ('opaque','ring') and type(c['moving'])is bool and type(c['noFocus'])is bool,'scene572_style')
    scenes=q.load(checked(c['construction']));scene=next((s for s in scenes if s['id']==c['scene']),None)
    q.require(scene is not None and c['partition']==scene['split'],'scene572_partition')
    q.require(c['partition'] in ('train','validation','qualification'),'scene572_role')
    q.require(c['offsets']==[0,.35,.8],'scene572_capture_points')
    q.require(Path(c['helper']).is_relative_to(WORKSPACE/'.local-work') and q.digest(Path(c['helper']))==c['helperSHA256'],'scene572_helper')
    q.require(c['sources'],'scene572_sources')
    for ref in c['sources']:checked(ref)
    app=q.local_path(q.ROOT,c['app']);q.require(app.is_dir()and app.name=='NavigationConsumer.app','scene572_app')
    pins={checked(ref).resolve() for ref in c['sources']}
    q.require({(app/'NavigationConsumer').resolve(),(app/'Info.plist').resolve()}<=pins,'scene572_app_identity')
    return c


def readiness(c,out):
    validate_config(c);metadata.OUT=out
    r=metadata.cli(c,['simulator','readiness','--simulator-udid',TARGET],'readiness')
    q.require(r.get('can_run') is True and r.get('ownership') and all(x['state']=='clear'for x in r['ownership']),'scene572_target_busy')
    from real_app_session554 import alert_check
    alert=alert_check(TARGET,out=out/'system-alert')
    q.require(alert['status']=='clear','scene572_system_alert:'+alert['status'])
    return r


def validate_spec(spec):
    c=validate_config(q.load(checked(spec['capture']['plan'])))
    q.require(spec['task']=='NATIVE572','scene572_task')
    q.require(spec['id']==c['id'] and spec['capture']['target']==TARGET and spec['capture']['endpoint']==ENDPOINT,'scene572_spec_identity')
    q.require(spec['limits']==dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),'scene572_limits')
    expected=[spec['capture']['plan'],c['construction'],*c['sources']]
    q.require(spec['inputs']==expected,'scene572_input_pins')
    q.require(spec['evidence']['reads']==[p['path'] for p in expected],'scene572_read_pins')


def build(path):
    c=validate_config(q.load(path))
    inputs=[pin(path),c['construction'],*c['sources']]
    return dict(version='research-spec-v2',id=c['id'],task='NATIVE572',owner='Maximum-mini-NUIAK',
        kind='screen',jobKind='capture',authority='capture',dependencies=[],
        question='Can the native scene provide aligned observed focus and geometry for its declared construction?',
        hypothesis='One source-built adapter captures three review-only frames for separate construction groups.',
        controlledComparison='Fixed source, target, offsets and raw role; configuration changes scene, style, motion or no-focus.',
        decisionRule='Preserve all endpoints. Qualify labels separately; unknown focus is not known no-focus.',
        nextActionByOutcome=dict(supported='Prepare existing crop and pair consumers after label checks.',
                                 contradicted='Preserve evidence and diagnose the specific capture or label defect.'),
        capture=dict(target=TARGET,endpoint=ENDPOINT,plan=pin(path),
                     approval='User approves NUIAK implementation, idle activation and resumption. Standing bounded Simulator authority: 3 frames, 0 inputs, 800 s, 100 MB.'),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        inputs=inputs,evidence=dict(reads=[p['path'] for p in inputs],captureReceipt='capture-evidence.json'),
        adapter=dict(type='python-callable',steps=['native_scene572.run'],outputAttributes=['native_scene572.OUT']))


class Client:
    def __init__(self,c):
        self.config=c
        self.sequence=0

    def call(self,*args):
        self.sequence+=1
        return metadata.cli(self.config,list(args),'remote-'+str(self.sequence))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');validate_spec(spec)
    c=validate_config(q.load(checked(spec['capture']['plan'])))
    readiness(c,OUT);metadata.OUT=OUT
    app=q.local_path(q.ROOT,c['app']);bundle='example.ttr.navigation.consumer'
    key=base64.b64encode(os.urandom(32)).decode()
    env=dict(os.environ,SIMCTL_CHILD_TTR_SAMPLE_KEY=key,SIMCTL_CHILD_SIMULATOR_UDID=TARGET)
    args=['--ttr-sdk-enabled=true','--sample-pilot-scene',c['scene'],'--nuiak572-native-corpus','--nuiak572-'+c['style']+'-focus']
    if c['moving']:args.append('--nuiak572-moving-content')
    if c['noFocus']:args.append('--nuiak572-no-focus')
    local=WORKSPACE/'.local-work/nuiak572';credentials=local/'enrollments';credentials.mkdir(exist_ok=True)
    enrollment=credentials/(c['id']+'-private.json');packets=local/'packets';packets.mkdir(exist_ok=True)
    q.require(not enrollment.exists(),'scene572_existing_enrollment')
    child=None;session=None;images=[];frames=[];cleanup={};client=Client(c)
    result=dict(version='native-scene572-result-v1',scene=c['scene'],intendedPartition=c['partition'],
        styleDeclared=c['style'],motionDeclared=c['moving'],profileObserved='unknown',group=c['scene'],
        role='review_only',trainingAdmitted=False,inputsDispatched=0,modelAccepted=False,metricsStatus='provisional')
    try:
        q.save(OUT/'connect-intent.json',dict(target=TARGET,automaticRetry=False))
        connection=capture.remote(client,'connect');session=connection['operationID'];q.save(OUT/'remote-session.json',connection)
        if connection['state']!='ready':capture.wait_remote(client,session,'ready')
        installed=subprocess.run(['xcrun','simctl','install',TARGET,str(app)],capture_output=True,text=True,timeout=120)
        q.require(installed.returncode==0,'scene572_install')
        with (OUT/'console.log').open('wb')as log:
            child=subprocess.Popen(['xcrun','simctl','launch','--console-pty',TARGET,bundle,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
            identity=metadata.identity(child,log,prefix=b'TTR_SAMPLE_READY ')
            q.require(identity['appID']==bundle and identity['endpoint']==ENDPOINT,'scene572_launch_identity')
            fd=os.open(enrollment,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w')as f:json.dump(dict(appID=bundle,processID=identity['processID'],runID=identity['runID'],secretBase64=key),f)
            from real_app_session554 import alert_check
            alert=alert_check(TARGET,out=OUT/'postlaunch-alert')
            q.require(alert['status']=='clear','scene572_postlaunch_alert:'+alert['status'])
            snapshot=metadata.cli(c,['sdk','snapshot','--endpoint',ENDPOINT,'--enrollment',str(enrollment)],'initial-snapshot')
            q.require(snapshot.get('sourceKind')=='authenticated_sdk_challenge' and snapshot.get('fresh')is True,'scene572_snapshot_unavailable')
            start=time.monotonic()
            for i,offset in enumerate(c['offsets']):
                delay=offset-(time.monotonic()-start)
                if delay>0:time.sleep(delay)
                actualOffset=time.monotonic()-start
                dest=packets/(c['id']+'-frame-'+str(i));q.require(not dest.exists(),'scene572_packet_exists')
                metadata.cli(c,['sdk','packet','--endpoint',ENDPOINT,'--enrollment',str(enrollment),'--simulator-udid',TARGET,'--output',str(dest)],'packet-'+str(i))
                image=dest/'frame.png';evidence=dest/'evidence.json'
                q.require(image.is_file()and evidence.is_file()and not image.is_symlink()and not evidence.is_symlink(),'scene572_packet_missing')
                folder=OUT/('frame-'+str(i));folder.mkdir()
                for source in [image,evidence]:
                    shutil.copyfile(source,folder/source.name)
                    q.require(q.digest(source)==q.digest(folder/source.name),'scene572_copy_changed')
                doc=q.load(folder/'evidence.json')
                q.require(doc['sourceID']==TARGET and all(doc[side][k]==identity[k]for side in ['before','after']for k in ['appID','processID','runID']),'scene572_evidence_identity')
                frames.append(dict(index=i,offsetRequested=offset,offsetActual=actualOffset,image=pin(folder/'frame.png'),evidence=pin(folder/'evidence.json'),review=review(doc,folder/'frame.png')))
                images.append(dict(path='frame-'+str(i)+'/frame.png',sha256=q.digest(folder/'frame.png')))
                q.require(q.live_output_bytes(OUT)<95000000,'scene572_output_limit')
    finally:
        if child is not None:
            stopped=subprocess.run(['xcrun','simctl','terminate',TARGET,bundle],capture_output=True,text=True,timeout=30)
            cleanup['appReturnCode']=stopped.returncode
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        if enrollment.exists():enrollment.unlink()
        if session:
            try:
                state=capture.remote(client,'disconnect',session)
                cleanup['remote']=state if state['state']=='closed' else capture.wait_remote(client,session,'closed')
                ready=metadata.cli(c,['simulator','readiness','--simulator-udid',TARGET],'postflight-readiness')
                cleanup['targetReady']=ready.get('can_run')is True and bool(ready.get('ownership')) and all(x['state']=='clear'for x in ready['ownership'])
            except Exception as error:cleanup['error']=str(error)
        result.update(frames=frames,capturesDispatched=len(images),cleanup=cleanup)
        q.save(OUT/'benchmark_summary.json',result);q.save(OUT/'cleanup.json',cleanup)
    q.require(cleanup.get('appReturnCode')==0 and cleanup.get('targetReady')is True and not cleanup.get('error')and len(images)==3,'scene572_incomplete_or_cleanup')
    q.save(OUT/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=images,inputsDispatched=0))


def build_review(producer):
    return dict(version='research-spec-v2',id=producer['id']+'-review',task='NATIVE572',owner='Maximum-mini-NUIAK',
        kind='screen',jobKind='artifact',authority='diagnostic',inputs=[],
        dependencies=[dict(job=producer['id'],specSHA256=q.text_digest(producer),outputs=['benchmark_summary.json','cleanup.json'])],
        question='Do the native packets supply observed focus and aligned geometry without admitting data?',
        hypothesis='The existing packet and episode reviewers expose missing labels, timing and profile evidence.',
        controlledComparison='Reuse unchanged producer packets, construction groups and raw review-only roles.',
        decisionRule='Report unknown labels and profile gaps. No action timing or training admission is inferred.',
        nextActionByOutcome=dict(supported='Prepare eligible static crops and matched scoring after required profile checks.',
                                 contradicted='Preserve packets and isolate the precise missing evidence.'),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(reads=[],artifactReceipt='artifact-receipt.json'),
        adapter=dict(type='python-callable',steps=['native_scene572.run_review'],outputAttributes=['native_scene572.OUT']))


def run_review():
    from collections import Counter
    from sdk_episode529 import episode
    spec=q.load(OUT.parents[2]/'spec.json')
    dependencies=q.dependency_inputs(spec,OUT.parents[4])
    refs={Path(ref['path']).name:ref for dep in dependencies for ref in dep['outputs']}
    result=q.load(checked(refs['benchmark_summary.json']));cleanup=q.load(checked(refs['cleanup.json']))
    q.require(cleanup.get('targetReady')is True and cleanup.get('appReturnCode')==0 and not cleanup.get('error'),'scene572_review_cleanup')
    q.require(result['role']=='review_only'and result['trainingAdmitted']is False and len(result['frames'])==3,'scene572_review_role')
    frames=[dict(image=f['image'],evidence=f['evidence'])for f in result['frames']]
    row=dict(id=spec['id'],scenario='native-unchanged-focus',group=result['group'],role='review_only',frames=frames)
    measured=episode(row)
    summary=dict(version='native-scene572-review-v1',episode=measured,
        focusStates=dict(Counter(f['review']['focusState']for f in result['frames'])),
        group=result['group'],relatedFrames=3,independentApplications=0,
        profileObserved=result['profileObserved'],trainingAdmitted=False,modelAccepted=False,metricsStatus='provisional',
        limitation='No input is sent. Pixel changes alone do not prove background motion or focus transitions.')
    q.save(OUT/'episode-request.json',dict(version='sdk-episode-request-v1',id=spec['id'],episodes=[row]))
    q.save(OUT/'benchmark_summary.json',summary)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[pin_out(OUT/'benchmark_summary.json'),pin_out(OUT/'episode-request.json')]))


def pin_out(path):
    return dict(path=str(path.relative_to(OUT)),sha256=q.digest(path))
