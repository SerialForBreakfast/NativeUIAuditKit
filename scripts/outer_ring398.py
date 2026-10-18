"""Score retained images with the exact received TTR kernel, not a rewritten rule."""
from pathlib import Path
import re
import time
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs, command

OUT=None
# B405-119: frozen kernel settings. `frozen-v2` compiles the received kernel unchanged (the default).
# `relaxed-v1` lowers the brightness, side-support and contrast gates by fixed amounts. Geometry gates stay.
# Each replacement must match the received source exactly the listed number of times.
KERNEL_SETTINGS={
    'frozen-v2':[],
    'relaxed-v1':[
        ('static let version = "outer-ring-v2"','static let version = "outer-ring-v2-relaxed-v1"',1),
        ('pixels[seed] >= 160','pixels[seed] >= 128',1),
        ('pixels[n] >= 160','pixels[n] >= 128',1),
        ('peak >= 160.0/255 && delta >= 0.12','peak >= 128.0/255 && delta >= 0.08',1),
        ('support >= 0.65, contrast >= 0.12','support >= 0.50, contrast >= 0.08',1)],
    # B405-148: sides shorter than 48 analysis px sample their middle third, not their middle 60 %.
    # B405-147 shows that short rounded sides of small controls fail side support at the corners. All gates stay.
    'short-side-v1':[
        ('static let version = "outer-ring-v2"','static let version = "outer-ring-v2-short-side-v1"',1),
        ('let inset = max(1, (hi - lo) / 5)','let inset = max(1, (hi - lo) / (hi - lo < 48 ? 3 : 5))',1)],
    # B405-150: draw the 960 px analysis buffer with high-quality interpolation. B405-148 shows that the
    # low-quality drawing erases thin rings on some sides. All gates and the analysis size stay.
    'interpolation-high-v1':[
        ('static let version = "outer-ring-v2"','static let version = "outer-ring-v2-interpolation-high-v1"',1),
        ('context.interpolationQuality = .low','context.interpolationQuality = .high',1)],
    # B405-152: exactly the drawing change of interpolation-high-v1 plus the sampling change of short-side-v1.
    'interpolation-high-short-side-v1':[
        ('static let version = "outer-ring-v2"','static let version = "outer-ring-v2-interpolation-high-short-side-v1"',1),
        ('context.interpolationQuality = .low','context.interpolationQuality = .high',1),
        ('let inset = max(1, (hi - lo) / 5)','let inset = max(1, (hi - lo) / (hi - lo < 48 ? 3 : 5))',1)],
    # B405-155: the combined setting plus a 2 px wider inner dark-moat search. Thick rings keep offset 3 bright.
    'interpolation-high-short-side-inner-v1':[
        ('static let version = "outer-ring-v2"','static let version = "outer-ring-v2-interpolation-high-short-side-inner-v1"',1),
        ('context.interpolationQuality = .low','context.interpolationQuality = .high',1),
        ('let inset = max(1, (hi - lo) / 5)','let inset = max(1, (hi - lo) / (hi - lo < 48 ? 3 : 5))',1),
        ('let inner = (1...band).map','let inner = (1...(band + 2)).map',1)],
}


def kernel_source(kernel,settings,out):
    """Return the kernel source to compile. Only a listed setting rewrites a copy in the job output."""
    q.require(settings in KERNEL_SETTINGS,'kernel_settings')
    if settings=='frozen-v2':return kernel
    text=kernel.read_text()
    for old,new,count in KERNEL_SETTINGS[settings]:
        q.require(text.count(old)==count,'kernel_settings_source_changed')
        text=text.replace(old,new)
    path=out/kernel.name;path.write_text(text)
    q.save(out/'kernel-settings.json',dict(version='outer-ring-kernel-settings-v1',settings=settings,
        source=dict(path=q.relative(kernel),sha256=q.digest(kernel)),compiled=dict(path=path.name,sha256=q.digest(path)),
        replacements=[dict(old=o,new=n) for o,n,_ in KERNEL_SETTINGS[settings]]))
    return path


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
        settings=contract['parameters'].get('kernelSettings','frozen-v2')
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
                 str(q.ROOT/'.build/standard391-swift-cache'),str(kernel_source(kernel,settings,OUT)),str(errors),str(OUT/'Geometry.swift'),
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
        result.update(method='TTR-outer-ring-v2-proposals'+('' if settings=='frozen-v2' else '-'+settings),
            sourceManifest=inputs['sourceManifest'],
            limitation='All decisions abstain. Use proposals for a separate crop comparison; ring bounds are not body bounds.')
        q.save(OUT/'comparison.json',result)
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
            dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',code=str(error)[:500],modelAccepted=False));raise
