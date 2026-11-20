"""Collect compositor screenshots with host monotonic time brackets and native display-link observations."""
from pathlib import Path
import json,subprocess,time,sys,shutil,hashlib
ROOT=Path.cwd(); app=ROOT/'.build/ios611/dd/Build/Products/Debug-iphonesimulator/TranslucentStudy.app'
bundle='com.example.nuiak.ios611.translucent'
targets={'2':'88087E97-5669-468B-8B05-635B194E1A52','3':'F3EF9DB8-0B0F-4757-B653-D1628269F6FF'}
def sim(*args):
    return subprocess.check_output(['xcrun','simctl',*map(str,args)],stderr=subprocess.DEVNULL,text=True,timeout=95).strip()
def capture(scale, offset=False):
    u=targets[scale];dst=ROOT/'reports/work/IOS611'/(('matched-' if offset else 'episodes-')+scale);dst.mkdir(exist_ok=False)
    states=json.loads(sim('list','devices','available','-j'))['devices']
    dev=next(d for devices in states.values() for d in devices if d['udid']==u)
    started=dev['state']=='Shutdown'
    if started:sim('boot',u)
    installed=False
    try:
        sim('bootstatus',u,'-b')
        try: existing=sim('get_app_container',u,bundle,'app')
        except subprocess.CalledProcessError: existing=None
        if existing and Path(existing).is_dir():
            prior=Path(existing)/'TranslucentStudy'
            assert prior.is_file() and hashlib.sha256(prior.read_bytes()).digest()==hashlib.sha256((app/'TranslucentStudy').read_bytes()).digest(), 'unrelated existing binary'
        sim('install',u,app);installed=True
        binary=Path(sim('get_app_container',u,bundle,'app'))/'TranslucentStudy'
        digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest(binary)==digest(app/'TranslucentStudy')
        (dst/'device.json').write_text(json.dumps(dict(device=dev['name'],binary=digest(binary))))
        for fw in ['UIKit','SwiftUI']:
            for mode in ['opaque','translucent']:
                for role in (['training'] if offset else ['development'] if mode=='opaque' else ['development','training']):
                    out=dst/(fw+'-'+mode+'-'+role);out.mkdir()
                    args=(['--swiftui'] if fw=='SwiftUI' else [])+(['--opaque'] if mode=='opaque' else [])+(['--training'] if role=='training' else [])
                    sim('launch',u,bundle,*args,*(['--offset-layout'] if offset else []))
                    path=Path(sim('get_app_container',u,bundle,'data'))/'Documents/trace.json'
                    start=time.monotonic();records=[]
                    while time.monotonic()-start<14.5:
                        a=time.monotonic();file=out/f'{len(records):03}.png'
                        scratch=path.parent / 'compositor.png'
                        subprocess.run(['xcrun','simctl','io',u,'screenshot','--type=png',str(scratch)],
                                       check=True,timeout=10,stdout=subprocess.DEVNULL)
                        shutil.copyfile(scratch,file);scratch.unlink()
                        assert file.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
                        b=time.monotonic();records.append(dict(png=file.name,start=a,end=b))
                        time.sleep(.11)
                    assert path.is_file() and path.stat().st_mtime>time.time()-6,'no current native trace'
                    shutil.copyfile(path,out/'trace.json');(out/'frames.json').write_text(json.dumps(records))
                    sim('terminate',u,bundle)
                    print(scale,fw,mode,role,len(records),flush=True)
    finally:
        if installed:sim('uninstall',u,bundle)
        if started:sim('shutdown',u)
if __name__=='__main__':capture(sys.argv[1], '--offset' in sys.argv[2:])
