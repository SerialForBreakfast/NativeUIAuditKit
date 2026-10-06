"""Freeze native page-style coverage; planning never launches a simulator."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import uuid
import os
import plistlib
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
AXES=(('account-summary210','document-stack210'),('light','dark'),
      ('automatic','prominent'),(False,True),(3,5,9),('leading','center','trailing'))


def catalog(target):
    if str(uuid.UUID(target)).upper()!=target:
        raise ValueError('exact_uppercase_target_required')
    rows=[]
    for n,(family,theme,style,interaction,pages,position) in enumerate(itertools.product(*AXES)):
        # Related appearance variants stay together regardless of eventual data role.
        group=f'{family}:pages{pages}:position{position}'
        rows.append(dict(id=f'style210-{n:03d}',family=family,theme=theme,
            backgroundStyle=style,interaction=interaction,pages=pages,position=position,
            seed=210000+n,group=group))
    return dict(version='native-style210-v1',target=target,role='training_candidate',
                trainingEligible=False,members=rows)


def validate(value):
    if value != catalog(value['target']):
        raise ValueError('changed_catalog')
    return value


def execute(path):
    path=path.absolute()
    if path.resolve()!=path or not path.is_relative_to(ROOT):raise ValueError('catalog_boundary')
    raw=path.read_bytes();doc=validate(json.loads(raw));target=doc['target']
    devices=json.loads(subprocess.check_output(['xcrun','simctl','list','devices','available','-j']))
    selected=[(r,d) for r,ds in devices['devices'].items() for d in ds if d['udid']==target]
    if len(selected)!=1 or selected[0][1]['state']!='Booted' or 'iOS-26-5' not in selected[0][0]:
        raise ValueError('wrong_or_unready_runtime')
    if shutil.disk_usage(ROOT).free < 4*1024**3:raise ValueError('storage_reserve')
    products=ROOT/'.build/native-page150/Build/Products'
    base=products/'GeneratorRunnerTests_iphonesimulator27.0-arm64.xctestrun'
    run=plistlib.loads(base.read_bytes());env=run['GeneratorRunnerTests'].setdefault('EnvironmentVariables',{})
    env.update(NUA_STYLE210='capture',NUA_STYLE210_TARGET=target,
               NUA_STYLE210_CATALOG=str(path),NUA_STYLE210_SHA256=hashlib.sha256(raw).hexdigest())
    output=path.parent/'execution01'
    if output.exists():raise ValueError('execution_collision')
    output.mkdir()
    configuration=products/'style210-execution01.xctestrun'
    with configuration.open('xb') as stream:plistlib.dump(run,stream)
    command=['xcodebuild','test-without-building','-xctestrun',str(configuration),
             '-destination','platform=iOS Simulator,id='+target,'-parallel-testing-enabled','NO',
             '-only-testing:GeneratorRunnerTests/NativePageStyle210Test/testCaptureStyle210',
             '-resultBundlePath',str(output/'capture.xcresult')]
    def write(name,value):
        with (output/name).open('x') as stream:json.dump(value,stream,indent=2)
    pins=[]
    for p in [products/'Debug-iphonesimulator/GeneratorRunner.app/GeneratorRunner',
              products/'Debug-iphonesimulator/GeneratorRunner.app/PlugIns/GeneratorRunnerTests.xctest/GeneratorRunnerTests',
              ROOT/'GeneratorRunner/GeneratorRunnerTests/KitchenSinkValidationTest.swift']:
        pins.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    write('launch.json',dict(command=command,catalogSHA256=hashlib.sha256(raw).hexdigest(),pins=pins,
          target=selected[0],storage='authorized exact simulator container; host outputs project-local'))
    start=time.monotonic()
    with (output/'capture.log').open('x') as stream:
        try:
            result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=720,
                                  env=dict(os.environ,TMPDIR=str(ROOT/'.build/tmp')))
            code=result.returncode
        except subprocess.TimeoutExpired:
            code='timeout'
    write('terminal.json',dict(exitCode=code,seconds=time.monotonic()-start))
    if code!=0:raise ValueError('capture_failed_preserve_evidence')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target');p.add_argument('--output',type=Path)
    p.add_argument('--execute-catalog',type=Path)
    a=p.parse_args()
    if a.execute_catalog:
        if a.target or a.output:raise ValueError('exclusive_execution_mode')
        execute(a.execute_catalog);return
    if not a.target or not a.output:raise ValueError('planning_inputs_required')
    doc=validate(catalog(a.target));out=a.output.absolute()
    if not out.is_relative_to(ROOT) or out.resolve()!=out or out.exists():
        raise ValueError('output_boundary_collision')
    raw=(json.dumps(doc,sort_keys=True,indent=2)+'\n').encode()
    with out.open('xb') as stream:stream.write(raw)
    print(json.dumps(dict(recipes=144,groups=18,sha256=hashlib.sha256(raw).hexdigest(),
                          captureExecuted=False,trainingEligible=False)))


if __name__=='__main__':main()
