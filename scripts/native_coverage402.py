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


# T45: native control families. A new version; native-hcf402-v1 above is unchanged.
CONTROLS_VERSION='native-controls-t45-v1'
CONTROL_FAMILIES=('button','row','tab')
# Requested design sizes only. Annotations use the measured rendered body from each capture.
CONTROL_SIZES={'button':(300,80),'row':(800,80),'tab':(300,70)}
CONTROL_POSITIONS={'button':[(160,160),(1100,160),(160,760),(1100,760)],
                   'row':[(120,160),(1000,160),(120,760),(1000,760)]}


def validate_controls(plan):
    """Admit native button, row, and tab cases with native_button focus. Never admit requested bounds."""
    import fixture_composition
    q.require(plan['version']==CONTROLS_VERSION, 'controls_version')
    q.require(plan['binding']['simulatorUDID']==native.TARGET and
              plan['binding']['endpoint']=='http://127.0.0.1:8080', 'controls_target')
    q.require(plan['role']=='study-pending' and plan['trainingEligible'] is False, 'controls_role')
    q.require(plan['profiles']==['standard','hcf'] and plan['repeats']==1, 'controls_profiles')
    cases=plan['cases']
    q.require(1<=len(cases)<=3 and len({c['id'] for c in cases})==len(cases), 'controls_cases')
    q.require(plan['expectedFrames']==2*sum(len(c['targets']) for c in cases)<=24, 'controls_frames')
    q.require(plan['captureBudgetBytes']==100_000_000, 'controls_budget')
    q.require(plan['qualification']['complete'] and plan['qualification']['restoration']=='verified', 'controls_caller')
    groups={}
    for case in cases:
        q.require(q.ID.fullmatch(case['id']) and case['role']=='development', 'controls_identity')
        q.require(case['family'] in CONTROL_FAMILIES and isinstance(case['group'],str) and
                  q.ID.fullmatch(case['group']), 'controls_family')
        # 1 group holds 1 family and 1 role. Related variants never cross roles.
        q.require(groups.setdefault(case['group'],(case['family'],case['role']))==(case['family'],case['role']),
                  'controls_group_ancestry')
        q.require(not {'bodies','bounds','annotations','labels'} & set(case), 'requested_geometry_forbidden')
        q.require(case['condition']=='position', 'controls_condition')
        recipe=case['recipe'];composition=recipe['appearance']['composition']
        q.require(recipe['archetype']=='grid_matrix', 'controls_archetype')
        items,_=fixture_composition.resolve(composition,recipe,q.require)
        focusable=[i for i in items if i['focusable']]
        q.require({i['kind'] for i in focusable}=={case['family']} and
                  all(i['kind']=='text' for i in items if not i['focusable']), 'controls_kinds')
        q.require(all(i['style']['focus']['kind']=='native_button' for i in focusable), 'controls_focus')
        q.require(all(i['kind']=='tab' or not i['selected'] for i in items), 'controls_selected')
        ids=[i['id'] for i in focusable]
        q.require(case['targets'] and len(case['targets'])==len(set(case['targets']))<=4 and
                  set(case['targets'])<=set(ids), 'controls_targets')
        q.require(1<=len(composition['regions'])<=5, 'controls_regions')


