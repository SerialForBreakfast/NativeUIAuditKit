"""Prepare a local TTR review pack. Do not publish a public release."""
import json
import shutil
from pathlib import Path
import model_release as release

ROOT = release.ROOT
OUT = ROOT / 'reports/work/RELEASE-304'
SOURCE = ROOT / 'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage'
PIN = 'cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0'


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)


def prepare():
    reference = OUT / 'reference-r2'
    release.require((reference / 'review-receipt.json').is_file(), 'reference_required')
    destination = OUT / 'delivery'
    release.require(not destination.exists(), 'output_exists')
    # Check every source member before copying the package.
    original = release.inventory(SOURCE)
    destination.mkdir()
    payload = OUT / 'payload'
    payload.mkdir()
    shutil.copytree(SOURCE, payload / 'model.mlpackage')
    release.require(release.inventory(SOURCE) == original, 'source_changed')
    contract = dict(schemaVersion=1, preprocessing='yolo-letterbox-v1',
                    manifest=release.read_json(reference / 'manifest.json'),
                    metadata=release.read_json(reference / 'metadata.json'))
    write(payload / 'contract.json', contract)
    (payload / 'NOTICES.txt').write_text(
        'Existing tvOS Run 012 YOLO11n export. Ultralytics export metadata records AGPL-3.0.\n'
        'This pack supports the approved NUIAK/TTR integration review only.\n'
        'No new license or public distribution approval is granted.\n'
        'The maintainer must review applicable terms before public distribution.\n')
    files = release.inventory(payload)
    archive = destination / 'nativeui-tvos-v3.0-review304.zip'
    receipt = release.pack(payload, archive, files)
    entry = dict(modelID='nativeui-tvos-v3.0', artifactVersion='3.0.0-review.304',
        task='element_detection', screenshotDomain='tvOS', modelRoot='model.mlpackage', files=files,
        expandedBytes=sum(f['bytes'] for f in files), **receipt,
        url='https://github.com/SerialForBreakfast/NativeUIAuditKit/releases/download/models-review304/nativeui-tvos-v3.0-review304.zip',
        hosts=[dict(platform='macOS', minimumVersion='14.0',
                    evidence='Package minimum only. Execution verified on macOS 27.0.1 arm64; macOS 14 and Intel unverified.')],
        runtimeContract='nuiak-model-v1', preprocessing='yolo-letterbox-v1',
        tensorContractSHA256=release.digest((payload / 'contract.json').read_bytes()),
        licensePath='NOTICES.txt', qualification='Existing tvOS baseline for observer integration tests only. No navigation authority.',
        sourceRevision=PIN + ': runtime; resident Run 012 export identified by exact member hashes',
        releaseStatus='review-only', approvalReference='')
    release.validate_catalog(dict(schemaVersion=1, models=[entry]))
    release.verify_archive(archive, entry)
    write(destination / 'catalog-review.json', dict(schemaVersion=1, models=[entry]))
    write(destination / 'inventory.json', files)
    write(destination / 'entry.json', entry)
    for name in ('manifest.json', 'metadata.json', 'reference.png', 'reference-results.json', 'review-receipt.json'):
        shutil.copyfile(reference / name, destination / name)
    shutil.copyfile(payload / 'contract.json', destination / 'contract.json')
    write(destination / 'source-inventory.json', original)
    shutil.copyfile(ROOT / 'Research/TTRReview304.md', destination / 'README.md')
    shutil.copyfile(ROOT / 'Tests/NativeUIAuditKitTests/TTRReviewAdapterTests.swift', destination / 'TTRReviewAdapter.swift')
    print(json.dumps(receipt))


def seal():
    destination = OUT / 'delivery'
    final = OUT / 'verified'
    release.require((final / 'review-receipt.json').is_file(), 'final_archive_test_required')
    receipt = release.read_json(final / 'review-receipt.json')
    entry = release.read_json(destination / 'entry.json')
    release.require(receipt['archiveSHA256'] == entry['archiveSHA256'] and receipt['detections'] == '25', 'final_parity')
    release.verify_archive(destination / 'nativeui-tvos-v3.0-review304.zip', entry)
    shutil.copyfile(final / 'review-receipt.json', destination / 'final-archive-receipt.json')
    members = release.inventory(destination)
    archive = OUT / 'nuiak-tvos-review304-handoff.zip'
    result = release.pack(destination, archive, members)
    write(OUT / 'handoff-inventory.json', members)
    write(OUT / 'transfer.json', dict(version=1, requestID='nuiak-tvos-review304-handoff',
        sharedPath='nuiak/nuiak-tvos-review304-handoff.zip', localPath=str(archive.relative_to(ROOT)),
        bytes=result['archiveBytes'], sha256=result['archiveSHA256'], receiptPath=None))
    print(json.dumps(result))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'seal'])
    args = parser.parse_args()
    (prepare if args.action == 'prepare' else seal)()
