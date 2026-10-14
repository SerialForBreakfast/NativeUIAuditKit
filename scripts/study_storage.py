"""Check study storage before a bounded producer starts."""
import shutil
from pathlib import Path

STUDY_LIMIT = 250 * 1024**3


def reservation(total, free, retained, next_shard, temporary, quota=STUDY_LIMIT):
    values = (total, free, retained, next_shard, temporary, quota)
    if any(type(v) is not int or v < 0 for v in values) or total == 0 or free > total:
        raise ValueError('invalid_storage_counts')
    reasons = []
    if retained + next_shard > quota:
        reasons.append('study_quota')
    if free - next_shard - temporary < (total + 4)//5:
        reasons.append('volume_free_reserve')
    return dict(ready=not reasons, blockers=reasons, retainedBytes=retained,
        reservedBytes=next_shard+temporary, quotaBytes=quota, minimumFreeFraction=.2)


def check(root, next_shard, temporary):
    root = Path(root)
    volume = Path('/Volumes/training-drive')
    if not volume.is_mount() or not root.is_dir() or not root.resolve().is_relative_to(volume.resolve()):
        raise ValueError('verified_mounted_storage_required')
    retained = 0
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('storage_symlink')
        if path.is_file():
            retained += path.stat().st_size
    usage = shutil.disk_usage(root)
    return reservation(usage.total, usage.free, retained, next_shard, temporary)
