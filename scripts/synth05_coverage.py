"""Hash-only retained-evidence overlap and diagnostic SYNTH05 coverage; no admission."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from focus_surface_intake import ROOT, sha, write, require, fresh
from focus_dataset_contract import local
from focus_dataset_contract import validate_manifest
from synth05_intake import verify_package


def hashes(value):
    out = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ('sha256','pixelSHA256','pixel_sha256','imageSHA256') and isinstance(child,str):
                out.add(child)
            out.update(hashes(child))
    elif isinstance(value,list):
        for child in value: out.update(hashes(child))
    return out


def audit(qa, output):
    qa,output=local(qa),fresh(output)
    inventory=json.loads((qa/'review-sheets/inventory.json').read_text())
    pair_keys=set(); labels=defaultdict(set); duplicate_pairs=[]
    for p in inventory['pairs']:
        key=tuple(p['crops'][role]['pixelSHA256'] for role in ('focused','unfocused'))
        if key in pair_keys: duplicate_pairs.append(p['number'])
        pair_keys.add(key)
        for role in ('focused','unfocused'): labels[p['crops'][role]['pixelSHA256']].add(role)
    conflicts=[h for h,v in labels.items() if len(v)>1]
    all_new=hashes(inventory)
    references=[
        ('candidate-and-retention','reports/work/FOCUS-GAP-LIVE-20260929/training-extension/focus_dataset_manifest.json'),
        ('historical-protected-metadata','reports/work/APPEAR-EVAL-RESERVE-20260927/overlap.json'),
        ('surface-validation','reports/work/APPEAR-EVAL-RESERVE-20260927/intake/cinema_rows.json'),
        ('surface-validation','reports/work/APPEAR-EVAL-RESERVE-20260927/intake/album_grid.json'),
        ('protected-challenge-metadata-only','reports/work/APPEAR-EVAL-RESERVE-20260927/intake/memory_mosaic.json'),
        ('protected-challenge-metadata-only','reports/work/APPEAR-EVAL-RESERVE-20260927/intake/icon_shelf.json'),
    ] + [('real-regression',f'reports/work/FOCUS-TTR-TEST-CYCLE-01/batch{i:02d}-protocol.json') for i in (1,2,3)]
    comparisons=[]
    for scope,name in references:
        path=ROOT/name; doc=json.loads(path.read_text()); prior=hashes(doc)
        matches=sorted(all_new & prior)
        comparisons.append(dict(scope=scope,path=name,sha256=sha(path),
                                availableHashCount=len(prior),matchingHashes=matches))
    manifests=sorted(qa.glob('*/focus_dataset_manifest.json'))
    for path in manifests:validate_manifest(json.loads(path.read_text()),path.parent)
    inputs=json.loads((qa/'input-index.json').read_text())
    for entry in inputs['packages']:
        require(sha(ROOT/entry['path'])==entry['sha256'],'changed_package_manifest')
        verify_package(ROOT/entry['path'])
    summary=json.loads((qa/'intake.json').read_text())
    result=dict(version='synth05-coverage-v1',inventorySHA256=sha(qa/'review-sheets/inventory.json'),
        completePairs=len(pair_keys),duplicatePairs=duplicate_pairs,contradictoryCropLabels=conflicts,
        overlap= comparisons, trainingAdmittedPairs=0, independentSourceGroupsEstablished=0,
        conservativeRelatedSourceGroup='fixture-procedural-development',
        uniqueSeeds=sorted({g['recipe']['seed'] for g in summary['groups']}),
        themes=dict(Counter({theme:sum(g['acceptedPairs'] for g in summary['groups'] if g['recipe']['theme']==theme)
                             for theme in {g['recipe']['theme'] for g in summary['groups']}})),
        classes=dict(sum((Counter(g['classes']) for g in summary['groups']),Counter())),
        limitations=['Hash overlap is not source independence or perceptual similarity.',
                     'Protected challenge checked through retained metadata only; no viewing/scoring.',
                     'Capture method and native telemetry are reported by producer, not authenticated attestation.',
                     'Calibration remains development-only; no training reservation reassignment.',
                     'Imported-owned is one generated 32x24 asset, not a photographic corpus.'])
    write(output,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qa',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.qa,a.output)
