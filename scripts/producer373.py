"""Check native campaign plans without generating or starting a campaign."""
import json
import subprocess
import research_queue as q
from qualify_hcf362 import CLI, TTR

OUT = None


def run():
    cfg=q.load(OUT/'config.json')
    q.require(q.digest(CLI.resolve())==cfg['helperSHA256'],'helper_changed')
    rows=[]
    for pin in cfg['requests']:
        path=q.ROOT/pin['path'];q.require(q.digest(path)==pin['sha256'],'request_changed')
        request=q.load(path)
        # Keep the original target and role. This command checks bytes, not target readiness.
        name=path.stem
        with (OUT/(name+'.json')).open('x') as stdout, (OUT/(name+'.stderr')).open('x') as stderr:
            result=subprocess.run([str(CLI),'--project',str(TTR),'--json','campaign','plan',
                '--request-json',json.dumps(request,separators=(',',':'))],stdout=stdout,stderr=stderr,timeout=60)
        response=q.load(OUT/(name+'.json'))
        rows.append(dict(request=pin,exitCode=result.returncode,accepted=result.returncode==0 and response.get('success') is True,
            role=request['source_role'],report=name+'.json',captureStarted=False))
    q.save(OUT/'summary.json',dict(rows=rows,accepted=sum(r['accepted'] for r in rows),total=len(rows),
        modelAccepted=False,trainingAdmitted=False,captureStarted=False,
        decision='Prepare bounded local capture successors for accepted plans after HCF releases the target. Diagnose rejected plans from exact replies.',
        limitation='Plan acceptance does not establish native pixels, target ownership, label quality, or training admission.'))
