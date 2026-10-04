"""Verify existing DTM025 CLI and package metadata-only consumer conformance tests.

No training, capture, model export or producer mutation. All outputs are new and
project-local. The existing delivered synthetic pixels are used only locally.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
import shadow_feedback_contract as c
from test_shadow_feedback_contract import case, module

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/work/TRANSITION-SHADOW-106/artifacts'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main(out):
    out=out.resolve();out.relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    tool=ROOT/'.build/arm64-apple-macosx/release/TransitionShadowTool'
    delivery=BASE/'delivery'; bundle=BASE/'bundle'
    request=json.loads((delivery/'sample-request.template.json').read_text().replace('$ROOT',str(delivery)))
    contract=digest(bundle/'contract.json'); results=[]
    for name in ('off','score','wrong-hash'):
        value=copy.deepcopy(request);value['mode']='off' if name=='off' else 'score'
        selected_bundle=bundle
        if name=='off':
            value['pairs'][0]['before']['path']=str(delivery/'absent.png')
            selected_bundle=out/'absent-model'
        if name=='wrong-hash':value['pairs'][0]['before']['sha256']='0'*64
        path=out/(name+'-request.json');reply=out/(name+'-reply.json');write(path,value)
        start=time.monotonic()
        execution=subprocess.run([str(tool),'--bundle',str(selected_bundle),'--manifest-sha256',contract,
            '--request',str(path),'--output',str(reply)],capture_output=True,text=True,timeout=60)
        (out/(name+'-stderr.txt')).write_text(execution.stderr)
        c.require(execution.returncode==(1 if name=='wrong-hash' else 0),'cli_exit_'+name)
        raw=c.load(reply);p=value['pairs'][0]
        binding=dict(case_id=p['id'],action_id=p['actionID'],before_observation_id=p['beforeObservationID'],
            after_observation_id=p['afterObservationID'],before_sha256=p['before']['sha256'],after_sha256=p['after']['sha256'])
        label=dict(binding=binding,source='unknown',relation='unknown',review_id='')
        normalized=c.normalize_cli(path.read_bytes(),raw,[label],test_only=True)
        write(out/(name+'-evaluation.json'),normalized)
        c.require(normalized['accounting']['assessed']==0,'invented_truth')
        if name=='score':
            expected=c.load(delivery/'synthetic-expected.json');actual=raw['results'][0]
            c.require(actual['encodedSHA256']==expected['encodedSHA256'] and actual['decision']==expected['decision']
                and abs(actual['probability']-expected['probability'])<=1e-5,'synthetic_parity')
        if name=='wrong-hash':c.require(raw['results'][0]['error']=='changedBytes','wrong_error')
        results.append(dict(case=name,exit_code=execution.returncode,seconds=time.monotonic()-start,
            state=raw['results'][0]['state'],model_loaded=raw['modelLoaded'],reply_sha256=digest(reply),
            evaluation_sha256=digest(out/(name+'-evaluation.json'))))
    package=out/'package';package.mkdir()
    for name in ('shadow_feedback_contract.py','test_shadow_feedback_contract.py'):
        shutil.copy2(ROOT/'scripts'/name,package/name)
    shutil.copy2(ROOT/'reports/work/SHADOW-CONTRACT-110/validation-guide.md',package/'README.md')
    cases=[case(),case('native_hint'),case(relation='unchanged'),case(probability=.5),case('unknown','unknown')]
    cases[2]['context']['content_motion']='animated'
    for state in sorted(c.STATES-{'scored'}):
        item=case();item['prediction'].update(state=state,probability=None,decision=None);cases.append(item)
    for n,item in enumerate(cases):
        for section in (item,item['prediction'],item['label']):section['binding']['case_id']=f'synthetic-{n}'
    doc=dict(version=c.VERSION,test_only=True,cases=cases,module_cases=[module(),module(module_present=True),
        module(enabled=True,state='model_unavailable'),module(module_present=True,enabled=True,state='scored',
            model_loads=1,pixel_reads=2,inference_calls=1)])
    write(package/'synthetic-cases.json',doc);write(package/'synthetic-expected.json',c.run(doc))
    manifest=dict(schema_version=1,test_only=True,private_images=False,models_included=False,
        members=[dict(path=p.name,bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(package.iterdir())])
    write(package/'manifest.json',manifest)
    archive=out/'nuiak-shadow-contract110-v1.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(package.iterdir()):z.write(path,path.name)
    verification=dict(real_cli=results,tool_sha256=digest(tool),contract_sha256=contract,
        artifact=dict(file=archive.name,bytes=archive.stat().st_size,sha256=digest(archive)),
        software_verified=True,data_eligible=False,live_integration_qualified=False,model_gate_passed=False)
    write(out/'verification.json',verification);print(json.dumps(verification,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
