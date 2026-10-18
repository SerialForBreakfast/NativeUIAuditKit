"""Verify the owned HCF recovery before releasing the native capture guard."""
import os
import shutil
import signal
import research_queue as q
import qualify_hcf362 as h
import native343 as n
from generation352 import MARKER
from focus_batch_harness import lock
from research_campaign340 import pin

OUT=None


def valid_result(report):
    q.require(report.get('complete') is True, 'recovery_incomplete')
    state=report.get('route',{}).get('hcf',{})
    q.require(state.get('status')=='completed' and state.get('desiredVerified') is True, 'profile_unverified')
    q.require(state.get('original')==state.get('observed')=='standard' and
        state.get('restoration')=='verified', 'standard_restoration_unverified')
    q.require(report.get('disconnect',{}).get('state')=='closed', 'session_not_closed')
    ready=report.get('postflight',{})
    q.require(ready.get('can_run') and ready.get('ownership') and
        all(r['state']=='clear' for r in ready['ownership']), 'ownership_not_clear')


def run():
    spec=q.load(OUT.parent.parent.parent/'spec.json');contract=spec['capture']
    ref=contract['plan'];q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'plan_changed')
    plan=q.load(q.ROOT/ref['path'])
    if plan.get('version') == 'native-capture-recovery-v2':
        import native_capture_recovery
        native_capture_recovery.OUT = OUT
        return native_capture_recovery.run()
    q.require(plan['version']=='hcf-recovery367-v1' and contract['target']==n.TARGET and
        contract['endpoint']=='http://127.0.0.1:8080','recovery_scope')
    q.require(q.digest(h.CLI.resolve())==plan['helperSHA256'],'helper_changed')
    q.require(q.digest(MARKER)==plan['markerSHA256'],'marker_changed')
    marker=q.load(MARKER)
    q.require(marker['job']==plan['failedJob'],'recovery_owner')
    try:os.kill(marker['pid'],0)
    except ProcessLookupError:pass
    else:raise ValueError('previous_process_still_exists')
    q.require(shutil.disk_usage(q.ROOT).free>3*(1<<30),'recovery_storage')
    q.save(OUT/'previous-marker.json',marker)
    before=h.d.Fixture(contract['endpoint']).snapshot()
    q.require(before['device']['simulator_udid']==n.TARGET,'wrong_fixture')
    q.save(OUT/'fixture-before.json',before)
    previous=signal.getsignal(signal.SIGTERM)
    def stop(signum,frame):
        signal.signal(signal.SIGTERM,signal.SIG_IGN)
        raise RuntimeError('recovery_cancelled')
    signal.signal(signal.SIGTERM,stop)
    try:
        report=h.run(OUT/'qualification', normalize=plan.get('normalizeSettings',False))
        valid_result(report)
        with lock():
            fixture=h.d.Fixture(contract['endpoint'])
            after=n.settle(fixture,before,before['scene']['focused_element_id'])
            q.save(OUT/'fixture-after.json',after)
            q.require(q.digest(MARKER)==plan['markerSHA256'],'marker_changed_during_recovery')
            q.save(OUT/'recovery.json',dict(complete=True,previousMarker=pin(OUT/'previous-marker.json'),
                qualification=pin(OUT/'qualification/qualification.json'),fixture=pin(OUT/'fixture-after.json'),
                target=n.TARGET,trainingEligible=False))
            # Preserve the exact failed marker before removing the owned guard.
            MARKER.unlink()
            q.save(OUT/'qualification.json',dict(version='research-condition-v1',outcome='supported',
                reason='Standard restoration, closed session, clear ownership, and original Fixture state pass.',
                evidence=[pin(OUT/'recovery.json')]))
    finally:
        signal.signal(signal.SIGTERM,previous)


def register():
    folder=q.ROOT/'Research/ResearchSpecs/HCF367';q.require(not folder.exists(),'revision_exists');folder.mkdir()
    ident='hcf367-recover'
    plan=dict(version='hcf-recovery367-v1',failedJob=q.load(MARKER)['job'],markerSHA256=q.digest(MARKER),
        helperSHA256=q.digest(h.CLI.resolve()),target=n.TARGET)
    pp=folder/'recovery-plan.json';q.save(pp,plan)
    spec=dict(version=q.SPEC_VERSION,id=ident,task='HCF367',owner='research-host-NUIAK',kind='screen',authority='capture',
        hypothesis='Can current local TTR verify HCF recovery and restore the original Fixture state?',
        decisionRule='Remove only the exact owned guard after verified Standard restoration and closed ownership. Preserve it on failure.',
        inputs=[pin(q.ROOT/'scripts'/v) for v in ('hcf_recovery367.py','qualify_hcf362.py','native343.py','generation352.py')],
        capture=dict(target=n.TARGET,endpoint='http://127.0.0.1:8080',plan=pin(pp),
            approval='The maintainer explicitly approves queued local HCF recovery and fresh capture. Do not operate physical devices.'),
        adapter=dict(type='python-callable',steps=['hcf_recovery367.run'],outputAttributes=['hcf_recovery367.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    sp=folder/(ident+'.json');q.save(sp,spec);q.submit(sp)
    q.save(folder/'additions.json',[dict(id=ident,sha256=q.text_digest(spec))])
    print(ident)


if __name__=='__main__':register()
