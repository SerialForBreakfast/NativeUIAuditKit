"""Assigned SYNTH05 archive receipt; immutable local copies and bounded extraction."""
import datetime
import json
from pathlib import Path
import shutil
import tarfile

from focus_surface_intake import ROOT, require, safe_members, sha, fresh, write

ENTRIES = [
    ('ttr-synth05-recovery-pilot-20260929.tar.gz', 66173275, '7bcb28671453fd0204d458d54926a942a69ef480832ad22d43ce9d3fe624b91c'),
    ('ttr-synth05-partial-pilot-20260929.tar.gz', 89516603, '865f9c0496db82a3efab6e0de1423fe868d8bb7bb34b5edac0f38728d1bde636'),
    ('ttr-synth05-source-0ef89d79-20260929T070444Z.tar.gz', 598382, '7d0b956cc5d5e1151aedb7c9f37db817211bd2d227fb5c97928517b992e18286'),
    ('ttr-synth05-recovery-afc948ca-20260929T161814Z.tar.gz', 793153, '3deecb638f508cf6861143d02b9ccbabe1a8f5ba1b5e7c1a8f4435d18909f504'),
]


def bounded_members(archive):
    # POSIX tar commonly emits a root './' directory. It has no destination
    # to extract. Permit precisely that harmless directory, never a root file.
    members = []
    root_seen = False
    for member in archive:
        require(len(members) < 1000, 'archive_member_limit')
        if member.name in ('.', './'):
            require(member.isdir() and not root_seen and member.size == 0, 'unsafe_archive_root')
            root_seen = True
        else:
            members.append(member)
    return safe_members(members)


def receive(share, root):
    require(not any(p.is_symlink() for p in (root, *root.parents)), 'symlink_output')
    root = root.resolve()
    require(root.is_relative_to(ROOT) and not root.is_symlink(), 'output_boundary')
    require(shutil.disk_usage(ROOT).free > sum(e[1] for e in ENTRIES) + 5_000_000_000,
            'insufficient_storage_reserve')
    root.mkdir(parents=True, exist_ok=True)
    receipts = []
    for name, size, expected in ENTRIES:
        source, target = share / name, root / name
        require(source.is_file() and not source.is_symlink() and source.stat().st_size == size,
                'source_size')
        if not target.exists():
            with source.open('rb') as a, target.open('xb') as b:
                shutil.copyfileobj(a, b)
        require(not target.is_symlink() and target.stat().st_size == size and sha(target) == expected,
                'copied_archive_integrity')
        output = fresh(root / name.removesuffix('.tar.gz'))
        with tarfile.open(target) as archive:
            members, expanded = bounded_members(archive)
            require(shutil.disk_usage(ROOT).free > expanded + 5_000_000_000, 'storage_reserve')
            output.mkdir()
            for member in members:
                destination = output / member.name
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as a, destination.open('xb') as b:
                        shutil.copyfileobj(a, b)
        require(sha(target) == expected, 'changed_archive')
        receipts.append(dict(name=name, bytes=size, sha256=expected, expandedBytes=expanded,
                             members=len(members), localPath=str(target.relative_to(ROOT)),
                             verifiedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                             transfer='copied_and_verified', intake='pending'))
        print(name, len(members), expanded, flush=True)
    write(root / 'receipt.json', receipts)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verified-share', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receive(args.verified_share, args.output)
