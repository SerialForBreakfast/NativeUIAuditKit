"""Prepare exact model archives locally. This tool never publishes or installs."""
import argparse
import hashlib
import io
import json
import re
import stat
import subprocess
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAX_ARCHIVE = 32 * 1024**2
MAX_EXPANDED = 64 * 1024**2
MAX_FILES = 256
SUPPORTED = {'nativeui-ios-v2.0': ('element_detection', 'iOS'),
             'nativeui-tvos-v3.0': ('element_detection', 'tvOS'),
             'focus-ring-detector-v1.0': ('single_frame_focus', 'tvOS')}
SHA = re.compile(r'[0-9a-f]{64}\Z')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    require(path.stat().st_size <= 1024**2, 'json_size')
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))


def relative_name(value):
    require(isinstance(value, str) and 0 < len(value.encode()) <= 512, 'path_length')
    parts = value.split('/')
    require(not PurePosixPath(value).is_absolute() and all(p not in ('', '.', '..') for p in parts), 'unsafe_path')
    require(all(re.fullmatch(r'[A-Za-z0-9_.-]+', p) for p in parts), 'unsupported_path')
    return value


def local_path(path):
    path = Path(path).absolute()
    require(path == path.resolve(), 'linked_path')
    require(path.is_relative_to(ROOT) and path != ROOT, 'outside_project')
    return path


def inventory(directory):
    directory = local_path(directory)
    require(directory.is_dir(), 'missing_directory')
    files = []
    names = set()
    total = 0
    for path in sorted(directory.rglob('*')):
        require(not path.is_symlink(), 'linked_member')
        if path.is_dir():
            continue
        require(path.is_file(), 'special_member')
        name = relative_name(path.relative_to(directory).as_posix())
        require(name.casefold() not in names, 'case_collision')
        names.add(name.casefold())
        size = path.stat().st_size
        total += size
        require(len(files) < MAX_FILES and total <= MAX_EXPANDED, 'inventory_limit')
        content = path.read_bytes()
        require(len(content) == size, 'source_changed')
        files.append(dict(path=name, bytes=size, sha256=digest(content)))
    require(bool(files), 'empty_inventory')
    return files


def validate_entry(entry, publication=False):
    required = {'modelID', 'artifactVersion', 'task', 'screenshotDomain', 'modelRoot', 'files',
                'expandedBytes', 'archiveBytes', 'archiveSHA256', 'url', 'hosts', 'runtimeContract',
                'preprocessing', 'tensorContractSHA256', 'licensePath', 'qualification', 'sourceRevision',
                'releaseStatus', 'approvalReference'}
    require(set(entry) == required, 'entry_fields')
    require(entry['modelID'] in SUPPORTED, 'unknown_model')
    require((entry['task'], entry['screenshotDomain']) == SUPPORTED[entry['modelID']], 'task_mapping')
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?', entry['artifactVersion'] or ''), 'version')
    require(entry['runtimeContract'] == 'nuiak-model-v1', 'runtime_contract')
    for key in ('preprocessing', 'qualification', 'sourceRevision'):
        require(isinstance(entry[key], str) and 0 < len(entry[key]) <= 1024, 'missing_context')
    require(bool(SHA.fullmatch(entry['tensorContractSHA256'])), 'tensor_hash')
    require(entry['releaseStatus'] in ('review-only', 'approved'), 'release_status')
    require(isinstance(entry['approvalReference'], str), 'approval_reference')
    if publication:
        require(entry['releaseStatus'] == 'approved' and bool(entry['approvalReference'].strip()), 'approval_required')
    require(isinstance(entry['hosts'], list) and bool(entry['hosts']), 'hosts')
    host_names = set()
    for host in entry['hosts']:
        require(set(host) == {'platform', 'minimumVersion', 'evidence'}, 'host_fields')
        require(host['platform'] in ('macOS', 'iOS', 'macCatalyst', 'visionOS'), 'unsupported_host')
        require(host['platform'] not in host_names, 'duplicate_host')
        host_names.add(host['platform'])
        require(re.fullmatch(r'\d+\.\d+(?:\.\d+)?', host['minimumVersion']), 'host_version')
        require(isinstance(host['evidence'], str) and bool(host['evidence']), 'host_evidence')
    model_root = relative_name(entry['modelRoot'])
    require(model_root.endswith('.mlpackage') and '/' not in model_root, 'source_model_required')
    license_path = relative_name(entry['licensePath'])
    require(not license_path.startswith(model_root + '/'), 'separate_license_required')
    files = entry['files']
    require(isinstance(files, list) and 0 < len(files) <= MAX_FILES, 'file_count')
    names = set()
    total = 0
    for member in files:
        require(set(member) == {'path', 'bytes', 'sha256'}, 'member_fields')
        name = relative_name(member['path'])
        require(name.casefold() not in names, 'duplicate_member')
        names.add(name.casefold())
        require(type(member['bytes']) is int and member['bytes'] >= 0, 'member_size')
        require(isinstance(member['sha256'], str) and bool(SHA.fullmatch(member['sha256'])), 'member_hash')
        require(name.startswith(model_root + '/') or name in (license_path, 'contract.json'), 'unexpected_member')
        total += member['bytes']
    require(model_root.casefold() + '/manifest.json' in names, 'package_manifest_missing')
    require(license_path.casefold() in names and 'contract.json' in names, 'notices_missing')
    contract = next(f for f in files if f['path'] == 'contract.json')
    require(contract['sha256'] == entry['tensorContractSHA256'], 'contract_identity')
    require(next(f for f in files if f['path'] == license_path)['bytes'] > 0, 'empty_license')
    require(type(entry['expandedBytes']) is int and entry['expandedBytes'] == total <= MAX_EXPANDED, 'expanded_size')
    source_bytes = sum(f['bytes'] for f in files if f['path'].startswith(model_root + '/'))
    if entry['task'] == 'single_frame_focus':
        require(source_bytes <= 5_000_000, 'focus_size_gate')
    require(type(entry['archiveBytes']) is int and 0 < entry['archiveBytes'] <= MAX_ARCHIVE, 'archive_size')
    require(isinstance(entry['archiveSHA256'], str) and bool(SHA.fullmatch(entry['archiveSHA256'])), 'archive_hash')
    url = urlsplit(entry['url'])
    parts = url.path.split('/')
    require(url.scheme == 'https' and url.hostname == 'github.com' and url.port is None
            and url.username is None and url.password is None and not url.query and not url.fragment, 'release_url')
    require(len(parts) == 7 and parts[3:5] == ['releases', 'download'] and
            all(re.fullmatch(r'[A-Za-z0-9_.-]+', p) for p in (parts[1], parts[2], parts[5], parts[6]))
            and parts[5] not in ('latest', 'nightly') and parts[6].endswith('.zip'), 'pinned_release_url')


