"""Single-device fixed-geometry comparison. Each condition owns a new trace and 3 compositor PNGs."""
from capture import sim,targets,ROOT,bundle
from pathlib import Path
import hashlib,json,time,subprocess,shutil

conditions=[('system',0),('system',10),('system',30),('system',55),('system',80),('system',100),
            ('thin',10),('thick',10),('clear',10)]
def run(cases=conditions, probes=False, low_sheet=False):
    app=ROOT/('.build/ios615' if low_sheet else '.build/ios613' if probes else '.build/ios612')/'dd/Build/Products/Debug-iphonesimulator/TranslucentStudy.app'
    dst=ROOT/('reports/work/PAR615/ios' if low_sheet else 'reports/work/PAR613' if probes else 'reports/work/IOS612');u=targets['3'];devices=json.loads(sim('list','devices','available','-j'))['devices']
    runtime,device=next((r,d) for r,ds in devices.items() for d in ds if d['udid']==u)
    assert runtime.endswith('26-5') and device['name']=='iPhone 17 Pro'
    started=device['state']=='Shutdown'
    if started:sim('boot',u)
    installed=False
    try:
        sim('bootstatus',u,'-b')
        try: previous=sim('get_app_container',u,bundle,'app')
        except subprocess.CalledProcessError: previous=None
        assert not previous or not Path(previous).is_dir(),'unexpected installation'
        sim('install',u,app);installed=True
        binary=Path(sim('get_app_container',u,bundle,'app'))/'TranslucentStudy'
        digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest(binary)==digest(app/'TranslucentStudy')
        code=digest(binary.with_name('TranslucentStudy.debug.dylib'))
        assert code==digest(app/'TranslucentStudy.debug.dylib')
        (dst/'device.json').write_text(json.dumps(dict(name=device['name'],runtime=runtime,device=u,binary=digest(binary),loadedDebugLibrarySHA256=code)))
        docs=Path(sim('get_app_container',u,bundle,'data'))/'Documents'
        for condition in cases:
            material,alpha=condition[:2]
            target,treatment=condition[2:] if probes else ('','')
            for fw in ('UIKit','SwiftUI'):
                out=dst/('-'.join(filter(None,[fw,material,str(alpha),target,treatment])));out.mkdir()
                trace=docs/'trace.json';trace.unlink(missing_ok=True)
                sim('launch',u,bundle,'--material-study','--training','--offset-layout','--backing='+material,
                    f'--alpha={alpha/100}',*(['--low-sheet'] if low_sheet else []),*(['--probe='+target,'--'+treatment] if probes and target!='clean' else []),*(['--swiftui'] if fw=='SwiftUI' else []))
                def snap(name):
                    tmp=docs/'frame.png';a=time.monotonic();sim('io',u,'screenshot',tmp);b=time.monotonic()
                    shutil.copyfile(tmp,out/(name+'.png'));tmp.unlink();return [a,b]
                times={'initial':snap('initial')}
                limit=time.monotonic()+12
                while not trace.is_file() and time.monotonic()<limit:time.sleep(.08)
                assert trace.is_file()
                times['settled1']=snap('settled1');time.sleep(.15);times['settled2']=snap('settled2')
                shutil.copyfile(trace,out/'trace.json');(out/'times.json').write_text(json.dumps(times))
                sim('terminate',u,bundle);print(out.name,flush=True)
    finally:
        if installed:sim('uninstall',u,bundle)
        if started:sim('shutdown',u)
if __name__=='__main__':
    import sys
    run([('system',40),('system',45),('system',50),('clear',30),('thin',30),('thick',30)]
        if '--refine' in sys.argv else [('system',35)] if '--midpoint' in sys.argv else conditions)
