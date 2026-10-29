"""Own a bounded test-only profile pair through the existing TTR producer."""
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
import sdk_capture527 as capture
from sdk_episode529 import episode
OUT = None


def validate_config(c):
    q.require(set(c) == {'version','id','capture','plan','producer','sources'}, 'profile538_fields')
    q.require(c['version'] == 'sdk-profile-pair-v1' and q.ID.fullmatch(c['id']), 'profile538_identity')
    capture.validate_config(c['capture'])
    q.require(c['id'] == c['capture']['id'], 'profile538_capture_identity')
    plan = q.load(checked(c['plan']))
    q.require(plan.get('case', {}).get('split') == 'test' and plan['case'].get('platform') == 'tvOS', 'profile538_test_only')
    q.require(plan['source']['appID'] == c['capture']['expectedAppID'] and
              plan['endpoint'] == c['capture']['endpoint'] and
              plan['enrollment'] == c['capture']['enrollment']['path'], 'profile538_plan_identity')
    q.require(plan.get('button') in ('up','down','left','right') and
              plan.get('expected') in ('move','unchanged','arrival','departure','no_focus'), 'profile538_input')
    producer = checked(c['producer'])
    q.require(producer.name == 'export-evidence.rb' and c['sources'], 'profile538_producer')
    actual = {p.resolve() for p in producer.parent.glob('*.rb')}
    pinned = {checked(ref).resolve() for ref in c['sources']}
    q.require(actual == pinned and producer.resolve() in pinned, 'profile538_source_closure')
    return plan


class Client(capture.Client):
    def call(self, *args):
        self.sequence += 1
        helper = capture.external(self.config['helper'], capture.TTR/'.local-work')
        env = dict(os.environ); env.pop('TVTESTRIG_PROJECT', None)
        argv = [str(helper), '--project', str(capture.TTR), '--json', *args]
        r = subprocess.run(argv, capture_output=True, text=True, timeout=45, env=env)
        q.require(len(r.stdout.encode()) + len(r.stderr.encode()) <= 8*1048576, 'profile538_reply_size')
        q.save(self.out/f'{self.prefix}-{self.sequence:03}.json', dict(arguments=list(args), returnCode=r.returncode, stdout=r.stdout, stderr=r.stderr))
        d = json.loads(r.stdout)
        q.require(r.returncode == 0 and d.get('success') is True, 'profile538_call_failed:'+str(d.get('error')))
        return next(iter(d['data'].values()))['_0']


def readiness(c, out):
    validate_config(c)
    r = Client(c['capture'], out, 'readiness').call('simulator','readiness','--simulator-udid',c['capture']['target'])
    q.require(r.get('can_run') is True and r.get('ownership') and all(x['state']=='clear' for x in r['ownership']), 'profile538_busy')
    status = Client(c['capture'], out, 'configuration-preflight').call('configuration','status')
    q.require(not status.get('inFlight') and not status.get('pending'), 'profile538_configuration_busy')
    return r


def build(path):
    c = q.load(path); validate_config(c)
    s = dict(version='research-spec-v2',id=c['id'],task='PIPELINE538',owner='Maximum-mini-NUIAK',
             kind='screen',jobKind='capture',authority='capture',dependencies=[],
             capture=dict(target=c['capture']['target'],endpoint=c['capture']['endpoint'],plan=pin(path),approval='bounded producer qualification'),
             limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
             evidence=dict(reads=[],captureReceipt='capture-evidence.json'),
             nextActionByOutcome=dict(supported='Release review-only episode and crop consumers.',contradicted='Preserve evidence and diagnose the exact failed boundary.'))
    s.update(id=c['id'], task='PIPELINE538', question='Can the pinned collector supply a native focus pair with observed profile continuity and owned cleanup?',
             hypothesis='One project-scoped queue job joins session entry, paired collection, and verified sample return.',
             controlledComparison='Pinned test-only source and construction. Two frames and one directional input. No settings mutation.',
             decisionRule='Release review consumers only after pair integrity and cleanup pass. Preserve failures; never infer a training role.')
    s['capture']['plan'] = pin(path)
    s['capture']['approval'] = 'Maintainer approves bounded capture-to-comparison qualification on the intended Simulator; 2 frames, 1 directional input, 800 s and 100 MB. No settings changes.'
    s['adapter'] = dict(type='python-callable',steps=['sdk_profile538.run'],outputAttributes=['sdk_profile538.OUT'])
    s['inputs'] = [pin(path),c['plan'],c['producer'],*c['sources']]
    s['evidence']['reads'] = list(dict.fromkeys(ref['path'] for ref in s['inputs']))
    return s


