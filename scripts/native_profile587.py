"""Own fresh native training constructions through the existing profile collector."""
import base64
import copy
import json
import os
from pathlib import Path
import subprocess

import research_queue as q
from template_inputs398 import checked,pin
import sdk_capture527 as capture
import real_app_sdk572 as metadata


def validate_config(c):
    q.require(set(c)=={'version','id','capture','plan','producer','sources','nativeScene'} and c['version']=='sdk-profile-pair-v2','native587_fields')
    a=c['capture'];n=c['nativeScene'];plan=q.load(checked(c['plan']))
    q.require(q.ID.fullmatch(c['id']) and a['id']==c['id'] and a['target']==capture.TARGET and a['endpoint']==capture.ENDPOINT,'native587_identity')
    capture.external(a['helper'],capture.TTR/'.local-work')
    q.require(a['expectedAppID']=='example.ttr.navigation.consumer' and len(a['sourceRevision'])==40,'native587_source')
    enrollment=Path(a['enrollment']);output=Path(a['output']);local=capture.TTR/'.local-work/native587'
    q.require(enrollment.is_absolute() and enrollment.resolve()==enrollment and enrollment.is_relative_to(local) and not enrollment.exists(),'native587_enrollment')
    q.require(output.is_absolute() and output.resolve()==output and output.is_relative_to(local) and not output.exists(),'native587_output')
    q.require(set(n)=={'app','sources','construction','scene','partition','style','noFocus'},'native587_scene_fields')
    constructions=q.load(checked(n['construction']));scene=next((x for x in constructions['scenes'] if x['id']==n['scene']),None)
    q.require(scene is not None and scene['split']==n['partition'] and scene['id']==a['group'],'native587_scene_role')
    q.require(n['partition'] in ('train','validation') and n['style'] in ('opaque','ring') and type(n['noFocus']) is bool,'native587_role')
    q.require(plan['schemaVersion']==2 and plan['case']['split']==n['partition'] and plan['case']['group']==n['scene'] and plan['case']['contentGroup']==n['scene'],'native587_plan_role')
    q.require(plan['source']['appID']==a['expectedAppID'] and plan['source']['sourceRevision']==a['sourceRevision'] and plan['enrollment']==a['enrollment'] and plan['endpoint']==a['endpoint'],'native587_plan_binding')
    q.require(plan['button'] in ('up','down','left','right') and plan['expected'] in ('move','unchanged','no_focus'),'native587_direction')
    app=q.local_path(q.ROOT,n['app']);q.require(app.is_dir() and app.name=='NavigationConsumer.app','native587_app')
    source_paths={checked(r).resolve() for r in n['sources']}
    q.require({(app/'NavigationConsumer').resolve(),(app/'Info.plist').resolve()}<=source_paths,'native587_app_binding')
    producer=checked(c['producer']);source_paths={checked(r).resolve() for r in c['sources']}
    q.require(producer.name=='export-evidence.rb' and producer.resolve() in source_paths and source_paths=={p.resolve() for p in producer.parent.glob('*.rb')},'native587_producer_binding')
    return plan


def build(path):
    c=q.load(path);validate_config(c)
    refs=[pin(path),c['plan'],c['producer'],*c['sources'],c['nativeScene']['construction'],*c['nativeScene']['sources']]
    refs=list({r['path']:r for r in refs}.values())
    return dict(version='research-spec-v2',id=c['id'],task='NATIVE587',owner='Maximum-mini-NUIAK',kind='screen',jobKind='capture',authority='capture',
        hypothesis='Fresh native constructions with observed profile continuity can supply eligible static focus crops.',
        question='Does this fresh native construction supply observed focus, measured bounds, and verified profile continuity?',
        controlledComparison='Freeze construction, source, role and target before capture. Observe actual outcomes. Do not alter settings.',
        decisionRule='Reject missing profile, stale focus, group overlap, uncertain input and incomplete cleanup. Raw export does not admit training.',
        nextActionByOutcome=dict(supported='Run existing SDK intake and production crops before matched training.',contradicted='Preserve the attempt and repair the exact failed boundary without repeating successful capture.'),
        inputs=refs,dependencies=[],evidence=dict(reads=[r['path'] for r in refs],captureReceipt='capture-evidence.json'),
        adapter=dict(type='python-callable',steps=['sdk_profile538.run'],outputAttributes=['sdk_profile538.OUT']),
        capture=dict(target=capture.TARGET,endpoint=capture.ENDPOINT,plan=pin(path),approval='User requests native focus training data. Standing scoped Simulator authority permits this fresh 2-frame pair, 1 directional input, 800 s and 100 MB. No settings changes or physical device.'),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))


