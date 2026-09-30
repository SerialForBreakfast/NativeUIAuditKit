"""Frozen real-transfer and native-fixture diagnostics; never trains or scores challenges."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import human_focus_evaluation as evaluation
from focus_dataset_contract import ROOT, digest, pixel_digest, validate_manifest
from focus_mixed_assembly import checked, reference
from focus_ring_baseline import model_contract
from focus_runtime import RUNTIME_PREPROCESSING, bounded_batches, invoke
from focus_surface_evaluation import runtime, seal_check
from focus_surface_intake import fresh, require, write

VERSION='focus-representative-validation-v1'
STRATA=('buttons','tabs','artwork','rows','other')


def stratum(row):
    if row.get('stratum'):return row['stratum']
    return {'primaryButton':'buttons','secondaryButton':'buttons','focus:tabItem':'tabs',
            'collectionItem':'artwork','imageView':'artwork','listRow':'rows'}.get(row['control'],'other')


def summarize(rows, predictions, policy=None):
    measured=evaluation.metrics(rows,predictions,[],policy)
    supported=[r for r in rows if (not policy or (r['population']=='candidate' and r['settlement']=='settled'))]
    values={p['id']:p for p in predictions}
    breakdown={}
    for name in STRATA:
        members=[r for r in supported if stratum(r)==name]
        if not members:
            breakdown[name]={'status':'unavailable','n':0,'recall':None,'fpr':None}
        else:
            m=evaluation.metrics(members,[values[r['id']] for r in members],[])['full']['groups']['overall']
            breakdown[name]={'status':'available',**m}
    recalls=[breakdown[s]['recall'] for s in STRATA[:4] if breakdown[s]['recall'] is not None]
    return dict(metrics=measured,strata=breakdown,macroRecall=sum(recalls)/len(recalls) if recalls else None,
                supportedMacroStrata=len(recalls),macroRequiredStrata=4)


def synthetic_rows(doc, directory):
    require(doc.get('purpose')=='development-pilot' and doc.get('sourceKind')=='simulatorFixture'
            and doc.get('evidenceKind')=='test-only' and 'trainingApproval' not in doc,'wrong_diagnostic_role')
    validate_manifest(doc,directory)
    rows=[];frames=[]
    for pair in doc['pairs']:
        require(pair['split']=='development' and pair['original_split']=='validation','reserved_calibration_required')
        scene=pair['observationBinding']['focusedScene']; canvas=scene['recipe']['appearance'].get('canvas',{})
        presentation=canvas.get('presentation')
        group=doc['corpusID']; pid=group+':'+pair['pair_id']
        lane='tabs' if presentation in ('tabs','nested_tabs_v1') else 'rows' if presentation=='settings_rows' else 'buttons' if presentation=='buttons' else 'artwork'
        common=dict(family=group,theme=pair['theme'],control=pair['element_type'],stratum=lane,hard=False,
                    pairID=pid,population='candidate',settlement='settled',role='development-diagnostics')
        for role,label in [('focused',1),('unfocused',0)]:
            frame=pair['frames'][role]; image=reference(ROOT/doc['sourceRoot']/frame['path'])
            crop=reference(directory/pair[role+'_crop'])
            rows.append(dict(common,id=pid+':pair:'+role,label=label,kind='pair',frameID=pid+':'+role,
                image=image,crop=crop,bounds=frame['bounds'],pixelSHA256=pixel_digest(ROOT,crop)))
        elements=scene['elements'];ids={e['element_id'] for e in elements}
        require(len(ids)==len(elements)==scene['recipe']['element_count'] and
                ids==set(scene['focus_observation']['plannedFocusIDs']) and
                sum(e['is_focused'] for e in elements)==1,'incomplete_native_frame')
        frames.append(dict(id=pid,settlement='settled',coverage='complete'))
        frame=pair['frames']['focused'];image=reference(ROOT/doc['sourceRoot']/frame['path'])
        for e in elements:
            rows.append(dict(common,id=pid+':candidate:'+e['element_id'],kind='competition',frameID=pid,
                label=int(e['is_focused']),image=image,bounds=e['pixel_bounds'],control=e['taxonomy_class'],
                selected='isSelected' in e.get('accessibility_traits',[]),parent=e.get('parent_element_id')))
    return rows,frames


def prepare(qa, output):
    output=fresh(output);qa=checked(reference(qa/'intake.json')).parent
    intake=json.loads((qa/'intake.json').read_text())
    require(intake['totals']['acceptedPairs']==50 and intake['totals']['blockedPairs']==0,'incomplete_intake')
    output.mkdir(parents=True)
    rows=[];frames=[];sources=[]
    for p in sorted(qa.glob('*/focus_dataset_manifest.json')):
        sources.append(reference(p));r,f=synthetic_rows(json.loads(p.read_text()),p.parent);rows+=r;frames+=f
    crops=output/'competition-crops';crops.mkdir()
    missing=[r for r in rows if 'crop' not in r];by_id={r['id']:r for r in missing}
    items=[dict(id=r['id'],path=str(checked(r['image'])),sha256=r['image']['sha256'],bounds=r['bounds']) for r in missing]
    for batch in bounded_batches(items):
        reply=invoke(batch)
        for result in reply['results']:
            p=crops/(digest(result['id'])+'.png');p.write_bytes(base64.b64decode(result['png'],validate=True))
            r=by_id[result['id']];r['crop']=reference(p);r['pixelSHA256']=pixel_digest(ROOT,r['crop'])
    real=json.loads((ROOT/'reports/work/FOCUS-TTR-TEST-CYCLE-01/batch01-protocol.json').read_text())
    models={'shipped':real['models']['shipped'],'fdr010':reference(ROOT/'NativeUITrainer/focus_ring_runs/fdr010-gap-retention/weights/best.pt')}
    code=['focus_representative_validation.py','human_focus_evaluation.py','human_focus_roles.py',
          'focus_ring_baseline.py','focus_ring_backbone.py','focus_runtime.py']
    doc=dict(version=VERSION,role='development-diagnostics',trainingEligible=False,finalChallengeScored=False,
        independentEvaluationEligible=False,threshold=.85,preprocessing=RUNTIME_PREPROCESSING,
        models=models,runtime=runtime(),sources=sources,samples=rows,frames=frames,
        implementation=[reference(ROOT/'scripts'/p) for p in code],
        authorization=reference(ROOT/'Research/Plans/FocusRepresentativeValidation.md'))
    doc['seal']=digest(doc);write(output/'protocol.json',doc);validate(doc)
    print(json.dumps({'samples':len(rows),'pairs':sum(r['kind']=='pair' for r in rows)//2,'completeFrames':len(frames)}))


def validate(doc):
    seal_check(doc)
    require(doc['version']==VERSION and doc['role']=='development-diagnostics' and doc['threshold']==.85
            and doc['trainingEligible'] is False and doc['finalChallengeScored'] is False
            and doc['independentEvaluationEligible'] is False and doc['preprocessing']==RUNTIME_PREPROCESSING,
            'wrong_validation_policy')
    require(set(doc['models'])=={'shipped','fdr010'} and runtime()==doc['runtime'],'changed_runtime_or_models')
    require(model_contract(ROOT/doc['models']['shipped']['path'])==
            {k:v for k,v in doc['models']['shipped'].items() if k!='path'},'changed_shipped_model')
    checked(doc['models']['fdr010']);checked(doc['authorization'])
    for ref in doc['implementation']:checked(ref)
    expected=[];frames=[]
    for ref in doc['sources']:
        p=checked(ref);r,f=synthetic_rows(json.loads(p.read_text()),p.parent);expected+=r;frames+=f
    require(frames==doc['frames'] and len(expected)==len(doc['samples']),'changed_frame_membership')
    require(len({r['id'] for r in doc['samples']})==len(expected),'duplicate_membership')
    for actual,original in zip(doc['samples'],expected,strict=True):
        require(all(actual.get(k)==v for k,v in original.items()),'changed_native_sample')
        checked(actual['image']);checked(actual['crop'])
        require(pixel_digest(ROOT,actual['crop'])==actual['pixelSHA256'],'changed_crop_pixels')


def run(protocol, output):
    doc=json.loads(protocol.read_text());validate(doc);output=fresh(output)
    write(protocol.with_suffix('.started.json'),{'startedAt':datetime.now(timezone.utc).isoformat(),'protocol':reference(protocol)})
    output.mkdir(parents=True);results={}
    for model in ('shipped','fdr010'):
        predictions=[];receipts=[];start=time.monotonic()
        try:
            evaluation.infer(model,doc,predictions,receipts)
            full=summarize(doc['samples'],predictions)
            values={p['id']:p for p in predictions};subsets={}
            for kind in ('pair','competition'):
                rows=[r for r in doc['samples'] if r['kind']==kind]
                policy=None if kind=='pair' else dict(populations=dict(candidate=[r['id'] for r in rows],auxiliary=[],unresolved=[]),frames=doc['frames'])
                subsets[kind]=summarize(rows,[values[r['id']] for r in rows],policy)
            result=dict(state='complete',subsets=subsets)
        except Exception as error:
            result=dict(state='failed',error=f'{type(error).__name__}: {error}')
        valid=[p for p in predictions if type(p.get('probability')) in (int,float) and 0<=p['probability']<=1]
        result.update(predictions=valid,invalidPredictions=[str(p) for p in predictions if p not in valid],
            receipts=receipts,model=doc['models'][model],runtime=doc['runtime'],protocol=reference(protocol),
            expected=len(doc['samples']),scored=len(valid),
            unscored=[r['id'] for r in doc['samples'] if r['id'] not in {p['id'] for p in valid}],
            elapsedSeconds=time.monotonic()-start,backend='CoreML CPU' if model=='shipped' else 'PyTorch CPU')
        write(output/(model+'.json'),result);results[model]=result
        print(json.dumps({'model':model,'state':result['state'],'scored':len(valid)}),flush=True)
        require(result['state']=='complete','model_scoring_failed')
    validate(doc)
    write(output/'comparison.json',dict(version=VERSION,protocol=reference(protocol),results=results,
          independentEvaluationEligible=False,modelGatePassed='not_assessed',finalChallengeScored=False))


def real_reuse(output):
    """Frozen legacy adapter is a retained local implementation dependency, not a new model run."""
    import importlib.util
    adapter=ROOT/'reports/work/FDR-010/compare.py'
    spec=importlib.util.spec_from_file_location('retained_fdr010',adapter)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    freeze=json.loads((ROOT/'reports/work/FDR-010/comparison-freeze.json').read_text())
    results=[];allrows=[];allpred={'shipped':[],'fdr010':[]}
    for source in freeze['inputs']:
        doc,old=module.retained(checked(source['protocol']),checked(source['comparison']))
        current_path=ROOT/'reports/work/FDR-010'/(source['name']+'-candidate.json')
        current=json.loads(current_path.read_text())
        require(current['state']=='complete' and current['candidate']==freeze['candidate'] and
                current['scored']==current['expected']==len(doc['samples']) and
                not current['unscored'] and not current['invalidPredictions'],'incompatible_candidate_scores')
        preds={'shipped':old['results']['shipped']['predictions'],'fdr010':current['predictions']}
        require(evaluation.metrics(doc['samples'],preds['fdr010'],doc['pairs'],doc.get('roleAdmission'))==current['metrics'],
                'changed_candidate_metrics')
        results.append(dict(name=source['name'],protocol=source['protocol'],comparison=source['comparison'],
            candidateScores=reference(current_path),models={m:summarize(doc['samples'],p,doc.get('roleAdmission')) for m,p in preds.items()}))
        supported=[r for r in doc['samples'] if not doc.get('roleAdmission') or
                   (r['population']=='candidate' and r['settlement']=='settled')]
        for r in supported:
            rid=source['name']+':'+r['id'];allrows.append({**r,'id':rid})
            for m in preds:
                value=next(p['probability'] for p in preds[m] if p['id']==r['id'])
                allpred[m].append(dict(id=rid,probability=value))
    report=dict(version=VERSION,adapter=reference(adapter),inputs=results,
                combinedSettledDiagnostics={m:summarize(allrows,p) for m,p in allpred.items()},
                caveat='Combined crop counts are descriptive; preserve source/session groups and per-benchmark decisions.')
    write(fresh(output),report)
    print(json.dumps({'retainedBenchmarks':len(results),'supportedSettledCrops':len(allrows)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run','real-reuse'])
    parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    if a.command=='prepare':prepare(a.input,a.output)
    elif a.command=='run':run(a.input,a.output)
    else:real_reuse(a.output)
