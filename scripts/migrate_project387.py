"""Verify the USB project before repairing links or removing copied bulk files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import time

SOURCE = Path.home() / 'Documents/GitHub/NativeUIAuditKit'
VOLUME = Path('/Volumes/training-drive')
TARGET = VOLUME / 'data/NUIAK/project/NativeUIAuditKit'
EVIDENCE = VOLUME / 'data/NUIAK/project-migration-387'
UUID = 'FD8D8E36-FAAC-4205-87ED-86134C3582B1'
# Keep the source checkout and coordination credentials until Codex changes folders.
BULK = ('dataset', 'NativeUITrainer', 'reports/work')
KEEP = ('reports/work/CHAT-288', 'reports/work/USB386', 'reports/work/QUEUE-SYNC-01')


def volume():
    assert VOLUME.is_mount() and VOLUME.resolve() == VOLUME, 'USB mount missing'
    info = plistlib.loads(subprocess.check_output(['diskutil', 'info', '-plist', str(VOLUME)]))
    assert (info.get('VolumeUUID') == UUID and info.get('MountPoint') == str(VOLUME)
            and info.get('FilesystemType') == 'apfs' and info.get('Internal') is False
            and info.get('Writable') is True), 'USB identity differs'
    assert TARGET.is_dir() and TARGET.resolve() == TARGET, 'Target differs'
    usage = shutil.disk_usage(VOLUME)
    assert usage.free > usage.total * .2, 'USB reserve is too small'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(name, value):
    EVIDENCE.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = EVIDENCE / name
    with path.open('x') as stream:
        os.chmod(path, 0o600)
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())


def paths():
    for base, dirs, files in os.walk(SOURCE):
        dirs[:] = sorted(d for d in dirs if d != '__pycache__')
        for name in sorted(files + dirs):
            path = Path(base) / name
            if path.is_symlink() or path.is_file():
                yield path, str(path.relative_to(SOURCE))


def verify():
    volume()
    EVIDENCE.mkdir(mode=0o700, parents=True, exist_ok=True)
    manifest = EVIDENCE / 'verified-files.jsonl'
    count = size = links = 0
    started = time.monotonic()
    with manifest.open('x') as out:
        os.chmod(manifest, 0o600)
        for source, relative in paths():
            destination = TARGET / relative
            assert not any(p.is_symlink() for p in destination.parents
                           if p != TARGET.parent), 'Linked destination parent: ' + relative
            if source.is_symlink():
                assert destination.is_symlink(), 'Missing link: ' + relative
                value = os.readlink(source)
                assert os.readlink(destination) == value, 'Link differs: ' + relative
                row = dict(path=relative, kind='link', target=value)
                links += 1
            else:
                assert destination.is_file() and not destination.is_symlink(), 'Missing file: ' + relative
                before = source.stat()
                assert before.st_size == destination.stat().st_size, 'Size differs: ' + relative
                checksum = digest(source)
                assert checksum == digest(destination), 'Content differs: ' + relative
                after = source.stat()
                assert (before.st_mtime_ns, before.st_size, before.st_ino) == (after.st_mtime_ns, after.st_size, after.st_ino), 'Source changed: ' + relative
                row = dict(path=relative, kind='file', bytes=after.st_size, sha256=checksum)
                size += after.st_size
                count += 1
            out.write(json.dumps(row) + '\n')
            if (count + links) % 25000 == 0:
                print(json.dumps(dict(files=count, links=links, bytes=size)), flush=True)
        out.flush()
        os.fsync(out.fileno())
    result = dict(files=count, links=links, bytes=size, seconds=time.monotonic()-started,
                  manifestSHA256=digest(manifest), volumeUUID=UUID)
    write('verification.json', result)
    print(json.dumps(result), flush=True)


def repair():
    volume()
    receipt = json.loads((EVIDENCE/'verification.json').read_text())
    assert digest(EVIDENCE/'verified-files.jsonl') == receipt['manifestSHA256']
    repaired = 0
    with (EVIDENCE/'verified-files.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['kind'] != 'link' or not row['target'].startswith(str(SOURCE)+'/'):
                continue
            path = TARGET/row['path']
            target = str(TARGET) + row['target'][len(str(SOURCE)):]
            assert not path.exists() or path.is_symlink(), 'Link replaced by file'
            assert not path.is_symlink() or os.readlink(path) in (row['target'], target)
            if path.is_symlink() and os.readlink(path) == target:
                continue
            if path.is_symlink():path.unlink()
            path.symlink_to(target)
            repaired += 1
    # Environment launchers are generated files, not experiment specifications.
    launchers = 0
    for folder in TARGET.glob('.venv*'):
        if not folder.is_dir() or folder.is_symlink():
            continue
        for path in list((folder/'bin').glob('*')) + [folder/'pyvenv.cfg']:
            if not path.is_file() or path.is_symlink() or path.stat().st_size > 1000000:
                continue
            content = path.read_bytes()
            if b'\x00' in content or str(SOURCE).encode() not in content:
                continue
            path.write_bytes(content.replace(str(SOURCE).encode(), str(TARGET).encode()))
            launchers += 1
    profile=TARGET/'reports/work/CHAT-288/profile.json'
    profile_changes=0
    if profile.is_file():
        doc=json.loads(profile.read_text())
        for key in ('ca','certificate','key'):
            value=doc.get(key)
            if isinstance(value,str) and value.startswith(str(SOURCE)+'/'):
                changed=str(TARGET)+value[len(str(SOURCE)):]
                assert digest(Path(value))==digest(Path(changed)), 'Credential file differs'
                doc[key]=changed;profile_changes+=1
        if profile_changes:
            profile.write_text(json.dumps(doc,indent=2)+'\n')
    write('path-repair.json', dict(links=repaired, environmentFiles=launchers,profilePaths=profile_changes,
          historicalRecords='Preserved unchanged. Old absolute paths require explicit review before replay.'))
    print(json.dumps(dict(repairedLinks=repaired, environmentFiles=launchers)), flush=True)


def reclaim():
    volume()
    receipt = json.loads((EVIDENCE/'verification.json').read_text())
    assert digest(EVIDENCE/'verified-files.jsonl') == receipt['manifestSHA256']
    assert (EVIDENCE/'path-repair.json').is_file(), 'Repair links first'
    count = removed = already_removed = 0
    device = VOLUME.stat().st_dev
    # Exact manifest members only. Never remove the workspace root or follow links.
    with (EVIDENCE/'verified-files.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line); name = row['path']
            if not any(name.startswith(p+'/') for p in BULK):
                continue
            if any(name == p or name.startswith(p+'/') for p in KEEP):
                continue
            source = SOURCE/name; target = TARGET/name
            assert not any(p.is_symlink() for p in source.parents), 'Linked source parent'
            if row['kind'] == 'link':
                expected = row['target'].replace(str(SOURCE)+'/', str(TARGET)+'/', 1) if row['target'].startswith(str(SOURCE)+'/') else row['target']
                assert target.is_symlink() and os.readlink(target) == expected
                if not source.exists() and not source.is_symlink():
                    already_removed += 1
                    continue
                assert source.is_symlink() and os.readlink(source) == row['target']
            else:
                assert target.is_file() and not target.is_symlink()
                assert digest(target) == row['sha256'], 'Target changed: '+name
                if not source.exists() and not source.is_symlink():
                    already_removed += 1
                    continue
                assert source.is_file() and not source.is_symlink()
                assert digest(source) == row['sha256'], 'Source changed: '+name
                removed += row['bytes']
            assert VOLUME.is_mount() and VOLUME.stat().st_dev == device, 'USB disconnected'
            source.unlink(); count += 1
            if count % 10000 == 0:
                print(json.dumps(dict(removedFiles=count, removedBytes=removed)), flush=True)
    write('reclamation.json', dict(removedFiles=count, removedBytes=removed, alreadyRemoved=already_removed,
          kept=list(KEEP), internalFree=shutil.disk_usage(SOURCE).free,
          restore='Restore named files from the USB project. Reverse the recorded link mapping for the old path.',backup=False))
    print(json.dumps(dict(removedFiles=count, removedBytes=removed)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify','repair','reclaim'))
    args = parser.parse_args()
    {'verify':verify,'repair':repair,'reclaim':reclaim}[args.action]()
