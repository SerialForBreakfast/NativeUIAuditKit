"""Like-for-like exposure and terminal metric checks for the two augmentation arms."""
from collections import defaultdict,Counter
import human_annotation_review as h
from fullscreen_readthrough import score_boxes

BASE=h.ROOT/'reports/work/FOCUS-AUGMENTATION-47'


def geometry_inventory(checked):
    result={}
    for split in ('train','evaluation'):
        shapes=Counter();xphase=Counter();yphase=Counter();count=0
        for f in checked['frames']:
            if f['split']!=split:continue
            ann=h.read(h.checked(h.ROOT,f['annotation']))
            c=next(c for c in ann['controls'] if c['state']=='focused')
            x,y,bw,bh=c['bounds'];w,v=f['size'];scale=640/max(w,v)
            padx=(640-round(w*scale))//2;pady=(640-round(v*scale))//2
            shapes[f'{bw*scale:.1f}x{bh*scale:.1f}']+=1
            xphase[f'{((x+bw/2)*scale+padx)%32:.2f}']+=1
            yphase[f'{((y+bh/2)*scale+pady)%32:.2f}']+=1;count+=1
        result[split]=dict(frames=count,bodySizesAt640=dict(shapes),centerXModulo32=dict(xphase),centerYModulo32=dict(yphase))
    return result


def terminal(doc,report):
    frames=[f for f in doc['frames'] if f['split']=='evaluation']
    h.require([f['id'] for f in frames]==[f['id'] for f in report['frames']],'terminal_membership')
    counts=dict(tp=0,fp=0,fn=0);pairs=defaultdict(list);exact=0;slots=defaultdict(lambda:dict(frames=0,exact=0))
    for f,row in zip(frames,report['frames']):
        ann=h.read(h.checked(h.ROOT,f['annotation']));focus=[c for c in ann['controls'] if c['state']=='focused']
        h.require(len(focus)==1,'single_focus')
        targets=[[x,y,x+w,y+v] for x,y,w,v in [focus[0]['bounds']]]
        scored=score_boxes(row['predictedBounds'],targets)
        h.require(scored=={k:row[k] for k in counts},'terminal_score')
        for k in counts:counts[k]+=scored[k]
        good=scored['fp']==0 and scored['fn']==0;exact+=good
        pairs[f['id'].rsplit('-',1)[0]].append(good)
        slots[focus[0]['id']]['frames']+=1;slots[focus[0]['id']]['exact']+=good
    h.require(counts==report['totals'] and exact==report['exactFrames'],'terminal_aggregate')
    h.require(len(pairs)==250 and all(len(v)==2 for v in pairs.values()),'pair_membership')
    return dict(frames=500,totals=counts,exactFrames=exact,completePairs=sum(all(v) for v in pairs.values()),
                focusedSlots=dict(slots),evaluationSeconds=report['seconds'])


def main():
    original=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41'
    baseline=h.read(original/'run.json');reports={}
    old=h.read(original/'evaluation/terminal-evaluation.json')
    reports['FSF001']=dict(terminal=terminal(baseline,old),fit=h.read(original/'run/training-complete.json'))
    for name,run_id in [('translation','FSF003'),('translation-scale','FSF004')]:
        contract=h.read(BASE/'contracts'/(name+'.json'))
        for k in ('frames','checkpoint','runtime','seed','epochs','batch','imgsz','admission'):
            h.require(contract[k]==baseline[k],'unmatched_configuration_'+k)
        report=h.read(BASE/'runs'/name/'terminal-evaluation.json')
        fit=h.read(BASE/'runs'/name/'training-complete.json')
        h.require(report['checkpoint']==fit['checkpoint'] and fit['epochs']==1 and
                  fit['trainingFrames']==2000 and fit['batchesPerEpoch']==250,'fit_exposure')
        reports[run_id]=dict(terminal=terminal(contract,report),fit=fit,
                            execution=h.read(BASE/(name+'-execution.json')))
    geometry=geometry_inventory(h.read(original/'run/validated.json'))
    h.write(h.fresh(BASE/'terminal-comparison.json'),dict(reports=reports,geometryBeforeAugmentation=geometry,matchedMembershipSHA256=h.digest(baseline['frames']),
        interpretation='Same nominal one-epoch exposure/initializer; original baseline lacks direct optimizer-step instrumentation.'))
    print({k:v['terminal'] for k,v in reports.items()})


if __name__=='__main__':main()
