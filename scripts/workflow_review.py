"""Read-only operational status and exact source handoff. No Git or share writes."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from shared_transfer import document, mounted, SHARE

ROOT = Path(__file__).resolve().parents[1]


def freshness(entry, now):
    try:
        start = dt.datetime.fromisoformat(str(entry['updated_at']).replace('Z', '+00:00'))
        end = dt.datetime.fromisoformat(str(entry['valid_until']).replace('Z', '+00:00'))
        if start.tzinfo is None or end.tzinfo is None or end < start or start > now:
            return 'unknown'
        return 'expired' if end <= now else 'current'
    except (KeyError, ValueError, TypeError):
        return 'unknown'


def status_view(path, now):
    if path.is_relative_to(SHARE):
        mounted()
        if path.resolve() != path:
            raise ValueError('status_symlink')
    if path.stat().st_size > 1_048_576:
        raise ValueError('metadata_size')
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    data = document(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != before:
        raise ValueError('status_changed_during_read')
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('unsupported_status')
    actionable = []

    def visit(value, pointer=''):
        if isinstance(value, dict):
            for key, child in value.items():
                location = pointer + '/' + key.replace('~', '~0').replace('/', '~1')
                if key in {'pending_requests', 'blockers'} and child:
                    actionable.append({'pointer': location, 'value': child})
                else:
                    visit(child, location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, pointer + '/' + str(index))

    visit(data)
    packets = data.get('packets', {})
    if not isinstance(packets, dict) or any(not isinstance(v, dict) for v in packets.values()):
        raise ValueError('invalid_packets')
    fields = ('owner', 'state', 'summary', 'next', 'outcomes', 'evidence', 'updated_at', 'valid_until')
    return {'version': 1, 'sourceSHA256': before,
            'readOnly': True, 'freshness': freshness(data, now), 'work': data.get('work'),
            'packets': {key: {**{f: value[f] for f in fields if f in value},
                              'freshness': freshness(value, now),
                              'otherFields': sorted(set(value) - set(fields))}
                        for key, value in packets.items()},
            'actionable': actionable, 'sourceFields': sorted(data),
            'note': 'Snapshot only; expired unresolved requests are retained. Source is authoritative.'}


def parse_porcelain(raw):
    records = raw.split(b'\0')
    result = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b' ':
            raise ValueError('invalid_git_record')
        status = record[:2].decode('ascii')
        row = {'status': status, 'path': record[3:].decode('utf-8', errors='surrogateescape')}
        if 'R' in status or 'C' in status:
            if index >= len(records) or not records[index]:
                raise ValueError('missing_rename_origin')
            row['originalPath'] = records[index].decode('utf-8', errors='surrogateescape')
            index += 1
        result.append(row)
    return result


def git_output(*args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(ROOT), *args], timeout=30)


def git_view(intended, message, evidence, uptake):
    if len(intended) != len(set(intended)):
        raise ValueError('duplicate_intended_path')
    head = git_output('rev-parse', 'HEAD').decode().strip()
    inventory = parse_porcelain(git_output('status', '--porcelain=v1', '-z', '--untracked-files=all'))
    paths = {row['path'] for row in inventory}
    for path in intended:
        if path not in paths or Path(path).is_absolute() or '..' in Path(path).parts:
            raise ValueError('intended_path_not_changed: ' + path)
    if git_output('rev-parse', 'HEAD').decode().strip() != head:
        raise ValueError('head_changed_during_inventory')
    return {'version': 1, 'readOnly': True, 'base': head, 'head': head,
            'scope': 'Uncommitted changes against current HEAD; ignored paths excluded by Git',
            'inventory': inventory, 'intendedPaths': intended,
            'unassignedPaths': sorted(paths - set(intended)),
            'reportedTestEvidence': evidence, 'consumerUptake': uptake,
            'suggestedCommitMessage': message, 'published': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    status = sub.add_parser('status')
    status.add_argument('path', type=Path)
    git = sub.add_parser('git')
    git.add_argument('--intended', action='append', default=[])
    git.add_argument('--message', required=True)
    git.add_argument('--evidence', action='append', default=[])
    git.add_argument('--uptake', required=True)
    args = parser.parse_args()
    if args.command == 'status':
        result = status_view(args.path.absolute(), dt.datetime.now(dt.timezone.utc))
    else:
        result = git_view(args.intended, args.message, args.evidence, args.uptake)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True, default=str))


if __name__ == '__main__':
    main()
