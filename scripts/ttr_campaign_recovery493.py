"""Resume one approved retained campaign. Never replay a failed case."""
import signal
import time
import research_queue as q
from experiment_templates import checked
from ttr_campaign_queue493 import Client, TARGET, readiness, fixture_binding

OUT = None
CAMPAIGN = 'A22DBCB6-F160-4EC1-8FD0-50FA7D801101'
MANIFEST = '74030d1d70ddc6862f9d62a0bdecf0d813b334a31b63b8f34b2f1489d6050d62'


def validate_config(config):
    q.require(config.get('version') in ('campaign-recovery493-v1','campaign-recovery493-v2','campaign-recovery493-v3'), 'recovery_version')
    q.require(config.get('campaign') == CAMPAIGN and config.get('manifestSHA256') == MANIFEST, 'recovery_campaign')
    before=config['before']
    q.require(before['campaign_id']==CAMPAIGN and before['manifest_sha256']==MANIFEST, 'recovery_reference')
    successor=config['version']=='campaign-recovery493-v3'
    q.require(before['state']==('completed_with_failures' if successor else 'cleanup_unknown') and before['completed_cases']==0 and
              before['failed_cases']==(2 if successor else 1) and before['unattempted_cases']==(6 if successor else 7), 'recovery_membership')
    if successor:
        q.require(len(before['cases'])==8 and len({r['case_id'] for r in before['cases']})==8 and
                  sum(r['state']=='failed' for r in before['cases'])==2 and
                  sum(r['state']=='unattempted' for r in before['cases'])==6 and
                  all(r['duration_seconds']==0 for r in before['cases'] if r['state']=='unattempted'),
                  'recovery_case_membership')
        q.require(config.get('callerExport') and config.get('fixtureBinaries'), 'recovery_launch_contract')
    q.require(0 < before['budget_remaining_seconds'] <= 519 and
              0 < before['budget_remaining_bytes'] <= 1073741824, 'recovery_budget')


def retained_restart(config):
    """Verify exported proof. TTR still decides whether its retained guard can clear."""
    manifest_path=checked(config['retainedRestart'])
    manifest=q.load(manifest_path)
    q.require(manifest.get('operation','').lower()=='b838426c-3f16-40bc-8064-f73b584c8d00' and
              manifest.get('reportAvailable') is True, 'recovery_export_identity')
    members=manifest.get('members',[])
    expected={'report.json','prior-recovery-marker.json','shutdown-verification.stdout','boot.stdout','shutdown.stdout'}
    q.require(len(members)==5 and {m['name'] for m in members}==expected, 'recovery_export_members')
    for member in members:
        path=manifest_path.parent/member['name']
        if member['name']=='prior-recovery-marker.json':
            q.require(member['state']=='absent' and not path.exists(), 'recovery_export_marker')
        else:
            q.require(member['state']=='collected' and not path.is_symlink() and path.is_file() and
                      path.stat().st_size==member['size'] and q.digest(path)==member['sha256'], 'recovery_export_bytes')
    report=q.load(manifest_path.parent/'report.json')
    q.require(not report.get('cleanup_unknown_all',True) and report.get('cleanup_unknown_targets')==[] and
              report.get('ownership')==[] and
              any(c.get('code')=='restart_completed' and c.get('state')=='ready' for c in report.get('checks',[])) and
              len([d for d in report.get('inventory',[]) if d.get('id')==TARGET and d.get('state')=='Booted'])==1,
              'recovery_export_proof')
    return report