def run(out):
    import sdk_profile538 as profile
    spec=q.load(out.parents[2]/'spec.json');c=q.load(checked(spec['capture']['plan']));validate_config(c)
    for ref in spec['inputs']:checked(ref)
    q.save(out/'readiness.json',profile.readiness(c,out))
    from real_app_session554 import alert_check
    q.require(alert_check(capture.TARGET,out=out/'system-alert')['status']=='clear','native587_system_alert')
    a=copy.deepcopy(c['capture']);n=c['nativeScene'];app=q.local_path(q.ROOT,n['app']);bundle=a['expectedAppID']
    enrollment=Path(a['enrollment']);enrollment.parent.mkdir(parents=True,exist_ok=True)
    Path(a['output']).parent.mkdir(parents=True,exist_ok=True)
    key=base64.b64encode(os.urandom(32)).decode();child=None;session=None;result=None;cleanup={};failure=None
    client=profile.Client(a,out)
    try:
        connection=capture.remote(client,'connect');session=connection['operationID'];q.save(out/'remote-session.json',connection)
        if connection['state']!='ready':capture.wait_remote(client,session,'ready')
        installed=subprocess.run(['xcrun','simctl','install',capture.TARGET,str(app)],capture_output=True,text=True,timeout=120)
        q.require(installed.returncode==0,'native587_install')
        args=['--ttr-sdk-enabled=true','--sample-pilot-scene',n['scene'],'--nuiak572-native-corpus','--nuiak572-'+n['style']+'-focus']
        if n['noFocus']:args.append('--nuiak572-no-focus')
        env=dict(os.environ,SIMCTL_CHILD_TTR_SAMPLE_KEY=key,SIMCTL_CHILD_SIMULATOR_UDID=capture.TARGET)
        with (out/'console.log').open('wb') as log:
            child=subprocess.Popen(['xcrun','simctl','launch','--console-pty',capture.TARGET,bundle,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
            identity=metadata.identity(child,log,prefix=b'TTR_SAMPLE_READY ')
            q.require(identity['appID']==bundle and identity['endpoint']==capture.ENDPOINT,'native587_launch_identity')
            fd=os.open(enrollment,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w') as f:json.dump(dict(appID=bundle,processID=identity['processID'],runID=identity['runID'],secretBase64=key),f)
            a['enrollment']=dict(path=str(enrollment),sha256=q.digest(enrollment));client.config=a
            q.require(alert_check(capture.TARGET,out=out/'postlaunch-alert')['status']=='clear','native587_postlaunch_alert')
            profile.wait_sample(client,identity)
            prepared=client.call('configuration','inspect','--simulator-udid',capture.TARGET,'--session',session,'--profile','hcf')
            q.save(out/'prepared.json',profile.wait_configuration(client,session,prepared,True))
            runtime=copy.deepcopy(c);runtime['capture']=a
            result=profile.collect(runtime,session,out)
    except Exception as error:failure=error
    finally:
        if session:
            try:
                status=client.call('configuration','status');record=status.get('record') or {}
                if record.get('session')==session:
                    q.require(record.get('target')==capture.TARGET,'native587_cleanup_target')
                    cleanup['configuration']=profile.wait_configuration(client,session,client.call('configuration','cancel'),False)
                else:q.require(not status.get('inFlight') and not status.get('pending'),'native587_configuration_owner')
            except Exception as error:cleanup['configurationError']=str(error)
            try:
                reply=capture.remote(client,'disconnect',session)
                cleanup['remote']=reply if reply['state']=='closed' else capture.wait_remote(client,session,'closed')
            except Exception as error:cleanup['remoteError']=str(error)
        if child is not None:
            stopped=subprocess.run(['xcrun','simctl','terminate',capture.TARGET,bundle],capture_output=True,text=True,timeout=30)
            cleanup['sampleReturnCode']=stopped.returncode
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        if enrollment.exists():enrollment.unlink()
        try:
            ready=client.call('simulator','readiness','--simulator-udid',capture.TARGET)
            cleanup['targetReady']=ready.get('can_run') is True and bool(ready.get('ownership')) and all(r['state']=='clear' for r in ready['ownership'])
        except Exception as error:cleanup['readinessError']=str(error)
        q.save(out/'cleanup.json',cleanup)
    if failure:raise failure
    q.require(cleanup.get('sampleReturnCode')==0 and cleanup.get('targetReady') is True and not any(k.endswith('Error') for k in cleanup),'native587_cleanup_incomplete')
    profile.publish(c,out,result)
