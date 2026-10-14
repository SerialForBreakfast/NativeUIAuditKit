"""Run the existing Vision helper and record an observation-only consumer receipt."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from observer_identity398 import compiled_digest


def run(request, tool, bundle_sha, revision):
    if request.get('version')!=1 or request.get('mode')!='vision':
        raise ValueError('observer_requires_vision_v1')
    if len(bundle_sha)!=64 or any(c not in '0123456789abcdef' for c in bundle_sha):
        raise ValueError('observer_bundle_hash')
    root=Path(request['root']).resolve(); tool=Path(tool).resolve()
    if not tool.is_relative_to(root/'.build') or tool.name!='FocusRingTool' or not (root/'Package.swift').is_file():
        raise ValueError('observer_tool_boundary')
    model=Path(request['model']).resolve()
    if not model.is_relative_to(root): raise ValueError('observer_model_boundary')
    before=compiled_digest(model)
    with tempfile.TemporaryDirectory(dir=root/'.build',prefix='observer398-') as scratch:
        result=subprocess.run([str(tool)],input=json.dumps(request),capture_output=True,text=True,timeout=120,
                              env=dict(os.environ,TMPDIR=scratch))
    if result.returncode: raise ValueError('observer_vision_failed')
    value=json.loads(result.stdout); actual=value['results']; items=request['items']
    if [r['id'] for r in actual]!=[r['id'] for r in items]: raise ValueError('observer_membership')
    after=compiled_digest(model)
    if before!=after: raise ValueError('observer_loaded_bytes_changed')
    rows=[dict(id=r['id'],candidateID=i['id'],parentSHA256=i['sha256'],bounds=i['bounds'],
               modelInputRGBSHA256=r['modelInputRGBSHA256'],score=r['probability'],state='scored')
          for i,r in zip(items,actual)]
    return dict(version='ttr-crop-observer-v2',bundleSHA256=bundle_sha,navigationAuthority=False,
        backend='Vision',compiledDigestAlgorithm='compiled-tree-sha256-v1',compiledBeforeSHA256=before,
        compiledAfterSHA256=after,sourceRevision=revision,results=rows,host=value.get('host'),
        limitation='Observation only. Caller must supply consumer OS, architecture, and compiler identity before qualification.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('request','tool','bundle-sha256','source-revision','output'): parser.add_argument('--'+arg,required=True)
    args=parser.parse_args()
    try:
        request=json.loads(Path(args.request).read_text())
        receipt=run(request,args.tool,args.bundle_sha256,args.source_revision)
        receipt.update(osVersion=subprocess.check_output(['/usr/bin/sw_vers','-productVersion'],text=True).strip(),
            architecture=os.uname().machine,
            compilerVersion=subprocess.check_output(['/usr/bin/xcrun','swiftc','--version'],text=True).strip())
        with Path(args.output).open('x') as stream: json.dump(receipt,stream,indent=2)
    except Exception as error:
        raise SystemExit('observer failed: '+str(error))