def validate_spec(spec):
    c = q.load(checked(spec['capture']['plan'])); validate_config(c)
    q.require(spec['id']==c['id'] and spec['capture']['target']==c['capture']['target'] and
              spec['capture']['endpoint']==c['capture']['endpoint'], 'profile538_spec_identity')
    q.require(spec['limits']['timeoutSeconds']<=800 and spec['limits']['maxOutputBytes']<=100000000 and spec['limits']['maxAttempts']==1, 'profile538_budget')


def wait_configuration(client, session, first, prepared):
    result = first
    for _ in range(120):
        record = result.get('record') or {}
        if record:
            q.require(record.get('session') == session and record.get('target') == client.config['target'], 'profile538_configuration_identity')
        if not result.get('inFlight'):
            q.require(not result.get('pending'), 'profile538_restore_debt')
            if prepared:q.require(record.get('phase') == 'prepared', 'profile538_setup_failed:'+str(record.get('phase')))
            else:q.require(record.get('phase') not in ('restore_failed','blocked'), 'profile538_cleanup_failed')
            return result
        time.sleep(.25)
        result = client.call('configuration','status')
    raise ValueError('profile538_configuration_timeout')


def collect(c, session, out):
    dest = Path(c['capture']['output']); q.require(not dest.exists(), 'profile538_output_exists')
    argv = ['/usr/bin/ruby',str(checked(c['producer'])),'collect-focus-pair',c['capture']['helper']['path'],
            str(capture.TTR),c['capture']['target'],session,str(checked(c['plan'])),str(dest)]
    with (out/'producer.stdout').open('w') as stdout, (out/'producer.stderr').open('w') as stderr:
        process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, start_new_session=True)
        began = time.monotonic()
        try:
            while process.poll() is None:
                q.require(time.monotonic()-began < 550, 'profile538_collection_timeout')
                size=sum(p.stat().st_size for p in dest.rglob('*') if p.is_file()) if dest.exists() else 0
                q.require(size < 45000000, 'profile538_collection_bytes')
                time.sleep(.2)
            q.require(process.returncode==0, 'profile538_producer_failed')
        finally:
            if process.poll() is None:
                import signal
                os.killpg(process.pid, signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid, signal.SIGKILL);process.wait()
    verify=subprocess.run(['/usr/bin/ruby',str(checked(c['producer'])),'verify-action-pair',str(dest/'pair')],capture_output=True,text=True,timeout=30)
    q.save(out/'pair-verification.json',dict(returnCode=verify.returncode,stdout=verify.stdout,stderr=verify.stderr))
    q.require(verify.returncode==0,'profile538_pair_verification')
    result=q.load(dest/'result.json')
    q.require(result.get('state')=='completed_review_only', 'profile538_collection_failed:'+str(result.get('failure')))
    return result


def wait_sample(client, identity):
    """Wait for observed foreground readiness without sending input or capture."""
    for attempt in range(20):
        try:
            capture.wait_observed(client, identity, None)
            return
        except ValueError as error:
            if str(error) not in ('sdk_sequence_observation_unknown', 'sdk_sequence_sample_not_ready', 'sdk_sequence_focus_stale'):
                raise
            if attempt == 19:
                raise
            time.sleep(.25)


