"""Publish the named input package and fixed worker assignment."""
from datetime import datetime,timezone,timedelta
import shutil
import shared_transfer as s
import transition249_package as package


def run():
    s.mounted();base=package.OUT;artifact=package.t.h.read(base/'transfer.json')
    now=datetime.now(timezone.utc)
    request=dict(schema_version=1,id='nuiak-transition249-replication-v1',
        request_id='nuiak-transition249-replication-v1',**{'from':'NUIAK','to':'joe-big-dog/NUIAK'},
        created_at=now.isoformat(),expires_at=(now+timedelta(days=7)).isoformat(),state='requested',
        priority='Low-priority sequential CPU batch. Preserve existing GPU assignments.',
        message='Run the 3 fixed comparisons with the supplied entrypoint. No TTR runtime or new coordination service is required.',
        artifact=artifact,
        extraction='Verify archive bytes/hash first. Extract exactly 20 flat regular files into a new project-local directory. Reject links, paths, duplicates, and more than 2929020842 expanded bytes.',
        entrypoint='PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 <resident-python> transition249_worker.py <absolute-package-dir> <new-output-dir> --execute',
        preflight='Run the same entrypoint without --execute first. It verifies all 19 members and DTM054 score parity without fitting.',
        runs=['DTM068: group weights, seed 43','DTM069: group weights, seed 44','DTM070: matched class weights, seed 42'],
        settings='CPU only; 2 threads; 120 epochs each; Adam 0.0001; batch 16; final epoch only. Reuse the exact packaged trainer.',
        roles='training.npy is the only fitting input. Native evaluation contains protected cases. Do not change membership or fit evaluation arrays.',
        limits='3 fits; at most 90 min total; 2 GiB peak process RAM; 2 GiB result outputs; at least 6 GiB free before extraction. If memory exceeds the limit, stop and report. Do not silently change settings.',
        stop='Stop on changed inputs, baseline mismatch, missing dependencies, collision, nonfinite training, or resource excess. Preserve partial evidence. Do not retry automatically.',
        boundaries='No downloads, installations, capture, service operations, export, promotion, new models, or extra sweep.',
        return_contract='Return complete.json, all 3 checkpoints and result.json files, runtime versions, command exit codes, peak memory, and source/manifest hashes. Package with exact size/hash. Retain originals.',
        coordination='Record input publication observation, pickup/start, finish, result publication, and sender cleanup separately. Local simulated timings are not cross-device timings.',
        receipts='NUIAK is the sole intended receiver of results. Big Dog is the sole intended receiver of this input. Return an exact input receipt before NUIAK cleanup.',
        acceptance='NUIAK verifies returned checkpoint predictions locally. No replacement or navigation permission follows from completion.',
        peer_review='NUIAK reads COORD251: 10 local cases pass by worker report. Production wire integration and independent cross-device timing remain separate.')
    local=base.parent/'worker-request.json'
    if not local.exists():package.t.h.write(local,request)
    for path,relative in [(base/'transition249-inputs-v1.tar.gz',artifact['file']),
                          (local,'nuiak/requests/nuiak-transition249-replication-v1.json')]:
        tx=dict(requestID=request['id'],sharedPath=relative,bytes=path.stat().st_size,sha256=package.worker.digest(path))
        require_space=tx['bytes']+1024**3
        s.require(shutil.disk_usage(s.SHARE).free>require_space,'share_capacity')
        dest=s.path_under(s.SHARE,relative);print(relative,s.copy_verified(path,dest,tx),flush=True);s.verified(dest,tx)


if __name__=='__main__':run()
