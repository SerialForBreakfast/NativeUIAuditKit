"""Finish reports for the 2 approved runs without an active chat."""
import subprocess
import sys
import time
import research_queue as q


def main():
    root=q.ROOT/'reports/work/FOCUS-341'
    destination=root/'unattended-summary.json'
    q.require(not destination.exists(),'output_collision')
    deadline=time.monotonic()+2700
    results=[]
    for arm in ('added-detail','added-detail-and-content'):
        result=q.QUEUE/'jobs'/('focus341-'+arm)/'attempts/1/result.json'
        while not result.exists() and time.monotonic()<deadline:
            time.sleep(10)
        if not result.exists():
            results.append(dict(arm=arm,state='waiting_limit',modelAccepted=False));break
        record=q.load(result)
        if record['status']!='complete':
            results.append(dict(arm=arm,state=record['status'],modelAccepted=False));continue
        report=root/(arm+'-report.json')
        if not report.exists():
            try:
                completed=subprocess.run([sys.executable,str(q.ROOT/'scripts/report_additive341.py'),arm],
                                         cwd=q.ROOT,timeout=800,check=False)
            except subprocess.TimeoutExpired:
                results.append(dict(arm=arm,state='report_timeout',modelAccepted=False));continue
            if completed.returncode:
                results.append(dict(arm=arm,state='report_failed',modelAccepted=False));continue
        value=q.load(report)
        results.append(dict(arm=arm,state='reported',report=str(report.relative_to(q.ROOT)),
                            reportSHA256=q.digest(report),modelAccepted=False,
                            matched=value['byCondition'],previousAuthored=value['authored'],
                            retained=value['comparisons']['FOCUS329']['summary'],
                            lostPreviousSuccesses=value['knownLostPreviousSuccesses']))
    q.save(destination,dict(results=results,productionChanged=False,
                            note='Review gains and losses together. Completion does not approve a model.'))
    print(destination,flush=True)


if __name__=='__main__':main()