def execute(config, client, output, clock=time.monotonic, sleep=time.sleep):
    validate_config(config)
    successor=config['version']=='campaign-recovery493-v3'
    retained=retained_restart(config) if config['version']!='campaign-recovery493-v1' else None
    if successor:
        binding=fixture_binding(config)
        q.save(output/'fixture-before.json',binding)
        scene=client.call('fixture','scene','--fixture-url','http://127.0.0.1:8080')
        q.require(scene.get('isSettled') is True and scene.get('elementCount',0)>0,
                  'recovery_fixture_not_settled')
    before=client.call('campaign','status',CAMPAIGN)
    q.require(before == config['before'], 'recovery_checkpoint_changed')
    readiness(client)
    status=client.call('status')
    q.require(status.get('commandActive') is False and status.get('observationActive') is False and
              status.get('queuedCommandCount') == 0, 'recovery_coordinator_occupied')
    marker=q.ROOT/('.build/campaign493-retained-six-resume-dispatch.json' if successor else
                   '.build/campaign493-retained-resume-dispatch.json' if retained is not None else
                   '.build/campaign493-recovery-dispatch.json')
    q.require(not marker.exists(), 'recovery_dispatch_already_attempted')
    marker.parent.mkdir(parents=True, exist_ok=True)
    q.save(marker,dict(campaign=CAMPAIGN,output=str(output),before=before))
    # One supported restart establishes termination evidence. Never retry a lost reply.
    restart=retained if retained is not None else client.call('simulator','restart','--simulator-udid',TARGET,'--confirm-exclusive',timeout=180)
    q.save(output/'restart.json',restart)
    q.require(retained is not None or restart.get('can_run') is True, 'recovery_restart_not_ready')
    readiness(client)
    prior=signal.getsignal(signal.SIGTERM);active=True
    def stop(*_): raise RuntimeError('recovery_cancelled_by_queue')
    signal.signal(signal.SIGTERM,stop)
    started=clock()
    try:
        client.call('campaign','resume',CAMPAIGN,'--expect-manifest-sha',MANIFEST)
        while True:
            report=client.call('campaign','status',CAMPAIGN)
            q.save(output/'campaign-status.json',report,replace=True)
            if report['state'] not in ('running','cancelling'): break
            q.require(clock()-started < 540, 'recovery_remaining_time_exhausted')
            sleep(5)
        active=False
        q.require(report['state'] in ('completed','completed_with_failures','halted_budget_exhausted'), 'recovery_cleanup_unknown')
        old={r['case_id']:r for r in before['cases']};new={r['case_id']:r for r in report['cases']}
        q.require(set(old)==set(new) and report['manifest_sha256']==MANIFEST, 'recovery_membership_changed')
        q.require(all(r['state'] in ('completed','failed','cancelled','unattempted') for r in new.values()),
                  'recovery_case_cleanup_unknown')
        for key,row in old.items():
            if row['state']=='failed':
                q.require(new[key]==row, 'recovery_failed_case_replayed')
            if row['state']=='cleanup_unknown':
                q.require(new[key]['state']=='failed' and new[key]['duration_seconds']==row['duration_seconds'] and
                          new[key].get('failure')==row.get('failure'), 'recovery_failed_case_replayed')
        q.require(report['elapsed_seconds'] <= 600 and report['retained_bytes'] <= 1073741824, 'recovery_cumulative_budget')
        post=readiness(client)
        export=client.call('campaign','export',CAMPAIGN,'--output-dir',str(output/'corpus'),timeout=100)
        q.require(export.get('export_path')==str(output/'corpus'), 'recovery_export_path')
        images=[]
        from PIL import Image
        for path in sorted((output/'corpus').rglob('*.png')):
            with Image.open(path) as im: im.verify()
            images.append(dict(path=str(path.relative_to(output)),sha256=q.digest(path)))
        q.require(images, 'recovery_no_retained_images')
        q.save(output/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=images,cleanup=True))
        q.save(output/'recovery-complete.json',dict(version='campaign-recovery493-result-v1',campaign=CAMPAIGN,
            cleanup=True,failedEvidencePreserved=True,report=report,postflight=post,modelAccepted=False,trainingEligible=False))
    finally:
        if active:
            try: q.save(output/'cancel.json',client.call('campaign','cancel',CAMPAIGN))
            except Exception as error: q.save(output/'cleanup-error.json',dict(error=str(error)))
        signal.signal(signal.SIGTERM,prior)


def run():
    spec=q.load(OUT.parents[2]/'spec.json');config=q.load(checked(spec['capture']['plan']))
    execute(config,Client(config,OUT),OUT)
