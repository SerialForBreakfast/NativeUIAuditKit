"""Replay source-bound recipe-layer vectors with the actual NUIAK resolver."""
import argparse
from pathlib import Path
import json
from harvest_schema4_review import read,decode,digest,require,hydrate_recipe

EXPECTED={'accepted':'accepted','missing or ambiguous source reference':'missing_or_linked_file',
          'unsafe source reference':'unsafe_path','source size mismatch':'source_size',
          'source hash mismatch':'source_hash','source reference version':'source_reference_version',
          'canonical recipe identity mismatch':'source_identity'}


def replay(root):
    root=Path(root).absolute();require(root.resolve()==root,'input_boundary')
    raw=read(root,'manifest.json');manifest=decode(raw)
    require(type(manifest.get('version')) is int and manifest['version']==1,'manifest_version')
    files=manifest['files'];cases=manifest['cases']
    require(0<len(files)<=100 and 0<len(cases)<=100,'vector_count')
    names=set()
    for f in files:
        require(f['path'] not in names,'duplicate_member');names.add(f['path'])
        data=read(root,f['path']);require(len(data)==f['bytes'] and digest(data)==f['sha256'],'vector_integrity')
    results=[];ids=set()
    for case in cases:
        require(case['id'] not in ids and case['recipe'] in names and case['expected'] in EXPECTED,'case_contract');ids.add(case['id'])
        recipe=decode(read(root,case['recipe']))
        try:hydrate_recipe(root,recipe);observed='accepted'
        except ValueError as exc:observed=str(exc)
        results.append(dict(id=case['id'],expected=EXPECTED[case['expected']],observed=observed,
                            passed=observed==EXPECTED[case['expected']]))
    return dict(manifestSHA256=digest(raw),cases=results,passed=all(c['passed'] for c in results),
                trainingEligible=False,scope='recipe_hydration_only')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();project=Path(__file__).resolve().parents[1]
    require(args.output.absolute().resolve().is_relative_to(project),'output_boundary')
    result=replay(args.root)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2)
    print(f'{sum(c["passed"] for c in result["cases"])}/{len(result["cases"])} matched')
    raise SystemExit(0 if result['passed'] else 1)
