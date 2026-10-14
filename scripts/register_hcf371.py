"""Freeze the native HCF study and register its bounded dependency graph."""
import copy
from pathlib import Path
import plistlib
import subprocess
import shutil
import research_queue as q
import research_graph
from research_campaign340 import pin
import hcf_study371 as study


LAYOUTS = {
    'train-row': [(100,380),(520,380),(940,380),(1360,380)],
    'train-column': [(800,60),(800,290),(800,520),(800,750)],
    'train-stagger': [(120,100),(540,300),(960,500),(1380,700)],
    'development-diamond': [(780,80),(1400,400),(780,740),(140,400)],
    'calibration-tee': [(260,100),(780,100),(1300,100),(780,650)],
    'audit-perimeter': [(160,130),(1420,250),(1200,730),(280,650)],
}


def make_cases(base):
    cases=[];number=0
    for role,count in [('train',250),('development',30),('calibration',30),('audit',30)]:
        families=[key for key in LAYOUTS if key.startswith(role+'-')]
        for index in range(count):
            family=families[index%len(families)];recipe=copy.deepcopy(base)
            size=(120,160,200)[index%3]
            theme=('dark','light')[index%2]
            composition=recipe['appearance']['composition']
            composition['definitions']['poster'].update(width=size,height=size)
            seeds=[1_000_000+number*10+i for i in range(4)]
            for i,(region,(x,y)) in enumerate(zip(composition['regions'],LAYOUTS[family])):
                region['frame']=[x,y,max(220,size),max(220,size)]
                content=composition['contents']['content-'+str(i)]
                content.update(seed=seeds[i],title=f'Study {number} artwork {i}')
            composition['background']['colors']=[0x101827,0x304050] if theme=='dark' else [0xCDD5DF,0xFFFFFF]
            # Composition owns colors. Its outer recipe requires the dark enum.
            recipe.update(seed=500_000+number,theme='dark')
            case=dict(id=f'hcf371-scene-{number:04d}',family=family,group=f'hcf371-scene-{number:04d}',
                role=role,theme=theme,recipe=recipe,artworkSeeds=seeds,targets=['item-0','item-1','item-2','item-3'])
            cases.append(case);number+=1
    study.validate_groups(cases)
    return cases


