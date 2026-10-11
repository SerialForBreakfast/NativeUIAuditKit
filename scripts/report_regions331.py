"""Report family differences without selecting from evaluation data."""
from pathlib import Path
import regions331 as m

b=m.b;OUT=m.OUT


def summarize(rows):
    return {policy:{metric:m.c.summarize([v['measurements'][policy] for v in rows],metric)
        for metric in ('coverage','purity')} for policy in ('old',*m.POLICIES)}


def main():
    audit=b.read(OUT/'audit.json');reg=b.read(b.checked(audit['registration']))
    for key in ('source','membership','encoded','prior'):b.checked(reg[key])
    member=b.read(b.checked(reg['membership']));rows=audit['rows']
    b.require(len(rows)==sum(v['role']=='train' for v in member['rows']),'row_count')
    b.require(len({v['index'] for v in rows})==len(rows),'duplicate_row')
    for row in rows:
        source=member['rows'][row['index']]
        b.require(source['role']=='train' and source['id']==row['id'] and source['changed']==row['changed'],'role_or_label')
    group_results={}
    for policy in m.POLICIES:
        measured={key:values for key,values in audit['summary'].items()
            if key not in ('all','content') and values['old']['coverage']['mean'] is not None}
        group_results[policy]=dict(improved=[k for k,v in measured.items() if v[policy]['coverage']['mean']>v['old']['coverage']['mean']],
            reduced=[k for k,v in measured.items() if v[policy]['coverage']['mean']<v['old']['coverage']['mean']],
            unchanged=[k for k,v in measured.items() if v[policy]['coverage']['mean']==v['old']['coverage']['mean']])
    content={str(label):summarize([v for v in rows if 'content_contrast' in v['conditions'] and v['changed']==label]) for label in (0,1)}
    b.require(m.eligibility(audit['summary'])==audit['selectedPolicy'],'decision_mismatch')
    result=dict(audit=b.ref(OUT/'audit.json'),source=b.ref(Path(__file__)),groups=group_results,contentByLabel=content,
        rolesChanged=False,trainingStarted=False,productionEligible=False,
        interpretation='Both replacement rules fail the fixed training condition. Boundary evidence can help some families, but replaces useful existing evidence.')
    b.write(OUT/'report.json',result);print(group_results,flush=True)


if __name__=='__main__':main()
