"""Capture the original CORPUS640 layouts on an explicitly authorized Simulator."""
import argparse
import hashlib
import json
import os
import plistlib
import re
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(__file__).resolve().with_name('main.swift')
SOURCE_SHA256='73ff3834488aae24ade150fb171eec79102181460c97ba406ee7bde46096d1d5'
BUNDLE='org.nativeuiauditkit.corpus640'
UUID=re.compile(r'^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$')
REASONS=re.compile(r"^\[(?P<scene>[^\]]+)\] Setting deactivation reasons to: '(?P<reasons>[^']*)'")

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inside(value):
    path=(ROOT/value).resolve()
    if path==ROOT or not path.is_relative_to(ROOT):raise ValueError('Path must stay inside the project')
    return path

def sim(*args,timeout=60):
    return subprocess.check_output(['xcrun','simctl',*map(str,args)],text=True,stderr=subprocess.STDOUT,timeout=timeout).strip()

def assert_clear(udid):
    text=sim('spawn',udid,'log','show','--style','ndjson','--predicate','process == "PineBoard" AND category == "SceneDeactivation"','--last','1d',timeout=120)
    if not text.rstrip().endswith('"finished":1}'):raise ValueError('System alert log unavailable')
    latest={}
    for line in text.splitlines():
        if not line.startswith('{'):continue
        row=json.loads(line);match=REASONS.match(row.get('eventMessage',''))
        if match:latest[match['scene']]=match['reasons']
    if any('systemModalAlert' in reasons.split(', ') for reasons in latest.values()):raise ValueError('System alert is active')

def assert_not_installed(udid):
    raw=sim('listapps',udid)
    try:installed_apps=json.loads(raw)
    except json.JSONDecodeError:
        try:installed_apps=plistlib.loads(raw.encode())
        except (plistlib.InvalidFileException,ValueError):
            try:
                converted=subprocess.run(['plutil','-convert','json','-o','-','--','-'],input=raw,text=True,capture_output=True,check=True,timeout=30)
                installed_apps=json.loads(converted.stdout)
            except (subprocess.SubprocessError,json.JSONDecodeError) as error:raise ValueError('Cannot parse Simulator app inventory') from error
    if not isinstance(installed_apps,dict):raise ValueError('Invalid Simulator app inventory')
    if BUNDLE in installed_apps:raise ValueError('The app is already installed; reconcile ownership before capture')

def cleanup_owned(udid,owned,proc,success):
    cleanup={'ownedInstallation':owned,'terminated':False,'uninstalled':False}
    try:
        if owned and proc is not None:
            sim('terminate',udid,BUNDLE);proc.wait(timeout=10);cleanup['terminated']=True
        if success:
            if not cleanup['terminated']:raise ValueError('Owned app termination is unverified')
            sim('uninstall',udid,BUNDLE);assert_not_installed(udid);cleanup['uninstalled']=True
    except Exception as error:
        cleanup['error']=str(error)
    return cleanup