def register():
    from generation352 import MARKER
    import dataset351,hcf_capture362
    q.require(not MARKER.exists(),'capture_guard_present')
    folder=q.ROOT/'Research/ResearchSpecs/HCF371';q.require(not folder.exists(),'study_revision_exists')
    base=q.load(q.ROOT/'Research/ResearchSpecs/HCF368/small-dark-plan.json')
    q.require(dataset351.run(None)['binding']==base['binding'],'study_fixture_changed')
    q.require(q.digest(hcf_capture362.CLI.resolve())==base['helperSHA256'],'study_helper_changed')
    info=plistlib.loads(subprocess.check_output(['diskutil','info','-plist','/Volumes/training-drive']))
    storage=dict(mountPoint='/Volumes/training-drive',volumeUUID=info['VolumeUUID'],
        root='/Volumes/training-drive/data/NUIAK/HCF371',reserveBytes=2*1024**3,maximumBytes=250*1024**3)
    study.verify_storage(storage)
    q.require(shutil.disk_usage(q.ROOT).free >= 11*1024**3, 'study_internal_receipt_reserve')
    folder.mkdir()
    cases=make_cases(base['recipe'])
    design=dict(version='hcf-study-design-v1',cases=cases,storage=storage,
        targets=dict(train=1000,development=120,calibration=120,audit=120),
        limits=dict(gpuHours=1,epochs=30,secondsPerTraining=1800),
        limitations=['One qualified native control family.','Layout family support is 3/1/1/1, not 340 independent templates.',
                    'No-focus, custom controls, and Office transfer remain separate tests.'])
    dp=folder/'design.json';q.save(dp,design)
    code=[pin(q.ROOT/'scripts'/name) for name in ('hcf_study371.py','hcf_compare371.py','hcf_training371.py',
        'hcf_capture362.py','hcf_settings368.py','qualify_hcf362.py','generation352.py','dataset351.py',
        'native343.py','direct_tvos_capture.py','hcf_spatial_audit.py','focus_runtime.py','focus_ring_backbone.py',
        'train_focus_ring_detector.py','train_yolo.py','score_hcf_pilot.py')]
    code += [pin(q.ROOT/'.build/debug/FocusRingTool'),pin(q.ROOT/'Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift')]
    specs={};kinds={}
    def add(ident,step,question,answer,cfg=None,deps=None,base_spec=None,kind='experiment',extra=None):
        spec=copy.deepcopy(base_spec) if base_spec else dict(version=q.SPEC_VERSION,owner='research-host-NUIAK',
            kind='screen',authority='diagnostic',limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        spec.update(id=ident,task='HCF371',hypothesis=question,decisionRule=answer,inputs=code+[pin(dp)]+(extra or []),
            adapter=dict(type='python-callable',steps=[step],outputAttributes=[step.rsplit('.',1)[0]+'.OUT']))
        if deps:spec['dependencies']=deps
        if cfg is not None:
            cp=folder/(ident+'-config.json');q.save(cp,cfg)
            spec['stage']=[{'from':pin(cp),'to':'config.json'}]
        path=folder/(ident+'.json');q.save(path,spec);q.submit(path);specs[ident]=spec;kinds[ident]=kind
        return spec
    def dep(spec,*outputs):return dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=list(outputs))
    captures=[]
    for prefix in ('hcf368','hcf370'):
        for path in sorted((q.QUEUE/'jobs').glob(prefix+'-*-capture/attempts/1/out/capture/capture.json')):
            captures.append(pin(path))
    q.require(len(captures)==6,'retained_capture_count')
    retained=add('hcf371-00-retained','hcf_compare371.retained','Freeze the inspected native cases as regression tests.',
        'Keep inspected images out of training and final audit.',cfg=dict(captures=captures),extra=captures,kind='qualification')
    rule_old=add('hcf371-01-retained-rules','hcf_compare371.rules','Can a fixed bright-outline rule find native focus in the retained scenes?',
        'Count correct selections, wrong selections, and abstentions on both OS profiles.',
        cfg=dict(roles=['retained']),deps=[dep(retained,'admission.json')])
    admissions=[]; crop_parts=[]
    batches=[]
    for role in ('train','development','calibration','audit'):
        members=[c for c in cases if c['role']==role]
        batches.extend(members[start:start+50] for start in range(0,len(members),50))
    for number,members in enumerate(batches):
        plan=copy.deepcopy(base);plan.pop('recipe');plan.pop('targets')
        plan.update(version='native-hcf371-v1',role='study-pending',group='hcf371-study',cases=members,
            repeats=1,expectedFrames=len(members)*8,storage=storage,shard=f'shard-{number:03d}',captureBudgetBytes=2*1024**3)
        study.validate_capture_plan(plan)
        pp=folder/(plan['shard']+'-plan.json');q.save(pp,plan)
        capture_base=q.load(q.ROOT/'Research/ResearchSpecs/HCF368/hcf368-small-dark-capture.json')
        capture_base['capture']['plan']=pin(pp)
        capture_base['capture']['approval']='Maintainer approves native HCF study generation on the named Simulator, 2026-10-13.'
        producer=add(f'hcf371-10-part-{number:03d}-capture','generation352.run',
            f'Generate paired native HCF and Standard scenes for {members[0]["role"]}, part {number}.',
            'Record native focus and body bounds. Restore the OS profile. Store original images on verified USB.',base_spec=capture_base,kind='producer',
            deps=[dep(admissions[-1],'admission.json')] if admissions else None)
        admission=add(f'hcf371-10-part-{number:03d}-verify','hcf_study371.admit',
            f'Check hashes, native focus, geometry, and fixed roles for capture part {number}.',
            'Reject partial capture, conflicting labels, duplicate states, or changed inputs.',deps=[dep(producer,'artifact.json')],kind='qualification')
        admissions.append(admission)
        if members[0]['role'] in ('train','development'):
            crop_parts.append(add(f'hcf371-20-crops-{number:03d}','hcf_study371.prepare_crops',
                f'Make unchanged production crops for part {number}.',
                'Use the Swift cropper with 16% expansion. Preserve original frames and exclude final audit.',
                cfg=dict(roles=['train','development'],destination=f'production-crops-{number:03d}'),
                deps=[dep(admission,'admission.json')],kind='producer'))
    merges=[]
    for index in range(0,len(admissions),9):
        merges.append(add(f'hcf371-30-merge-{index//9}','hcf_study371.merge','Combine verified capture parts without changing data roles.',
            'Reject duplicate membership or artwork crossing training and evaluation.',deps=[dep(s,'admission.json') for s in admissions[index:index+9]],kind='qualification'))
    catalog=add('hcf371-40-catalog','hcf_study371.catalog','Does the admitted corpus meet the frozen stage counts?',
        'Require 1000 HCF training frames and 120 for each separate evaluation role.',
        cfg=dict(expectedCounts=design['targets']),deps=[dep(s,'admission.json') for s in merges],kind='qualification')
    crops=add('hcf371-50-crops','hcf_study371.merge_crops','Combine the verified production crop parts.',
        'Reject duplicate crops or different crop implementations.',
        deps=[dep(s,'crops.json') for s in crop_parts],kind='qualification')
    weights=pin(q.ROOT/'NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt')
    detector_weights=pin(q.ROOT/'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt')
    evaluations=[]
    deps=[dep(catalog,'admission.json'),dep(retained,'admission.json')]
    cfg=dict(roles=['development','retained'],storage=storage,baseline=weights)
    evaluations.append(add('hcf371-60-rules','hcf_compare371.rules','How well do fixed outline rules select HCF focus across held-out layouts?',
        'Score the same development and regression images as both learned methods.',cfg=cfg,deps=deps))
    evaluations.append(add('hcf371-61-baseline','hcf_compare371.candidate_crop','How well does the retained FocusRing model select focus on these images?',
        'Freeze its previous successes. Report oracle proposal performance separately from deployment.',cfg=cfg,deps=deps,extra=[weights]))
    for name,step,initialization,input_job,input_name in [('crop','hcf_training371.crop',weights,crops,'crops.json'),
                                                       ('detector','hcf_training371.detector',detector_weights,catalog,'admission.json')]:
        base_train=dict(version=q.SPEC_VERSION,owner='research-host-NUIAK',kind='confirm',authority='training',
            limits=dict(timeoutSeconds=1800,maxOutputBytes=2*1024**3,maxAttempts=1),training=dict(
                experimentLogRunId='HCF371',membership=[pin(dp)],initialization=initialization,epochs=30,
                storageBudgetBytes=2*1024**3,acceptanceEvidence='Matched development gains with no lost retained successes. No automatic production promotion.',resume='restart'))
        trained=add('hcf371-70-'+name+'-train',step,'Train a native HCF '+name+' candidate on frozen training groups.',
            'Use 30 epochs, patience 10, and the current 1800-second runner limit. A timeout is not a successful run.',
            cfg=dict(initialization=initialization),deps=[dep(input_job,input_name)],base_spec=base_train,extra=[initialization])
        evaluate=add('hcf371-80-'+name+'-evaluate','hcf_compare371.candidate_crop' if name=='crop' else 'hcf_compare371.detector',
            'Does the '+name+' candidate improve native HCF selection without losing previous successes?',
            'Use fixed thresholds on matched development and regression images. Report every gain and loss.',
            cfg=dict(cfg,candidate=True),deps=deps+[dep(trained,'model.json')],extra=[weights])
        evaluations.append(evaluate)
    add('hcf371-90-decision','hcf_compare371.decision','Which method improves selection, and what still fails?',
        'Require all 4 reports. Keep final audit sealed until a candidate and settings are frozen. No production replacement.',
        deps=[dep(s,'comparison.json') for s in evaluations],kind='decision')
    graph=dict(version='research-graph-v1',id='HCF371',nodes=[dict(job=s['id'],specSHA256=q.text_digest(s),
        question=s['hypothesis'],kind=kinds[s['id']]) for s in specs.values()])
    summary=research_graph.validate_graph(graph)
    q.save(folder/'graph.json',graph)
    q.save(folder/'additions.json',[dict(id=s['id'],sha256=q.text_digest(s)) for s in specs.values()])
    print(summary)


if __name__=='__main__':register()
