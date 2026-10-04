"""Export existing synthetic consumer fixtures and sanitized exposure, not training data."""
import hashlib
import json
from pathlib import Path
import zipfile
from test_ttr_sidecar_v2 import write_bundle,reindex
from test_harvest_bundle_validation import H1Tests
from harvest_bundle_validation import validate_bundle,HarvestValidationError

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/work/FLOW-CONFORMANCE-124/artifacts'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def edit(p,f):
    d=json.loads(p.read_text());f(d);write(p,d)


def verify_case(root,accepted):
    before={p.name:sha(p) for p in root.iterdir() if p.is_file()}
    try:
        result=validate_bundle(root)
        assert accepted,'invalid case unexpectedly accepted'
        assert not result['eligibleForTraining'] and result['identityEvidence'] is None
        out=dict(accepted=True,trainingEligible=False,provenance=result['provenance'])
    except HarvestValidationError as error:
        assert not accepted,str(error)
        out=dict(accepted=False,reason=str(error),trainingEligible=False)
    assert before=={p.name:sha(p) for p in root.iterdir() if p.is_file()},'validator mutated input'
    return out


def build(destination=BASE, *, exposure_audit=None, exposure_hash=None, expected_images=282):
    assert destination.is_relative_to(ROOT) and destination.resolve()==destination and not destination.exists()
    destination.mkdir(parents=True);pack=destination/'pack';pack.mkdir()
    names=['valid_v2','partial_receipt','unsupported_layout','altered_image','corrupt_image',
           'missing_member','duplicate_index','viewport_mismatch','stale_observed_focus','invalid_bounds','cross_split_baseline']
    cases=[]
    for name in names:
        root=pack/name
        if name=='cross_split_baseline':
            root.mkdir();fixture=H1Tests();fixture.d=root;fixture.write_bundle()
            fixture.test_cross_split_shared_baseline_fails_closed()
        else:
            write_bundle(root)
            if name=='partial_receipt':edit(root/'harvest-receipt.json',lambda d:d.update(outcome='partial'))
            elif name=='unsupported_layout':edit(root/'dataset-index.json',lambda d:d.update(datasetLayoutVersion=99))
            elif name=='altered_image':(root/'f.png').write_bytes((root/'f.png').read_bytes()+b'changed')
            elif name=='corrupt_image':(root/'f.png').write_bytes(b'not PNG');reindex(root)
            elif name=='missing_member':(root/'f.png').unlink()
            elif name=='duplicate_index':edit(root/'dataset-index.json',lambda d:d['artifacts'].append(d['artifacts'][0]))
            elif name=='viewport_mismatch':
                edit(root/'m.json',lambda d:d['focused_capture'].update(frame_width=63));reindex(root)
            elif name=='stale_observed_focus':
                edit(root/'m.json',lambda d:d['focused_capture']['after_scene']['focus_observation'].update(observedID='wrong'));reindex(root)
            elif name=='invalid_bounds':
                edit(root/'m.json',lambda d:d['elements'][0].update(pixel_bounds=[0,0,999,999]));reindex(root)
        cases.append(dict(id=name,expected=verify_case(root,name=='valid_v2')))
    audit=exposure_audit or ROOT/'reports/work/TRANSITION-COVERAGE-119/artifacts/audit/report.json'
    expected_hash=exposure_hash or 'a637256160afc73f83941f296c8cb7f99ea89ece1b25a7eacfc12b66d89bf085'
    assert sha(audit)==expected_hash,'changed exposure source'
    source=json.loads(audit.read_text());rows=[]
    for row in source['exposure']:
        assert row['currentRole']=='training_exposed' and row['finalEligible'] is False
        rows.append(dict(sha256=row['image']['sha256'],ancestry=row['ancestry'],role='training_exposed',finalEligible=False))
    assert len(rows)==len({r['sha256'] for r in rows})==expected_images
    write(pack/'exposure.json',dict(version=1,sourceAuditSHA256=sha(audit),knownImages=rows,
        absentHashMeaning='unknown_not_independent',independentFinalMembership=[],
        scope='Current DTM030 transition lane only; not a universal NUIAK dataset registry'))
    sources=['scripts/harvest_bundle_validation.py','scripts/harvest_sidecar_v2.py','scripts/harvest_target_coverage.py',
             'scripts/test_ttr_sidecar_v2.py','scripts/test_harvest_bundle_validation.py','Research/schemas/category_map.json',
             'scripts/build_conformance124.py']
    write(pack/'contract.json',dict(version='nuiak-consumer-conformance-v1',consumerContract='harvest-compatibility-v1',
        testOnly=True,trainingEligible=False,cases=cases,sourceHashes={s:sha(ROOT/s) for s in sources},
        limitations=['No genuine capture or model accuracy','No full newer-producer feature coverage',
                     'No runtime crop or global ancestry qualification','Body versus focus-effect geometry remains distinct']))
    members=[dict(path=p.relative_to(pack).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(pack.rglob('*')) if p.is_file()]
    write(pack/'manifest.json',dict(version=1,files=members,testOnly=True,privateCaptures=False))
    archive=destination/'nuiak-conformance-exposure-v1.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(pack.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(pack).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(set(z.namelist())) and sum(i.file_size for i in z.infolist())<1_048_576
        for row in members:
            data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    report=dict(cases=cases,exposureImages=len(rows),archiveBytes=archive.stat().st_size,archiveSHA256=sha(archive),
                members=len(members)+1,readOnlyValidation=True,privateCaptures=False,trainingEligible=False)
    write(destination/'report.json',report);print(json.dumps(report,indent=2))
    return report


if __name__=='__main__':build()
