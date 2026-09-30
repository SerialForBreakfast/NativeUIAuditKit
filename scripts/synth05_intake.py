"""SYNTH05 immutable manifest verification, existing importer/crop QA and accounting."""
import argparse
from collections import Counter
import json
from pathlib import Path

from focus_surface_intake import ROOT, fresh, require, sha, write
from harvest_bundle_validation import validate_bundle
from ttr_focus_manifest import derive
from focus_fixture_review import prepare


def verify_package(path):
    doc = json.loads(path.read_text())
    entries = doc['files']
    seen = set()
    source = 'base_revision' in doc
    for entry in entries:
        name = entry['path']
        require(isinstance(name, str) and name not in seen and not Path(name).is_absolute()
                and '..' not in Path(name).parts and '\\' not in name, 'manifest_member_path')
        seen.add(name)
        file = path.parent / ('proposed' if source else '') / name
        require(file.is_file() and not file.is_symlink() and file.stat().st_size == entry['bytes']
                and sha(file) == entry['sha256'], 'member_integrity:' + name)
        if source and entry.get('base_sha256') is not None:
            base = path.parent / 'base' / name
            require(base.is_file() and sha(base) == entry['base_sha256'], 'base_integrity:' + name)
    if not source:
        actual = {str(p.relative_to(path.parent)) for p in path.parent.rglob('*') if p.is_file()}
        require(actual == seen | {path.name}, 'unlisted_capture_member')
    return {'path':str(path.relative_to(ROOT)), 'sha256':sha(path), 'membersVerified':len(entries)}


def run(received, output):
    received = received.resolve(); output = fresh(output)
    packages = sorted(received.glob('*pilot*/MANIFEST.json')) + sorted(received.glob('*pilot*/manifest.json'))
    packages += sorted(received.glob('*T*/*/manifest.json'))
    require(len(packages) == 4, 'missing_packages')
    frozen = [verify_package(p) for p in packages]
    output.mkdir(parents=True)
    write(output/'input-index.json', {'version':'synth05-input-index-v1','packages':frozen,
                                    'receipts':json.loads((received/'receipt.json').read_text())})
    results, manifests = [], []
    for index in sorted(received.glob('*pilot*/**/dataset-index.json')):
        bundle = index.parent
        key = bundle.parent.name + '-' + bundle.name
        rows = json.loads((bundle/'manifest.json').read_text())
        result = {'group':key,'rows':len(rows),'source':str(bundle.relative_to(ROOT)),
                  'rowDispositions':[]}
        try:
            contract = validate_bundle(bundle)
            document = derive(bundle, output/key, key, 'TTR SYNTH05 afc948ca plus received recovery delta',
                              test_only=True)
            manifests.append(output/key/'focus_dataset_manifest.json')
            result.update(acceptedPairs=len(document['pairs']), rejectedPairs=0, blockedPairs=0,
                          cropCount=2*len(document['pairs']), targetCoverage=contract['targetCoverage'],
                          classes=dict(Counter(p['element_type'] for p in document['pairs'])),
                          normalizedOriginSplits=dict(Counter(p['original_split'] for p in document['pairs'])),
                          rawSplits=dict(Counter(r['split'] for r in rows)))
            recipe = contract['usableRows'][0]['recipe']
            result['recipe'] = recipe
            result['sourceDescription'] = contract.get('sourceDescription')
            result['rowDispositions'] = [{'id':r['id'],'state':'accepted-diagnostic-only'} for r in rows]
        except (OSError, ValueError, TypeError, KeyError) as error:
            result.update(acceptedPairs=0, rejectedPairs=0, blockedPairs=len(rows), error=str(error))
            result['rowDispositions'] = [{'id':r.get('id'),'state':'blocked','reason':str(error)} for r in rows]
        results.append(result)
        write(output/(key+'-disposition.json'), result)
        print(key, result['acceptedPairs'], result['blockedPairs'], result.get('error',''),flush=True)
    review = prepare(manifests, output/'review-sheets') if manifests else None
    report = {'version':'synth05-intake-v1','groups':results, 'trainingApproval':False,
              'inputIndex':'input-index.json','visualReview':'pending',
              'totals':{k:sum(r.get(k,0) for r in results) for k in
                        ('rows','acceptedPairs','rejectedPairs','blockedPairs','cropCount')},
              'pixels':{k:review[k] for k in ('frameFiles','distinctFramePixels','distinctCropPixels')} if review else {}}
    write(output/'intake.json',report)
    for p in packages: verify_package(p)
    print(json.dumps({'totals':report['totals'],'pixels':report['pixels']}),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--received', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.received, args.output)
