"""Finish FOCUS366 using exact nonempty comparisons and unchanged acceptance rules."""
import research_queue as q
from research_campaign340 import decision as classify

OUT=None


def decide(documents, expected):
    arms={}
    all_reports=[r for d in documents for r in d['summaryRows']]
    q.require(len({r['job'] for r in all_reports})==len(all_reports),'duplicate_reports')
    for arm in ('control','notification'):
        reports=[r for r in all_reports if r['job'].startswith('focus366-'+arm+'-')]
        q.require({r['job'] for r in reports}==set(expected[arm]),'missing_comparisons')
        selected=[d for d in documents if any(r['job'].startswith('focus366-'+arm+'-') for r in d['summaryRows'])]
        targets=[r for d in selected for r in d['targetPredictions']]
        q.require(len(targets)==392 and len({r['id'] for r in targets})==392,'target_membership')
        corner=next(r for r in targets if r['id']=='artwork-s1-focus_maze-005')
        arms[arm]=dict(lostPrevious=sum(r['counts'].get('lost',0) for r in reports),
            falseChanges=sum(r['changed']==0 and classify(r['probability'])==1 for r in targets),
            correct=sum(classify(r['probability'])==r['changed'] for r in targets),
            cornerPreserved=classify(corner['probability'])==1,cornerProbability=corner['probability'])
    a,b=arms['control'],arms['notification']
    passes=b['lostPrevious']==0 and b['cornerPreserved'] and b['falseChanges']<a['falseChanges'] and b['correct']>a['correct']
    return dict(arms=arms,passesDevelopmentRule=passes,modelAccepted=False,productionChanged=False,
        nextAction='Review native transfer.' if passes else 'Diagnose lost successes before another correction.')


def run():
    cfg=q.load(OUT/'config.json');documents=[]
    for dep in q.load(OUT/'dependencies.json'):
        for pin in dep['outputs']:
            q.require(q.digest(q.ROOT/pin['path'])==pin['sha256'],'summary_changed')
            documents.append(q.load(q.ROOT/pin['path']))
    q.save(OUT/'decision.json',decide(documents,cfg['expected']))
