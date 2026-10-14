"""Remove repository paths from the pinned checkpoint without executing pickle code."""
import json
import pickletools
import struct
import shutil
import zipfile

import model_release as r

PIN = '4b726875488842540b9f43eb5cd5ce4f2bd55b2a7cb936404957e3aef8d3fa3c'
ROOT = r.ROOT
OUT = ROOT / 'reports/work/RELEASE-305/editable-source'


def sanitize(data, prefix):
    ops = list(pickletools.genops(data))
    r.require(ops and ops[0][0].name == 'PROTO' and ops[0][1] == 2, 'unsupported_protocol')
    r.require(ops[-1][0].name == 'STOP' and ops[-1][2] + 1 == len(data), 'pickle_tail')
    pieces = []
    replacements = 0
    for i, (op, value, start) in enumerate(ops):
        stop = ops[i + 1][2] if i + 1 < len(ops) else len(data)
        if isinstance(value, str) and prefix in value:
            r.require(op.name == 'BINUNICODE' and (value == prefix or value.startswith(prefix + '/')), 'unexpected_path')
            text = '.' if value == prefix else value[len(prefix) + 1:]
            encoded = text.encode('utf-8')
            pieces.append(b'X' + struct.pack('<I', len(encoded)) + encoded)
            replacements += 1
        else:
            pieces.append(data[start:stop])
    result = b''.join(pieces)
    new = list(pickletools.genops(result))
    r.require(len(ops) == len(new), 'changed_structure')
    for (a, av, _), (b, bv, _) in zip(ops, new):
        r.require(a.name == b.name, 'changed_opcode')
        if av != bv:
            r.require(a.name == 'BINUNICODE' and isinstance(av, str) and prefix in av, 'changed_value')
        if isinstance(bv, str):
            r.require('/Users/' not in bv and '/home/' not in bv and prefix not in bv, 'private_path')
    return result, replacements


