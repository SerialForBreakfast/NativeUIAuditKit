"""One source-pinned native placement batch; no TTR, trainer, or implicit retries."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import time
import numpy as np
from PIL import Image,ImageDraw
import diagnostic171 as d
import native_repair159 as n
import validate_reconstructed_corpus as validator
h=n.h
OUT=h.ROOT/'reports/work/IOS-NATIVE-172/attempt05/artifacts'
PRODUCTS=h.ROOT/'.build/native-page150/Build/Products'


def planned(doc):
    h.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}),'plan_seal')
    h.checked(h.ROOT,doc['sourceCatalog'])
    expected=d.catalog(h.read(n.CATALOG))
    h.require(doc['rows']==expected['rows'] and not doc['trainingEligible'],'changed_plan')
    first={}
    for row in doc['rows']:
        first.setdefault((row['family'],row['scale'],row['theme']),row['group'])
    phases={key:[] for key in ('qualification','batch')}
    for row in doc['rows']:
        key='qualification' if row['group'] in first.values() else 'batch'
        phases[key].append(dict(row['recipe'],id=row['id'],group=row['group'],placement=row['placement'],tint=row['tint']))
    h.require(len(phases['qualification'])==24 and len(phases['batch'])==264,'phase_membership')
    return phases


def prepare():
    h.require(not OUT.exists(),'output_collision')
    phases=planned(h.read(d.OUT/'native-batch-plan.json'))
    sources=[h.ref(p) for root in ('NativeUIDatasetGenerator','GeneratorRunner/GeneratorRunnerTests')
             for p in sorted((h.ROOT/root).rglob('*.swift'))]
    binary=PRODUCTS/'Debug-iphonesimulator/GeneratorRunner.app/PlugIns/GeneratorRunnerTests.xctest/GeneratorRunnerTests'
    app=PRODUCTS/'Debug-iphonesimulator/GeneratorRunner.app/GeneratorRunner'
    pins=dict(sources=sources,binaries=[h.ref(binary),h.ref(app)],plan=h.ref(d.OUT/'native-batch-plan.json'))
    OUT.mkdir(parents=True)
    for phase,rows in phases.items():
        h.write(OUT/(phase+'-catalog.json'),dict(version='native-placement-capture-v1',target=n.TARGET,split='train',members=rows,**pins),sealed=True)
    print('Prepared24 qualification and264 remaining recipes; no simulator mutation')


def catalog(phase):
    path=OUT/(phase+'-catalog.json');doc=h.read(path)
    h.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}),'catalog_seal')
    for ref in doc['sources']+doc['binaries']+[doc['plan']]:h.checked(h.ROOT,ref)
    h.require(doc['members']==planned(h.read(d.OUT/'native-batch-plan.json'))[phase],'catalog_membership')
    return path,doc


def execute(phase):
    path,doc=catalog(phase)
    if phase=='batch':
        qualified=h.read(OUT/'qualification-audit.json')
        h.require(qualified['seal']==h.digest({k:v for k,v in qualified.items() if k!='seal'}) and qualified['accepted']==24,'qualification_missing')
        for row in qualified['rows']:
            for key in ('image','annotation','hidden'):h.checked(h.ROOT,row[key])
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'insufficient_space')
    live=subprocess.check_output(['xcrun','simctl','list','devices','available','-j'],timeout=15)
    import json
    devices=[(runtime,x) for runtime,items in json.loads(live)['devices'].items() for x in items if x['udid']==n.TARGET]
    h.require(len(devices)==1 and devices[0][0].endswith('iOS-26-5') and devices[0][1]['isAvailable'] and devices[0][1]['name']=='iPhone 17 Pro','wrong_target')
    h.require(devices[0][1]['state']=='Booted','runtime_not_booted')
    container=Path(subprocess.check_output(['xcrun','simctl','get_app_container',n.TARGET,'com.nativeuiauditkit.generatorrunner','data'],timeout=15).decode().strip())
    h.require(not (container/'Documents'/('native-placement172-'+phase+'-r4')).exists(),'native_output_collision')
    result=OUT/(phase+'.xcresult');log=OUT/(phase+'.log')
    h.require(not result.exists() and not log.exists(),'execution_collision')
    candidates=[p for p in PRODUCTS.glob('*.xctestrun') if not p.name.startswith('placement172-')]
    h.require(len(candidates)==1,'ambiguous_test_product')
    run=plistlib.loads(candidates[0].read_bytes());env=run['GeneratorRunnerTests'].setdefault('EnvironmentVariables',{})
    env.update(NUA_PAGE_REGEN_EXECUTE='approved-172',NUA_PAGE_REGEN_TARGET=n.TARGET,
               NUA_PAGE_REGEN_CATALOG=str(path),NUA_PAGE_REGEN_SHA256=h.sha(path))
    execution=PRODUCTS/('placement172-attempt05-'+phase+'.xctestrun')
    h.require(not execution.exists(),'test_configuration_collision')
    with execution.open('xb') as f:plistlib.dump(run,f)
    cmd=['xcodebuild','test-without-building','-xctestrun',str(execution),'-destination','platform=iOS Simulator,id='+n.TARGET,
         '-parallel-testing-enabled','NO','-only-testing:GeneratorRunnerTests/PageDotRegenerationTest/testNativePageRepair159',
         '-resultBundlePath',str(result)]
    started=time.monotonic()
    h.write(OUT/(phase+'-execution.json'),dict(command=cmd,catalog=h.ref(path),target=devices[0],
        storageScope='Approved exact Simulator runtime/app container; explicit output project-local',limitSeconds=1900))
    with log.open('xb') as f:
        completed=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=1900,env=dict(os.environ,TMPDIR=str(h.ROOT/'.build/tmp')))
    h.write(OUT/(phase+'-terminal.json'),dict(exitCode=completed.returncode,seconds=time.monotonic()-started,log=h.ref(log)))
    h.require(completed.returncode==0,'native_execution_failed')
    print('native terminal',phase,completed.returncode)


def retrieve(phase):
    _,doc=catalog(phase)
    terminal=h.read(OUT/(phase+'-terminal.json'));h.require(terminal['exitCode']==0,'unfinished_capture')
    log=h.checked(h.ROOT,terminal['log']).read_text()
    emitted=re.findall(r'^NATIVE159_COMPLETE (.+)$',log,re.MULTILINE)
    h.require(len(emitted)==1,'missing_final_container')
    root=Path(emitted[0]);container=root.parent.parent
    h.require(root.name=='native-placement172-'+phase+'-r4' and root.parent.name=='Documents','output_identity')
    # XCTest may shut down its owned simulator after the test. Use the freshly
    # emitted final path and container metadata, never a prior installation UUID.
    metadata=plistlib.loads((container/'.com.apple.mobile_container_manager.metadata.plist').read_bytes())
    h.require(metadata['MCMMetadataIdentifier']=='com.nativeuiauditkit.generatorrunner','container_owner')
    h.require(root.is_absolute() and n.TARGET in root.parts and root.resolve()==root,'container_identity')
    receiptpath=root/'receipt.json'
    h.require(receiptpath.is_file() and not receiptpath.is_symlink() and receiptpath.stat().st_size<4*1024**2,'receipt_file')
    receipt=json.loads(receiptpath.read_text())
    h.require(receipt['version']=='native-placement-receipt-v1' and receipt['target']==n.TARGET and
              receipt['catalogSHA256']==h.sha(OUT/(phase+'-catalog.json')),'receipt_identity')
    names={'receipt.json'}|{r['id']+suffix for r in doc['members'] for suffix in ('.png','-hidden.png','.json')}
    h.require({p.name for p in root.iterdir()}==names,'file_membership')
    files=[root/name for name in sorted(names)]
    h.require(all(p.is_file() and not p.is_symlink() for p in files),'unsafe_member')
    size=sum(p.stat().st_size for p in files)
    h.require(size<2*1024**3 and shutil.disk_usage(h.ROOT).free>size+5*1024**3,'retrieval_space')
    dest=OUT/(phase+'-capture');h.require(not dest.exists(),'retrieval_collision');dest.mkdir()
    refs=[]
    for p in files:
        before=h.sha(p);out=dest/p.name;shutil.copyfile(p,out)
        h.require(h.sha(out)==before,'transfer_hash');refs.append(h.ref(out))
    h.write(OUT/(phase+'-retrieval.json'),dict(source=str(root),bytes=size,files=refs),sealed=True)
    print('retrieved',phase,len(files),size)


def check_position(recipe,row,actual):
    v=row['resolvedVariation'];w=recipe['width']/recipe['scale']
    h.require(v['placement']==recipe['placement'] and v['tint']==recipe['tint'] and v['rtl']==(recipe['layoutDirection']=='rtl'),'variation_identity')
    h.require(abs(actual[0]+actual[2]/2-v['requestedCenterX'])<=2,'rendered_position')
    h.require(actual[0]>=20 and actual[0]+actual[2]<=w-20,'safe_margins')
    for key in ('activeRGBA','inactiveRGBA'):
        # UIColor's resolved white is observed as1.000000119; preserve raw values
        # and permit only floating-point boundary roundoff, not arbitrary gamut.
        h.require(len(v[key])==4 and all(isinstance(x,(float,int)) and -1e-6<=x<=1+1e-6 for x in v[key]),'resolved_tint')


def audit(phase):
    path,doc=catalog(phase);root=OUT/(phase+'-capture');receipt=h.read(root/'receipt.json')
    h.require(receipt['catalogSHA256']==h.sha(path) and receipt['target']==n.TARGET,'receipt_identity')
    h.require([r['id'] for r in receipt['rows']]==[r['id'] for r in doc['members']],'receipt_membership')
    schema=validator.read_json(validator.SCHEMA);verified=[];seen={};previews=[]
    parents={r['id']:r for r in h.read(n.BASE/'audit.json')['rows']}
    for recipe,row in zip(doc['members'],receipt['rows']):
        images=[]
        for suffix,key in [('', 'sha256'),('-hidden','hiddenSHA256')]:
            p=root/(row['id']+suffix+'.png');h.require(h.sha(p)==row[key],'pixel_hash')
            with Image.open(p) as im:
                h.require(im.format=='PNG' and im.size==(recipe['width'],recipe['height']),'image_dimensions')
                images.append(np.array(im.convert('RGB')))
        actual=n.bounds(*images,row['frame'],row['scale']);n.check_measurement(actual,row['body'],row['scale'])
        check_position(recipe,row,actual)
        image=root/(row['id']+'.png');ann=image.with_suffix('.json')
        a,body,pixel=n.checked_annotation(recipe,image,ann,native_body=row['body']);validator.check_schema(a,schema,schema)
        parent=h.read(h.checked(h.ROOT,parents[recipe['group']]['annotation']))
        before={e['id']:e for e in parent['elements']};after={e['id']:e for e in a['elements']}
        h.require(set(before)==set(after) and len(after)>1,'partial_annotations')
        for key,element in after.items():
            h.require(element['elementType']==before[key]['elementType'],'changed_annotation_class')
            if element['elementType']!='pageControl':
                h.require(all(abs(element['boundsPoints'][k]-before[key]['boundsPoints'][k])<=1/recipe['scale']
                    for k in ('x','y','width','height')),'unrelated_annotation_drift')
        h.require(pixel not in seen,'duplicate_pixels');seen[pixel]=row['id']
        verified.append(dict(id=row['id'],group=recipe['group'],split='train',image=h.ref(image),annotation=h.ref(ann),
            hidden=h.ref(root/(row['id']+'-hidden.png')),decodedSHA256=pixel,
            pixelSHA256=hashlib.sha256(str((recipe['width'],recipe['height'])).encode()+images[0].tobytes()).hexdigest(),
            body=body,independentBody=actual))
        if phase=='qualification':
            im=Image.fromarray(images[0]);draw=ImageDraw.Draw(im);x,y,w,ht=actual;s=recipe['scale']
            draw.rectangle((x*s,y*s,(x+w)*s,(y+ht)*s),outline='red',width=2)
            top=max(0,int((y-15)*s));bottom=min(im.height,int((y+ht+15)*s))
            strip=im.crop((0,top,im.width,bottom));strip.thumbnail((390,80));previews.append((row['id'],strip))
    h.write(OUT/(phase+'-audit.json'),dict(accepted=len(verified),rows=verified,catalog=h.ref(path),receipt=h.ref(root/'receipt.json'),
        trainingEligible=False,reason='Requires combined corpus duplicate/ancestry audit; no automatic training'),sealed=True)
    if previews:
        mosaic=Image.new('RGB',(800,12*110),'#888888');draw=ImageDraw.Draw(mosaic)
        for i,(name,im) in enumerate(previews):
            x=i%2*400;y=i//2*110;mosaic.paste(im,(x,y));draw.text((x,y+82),name.replace('placement171-img_',''),fill='white')
        mosaic.save(OUT/'qualification-overlays.png')
    print('audited',phase,len(verified))


def finalize():
    from ios_repair165 import OVERLAY_SHA
    path=n.BASE/'overlay/manifest.json';h.require(h.sha(path)==OVERLAY_SHA,'base_manifest_changed')
    old=h.read(path,64*1024**2);h.require(not old['duplicates'] and old['evaluationPreserved']==5200,'base_eligibility')
    sources=[];rows=[]
    for phase in ('qualification','batch'):
        catalog(phase)
        auditpath=OUT/(phase+'-audit.json');a=h.read(auditpath)
        h.require(a['seal']==h.digest({k:v for k,v in a.items() if k!='seal'}),'audit_seal')
        for row in a['rows']:
            for key in ('image','annotation','hidden'):h.checked(h.ROOT,row[key])
        sources.append(h.ref(auditpath));rows.extend(a['rows'])
    plan=h.read(d.OUT/'native-batch-plan.json')
    h.require({r['id'] for r in rows}=={r['id'] for r in plan['rows']} and len(rows)==288,'incomplete_batch')
    parents={Path(r['id']).stem:r for r in old['rows'] if r['split']=='train'}
    h.require(all(r['group'] in parents and r['split']=='train' for r in rows),'ancestry_role')
    seen={r['pixelSHA256']:r for r in old['rows']};duplicates=[];reused=[];new=[]
    for row in rows:
        if row['pixelSHA256'] in seen:
            prior=seen[row['pixelSHA256']]
            if prior['split']=='train' and prior['id']=='train/'+row['group']+'.png':
                before=h.read(h.checked(h.ROOT,prior['annotation']))
                after=h.read(h.checked(h.ROOT,row['annotation']))
                if annotation_identity(before)==annotation_identity(after):
                    reused.append(dict(id=row['id'],existingID=prior['id'],reason='exact same-parent pixels and annotations; not added twice'))
                    continue
            duplicates.append(dict(id=row['id'],duplicateOf=prior['id']))
        else:seen[row['pixelSHA256']]=row;new.append(row)
    coverage=collections.Counter('|'.join(str(r[k]) for k in ('family','scale','theme','placement','tint')) for r in plan['rows'])
    h.require(len(coverage)==24 and set(coverage.values())=={12},'coverage_gap')
    classes=collections.Counter(e['elementType'] for r in new for e in h.read(h.checked(h.ROOT,r['annotation']))['elements'])
    h.write(OUT/'corpus-audit.json',dict(version='native-placement-corpus-v1',rows=rows,expected=288,accounted=len(rows),
        eligible=not duplicates,duplicates=duplicates,reusedControls=reused,newTrainingRows=new,
        newTrainingCount=len(new),coverage=dict(coverage),newClassInstances=dict(classes),baseManifest=h.ref(path),sources=sources,
        baseEvidenceReuse='Retained hash-bound decoded-pixel audit; no re-decoding unchanged base pixels.',
        evaluationPreserved=5200,modelGates='not-assessed'),sealed=True)
    h.require(not duplicates,'duplicate_or_leaking_batch')
    print('qualified288 captures;',len(new),'new unique training examples;',len(reused),'existing controls reused;5200 evaluation memberships unchanged')


def annotation_identity(doc):
    return sorted((e['id'],e['elementType'],tuple(sorted(e['boundsPoints'].items())),
                   tuple(sorted(e['boundsVisionNormalized'].items()))) for e in doc['elements'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','execute','retrieve','audit','finalize']);parser.add_argument('--phase',choices=['qualification','batch'],default='qualification');args=parser.parse_args()
    if args.action in ('prepare','finalize'):globals()[args.action]()
    else:globals()[args.action](args.phase)
