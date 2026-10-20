"""Share identical retained PNG bytes without removing evidence paths or journals."""
import fcntl
import os
from pathlib import Path
import shutil
import uuid

import research_queue as q

# Twelve approved captures. Each producer is bounded at 1 GiB.
# The measured archive after the first capture is 192,737,077 bytes.
# Reserve that entire measured archive again for each remaining capture.
MAX_UNIQUE_INPUT = 13 * 1024**3
MAX_ARCHIVE = 13 * 192_737_077


def after_job(output):
    """Opt-in retention runs only after the caller verifies cleanup."""
    spec = q.load(output.parents[2]/'spec.json')
    if 'retention' not in spec:
        return
    q.require(spec['retention'] == 'verified-png-hardlinks-v1', 'retention_contract')
    folder = output/'retention'
    folder.mkdir()
    local_compact(folder)


def compact(files, archive, receipt):
    """Caller holds target ownership and the producer lock. All inputs are immutable PNGs."""
    q.require(not receipt.exists(), 'compaction_receipt_exists')
    q.require(archive.resolve() == archive, 'compaction_archive_link')
    archive.mkdir(parents=True, exist_ok=True)
    files = sorted(set(files))
    q.require(0 < len(files) <= 10000, 'compaction_count')
    rows = []
    for path in files:
        q.require(path.suffix == '.png' and path.resolve() == path and path.is_file(), 'compaction_input')
        stat = path.stat()
        rows.append(dict(path=str(path), sha256=q.digest(path), bytes=stat.st_size,
                         device=stat.st_dev, inode=stat.st_ino))
    inodes = {(r['device'], r['inode']): r['bytes'] for r in rows}
    q.require(sum(inodes.values()) <= MAX_UNIQUE_INPUT, 'compaction_input_budget')
    payloads = {r['sha256']: r for r in rows}
    required = sum(r['bytes'] for h, r in payloads.items() if not (archive/(h+'.png')).exists())
    usage = shutil.disk_usage(archive)
    q.require(usage.free - required >= usage.total*.2, 'compaction_space')
    q.require(sum(p.stat().st_size for p in archive.glob('*.png')) + required <= MAX_ARCHIVE,
              'compaction_archive_budget')
    for digest, row in payloads.items():
        backup = archive/(digest+'.png')
        if not backup.exists():
            with Path(row['path']).open('rb') as source, backup.open('xb') as target:
                shutil.copyfileobj(source, target); target.flush(); os.fsync(target.fileno())
        q.require(not backup.is_symlink() and q.digest(backup) == digest, 'compaction_backup_changed')
    # Persist restoration information before replacing any duplicate directory entry.
    q.save(receipt.with_suffix('.plan.json'), dict(version=1, archive=str(archive), files=rows))
    canonical = {}; replaced = 0
    for row in rows:
        path = Path(row['path']); digest = row['sha256']
        q.require(path.resolve() == path and q.digest(path) == digest, 'compaction_source_changed')
        key = (row['device'], digest)
        if key not in canonical:
            canonical[key] = path; continue
        original = canonical[key]
        if path.stat().st_ino == original.stat().st_ino: continue
        q.require(q.digest(original) == digest and q.digest(archive/(digest+'.png')) == digest,
                  'compaction_canonical_changed')
        temporary = path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.link')
        try:
            os.link(original, temporary)
            q.require(q.digest(temporary) == digest and q.digest(path) == digest, 'compaction_link_changed')
            os.replace(temporary, path)
            replaced += 1
        finally:
            if temporary.exists(): temporary.unlink()
    q.require(all(Path(r['path']).is_file() and q.digest(Path(r['path'])) == r['sha256'] for r in rows),
              'compaction_verification')
    result = dict(version=1, files=len(rows), uniquePayloads=len(payloads), linksReplaced=replaced,
                  pathsRemoved=0, bytesChanged=0, journalsChanged=False, archive=str(archive),
                  originalLogicalBytes=sum(r['bytes'] for r in rows), uniqueBytes=sum(r['bytes'] for r in payloads.values()),
                  uniqueFileBytes=sum(inodes.values()), archiveBytesRequired=required,
                  maxUniqueInputBytes=MAX_UNIQUE_INPUT, maxArchiveBytes=MAX_ARCHIVE)
    q.save(receipt, result)
    return result


def retained_pngs(project, map_root):
    """Only include map evidence and providers named by its recovery journals."""
    roots = [map_root]
    for journal in sorted(map_root.glob('hcf-*/recovery.json')):
        q.require(journal.resolve() == journal, 'compaction_journal_link')
        document = q.load(journal)
        session = str(uuid.UUID(document['session']))
        q.require(document['state']['status'] in ('completed', 'stopped'), 'compaction_route_active')
        roots.append(project/'Diagnostics/Runtime/SimulatorDiagnostics'/session)
    files = set()
    for root in roots:
        q.require(root.resolve() == root and root.is_relative_to(project), 'compaction_root')
        if root.exists(): files.update(root.rglob('*.png'))
    return files


def local_compact(output):
    """Use the existing ownership check and the exact TTR route lock."""
    from focus_batch_harness import lock
    with lock():
        return compact_with_producer_lock(output)


def compact_with_producer_lock(output):
    """Caller holds the producer lock. Require closed target ownership before retention."""
    from qualify_hcf362 import TTR, Client
    from native343 import TARGET
    from usb_training386 import verify_volume, VOLUME
    verify_volume()
    map_root = TTR/'.local-work/nuiak-hcf362/hcf-map'
    ready = Client(output).call('compaction-readiness', 'simulator', 'readiness', '--simulator-udid', TARGET)
    q.require(ready.get('can_run') and ready.get('ownership') and
              all(r['state'] == 'clear' for r in ready['ownership']), 'compaction_target_busy')
    fd = os.open(map_root/'route-execution.lock', os.O_RDWR | os.O_NOFOLLOW)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        journals = {p: q.digest(p) for p in map_root.glob('hcf-*/recovery.json')}
        result = compact(retained_pngs(TTR, map_root), VOLUME/'data/NUIAK/archive-native458/png', output/'compaction.json')
        q.require(all(q.digest(p) == digest for p,digest in journals.items()), 'compaction_journal_changed')
        return result
    finally:
        os.close(fd)
