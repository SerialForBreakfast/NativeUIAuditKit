"""Validate a bounded native coverage campaign. Never infer focus from a border."""
import research_queue as q
import native343 as native


def validate(plan):
    q.require(plan['version']=='native-hcf402-v1', 'coverage_version')
    q.require(plan['binding']['simulatorUDID']==native.TARGET and
              plan['binding']['endpoint']=='http://127.0.0.1:8080', 'coverage_target')
    q.require(plan['role']=='study-pending' and plan['trainingEligible'] is False, 'coverage_role')
    q.require(plan['profiles']==['standard','hcf'] and plan['repeats']==1, 'coverage_profiles')
    cases=plan['cases']
    q.require(1<=len(cases)<=3 and len({c['id'] for c in cases})==len(cases), 'coverage_cases')
    q.require(plan['expectedFrames']==2*sum(len(c['targets']) for c in cases)<=18, 'coverage_frames')
    q.require(plan['captureBudgetBytes']==100_000_000, 'coverage_budget')
    q.require(plan['qualification']['complete'] and plan['qualification']['restoration']=='verified', 'coverage_caller')
    for case in cases:
        q.require(q.ID.fullmatch(case['id']) and case['role']=='development', 'coverage_identity')
        composition=case['recipe']['appearance']['composition']
        q.require(all(s['focus']['kind']=='native_image' for s in composition['styles'].values()), 'authored_focus')
        q.require(all(14<=s['fontSize']<=80 for s in composition['styles'].values()), 'native_font_size')
        q.require(case['recipe']['element_count']==sum(len(r['items']) for r in composition['regions']), 'native_item_count')
        kinds={d['kind'] for d in composition['definitions'].values()}
        if case['condition']=='no-focus':
            q.require(case['targets']==[None] and kinds <= {'poster','text'} and 'poster' in kinds, 'no_focus_recipe')
        else:
            q.require(case['condition']=='position' and kinds <= {'poster','text'} and 'poster' in kinds and
                      case['targets']==['item-0','item-1','item-2','item-3'], 'focused_recipe')
        q.require(4<=len(composition['regions'])<=5, 'coverage_regions')
        for region in composition['regions']:
            x,y,w,h=region['frame']
            q.require(w>0 and h>0 and x>=0 and y>=0 and x+w<=1920 and y+h<=1080, 'coverage_geometry')


def prepare(source, output, mode='combined'):
    """Freeze new development groups using the qualified native lifecycle."""
    import copy
    import direct_tvos_capture as d
    from qualify_hcf362 import CLI
    plan=copy.deepcopy(q.load(source));base=plan['cases'][0]
    plan.update(version='native-hcf402-v1',captureBudgetBytes=100_000_000,expectedFrames=18,
                shard='hcf402-native-coverage',group='hcf402-native',helperSHA256=q.digest(CLI.resolve()),
                binding=d.bind_target(native.TARGET,'http://127.0.0.1:8080'))
    cases=[]
    for index in range(3):
        case=copy.deepcopy(base);family=0 if index==0 else 1
        case.update(id='hcf402-case-'+str(index),group='hcf402-group-'+str(family),condition='position',role='development')
        recipe=case['recipe'];recipe['seed']=740200+family
        comp=recipe['appearance']['composition']
        positions=[(100,100),(1500,100),(100,720),(1500,720)] if family==0 else [(300,220),(1200,220),(300,650),(1200,650)]
        for number,(region,position) in enumerate(zip(comp['regions'],positions)):
            region['frame']=[*position,220,220]
            comp['contents']['content-'+str(number)]['seed']=7402000+family*10+number
        if family==1:
            comp['definitions']['decoy']=dict(kind='text',style='image',width=220,height=220)
            comp['contents']['decoy-content']=dict(title='□',seed=7402099,preset='artwork')
            comp['styles']['image']['fontSize']=80
            comp['regions'].append(dict(id='decoration',axis='row',frame=[800,400,220,220],gap=0,
                items=[dict(id='decoy',component='decoy',content='decoy-content',selected=False)]))
        if index==2:
            case.update(condition='no-focus',targets=[None])
        recipe['element_count']=sum(len(r['items']) for r in comp['regions'])
        case['artworkSeeds']=[7402000+family*10+n for n in range(4)]
        cases.append(case)
    q.require(mode in ('combined','focused','no-focus'), 'coverage_mode')
    plan['cases']=cases if mode=='combined' else cases[:2] if mode=='focused' else cases[2:]
    plan['expectedFrames']=2*sum(len(c['targets']) for c in plan['cases'])
    plan['shard']='hcf402-native-'+mode+'-r2'
    plan['limitation']='Development capture only. The decorative square is a text glyph, not a native focus border.'
    validate(plan);q.save(output,plan)
    return plan
