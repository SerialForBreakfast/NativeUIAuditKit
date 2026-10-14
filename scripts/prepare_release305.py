"""Prepare source evidence and full notices. Do not publish or approve a release."""
import base64
import csv
import json
import subprocess
import zipfile
from pathlib import Path

import model_release as release

ROOT = release.ROOT
OUT = ROOT / 'reports/work/RELEASE-305'
COMMIT = 'dd7b4a7fd6dd187504b2f2c1aea2ad534d67c6ec'


def record_matches(data, recorded):
    return recorded == 'sha256=' + base64.urlsafe_b64encode(
        __import__('hashlib').sha256(data).digest()).decode().rstrip('=')


def source_members():
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', COMMIT], cwd=ROOT).decode().splitlines()
    selected = {'scripts/generate_tvos_dataset.swift', 'scripts/export_tvos_coco.py',
                'scripts/train_tvos_model.py', 'scripts/export_yolo_coreml.py',
                'Research/schemas/category_map.json', 'LICENSE'}
    selected.update(n for n in names if n.startswith('NativeUIDatasetGenerator/Templates/tvOS/') and n.endswith('.swift'))
    members = {'historical/' + n: subprocess.check_output(['git', 'show', COMMIT + ':' + n], cwd=ROOT)
               for n in sorted(selected)}
    audits = []
    for environment, version, python in [('.venv-coreml', '8.4.153', '3.12'), ('.venv-yolo', '8.4.124', '3.13')]:
        site = ROOT / environment / 'lib' / ('python' + python) / 'site-packages'
        # Resolve the resident Python directory without installing dependencies.
        if not site.exists():
            candidates = list((ROOT / environment / 'lib').glob('python*/site-packages'))
            release.require(len(candidates) == 1, 'ambiguous_environment')
            site = candidates[0]
        dist = site / ('ultralytics-' + version + '.dist-info')
        records = {row[0]: row[1] for row in csv.reader((dist / 'RECORD').read_text().splitlines())}
        prefix = 'upstream/ultralytics-' + version + '/'
        count = 0
        differences = []
        for path in sorted((site / 'ultralytics').rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            release.require(not path.is_symlink(), 'linked_source')
            if path.suffix not in {'.py', '.yaml', '.yml', '.json', '.toml', '.txt', '.md'}:
                continue
            name = path.relative_to(site).as_posix()
            data = path.read_bytes()
            if not record_matches(data, records.get(name, '')):
                differences.append(dict(path=name, recordedHash=records.get(name), currentSHA256=release.digest(data)))
            members[prefix + name] = data
            count += 1
        members[prefix + 'LICENSE'] = (dist / 'licenses/LICENSE').read_bytes()
        members[prefix + 'METADATA'] = (dist / 'METADATA').read_bytes()
        audits.append(dict(version=version, files=count, differences=differences,
                           result='Compared with resident RECORD. Differences require historical review.'))
    config = (ROOT / 'NativeUITrainer/yolo_runs/phase6b_tvos_v3/args.yaml').read_text()
    config = config.replace(str(ROOT) + '/', '')
    release.require('/Users/' not in config, 'private_path')
    members['configuration/args.yaml'] = config.encode()
    members['AGPL-3.0.txt'] = (ROOT / 'Licenses/AGPL-3.0.txt').read_bytes()
    members['THIRD_PARTY_NOTICES.md'] = (ROOT / 'THIRD_PARTY_NOTICES.md').read_bytes()
    members['README.txt'] = (
        'Source evidence for the unchanged Run 012 tvOS model.\n'
        'Historical NUIAK source commit: ' + COMMIT + '\n'
        'The audit lists differences from installed package records. It does not authenticate historical execution.\n'
        'The exporter includes the recorded coremltools compatibility patch.\n'
        'Configuration paths are relative to the repository. Originals remain private.\n'
        'This archive excludes datasets, checkpoints, dependency binaries, and example artwork.\n'
        'It is source evidence, not a claim of complete Corresponding Source or reproducible training.\n'
        'The maintainer must review source completeness and combined distribution before publication.\n'
    ).encode()
    return members, audits


def prepare():
    release.require(not OUT.exists(), 'output_exists')
    members, audits = source_members()
    release.require(len(members) <= 1500 and sum(map(len, members.values())) <= 32 * 1024**2, 'source_limit')
    for name in members:
        release.relative_name(name)
    OUT.mkdir()
    archive = OUT / 'nativeui-tvos-source-review305.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(archive) as z:
        release.require(z.testzip() is None and all(z.read(n) == d for n, d in members.items()), 'source_roundtrip')
    inventory = [dict(path=n, bytes=len(d), sha256=release.digest(d)) for n, d in sorted(members.items())]
    (OUT / 'source-audit.json').write_text(json.dumps(dict(commit=COMMIT, audits=audits, files=inventory,
        archiveBytes=archive.stat().st_size, archiveSHA256=release.digest(archive.read_bytes())), indent=2))
    old = ROOT / 'reports/work/RELEASE-304'
    payload = OUT / 'payload'
    import shutil
    shutil.copytree(old / 'payload', payload)
    notices = '\n\n'.join((ROOT / p).read_text() for p in ['THIRD_PARTY_NOTICES.md', 'LICENSE', 'Licenses/AGPL-3.0.txt'])
    (payload / 'NOTICES.txt').write_text(notices)
    entry = release.read_json(old / 'delivery/entry.json')
    entry['artifactVersion'] = '3.0.0-review.305'
    entry['files'] = release.inventory(payload)
    entry['expandedBytes'] = sum(f['bytes'] for f in entry['files'])
    model = OUT / 'nativeui-tvos-v3.0-review305.zip'
    entry.update(release.pack(payload, model, entry['files']))
    entry['url'] = 'https://github.com/SerialForBreakfast/NativeUIAuditKit/releases/download/models-review305/' + model.name
    release.validate_catalog(dict(schemaVersion=1, models=[entry]))
    release.verify_archive(model, entry)
    (OUT / 'catalog-review.json').write_text(json.dumps(dict(schemaVersion=1, models=[entry]), indent=2))
    (OUT / 'inventory.json').write_text(json.dumps(entry['files'], indent=2))
    (OUT / 'SHA256SUMS').write_text(''.join(release.digest(p.read_bytes()) + '  ' + p.name + '\n'
        for p in [model, archive, OUT / 'catalog-review.json', OUT / 'source-audit.json']))
    print(json.dumps(dict(modelSHA256=entry['archiveSHA256'], sourceFiles=len(members), audits=audits)))


if __name__ == '__main__':
    prepare()