def controls_case(family, case_id, group, seed):
    """Build 1 development case with 4 controls of 1 family. Theme and density stay Fixture defaults."""
    q.require(family in CONTROL_FAMILIES, 'controls_family')
    width,height=CONTROL_SIZES[family]
    style=dict(foreground=0xF8F8FC,background=0x222A2E,fontSize=28,cornerRadius=12,opacity=1,blur=False,
               focus=dict(version=1,kind='native_button'))
    contents={f'content-{n}':dict(title=f'{family.title()} {n+1}',seed=seed*10+n,preset='gray_placeholder')
              for n in range(4)}
    item=lambda n:dict(id=f'item-{n}',component=family,content=f'content-{n}',selected=False)
    if family=='tab':
        # A tab bar: 4 tabs in 1 row region, none selected, so focus is the only changed state.
        regions=[dict(id='region-0',axis='row',frame=[360,60,4*width+3*24,height+40],gap=24,
                      items=[item(n) for n in range(4)])]
    else:
        regions=[dict(id=f'region-{n}',axis='row',frame=[x,y,width+40,height+40],gap=0,items=[item(n)])
                 for n,(x,y) in enumerate(CONTROL_POSITIONS[family])]
    composition=dict(version=3,styles={'control':style},
        definitions={family:dict(kind=family,style='control',width=width,height=height)},contents=contents,
        regions=regions,background=dict(colors=[0x101827,0x304050],locations=[0,1],direction='vertical',interpolation='linear'))
    # The Fixture accepts a composition only with the grid_matrix archetype (FixtureAppearance.supports).
    recipe=dict(schema_version=1,archetype='grid_matrix',theme='dark',
                density='regular',element_count=4,seed=seed,step_index=0,
                appearance=dict(version=1,preset='artwork',layout='standard',composition=composition))
    return dict(id=case_id,family=family,group=group,condition='position',role='development',theme='dark',
                targets=[f'item-{n}' for n in range(4)],recipe=recipe)


def prepare_controls(source, output, families, tag='r1', seed=745000):
    """Freeze a T45 capture plan from a qualified native plan. The binding is read fresh from the Fixture."""
    import copy
    import direct_tvos_capture as d
    from qualify_hcf362 import CLI
    base=q.load(source)
    q.require(base['version'] in ('native-hcf402-v1',CONTROLS_VERSION), 'controls_source')
    plan={k:copy.deepcopy(base[k]) for k in ('qualification','storage','originalProfile','normalizeSettings',
                                             'nativeReceiptBudgetBytes') if k in base}
    names='-'.join(families)+'-'+tag
    plan.update(version=CONTROLS_VERSION,role='study-pending',trainingEligible=False,profiles=['standard','hcf'],
                repeats=1,captureBudgetBytes=100_000_000,group='t45-native-controls',shard='t45-controls-'+names,
                helperSHA256=q.digest(CLI.resolve()),binding=d.bind_target(native.TARGET,'http://127.0.0.1:8080'),
                cases=[controls_case(f,f't45-{f}-case-{tag}',f't45-{f}-group-{tag}',seed+CONTROL_FAMILIES.index(f))
                       for f in families],
                limitation='Development capture only. Requested design sizes are not labels; '
                           'use the measured rendered body. Unavailable geometry fails the capture.')
    plan['expectedFrames']=2*sum(len(c['targets']) for c in plan['cases'])
    validate_controls(plan);q.save(output,plan)
    return plan


def measured_bodies(doc, plan):
    """Summarize measured focused-body geometry by family. Any unavailable body is a failure, not a fallback."""
    q.require(doc.get('version')==CONTROLS_VERSION and doc['complete'] and doc['cleanup'], 'controls_capture_incomplete')
    families={c['id']:c['family'] for c in plan['cases']}
    rows={}
    for frame in doc['frames']:
        boxes=[]
        for key in ('before','after'):
            scene=frame[key]['scene']
            element=next(e for e in scene['elements'] if e['element_id']==frame['focus'])
            body=element.get('rendered_body_geometry') or {}
            q.require(element['is_focused'] and body.get('availability')=='measured',
                      'unmeasured_body:'+str(body.get('unavailable_reason')))
            boxes.append(body['visible_pixel_bounds'])
        q.require(boxes[0]==boxes[1], 'body_changed_during_capture')
        x,y,w,h=boxes[0]
        row=rows.setdefault(families[frame['case']],dict(frames=0,aspects=[]))
        row['frames']+=1;row['aspects'].append(round(w/h,3))
    for row in rows.values():
        row.update(minimumAspect=min(row['aspects']),maximumAspect=max(row['aspects']))
    return dict(version=CONTROLS_VERSION,families=rows,trainingEligible=False,modelAccepted=False)
