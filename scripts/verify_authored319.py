"""Check repeated rendering and reject an unsupported focus target."""
import os
import subprocess
import time
import authored319 as a


def main():
    b=a.b;out=a.OUT/'producer-checks';b.require(not out.exists(),'output_collision')
    p=b.read(a.OUT/'plan.json');b.require(b.sha(a.SCRIPT.read_bytes())==p['renderer']['sha256'],'renderer_changed')
    out.mkdir();start=time.monotonic();results={}
    env=dict(os.environ,TMPDIR=str(b.ROOT/'.build'),CLANG_MODULE_CACHE_PATH=str(b.ROOT/'.build/ModuleCache'))
    for target,name in [('grid_r0_c0','repeat'),('missing-focus319','invalid')]:
        folder=out/name
        cmd=['swift','-module-cache-path',str(b.ROOT/'.build/ModuleCache'),str(a.SCRIPT),
             '--layout','grid','--resolution','1080p','--assets-dir',str(a.OUT/'assets-0-0'),
             '--output-dir',str(folder),'--focus-id',target]
        with (out/f'{name}.log').open('x') as log:
            result=subprocess.run(cmd,cwd=b.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
        if name=='repeat':
            b.require(result.returncode==0,'repeat_exit');pin,m=a.frame(folder,'grid',target)
            old=b.read(a.OUT/'render-0-0-grid-grid_r0_c0/grid_annotations.json')
            b.require(m['focusedImageSHA256']==old['focusedImageSHA256'] and
                      m['unfocusedImageSHA256']==old['unfocusedImageSHA256'],'repeat_pixels')
            results[name]=dict(exactPNGMatch=True,image=pin)
        else:
            rejection='producer_exit' if result.returncode else None
            if not rejection:
                try:a.frame(folder,'grid',target)
                except (ValueError,FileNotFoundError) as error:rejection=str(error)
            b.require(rejection is not None,'invalid_accepted')
            results[name]=dict(producerExit=result.returncode,consumerRejection=rejection)
    b.write(out/'result.json',dict(results=results,seconds=time.monotonic()-start,renderer=p['renderer']))
    print(results)


if __name__=='__main__':main()
