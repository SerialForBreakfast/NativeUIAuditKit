"""Compare completed FOCUS342 jobs without changing their attempts or models."""
from pathlib import Path
import time
import numpy as np
import research_queue as q
import report_additive341 as report
import report291
from input_use289 import compare

OUT=q.ROOT/'reports/work/FOCUS-342'
ARM='added-detail-and-content'


def main():
    started=time.monotonic();membership=q.load(report.a.b.PACKAGE/'membership.json');summaries={}
    report.a.t.set_num_threads(2)
    tiny,tinyrows,_=report.a.r.s.tiny_rows();detail,_=report.a.r.prepare(tiny,tinyrows,2)
    oldnet=report.a.e.load_candidate(report.a.e.OUT/'run/last.pt')
    tinybase=report.a.b.worker.score(oldnet,np.concatenate((tiny,detail),1))
    tinylabels=np.array([v['changed'] for v in tinyrows])
    for name in ('balanced','balanced-preservation'):
        job=q.QUEUE/'jobs'/('focus342-'+name)/'attempts/1'
        result=q.load(job/'result.json');q.require(result['status']=='complete','incomplete_job')
        q.require(q.outputs_intact(job,result),'changed_job_outputs')
        destination=OUT/(name+'-report.json')
        if not destination.exists():report.main(ARM,'focus342-'+name,destination)
        candidate=q.load(destination);extra={}
        for oldname in ('added-detail','added-detail-and-content'):
            previous=q.load(q.ROOT/f'reports/work/FOCUS-341/{oldname}-report.json')
            q.require(previous['matchedIDs']==candidate['matchedIDs'],'matched_membership')
            q.require(previous['matchedLabels']==candidate['matchedLabels'],'matched_labels')
            oldeval=q.load(q.QUEUE/'jobs'/('focus341-'+oldname)/f'attempts/1/out/run/{oldname}/evaluation.json')
            neweval=q.load(job/f'out/run/{ARM}/evaluation.json')
            summary,cases=report291.summarize_comparison(oldeval,neweval,membership)
            rows=q.load(q.ROOT/'reports/work/FOCUS-319/corpus.json')['rows']+q.load(q.ROOT/'reports/work/FOCUS-326/corpus.json')['rows']['independent']
            extra[oldname]=dict(matched=compare(np.array(previous['matchedProbabilities']),
                np.array(candidate['matchedProbabilities']),np.array(candidate['matchedLabels'])),
                matchedByCondition={condition:compare(np.array(previous['matchedProbabilities'])[selection],
                    np.array(candidate['matchedProbabilities'])[selection],np.array(candidate['matchedLabels'])[selection])
                    for condition,selection in [('content',slice(0,192)),('movement',slice(192,None))]},
                authored=compare(np.array(previous['authoredProbabilities']),np.array(candidate['authoredProbabilities']),
                                 np.array([r['changed'] for r in rows])),retained=summary,cases=cases)
        q.save(OUT/(name+'-prior-comparison.json'),extra)
        tinyprob=np.array(q.load(job/f'out/run/{ARM}/comparison.json')['tinyProbabilities'])
        tinycomparison=compare(tinybase,tinyprob,tinylabels)
        summaries[name]=dict(report=dict(path=str(destination.relative_to(q.ROOT)),sha256=q.digest(destination)),
            target=candidate['byCondition'],authored=candidate['authored'],retained=candidate['comparisons']['FOCUS329']['summary'],
            losses=candidate['knownLostPreviousSuccesses'],tiny=tinycomparison,candidateAccepted=False,
            reason='Require all previous successes and qualified domain evidence. No automatic promotion.')
    q.save(OUT/'summary.json',dict(candidates=summaries,seconds=time.monotonic()-started,
        productionChanged=False,originalCropsPreserved=True))


if __name__=='__main__':main()
