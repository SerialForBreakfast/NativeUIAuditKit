"""Build a bounded portable cached-evidence review pack; no remote operations."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'reports/work/EVIDENCE-223/artifacts/worker-pack01'
    out.mkdir()  # Deliberate collision rejection.
    manifest=json.loads((ROOT/'reports/work/EVIDENCE-223/inputs.json').read_text())
    names=['focus_evidence','review_focus_evidence','test_focus_evidence',
           'harvest_schema4_review','harvest_bundle_validation','harvest_sidecar_v2',
           'harvest_target_coverage','harvest_artwork','harvest_artwork_geometry','fixture_rendered_body']
    files=['scripts/'+n+'.py' for n in names]+['Research/schemas/category_map.json']
    for name in files:
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,dest)
    for key,ref in manifest['inputs'].items():
        raw=(ROOT/ref['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==ref['sha256']
        dest=out/'inputs'/f'{key}.json';dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(raw);ref['path']=f'inputs/{key}.json'
    (out/'inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=out.with_suffix('.zip')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(out))
    print(json.dumps({'path':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,
                      'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))

if __name__=='__main__':main()