def restore_sample(client):
    app=client.config['expectedAppID']
    r=subprocess.run(['/usr/bin/xcrun','simctl','launch',client.config['target'],app],capture_output=True,text=True,timeout=30)
    q.save(client.out/'sample-return.json',dict(returnCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    q.require(r.returncode==0 and r.stdout.startswith(app+': '), 'profile538_sample_return_failed')
    identity=q.load(capture.external(client.config['enrollment'],capture.TTR/'.local-work'))
    wait_sample(client,identity)
    return dict(appID=app,authenticated=True,nativeReady=True,exactOriginalFocusRestored='not_asserted')


def acquire(c, out):
    client=Client(c['capture'],out); session=None; setup=False; failure=None; result=None; cleanup={}
    identity=q.load(capture.external(c['capture']['enrollment'],capture.TTR/'.local-work'))
    wait_sample(client,identity)
    try:
        q.save(out/'connect-intent.json',dict(target=c['capture']['target'],automaticRetry=False))
        receipt=capture.remote(client,'connect');session=receipt['operationID'];q.save(out/'remote-session.json',receipt)
        if receipt['state']!='ready':capture.wait_remote(client,session,'ready')
        setup=True
        first=client.call('configuration','inspect','--simulator-udid',c['capture']['target'],'--session',session,'--profile','hcf')
        q.save(out/'prepared.json',wait_configuration(client,session,first,True))
        result=collect(c,session,out)
    except Exception as e:
        failure=e
    finally:
        if session:
            if setup:
                try:
                    state=client.call('configuration','status');record=state.get('record') or {}
                    q.require(record.get('session')==session and record.get('target')==c['capture']['target'], 'profile538_cleanup_owner_unknown')
                    cleanup['configuration']=wait_configuration(client,session,client.call('configuration','cancel'),False)
                except Exception as e:cleanup['configurationError']=str(e)
            try:
                state=capture.remote(client,'disconnect',session)
                cleanup['remote']=state if state['state']=='closed' else capture.wait_remote(client,session,'closed')
            except Exception as e:cleanup['remoteError']=str(e)
            if not any(k.endswith('Error') for k in cleanup):
                try:cleanup['sample']=restore_sample(client)
                except Exception as e:cleanup['sampleError']=str(e)
        q.save(out/'cleanup.json',cleanup)
    if failure:raise failure
    q.require(session and not any(k.endswith('Error') for k in cleanup) and 'sample' in cleanup, 'profile538_cleanup_incomplete')
    return result


def publish(c, out, result):
    dest=Path(c['capture']['output']);frames=[]
    # Preserve the complete producer package and all original references.
    q.require(not any(p.is_symlink() for p in dest.rglob('*')), 'profile538_output_symlink')
    q.require(sum(p.stat().st_size for p in dest.rglob('*') if p.is_file())<45000000,'profile538_output_bytes')
    shutil.copytree(dest,out/'producer')
    for side in ('before','after'):
        folder=out/'producer'/side
        frames.append(dict(image=pin(folder/'frame.png'),evidence=pin(folder/'evidence.json')))
    row=dict(id=c['id'],scenario='native-profile-pair',group=c['capture']['group'],role='review_only',frames=frames)
    reviewed=episode(row)
    q.save(out/'episode-request.json',dict(version='sdk-episode-request-v1',id=c['id'],episodes=[row]))
    q.save(out/'benchmark_summary.json',dict(version='sdk-profile-pair-result-v1',producer=result,episode=reviewed,
           trainingEligible=False,modelAccepted=False,cleanupVerified=True,exactOriginalFocusRestored=False))
    q.save(out/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=[dict(path=str(Path(f['image']['path']).resolve().relative_to(out.resolve())),sha256=f['image']['sha256']) for f in frames],inputsDispatched=1))
    q.save(out/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(out)),sha256=q.digest(p)) for p in out.rglob('*') if p.is_file()]))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');validate_spec(spec);c=q.load(checked(spec['capture']['plan']))
    q.save(OUT/'readiness.json',readiness(c,OUT))
    for ref in spec['inputs']:checked(ref)
    dest=Path(c['capture']['output']);q.require(not dest.exists(),'profile538_output_exists')
    q.require(shutil.disk_usage(dest.parent).free>200000000,'profile538_storage')
    result=acquire(c,OUT);publish(c,OUT,result)


def build_review(producer_spec, tool):
    checked(tool)
    return dict(version='research-spec-v2',id=producer_spec['id']+'-review',task='PIPELINE538',owner='Maximum-mini-NUIAK',
        kind='screen',jobKind='artifact',authority='diagnostic',
        dependencies=[dict(job=producer_spec['id'],specSHA256=q.text_digest(producer_spec),outputs=['episode-request.json','cleanup.json'])],
        inputs=[tool],adapter=dict(type='python-callable',steps=['sdk_profile538.run_review'],outputAttributes=['sdk_profile538.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(reads=[tool['path']],artifactReceipt='artifact-receipt.json'),
        question='Does the completed native pair provide aligned static crops and a verified temporal episode?',
        hypothesis='The same consumer prepares observed focus crops without requiring a detector taxonomy or a training role.',
        controlledComparison='Reuse exact producer endpoints and native observations. Preserve test ancestry and review-only labels.',
        decisionRule='Report static and temporal eligibility separately. No model acceptance or training admission.',
        nextActionByOutcome=dict(supported='Use observed failures to select matched frozen focus scoring.',contradicted='Report the exact missing evidence without rerunning capture.'))


def run_review():
    from sdk_episode529 import intake
    from sdk_episode_crops530 import normalize
    from sdk_training513 import prepare_crops
    spec=q.load(OUT.parents[2]/'spec.json');dependencies=q.dependency_inputs(spec,OUT.parents[4])
    refs={Path(r['path']).name:r for d in dependencies for r in d['outputs']}
    cleanup=q.load(checked(refs['cleanup.json']))
    q.require(cleanup.get('sample',{}).get('nativeReady') is True and not any(k.endswith('Error') for k in cleanup),'profile538_review_cleanup')
    request=dict(version='sdk-episode-crops-v1',id=spec['id'],episodes=refs['episode-request.json'],tool=spec['inputs'][0])
    data=normalize(request)
    q.save(OUT/'labels.json',data)
    crops=prepare_crops(data,OUT/'crops',request['tool']) if data['frames'] else dict(rows=[],trainingEligible=False)
    q.save(OUT/'crops.json',crops)
    summary=intake(q.load(checked(refs['episode-request.json'])))
    summary.update(cropCount=len(crops['rows']),trainingEligible=False,modelAccepted=False)
    q.save(OUT/'benchmark_summary.json',summary)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in OUT.rglob('*') if p.is_file()]))