def save(path,obj):
    temp=path.with_suffix(path.suffix+'.partial');temp.write_text(json.dumps(obj,indent=2)+'\n');temp.replace(path)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulator',default=os.environ.get('CORPUS640_SIMULATOR'),help='Authorized booted tvOS Simulator UUID')
    parser.add_argument('--build',required=True,help='Directory created by build.py')
    parser.add_argument('--output',required=True,help='New project-local output directory')
    args=parser.parse_args()
    if not args.simulator or not UUID.fullmatch(args.simulator):parser.error('Provide the exact authorized Simulator UUID')
    build=inside(args.build);out=inside(args.output)
    if out.exists():parser.error('Output already exists; preserve the previous attempt')
    receipt=json.loads((build/'build-receipt.json').read_text());app=build/'Study.app';exe=app/'Study'
    if digest(SOURCE)!=SOURCE_SHA256 or receipt.get('sourceSHA256')!=SOURCE_SHA256 or receipt.get('executableSHA256')!=digest(exe):raise ValueError('Build receipt does not match the source and executable')
    devices=json.loads(sim('list','devices','--json'))['devices']
    matches=[(runtime,d) for runtime,group in devices.items() for d in group if d.get('udid')==args.simulator]
    if len(matches)!=1 or 'tvOS' not in matches[0][0] or matches[0][1].get('state')!='Booted':raise ValueError('The exact tvOS Simulator is not booted')
    # An existing installation can belong to another session. Do not overwrite it.
    assert_not_installed(args.simulator)
    out.mkdir(parents=True);dest=out/'captures';dest.mkdir();chunks=out/'chunks';chunks.mkdir()
    cases=[];seen=set();last=-1;start=time.monotonic();owned=False;proc=None;pending_receipt=None
    try:
        assert_clear(args.simulator)
        sim('install',args.simulator,app);owned=True
        installed=Path(sim('get_app_container',args.simulator,BUNDLE,'app'))/'Study'
        if digest(installed)!=digest(exe):raise ValueError('Installed executable differs from the build')
        data=Path(sim('get_app_container',args.simulator,BUNDLE,'data'));docs=data/'Documents/CORPUS640-live-v1'
        if (docs/'stage.json').exists():raise ValueError('Unreconciled previous stage')
        identity={'sourceSHA256':SOURCE_SHA256,'executableSHA256':digest(exe),'renderer':'live simctl screenshot','target':args.simulator}
        save(out/'live-identity.json',identity)
        with (out/'live-console.log').open('w') as log:
            proc=subprocess.Popen(['xcrun','simctl','launch','--console',args.simulator,BUNDLE,'--simctl'],stdout=log,stderr=subprocess.STDOUT)
            assert_clear(args.simulator)
            group_start=time.monotonic();group_bytes=0;group_id=None;c=None;total_bytes=0
            while True:
                if time.monotonic()-start>=4500:raise ValueError('Capture exceeds 4500 s')
                if (docs/'complete.json').exists():
                    if json.loads((docs/'complete.json').read_text())['frames']!=300:raise ValueError('Incomplete producer run')
                    break
                stage=docs/'stage.json'
                if not stage.exists():time.sleep(.05);continue
                rec=json.loads(stage.read_text());seq=rec['sequence']
                if seq==last:time.sleep(.025);continue
                if rec['layoutGroup']!=group_id:group_id=rec['layoutGroup'];group_start=time.monotonic();group_bytes=0
                if time.monotonic()-group_start>=800:raise ValueError('Layout group exceeds 800 s')
                name=rec['name'];hidden=rec['hiddenID'];stem=name+'-'+hidden
                if not re.fullmatch(r'[\w.-]+',stem):raise ValueError('Unsafe producer filename')
                image=dest/(stem+'.png');temp=dest/'.screenshot.png'
                sim('io',args.simulator,'screenshot',temp);first=temp.read_bytes();temp.unlink()
                sim('io',args.simulator,'screenshot',temp);repeat=temp.read_bytes();temp.unlink()
                group_bytes+=len(first)+len(repeat);total_bytes+=len(first)+len(repeat)
                if group_bytes>100_000_000 or total_bytes>2_000_000_000:raise ValueError('Capture output budget exceeded')
                image.write_bytes(first);first_sha=hashlib.sha256(first).hexdigest();repeat_sha=hashlib.sha256(repeat).hexdigest()
                ref={'path':str(image.relative_to(ROOT)),'sha256':first_sha,'repeatSHA256':repeat_sha,'settled':first_sha==repeat_sha}
                if hidden=='base':
                    repeat_path=dest/(name+'-repeat.png');repeat_path.write_bytes(repeat);focus=rec['focusObservation'].copy()
                    if rec['family']=='modal':focus={'state':'unknown','id':None,'source':'UIAlertAction owner join unavailable'}
                    c={'id':name,'group':rec['layoutGroup'],'layoutGroup':rec['layoutGroup'],'family':rec['family'],'state':rec['state'],'contentVariant':rec['contentVariant'],'selectedSegment':rec['selectedSegment'],'sourceLineage':'CORPUS640/UIKit-native-procedural-v1','image':ref,'repeatImage':{'path':str(repeat_path.relative_to(ROOT)),'sha256':repeat_sha},'width':3840,'height':2160,'targets':rec['targets'],'captions':rec['captions'],'ownedMetadata':rec['ownedMetadata'],'focusObservation':focus,'nativeFocusBefore':rec['focusObservation'],'constructorSHA':SOURCE_SHA256,'exeSHA':digest(exe),'controlsHidden':{},'partialReasons':rec['partialReasons'].copy()}
                    if not ref['settled']:c['partialReasons'].append('base screenshot pair unsettled')
                else:
                    if not c or c['id']!=name:raise ValueError('Unexpected producer stage')
                    if rec['targets']!=c['targets']:c['partialReasons'].append('native target geometry changed during matched intervention')
                    if rec['focusObservation']!=c['nativeFocusBefore']:c['partialReasons'].append('native focus changed during matched intervention')
                    c['controlsHidden'][hidden]=ref
                    if not ref['settled']:c['partialReasons'].append('hidden screenshot pair unsettled:'+hidden)
                ack=docs/'ack.json';tmp=docs/'ack.tmp';tmp.write_text(json.dumps({'sequence':seq}));tmp.replace(ack);last=seq
                after=docs/('observed-after-'+str(seq)+'.json');deadline=time.monotonic()+20
                while not after.exists():
                    if time.monotonic()>=deadline:raise ValueError('Missing post-capture observation')
                    time.sleep(.025)
                observation=json.loads(after.read_text());save(dest/(stem+'-observation.json'),{'before':rec,'after':observation})
                if hidden=='base':
                    c['focusObservationAfter']=observation['focusObservation']
                    if observation['focusObservation']!=rec['focusObservation']:c['partialReasons'].append('focus changed across base screenshot')
                    if observation['targets']!=rec['targets']:c['partialReasons'].append('bounds changed across base screenshot')
                if hidden!='base' and len(c['controlsHidden'])==len(c['targets']):
                    if name in seen:raise ValueError('Duplicate case')
                    seen.add(name);cases.append(c);save(out/'partial-cases.json',cases)
                    if len(cases)%5==0:save(chunks/('group-'+str((len(cases)-1)//5).zfill(2)+'.json'),cases[-5:])
                    print(name,'completed',len(cases),'/ 300',flush=True)
            if len(cases)!=300:raise ValueError('Incomplete case membership')
            save(out/'cases.json',cases)
            output_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
            if output_bytes>2_000_000_000:raise ValueError('Stored output budget exceeded')
            pending_receipt={'completed':True,'frames':300,'elapsedSeconds':time.monotonic()-start,'partialAtCapture':sum(bool(c['partialReasons']) for c in cases),'sourceSHA256':SOURCE_SHA256,'executableSHA256':digest(exe),'renderer':'live simctl screenshot','outputBytes':output_bytes,'screenshotBytesProcessed':total_bytes,'outputBytesExcludes':['cleanup-receipt.json','capture-receipt.json']}
    except Exception as error:
        save(out/'failure.json',{'error':str(error),'frames':len(cases),'lastSequence':last,'elapsedSeconds':time.monotonic()-start})
        raise
    finally:
        cleanup=cleanup_owned(args.simulator,owned,proc,pending_receipt is not None)
        save(out/'cleanup-receipt.json',cleanup)
        if pending_receipt is not None:
            if not cleanup['uninstalled']:
                save(out/'failure.json',{'error':'Owned app cleanup is unverified','frames':len(cases),'lastSequence':last,'cleanup':cleanup})
                raise RuntimeError('Owned app cleanup is unverified')
            save(out/'capture-receipt.json',pending_receipt)

if __name__=='__main__':main()
