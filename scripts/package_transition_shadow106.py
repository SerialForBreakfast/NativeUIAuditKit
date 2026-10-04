"""Create a portable, source-only consumer delivery with synthetic examples."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
import human_annotation_review as h

BASE = h.ROOT / 'reports/work/TRANSITION-SHADOW-106/artifacts'


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main(base=BASE,model_id='focus-transition-experimental-dtm025-change-v1',expected_pairs=240,archive_name='nuiak-transition-shadow-dtm025-v1.zip'):
    BASE=base
    parity = h.read(BASE / 'parity-final/parity.json')
    h.require(parity['passed'] and parity['exactEncodings'] == expected_pairs and parity['decisionsEqual'] == expected_pairs,
              'parity_required')
    h.checked(h.ROOT, parity['tool'])
    root = h.fresh(BASE / 'delivery'); root.mkdir()
    sources = root / 'Sources/TransitionShadowTool'; sources.mkdir(parents=True)
    for name in ('Observer.swift', 'CLI.swift'):
        shutil.copyfile(h.ROOT / 'Tools/TransitionShadowTool' / name, sources / name)
    shutil.copyfile(h.ROOT / 'Tools/TransitionShadowTool/README.md', root / 'README.md')
    # Generated packaging scaffolding, not a second implementation.
    (root / 'Package.swift').write_text('''// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "TransitionShadowConsumer", platforms: [.macOS(.v15)],
    products: [.executable(name: "TransitionShadowTool", targets: ["TransitionShadowTool"])],
    targets: [.executableTarget(name: "TransitionShadowTool")])
''')
    shutil.copytree(BASE / 'bundle', root / 'Model')
    shutil.copytree(BASE / 'export/FocusTransitionChange.mlpackage', root / 'SourceModel/FocusTransitionChange.mlpackage')
    reference = h.read(BASE / 'parity-inputs/reference.json')
    sample = next(v for v in reference['examples'] if v['id'] == 'synthetic-0')
    expected = next(v for v in reference['reference'] if v['id'] == sample['id'])
    inputs = root / 'Synthetic'; inputs.mkdir()
    for side in ('before', 'after'):
        origin = Path(sample[side]['path']); dest = inputs / origin.name
        h.require(origin.parent == BASE / 'parity-inputs' and origin.name.startswith('synthetic-'), 'private_sample')
        shutil.copyfile(origin, dest)
        sample[side]['path'] = '$ROOT/Synthetic/' + dest.name
    h.write(root / 'sample-request.template.json', dict(schemaVersion=1, mode='score', root='$ROOT', pairs=[sample]))
    h.write(root / 'synthetic-expected.json', expected)
    # Only aggregate compatibility data leaves NUIAK; no private IDs or paths.
    summary = {k: parity[k] for k in ('version','passed','counts','exactEncodings','decisionsEqual',
        'maxProbabilityError','modelTreeSHA256','contractSHA256','loadSeconds',
        'inferenceMedianSeconds','inferenceP95Seconds','preprocessingMedianSeconds','elapsedSeconds','releaseEligible')}
    h.write(root / 'parity-summary.json', summary)
    members = []
    for path in sorted(root.rglob('*')):
        h.require(not path.is_symlink(), 'symlink')
        if path.is_file(): members.append(dict(path=path.relative_to(root).as_posix(), bytes=path.stat().st_size, sha256=digest(path)))
    h.require(h.read(BASE/'bundle/contract.json')['modelID']==model_id,'package_model_identity')
    h.write(root / 'manifest.json', dict(schemaVersion=1, modelID=model_id,
        contractSHA256=parity['contractSHA256'], files=members, scope='change-only experimental passive shadow',
        privateCaptures=False, rawCheckpoints=False, compiledBinaries=False, releaseEligible=False))
    h.require(Path(archive_name).name==archive_name and archive_name.endswith('.zip'),'archive_name')
    archive = BASE / archive_name
    h.require(not archive.exists(), 'archive_collision')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(root.rglob('*')):
            if path.is_file(): z.write(path, path.relative_to(root).as_posix())
    # Independent bounded extraction rejects links, special files and unsafe names.
    extracted = h.fresh(BASE / 'portable-check'); extracted.mkdir()
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist(); names = [i.filename for i in infos]
        h.require(len(names) == len(set(names)) and len(names) <= 128, 'archive_members')
        h.require(sum(i.file_size for i in infos) < 5_000_000, 'archive_size')
        for info in infos:
            p = Path(info.filename); mode = info.external_attr >> 16
            h.require(not p.is_absolute() and '..' not in p.parts and (mode & 0o170000) in (0,0o100000), 'unsafe_member')
        z.extractall(extracted)
    manifest = h.read(extracted / 'manifest.json')
    for item in manifest['files']:
        p = extracted / item['path']
        h.require(p.stat().st_size == item['bytes'] and digest(p) == item['sha256'], 'extraction_integrity')
    request = (extracted / 'sample-request.template.json').read_text().replace('$ROOT', str(extracted))
    (extracted / 'request.json').write_text(request)
    h.write(BASE / 'package-receipt.json', dict(archive=h.ref(archive), manifestSHA256=digest(root / 'manifest.json'),
        contractSHA256=parity['contractSHA256'], members=len(names), expandedBytes=sum(i.file_size for i in infos),
        extracted=str(extracted), verified=True), sealed=True)
    print(archive.name, archive.stat().st_size, digest(archive), 'members', len(names))


if __name__ == '__main__': main()