def prepare():
    r.require(not OUT.exists(), 'output_exists')
    source = ROOT / 'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt'
    raw = source.read_bytes()
    r.require(r.digest(raw) == PIN, 'source_hash')
    with zipfile.ZipFile(source) as z:
        names = z.namelist()
        r.require(len(names) == len(set(names)) and len(names) < 1000, 'member_count')
        r.require(sum(i.file_size for i in z.infolist()) < 16 * 1024**2, 'size_limit')
        members = {r.relative_name(n): z.read(n) for n in names}
    original = members['best/data.pkl']
    members['best/data.pkl'], count = sanitize(original, str(ROOT))
    r.require(count == 5, 'unexpected_path_count')
    OUT.mkdir()
    (OUT / 'weights').mkdir()
    destination = OUT / 'weights/best.pt'
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_STORED) as z:
        for name, data in members.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(destination) as z:
        r.require(z.testzip() is None and all(z.read(n) == d for n, d in members.items()), 'roundtrip')
    source_zip = ROOT / 'reports/work/RELEASE-305/nativeui-tvos-source-review305.zip'
    r.require(r.digest(source_zip.read_bytes()) == '519f674e6d54f5fe42ec96035b6de15f0057ac4c7d3bb43d07cab1104b430db3', 'source_archive_hash')
    (OUT / 'scripts').mkdir()
    with zipfile.ZipFile(source_zip) as z:
        (OUT / 'scripts/export_yolo_coreml.py').write_bytes(z.read('historical/scripts/export_yolo_coreml.py'))
    receipt = dict(schemaVersion=1, sourceSHA256=PIN, sanitizedSHA256=r.digest(destination.read_bytes()),
                   replacedPaths=count, tensorStorageFiles=sum('/data/' in n for n in members),
                   nonPickleMembersUnchanged=True, pickleChanges='5 path strings only; no pickle execution',
                   exportVerified=False)
    (OUT / 'privacy-receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt))


def replay():
    payload = OUT.parent / 'source-replay-payload'
    r.require(not payload.exists(), 'output_exists')
    payload.mkdir()
    shutil.copytree(OUT / 'weights/best.mlpackage', payload / 'model.mlpackage')
    files = r.inventory(payload)
    result = r.pack(payload, OUT.parent / 'source-replay.zip', files)
    (OUT.parent / 'source-replay-inventory.json').write_text(json.dumps(files, indent=2))
    (OUT.parent / 'source-replay-archive.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


def seal():
    parent = OUT.parent
    receipt = r.read_json(parent / 'source-replay-verified/review-receipt.json')
    archive = r.read_json(parent / 'source-replay-archive.json')
    r.require(receipt['archiveSHA256'] == archive['archiveSHA256'] and receipt['detections'] == '25', 'replay_required')
    public = parent / 'source-supplement'
    r.require(not public.exists(), 'output_exists')
    r.require(r.digest((OUT / 'weights/best.pt').read_bytes()) ==
              '4387e5c96175172b01c4f5c05bf8c614e19ef44a065deb5193e37c8f513bfb14', 'checkpoint_changed')
    public.mkdir()
    for name in ['README.md', 'privacy-receipt.json', 'weights/best.pt', 'scripts/export_yolo_coreml.py']:
        destination = public / name
        destination.parent.mkdir(exist_ok=True, parents=True)
        shutil.copyfile(OUT / name, destination)
    for path in ['Licenses/AGPL-3.0.txt', 'LICENSE', 'THIRD_PARTY_NOTICES.md']:
        shutil.copyfile(ROOT / path, public / path.split('/')[-1])
    shutil.copyfile(parent / 'source-replay-verified/review-receipt.json', public / 'native-replay-receipt.json')
    result = r.pack(public, parent / 'nativeui-tvos-editable-source-review305.zip', r.inventory(public))
    (parent / 'source-supplement-receipt.json').write_text(json.dumps(result, indent=2))
    names = ['nativeui-tvos-v3.0-review305.zip', 'nativeui-tvos-source-review305.zip',
             'nativeui-tvos-editable-source-review305.zip', 'catalog-review.json', 'source-audit.json',
             'source-supplement-receipt.json']
    with (parent / 'SHA256SUMS-final').open('x') as output:
        output.write(''.join(r.digest((parent / n).read_bytes()) + '  ' + n + '\n' for n in names))
    print(json.dumps(result))


def public_prepare():
    parent = OUT.parent
    public = parent / 'public306'
    payload = parent / 'public306-payload'
    r.require(not public.exists() and not payload.exists(), 'output_exists')
    receipt = r.read_json(parent / 'source-replay-verified/review-receipt.json')
    replay_archive = r.read_json(parent / 'source-replay-archive.json')
    r.require(receipt['detections'] == '25' and receipt['archiveSHA256'] == replay_archive['archiveSHA256'], 'replay_required')
    r.require(r.inventory(parent / 'source-replay-payload') == r.read_json(parent / 'source-replay-inventory.json'), 'replay_changed')
    # Use the verified rebuilt model. Preserve the old private review archives.
    shutil.copytree(parent / 'source-replay-payload', payload)
    for name in ['NOTICES.txt', 'contract.json']:
        shutil.copyfile(parent / 'payload' / name, payload / name)
    files = r.inventory(payload)
    for member in files:
        content = (payload / member['path']).read_bytes()
        r.require(all(token not in content for token in [b'josephmccraw', b'/Users/', b'/home/']), 'private_identity')
    public.mkdir()
    entry = r.read_json(parent / 'catalog-review.json')['models'][0]
    entry['artifactVersion'] = '3.0.0-review.306'
    entry['files'] = files
    entry['expandedBytes'] = sum(f['bytes'] for f in files)
    entry.update(r.pack(payload, public / 'nativeui-tvos-v3.0-review306.zip', files))
    entry['url'] = 'https://github.com/SerialForBreakfast/NativeUIAuditKit/releases/download/models-review306/nativeui-tvos-v3.0-review306.zip'
    entry['sourceRevision'] = 'cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0: runtime; Run 012 checkpoint sanitized and re-exported; source supplement included'
    catalog = dict(schemaVersion=1, models=[entry])
    r.validate_catalog(catalog)
    r.verify_archive(public / 'nativeui-tvos-v3.0-review306.zip', entry)
    (public / 'catalog-review.json').write_text(json.dumps(catalog, indent=2))
    (parent / 'public306-inventory.json').write_text(json.dumps(files, indent=2))
    names = ['nativeui-tvos-source-review305.zip', 'nativeui-tvos-editable-source-review305.zip',
             'source-audit.json', 'source-supplement-receipt.json']
    for name in names:
        shutil.copyfile(parent / name, public / name)
    names += ['catalog-review.json', 'nativeui-tvos-v3.0-review306.zip']
    (public / 'SHA256SUMS').write_text(''.join(r.digest((public / n).read_bytes()) + '  ' + n + '\n' for n in names))
    print(json.dumps(dict(archiveSHA256=entry['archiveSHA256'], archiveBytes=entry['archiveBytes'])))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'replay', 'seal', 'public'], default='prepare', nargs='?')
    args = parser.parse_args()
    {'prepare': prepare, 'replay': replay, 'seal': seal, 'public': public_prepare}[args.action]()
