"""Receive current evidence and publish bounded coordination preparation."""
import hashlib
import json
import tarfile
from datetime import datetime,timezone,timedelta

import shared_transfer as s
from focus_surface_intake import safe_members
from retained_feedback132 import extract


def write(path,value):
    raw=(json.dumps(value,indent=2)+'\n').encode()
    if path.exists():
        s.require(path.read_bytes()==raw,'local_output_collision')
    else:path.write_bytes(raw)


def run(publish=False):
    s.mounted();base=s.ROOT/'reports/work/COORD-REVIEW-241/artifacts/r15';base.mkdir(parents=True,exist_ok=True)
    reports=[]
    for name in ['joe-big-dog-coord255-install-verified01.json','joe-big-dog-coord254-approved-install-runtime-blocked01.json']:
        rel='joe-big-dog/'+name;source=s.path_under(s.SHARE,rel);doc=s.document(source)
        tx=dict(requestID=doc['id'],sharedPath=rel,bytes=source.stat().st_size,sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        s.copy_verified(source,base/name,tx);reports.append(dict(file=rel,bytes=tx['bytes'],sha256=tx['sha256']))
    failure=s.document(s.SHARE/'joe-big-dog/joe-big-dog-transition249-blocked01.json');offer=failure['artifact']
    local=base/'transition249-failure-evidence01.tar.gz'
    tx=dict(requestID=failure['request_id'],sharedPath=offer['file'],localPath=str(local.relative_to(s.ROOT)),bytes=offer['bytes'],sha256=offer['sha256'])
    s.copy_verified(s.path_under(s.SHARE,offer['file']),local,tx)
    with tarfile.open(local) as archive:
        members,total=safe_members(archive,max_member_bytes=1_048_576)
        s.require(len(members)<=10 and total<=1_048_576 and all(m.isfile() for m in members),'failure_archive_scope')
    transaction=base/'failure-transaction.json';write(transaction,tx)
    if not (base/'failure-extracted').exists():extract(transaction,base/'failure-extracted')
    inventory=s.document(base/'failure-extracted/extraction.json')
    s.require(inventory['archiveSHA256']==offer['sha256'],'extraction_identity')
    for item in inventory['inventory']:
        s.verified(s.path_under(base/'failure-extracted',item['path']),item)
    # Recheck the completed input transaction. Never remove a peer-owned file.
    old=s.document(s.ROOT/'reports/work/TRANSITION-249/artifacts/transfer.json')
    receipt=s.document(s.SHARE/'joe-big-dog/joe-big-dog-transition249-input-receipt01.json')
    s.require(receipt['request_id']=='nuiak-transition249-replication-v1' and receipt['receiver']=='joe-big-dog' and receipt['artifact']==old,'input_receipt')
    s.verified(s.ROOT/'reports/work/TRANSITION-249/artifacts/transition249-inputs-v1.tar.gz',old)
    shared=s.path_under(s.SHARE,old['file'])
    if shared.exists():
        s.verified(shared,old)
        s.require(s.document(s.SHARE/'joe-big-dog/joe-big-dog-transition249-input-receipt01.json')==receipt,'receipt_changed')
        if publish:shared.unlink()
    result=s.document(s.ROOT/'reports/work/TRANSITION-253/artifacts/edges-r3/result.json')
    s.require(len(result['results'])==16,'renderer_report')
    draft=s.ROOT/'reports/coordination/status256.json'
    if not draft.exists():
        now=datetime.now(timezone.utc)
        response=dict(schema_version=1,id='nuiak-status256-renderer-and-coordination-preparation',
            request_id='tvtestrig-coordination-parallel-prep-20261007-r1',
            **{'from':'NUIAK','to':['TVTestRig','joe-big-dog']},created_at=now.isoformat(),expires_at=(now+timedelta(days=7)).isoformat(),
            state='preparation_ready_live_approval_pending',received_reports=reports,
            artifact_receipts=[dict(receiver_id='nuiak',request_id=failure['request_id'],**offer,state='copied_and_verified',verified_at=now.isoformat())],
            previous_receipts='status254 supplies exact r12-r14 artifact and offer receipts, plus the completed worker model archive receipt. Please reconcile those receipts before asking for them again.',
            cleanup='NUIAK input archive shared copy is absent and its local original verifies. Senders own failure/result/r12-r14 shared copy cleanup after matching all required receipts. Do not delete status history.',
            installation='Big Dog coord255 reports installation verified, no database cluster, no listener, and no live service. This supersedes its earlier installation blocker.',
            ttr_next='Supply the exact r15 source revision through Git, actual package manifest and lockfile, and migration hashes. No binary or build request. Source delivery must not wait for a live database.',
            big_dog_next='Prepare the existing 10-job loopback test against the exact source when available. Reconcile single-root paths, explicit PostgreSQL plugin, installed versions, migrations, owned processes, and cleanup. Do not launch yet.',
            consumer_cases='Reuse the 10 metadata inputs from coord-deploy-r12 and the 10 NUIAK consumer cases. Preserve role, ancestry, current grant, uncertain-delivery, and multi-receiver receipt checks.',
            approval_needed='Maintainer approval is still needed for project-local database creation and loopback listeners on Big Dog: 10 synthetic metadata jobs, at most 2 workers, 30 min, 32 MiB outputs, no model tokens, no providers, no device operations, no autostart. Exact source/configuration required first.',
            later_scope='Cross-host TLS identities, private binds, independent backup and provider conversation authority remain separate. Do not use a PIN as the only worker identity.',
            renderer='16 retained pairs: checked interior error 0.7430; border error 6.0146; exterior error improves 10.0939 to 7.2755. A separate 8-pair artwork check exposes size-dependent growth. Size-based growth improves one artwork group from 15.80 to 5.14, but another remains near 11.3. No training admission or promotion.',
            fixture_followup='No remote capture requested. NUIAK first checks local retained artwork, alpha silhouettes and clean backgrounds. Keep TRANSITION252 coverage proposal separate; do not produce more copies of these same layouts.',
            evidence=['reports/work/COORD-REVIEW-241/preparation-r15.md','reports/work/TRANSITION-253/edges-r3.md'],
            outcomes=dict(software='renderer_checks_pass_live_coordination_not_run',data='development_only',integration='loopback_not_authorized',model='unchanged'))
        write(draft,response)
    if publish:
        response=s.document(draft);rel='nuiak/requests/'+response['id']+'.json'
        tx=dict(requestID=response['id'],sharedPath=rel,bytes=draft.stat().st_size,sha256=hashlib.sha256(draft.read_bytes()).hexdigest())
        s.copy_verified(draft,s.path_under(s.SHARE,rel),tx)
        s.require(s.document(s.SHARE/rel)==response,'readback')
        print('Published and read back:',rel)
    else:print('Evidence received and checked. Local response prepared; not published.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true')
    run(parser.parse_args().publish)
