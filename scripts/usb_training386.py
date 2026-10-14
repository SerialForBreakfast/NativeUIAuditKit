"""Keep queue evidence local and bounded training artifacts on the verified USB."""
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import threading
import time
import research_queue as q
import hcf_study371 as study
import hcf_complete_training
import hcf_factor_train376

OUT = None
VOLUME = Path('/Volumes/training-drive')
UUID = 'FD8D8E36-FAAC-4205-87ED-86134C3582B1'
BASE = VOLUME / 'data/NUIAK/queue-artifacts'
LOCAL_LIMIT = 100_000_000
TOTAL_LIMIT = 2 * 1024**3


def verify_volume():
    q.require(VOLUME.is_mount() and VOLUME.resolve() == VOLUME, 'usb_unmounted')
    info = plistlib.loads(subprocess.check_output(['diskutil', 'info', '-plist', str(VOLUME)], timeout=10))
    q.require(info.get('VolumeUUID') == UUID and info.get('FilesystemType') == 'apfs'
              and info.get('Internal') is False and info.get('Writable') is True
              and info.get('MountPoint') == str(VOLUME), 'usb_identity')
    q.require(BASE.resolve() == BASE, 'usb_linked_root')
    usage = shutil.disk_usage(VOLUME)
    q.require(usage.free - TOTAL_LIMIT >= usage.total * .2, 'usb_reserve')
    retained = bounded_bytes(BASE) + bounded_bytes(VOLUME / 'data/NUIAK/HCF371')
    q.require(retained + TOTAL_LIMIT <= 250 * 1024**3, 'usb_study_limit')
    return VOLUME.stat().st_dev


def bounded_bytes(root):
    size = 0
    if not root.exists():
        return 0
    for path in root.rglob('*'):
        q.require(not path.is_symlink(), 'usb_output_symlink')
        try:
            if path.is_file():
                size += path.stat().st_size
        except FileNotFoundError:
            continue
    return size


def check_budget(bulk, local, device):
    q.require(VOLUME.is_mount() and VOLUME.stat().st_dev == device, 'usb_disconnected')
    usage = shutil.disk_usage(VOLUME)
    q.require(usage.free >= usage.total * .2, 'usb_reserve')
    q.require(bounded_bytes(local) <= LOCAL_LIMIT, 'usb_local_limit')
    q.require(bounded_bytes(bulk) + bounded_bytes(local) <= TOTAL_LIMIT, 'usb_total_limit')


def copy_checked(source, destination):
    q.require(source.is_file() and not source.is_symlink() and not destination.exists(), 'usb_copy_input')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    q.require(q.digest(source) == q.digest(destination), 'usb_copy_hash')


def train():
    local = OUT
    cfg = q.load(local / 'usb.json')
    q.require(set(cfg) == {'mode', 'job', 'totalBytes', 'localBytes'}, 'usb_config')
    q.require(cfg['mode'] in ('detector', 'crop') and q.ID.fullmatch(cfg['job']), 'usb_mode')
    q.require(cfg['totalBytes'] == TOTAL_LIMIT and cfg['localBytes'] == LOCAL_LIMIT, 'usb_budget_changed')
    attempt = local.parent
    q.require(attempt.name.isdigit() and attempt.parents[1].name == cfg['job'], 'usb_attempt_identity')
    device = verify_volume()
    bulk = BASE / cfg['job'] / attempt.name / 'out'
    q.require(bulk.resolve() == bulk and not bulk.parent.exists(), 'usb_attempt_collision')
    bulk.mkdir(parents=True)
    for name in ('config.json', 'dependencies.json'):
        copy_checked(local / name, bulk / name)
    q.save(local / 'usb-location.json', dict(version='usb-training-v1', volumeUUID=UUID,
           path=str(bulk), totalBytes=TOTAL_LIMIT, localBytes=LOCAL_LIMIT, backup=False))
    original_progress = study.progress
    def progress(step, completed=None, total=None):
        check_budget(bulk, local, device)
        q.save(attempt / 'progress.json', dict(step=step, completed=completed, total=total,
                                             updatedAt=time.time()), replace=True)
    study.progress = progress
    stop = threading.Event()
    def guard():
        checked = time.monotonic()
        while not stop.wait(2):
            try:
                check_budget(bulk, local, device)
                if time.monotonic() - checked >= 30:
                    q.require(verify_volume() == device, 'usb_identity_changed')
                    checked = time.monotonic()
            except Exception as error:
                q.save(local / 'storage-failure.json', dict(reason=str(error), modelAccepted=False))
                # This is the runner-owned child. Preserve outputs and stop only this process.
                os._exit(76)
    monitor = threading.Thread(target=guard, daemon=True)
    monitor.start()
    try:
        if cfg['mode'] == 'detector':
            hcf_complete_training.OUT = bulk
            hcf_complete_training.detector()
        else:
            hcf_factor_train376.OUT = bulk
            hcf_factor_train376.train()
        check_budget(bulk, local, device)
        names = ['fit.json', 'history.json', 'model.json']
        if cfg['mode'] == 'detector':
            names += ['completion.json', 'detector/weights/best.pt']
        else:
            names += ['final.pt']
        for name in names:
            copy_checked(bulk / name, local / name)
        check_budget(bulk, local, device)
        inventory = []
        for path in sorted(bulk.rglob('*')):
            if path.is_file():
                inventory.append(dict(path=str(path.relative_to(bulk)), bytes=path.stat().st_size,
                                      sha256=q.digest(path)))
        q.save(local / 'usb-manifest.json', dict(version='usb-artifacts-v1', root=str(bulk), volumeUUID=UUID,
               files=inventory, bytes=sum(x['bytes'] for x in inventory), backup=False, modelAccepted=False))
        copy_checked(local / 'usb-manifest.json', bulk.parent / 'manifest.json')
        check_budget(bulk, local, device)
    finally:
        stop.set()
        monitor.join(timeout=3)
        study.progress = original_progress


def compare():
    from hcf_crop_review376 import review
    docs = {}; refs = []
    for dependency in q.load(OUT / 'dependencies.json'):
        ref, = dependency['outputs']; path = q.local_path(q.ROOT, ref['path'])
        q.require(q.digest(path) == ref['sha256'], 'comparison_changed')
        key = dependency['job'].removesuffix('-move387')
        q.require(key not in docs, 'comparison_duplicate_job')
        docs[key] = q.load(path); refs.append(ref)
    control = docs['hcf376-hcf-repeated-evaluate-v1-usb2']
    reports = {key: review(control, value, {}) for key, value in docs.items()
               if key != 'hcf376-hcf-repeated-evaluate-v1-usb2'}
    q.save(OUT / 'factor-comparison.json', dict(version='hcf-factor-comparison-v1', comparisons=reports,
           modelAccepted=False, finalAuditOpened=False,
           nextAction='Review gains and losses before selecting a repeat seed.',
           limitation='Fixed epochs do not match update counts. Duplicate removal also changes positive loss weighting.'))
    q.save(OUT / 'sources.json', refs)