def validate_catalog(catalog, publication=False):
    require(set(catalog) == {'schemaVersion', 'models'} and catalog['schemaVersion'] == 1, 'catalog_schema')
    require(isinstance(catalog['models'], list) and bool(catalog['models']), 'empty_catalog')
    identities = set()
    for entry in catalog['models']:
        validate_entry(entry, publication)
        identity = (entry['modelID'], entry['artifactVersion'])
        require(identity not in identities, 'duplicate_artifact')
        identities.add(identity)


def verify_archive(path, entry, publication=False):
    path = local_path(path)
    require(path.stat().st_size == entry['archiveBytes'], 'archive_size_mismatch')
    with path.open('rb') as stream:
        data = stream.read(MAX_ARCHIVE + 1)
    return verify_archive_bytes(data, entry, publication)


def verify_archive_bytes(data, entry, publication=False):
    validate_entry(entry, publication)
    require(len(data) == entry['archiveBytes'] <= MAX_ARCHIVE, 'archive_size_mismatch')
    require(digest(data) == entry['archiveSHA256'], 'archive_hash_mismatch')
    expected = {r['path']: r for r in entry['files']}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        require(len(members) == len(expected), 'archive_member_count')
        seen = set()
        for member in members:
            name = relative_name(member.filename)
            require(name.casefold() not in seen and name in expected, 'archive_member_name')
            seen.add(name.casefold())
            mode = member.external_attr >> 16
            require(stat.S_IFMT(mode) == stat.S_IFREG and not member.flag_bits & 1, 'archive_member_type')
            require(member.compress_type == zipfile.ZIP_STORED, 'archive_compression')
            record = expected[name]
            require(member.file_size == member.compress_size == record['bytes'], 'archive_member_size')
            require(digest(archive.read(member)) == record['sha256'], 'archive_member_hash')
    return dict(verified=True, files=len(expected), publicationApproved=publication)


