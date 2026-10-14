"""Compare retained scores without repeating inference."""
import json
import regions313 as r
import report291


def main():
    b=r.b;out=r.OUT;b.require((out/'completion.json').exists(),'incomplete_run')
    b.require(not (out/'comparison.json').exists(),'output_collision')
    registration=b.read(out/'registration.json')
    for key in ('runner','trainer','sourceHelper','cropper','initializer','membership'):b.checked(registration[key])
    membership=b.read(b.PACKAGE/'membership.json')
    baseline=b.read(b.ROOT/'reports/work/TRANSITION-292/DTM085/evaluation.json')
    reports={};conditions={}
    for name in ('regions-1','regions-2'):
        candidate=b.read(out/name/'evaluation.json')
        summary,cases=report291.summarize_comparison(baseline,candidate,membership)
        reports[name]=dict(summaries=summary,cases=cases)
        conditions[name]={key:row['summary'] for key,row in candidate['conditions'].items()}
    a=b.read(out/'regions-1/evaluation.json');c=b.read(out/'regions-2/evaluation.json')
    summary,cases=report291.summarize_comparison(a,c,membership)
    reports['two-versus-one']=dict(summaries=summary,cases=cases)
    one=b.read(out/'regions-1/views.json');previous=b.read(r.s.OUT/'views.json')
    b.require(one['sha256']==previous['sourceSHA256'],'original_detail_changed')
    two=b.read(out/'regions-2/views.json');counts={'twoDisjoint':0,'oneNonempty':0,'identical':0}
    b.require(len(one['rows'])==len(two['rows'])==1820,'view_count')
    for a,c in zip(one['rows'],two['rows']):
        b.require(a['images']==c['images'] and a['windows']==c['windows'][:1],'matched_view_identity')
        boxes=c['windows']
        if not boxes:counts['identical']+=1
        elif len(boxes)==1:counts['oneNonempty']+=1
        else:
            (x,y),(u,v)=boxes
            b.require(x+32<=u or u+32<=x or y+32<=v or v+32<=y,'window_overlap')
            counts['twoDisjoint']+=1
    tiny={name:b.read(out/name/'tiny.json')['results'] for name in ('regions-1','regions-2')}
    b.write(out/'comparison.json',dict(comparisons=reports,conditions=conditions,tiny=tiny,
        originalDetailMatchesFOCUS310=True,windowAudit=counts,productionEligible=False,
        limitation='Retained development comparisons. No independent final-domain qualification.'))
    print(json.dumps(dict(conditions=conditions,tiny=tiny),indent=2))


if __name__=='__main__':main()
