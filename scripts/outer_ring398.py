"""Score retained images with the exact received TTR kernel, not a rewritten rule."""
from pathlib import Path
import re
import time
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs, command

OUT=None


def run():
    from hcf_compare371 import summarize
    from hcf_prepare389 import OLD_ROOT
    contract=q.load(OUT.parents[2]/'spec.json')['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(contract,OUT)
        manifest=document(inputs['sourceManifest']);base=checked(inputs['sourceManifest']).parent
        for item in manifest['files']:
            path=base/item['path']
            q.require(path.resolve()==path and path.is_relative_to(base),'source_path')
            q.require(path.stat().st_size==item['bytes'] and q.digest(path)==item['sha256'],'source_hash')
        kernel=checked(inputs['kernel']);records=checked(inputs['geometry']);errors=checked(inputs['errors'])
        q.require(all(any(base/r['path']==p and r['sha256']==q.digest(p) for r in manifest['files'])
                      for p in (kernel,records,errors)),'source_membership')
        match=re.search(r'nonisolated struct NormalizedRectangle:.*?\n}\n',records.read_text(),re.S)
        q.require(match is not None,'geometry_declaration')
        (OUT/'Geometry.swift').write_text('import Foundation\n'+match.group())
        (OUT/'main.swift').write_bytes(checked(inputs['driver']).read_bytes())
        frames={r['id']:r for name in ('catalog','retained') for r in document(inputs[name])['rows']}
        rows=[];requests=[]
        for rule in document(inputs['membership'])['rows']:
            row=frames[rule['id']]
            q.require(row['role'] in ('development','retained'),'audit_locked')
            q.require(all(row[k]==rule[k] for k in ('sha256','group','role','profile')),'image_identity')
            path=Path(row['path'])
            if path.is_relative_to(OLD_ROOT):path=q.ROOT/path.relative_to(OLD_ROOT)
            q.require(path.resolve()==path and path.is_relative_to('/Volumes/training-drive/data/NUIAK'),'image_scope')
            q.require(q.digest(path)==row['sha256'],'image_hash')
            rows.append(row);requests.append(dict(id=row['id'],path=str(path),sha256=row['sha256']))
        q.require(0<len(rows)<=300 and len({r['id'] for r in rows})==len(rows),'membership_limit')
        q.save(OUT/'inputs.json',requests)
        binary=OUT/'outer-ring'
        command(['/usr/bin/xcrun','swiftc','-O','-D','SIMULATOR_COMPANION','-module-cache-path',
                 str(q.ROOT/'.build/standard391-swift-cache'),str(kernel),str(errors),str(OUT/'Geometry.swift'),
                 str(OUT/'main.swift'),'-o',str(binary)],OUT,'compile',timeout=180)
        command([str(binary),str(OUT/'inputs.json'),str(OUT/'raw.json')],OUT,'score',timeout=500)
        raw=q.load(OUT/'raw.json');q.require([r['id'] for r in raw]==[r['id'] for r in rows],'output_membership')
        predictions=[]
        for row,value in zip(rows,raw):
            report=value['report'];q.require(value['sha256']==row['sha256'] and report['navigationEligible'] is False,'output_identity')
            candidates=[]
            for candidate in report['candidates']:
                b=candidate['bounds']
                candidates.append([b['x']*row['width'],b['y']*row['height'],b['width']*row['width'],b['height']*row['height']])
            predictions.append(dict(id=row['id'],candidates=candidates,box=None,decision='abstain',
                reason='Unqualified ring proposals only; no body mapping or focus authority.',report=report))
        result=summarize(rows,predictions)
        result.update(method='TTR-outer-ring-v2-proposals',sourceManifest=inputs['sourceManifest'],
            limitation='All decisions abstain. Use proposals for a separate crop comparison; ring bounds are not body bounds.')
        q.save(OUT/'comparison.json',result)
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
            dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',code=str(error)[:500],modelAccepted=False));raise