def native_extract_probe(path, entry, destination):
    """Test macOS extraction in a new private folder. Do not install or activate."""
    path, destination = local_path(path), local_path(destination)
    require(not destination.exists(), 'output_exists')
    with path.open('rb') as stream:
        data = stream.read(MAX_ARCHIVE + 1)
    verify_archive_bytes(data, entry)
    destination.mkdir(mode=0o700)
    owned_archive = destination / 'verified-input.zip'
    with owned_archive.open('xb') as stream:
        stream.write(data)
    owned_archive.chmod(0o400)
    payload = destination / 'payload'
    payload.mkdir(mode=0o700)
    # Invoke the fixed system executable directly. Never use a shell or Archive Utility.
    with (destination/'ditto.log').open('xb') as log:
        subprocess.run(['/usr/bin/ditto', '-x', '-k', '--norsrc', '--noextattr', '--noacl',
                        str(owned_archive), str(payload)], stdout=log, stderr=log, timeout=30, check=True)
    require(inventory(payload) == entry['files'], 'extracted_inventory_mismatch')
    result = dict(verified=True, backend='/usr/bin/ditto', files=len(entry['files']),
                  installed=False, activated=False, ttrSandboxQualified=False)
    with (destination/'verified.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    return result


def pack(directory, output, expected_inventory):
    directory, output = local_path(directory), local_path(output)
    require(not output.exists(), 'output_exists')
    require(not output.is_relative_to(directory), 'output_inside_source')
    require(inventory(directory) == expected_inventory, 'source_inventory_mismatch')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream, zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for member in expected_inventory:
            data = (directory / member['path']).read_bytes()
            require(len(data) == member['bytes'] and digest(data) == member['sha256'], 'source_changed')
            info = zipfile.ZipInfo(member['path'], (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    require(output.stat().st_size <= MAX_ARCHIVE, 'archive_limit')
    return dict(archiveBytes=output.stat().st_size, archiveSHA256=digest(output.read_bytes()))


def audit_repository():
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = [p for p in paths if p]
    ignored = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin', '-z'], cwd=ROOT,
                             input=('\0'.join(paths)+'\0').encode(), stdout=subprocess.PIPE, check=False)
    require(ignored.returncode in (0, 1), 'ignore_check_failed')
    ignored_paths = [p for p in ignored.stdout.decode().split('\0') if p]
    findings = []
    patterns = {'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                'token_pattern': re.compile(rb'(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}'),
                'email_literal': re.compile(rb'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
                'private_ipv4': re.compile(rb'\b(?:192\.168|10\.[0-9]{1,3})\.[0-9]{1,3}\.[0-9]{1,3}\b')}
    size = 0
    for name in paths:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            continue
        size += path.stat().st_size
        if path.stat().st_size > 2 * 1024**2:
            continue
        data = path.read_bytes()
        if b'\0' in data:
            continue
        for kind, pattern in patterns.items():
            matches = list(pattern.finditer(data))
            if matches:
                # Report locations and counts, never matched private values.
                findings.append(dict(path=name, kind=kind, count=len(matches)))
    return dict(version=1, trackedFiles=len(paths), availableTrackedBytes=size,
                trackedByRoot=dict(Counter(p.split('/')[0] for p in paths)),
                trackedButIgnored=len(ignored_paths),
                ignoredByRoot=dict(Counter(p.split('/')[0] for p in ignored_paths)),
                findings=findings, findingsNeedReview=True, historyAudited=False,
                publicReleaseReady=False,
                limitations='Pattern findings include examples and author credits. No whole-history or semantic privacy clearance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    audit = sub.add_parser('audit'); audit.add_argument('--output', type=Path, required=True)
    check = sub.add_parser('validate'); check.add_argument('catalog', type=Path); check.add_argument('--publication', action='store_true')
    verify = sub.add_parser('verify'); verify.add_argument('entry', type=Path); verify.add_argument('archive', type=Path)
    verify.add_argument('--publication', action='store_true')
    extract = sub.add_parser('native-probe'); extract.add_argument('entry', type=Path)
    extract.add_argument('archive', type=Path); extract.add_argument('destination', type=Path)
    bundle = sub.add_parser('pack'); bundle.add_argument('directory', type=Path); bundle.add_argument('inventory', type=Path)
    bundle.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.command == 'audit':
        output = local_path(args.output); require(not output.exists(), 'output_exists')
        result = audit_repository(); output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream: json.dump(result, stream, indent=2)
        print(json.dumps({k: result[k] for k in ('trackedFiles', 'trackedButIgnored', 'publicReleaseReady')}))
    elif args.command == 'validate':
        validate_catalog(read_json(args.catalog), args.publication); print('Catalog contract passes. This does not establish legal rights or model efficacy.')
    elif args.command == 'verify':
        print(json.dumps(verify_archive(args.archive, read_json(args.entry), args.publication)))
    elif args.command == 'native-probe':
        print(json.dumps(native_extract_probe(args.archive, read_json(args.entry), args.destination)))
    else:
        print(json.dumps(pack(args.directory, args.output, read_json(args.inventory))))


if __name__ == '__main__':
    main()
