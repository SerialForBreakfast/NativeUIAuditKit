"""Review native class mappings and visible geometry without inventing inventory coverage."""
from pathlib import Path
from collections import Counter
import math
import research_queue as q
from experiment_templates import checked,pin
from sdk_packet502 import review
from sdk_semantics529 import classify,transformed_bounds
from detector_case_match411 import iou
OUT=None


def annotations(evidence,image,policy):
    reviewed=review(evidence,image)
    q.require(reviewed['reviewable'],'sdk529_annotation_frame_unqualified')
    q.require(set(policy)=={'rules','taxonomy','coverage','transform'},'sdk529_annotation_policy')
    q.require(isinstance(policy['taxonomy'],list) and policy['taxonomy'] and len(policy['taxonomy'])==len(set(policy['taxonomy'])),'sdk529_annotation_taxonomy')
    for rule in policy['rules']:
        q.require(rule['class'] in policy['taxonomy'],'sdk529_annotation_class')
    coverage=policy['coverage']
    q.require(set(coverage)=={'scope','reviewer','evidence','expectedIDs'} and coverage['scope'] in ('registered_only','complete_supported_classes'),'sdk529_annotation_coverage')
    raw=evidence['after']['elements'];ids=[x['identity']['id'] for x in raw]
    complete=coverage['scope']=='complete_supported_classes'
    if complete:
        q.require(coverage['reviewer'] and coverage['evidence'] and isinstance(coverage['expectedIDs'],list) and
                  len(coverage['expectedIDs'])==len(set(coverage['expectedIDs'])) and set(coverage['expectedIDs'])==set(ids),'sdk529_annotation_inventory')
        checked(coverage['evidence'])
    rows=[]
    for control in raw:
        state=control.get('observedState') or {};b=control.get('bounds') or {}
        visible=state.get('source')=='uikit_ancestor_state' and state.get('hidden') is False and type(state.get('effectiveAlpha')) in (int,float) and state['effectiveAlpha']>0
        geometry=None
        if visible and all(k in b for k in ('x','y','width','height')):
            matrix=policy['transform']
            if control.get('coordinateSpace')=='screenPixels':matrix=[1,0,0,1,0,0]
            elif matrix is not None:
                q.require(set(matrix)=={'coordinateSpace','affine','evidence'} and matrix['coordinateSpace']==control.get('coordinateSpace'),'sdk529_annotation_transform')
                checked(matrix['evidence']);matrix=matrix['affine']
            if matrix is not None:
                geometry=transformed_bounds([b[k] for k in ('x','y','width','height')],matrix,[evidence['width'],evidence['height']])
        label=classify(control,policy['rules'])
        rows.append(dict(identity=control['identity'],parentID=control.get('parentID'),nativeClass=control.get('className'),
            enabled=state.get('enabled'),visible=visible,geometry=geometry,**label))
    qualified=[r for r in rows if r['visible'] and r['geometry'] and r['geometry']['visible'] and r['state']=='mapped']
    duplicates=[]
    for i,a in enumerate(qualified):
        for b in qualified[i+1:]:
            if a['taxonomyClass']==b['taxonomyClass'] and a['geometry']['visible']==b['geometry']['visible']:
                duplicates.append([a['identity']['id'],b['identity']['id']])
    unresolved=[r['identity']['id'] for r in rows if r['visible'] and (r['state']!='mapped' or not r['geometry'])]
    return dict(rows=rows,qualifiedIDs=[r['identity']['id'] for r in qualified],duplicates=duplicates,unresolvedIDs=unresolved,
                completeSupportedInventory=complete and not duplicates and not unresolved,trainingAdmitted=False,
                limitation='Disabled visible controls remain detector targets. Hidden controls and unavailable occlusion are reported separately.')


def compare_labels(rows,predictions,baseline):
    """Use one-to-one class-aware matching on identical boxes; never infer full-scene precision."""
    truths=[r for r in rows if r['visible'] and r['geometry'] and r['geometry']['visible'] and r['state']=='mapped']
    result={}
    for arm in ('baseline','reviewed'):
        candidates=[]
        for i,t in enumerate(truths):
            label=baseline.get(t['identity']['id']) if arm=='baseline' else t['taxonomyClass']
            box=t['geometry']['visible'];x,y,w,h=box
            for j,p in enumerate(predictions):
                q.require(set(p)=={'box','class'} and len(p['box'])==4 and all(type(v) in (int,float) and math.isfinite(v) for v in p['box']),'sdk529_annotation_prediction')
                a,b,c,d=p['box'];q.require(c>0 and d>0,'sdk529_annotation_prediction_geometry')
                overlap=iou([x,y,x+w,y+h],[a,b,a+c,b+d])
                if label is not None and p['class']==label and overlap>=.5:candidates.append((-overlap,i,j))
        used_truth=set();used_prediction=set()
        for _,i,j in sorted(candidates):
            if i not in used_truth and j not in used_prediction:used_truth.add(i);used_prediction.add(j)
        result[arm]=dict(matchedIDs=[truths[i]['identity']['id'] for i in sorted(used_truth)],
                         unmatchedIDs=[t['identity']['id'] for i,t in enumerate(truths) if i not in used_truth and (arm=='reviewed' or baseline.get(t['identity']['id']) is not None)],
                         unlabelledIDs=[t['identity']['id'] for t in truths if arm=='baseline' and baseline.get(t['identity']['id']) is None])
    return dict(**result,annotationCorrectionOnly=True,modelImprovement=False)


def evaluate(request):
    q.require(set(request)=={'version','id','frames','policy'} and request['version']=='sdk-annotation-review-v1' and q.ID.fullmatch(request['id']),'sdk529_annotation_request')
    q.require(0<len(request['frames'])<=64,'sdk529_annotation_count')
    policy=q.load(checked(request['policy']));rows=[]
    for rule in policy['rules']:
        q.require(isinstance(rule.get('evidence'),dict),'sdk529_mapping_evidence_pin')
        checked(rule['evidence'])
    for f in request['frames']:
        q.require(set(f)=={'id','image','evidence','baselineLabels','predictions'},'sdk529_annotation_frame')
        e=q.load(checked(f['evidence']));r=annotations(e,checked(f['image']),policy)
        predictions=q.load(checked(f['predictions']))
        if 'runtime' in predictions:
            predictions=dict(imageSHA256=predictions['inputSHA256'],elements=[dict(box=[e['boundingBoxPixels'][k] for k in ('x','y','width','height')],class_=e['elementType']) for e in predictions['runtime']['result']['elements']])
            for e in predictions['elements']:e['class']=e.pop('class_')
        q.require(predictions['imageSHA256']==f['image']['sha256'],'sdk529_annotation_prediction_lineage')
        rows.append(dict(id=f['id'],annotation=r,comparison=compare_labels(r['rows'],predictions['elements'],f['baselineLabels'])))
    return dict(version='sdk-annotation-report-v1',frames=rows,modelAccepted=False,trainingAdmitted=False)


def build(path):
    r=q.load(path);evaluate(r)
    policy=q.load(checked(r['policy']));refs=[pin(path),r['policy']]+[f[k] for f in r['frames'] for k in ('image','evidence','predictions')]
    refs.extend(rule['evidence'] for rule in policy['rules'])
    if policy['coverage'].get('evidence'):refs.append(policy['coverage']['evidence'])
    if policy['transform'] is not None:refs.append(policy['transform']['evidence'])
    refs=list({v['path']:v for v in refs}.values())
    return dict(version='research-spec-v2',id=r['id'],task='SDK529',owner='Maximum-mini-NUIAK',kind='screen',jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs+[pin(Path(__file__))],
        adapter=dict(type='python-callable',steps=['sdk_annotations529.run'],outputAttributes=['sdk_annotations529.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),evidence=dict(reads=[v['path'] for v in refs],artifactReceipt='artifact-receipt.json'),
        question='How do reviewed native class annotations change matched detector error classification?',
        hypothesis='Class, identity, and measured geometry distinguish annotation errors from model errors.',
        controlledComparison='Pinned identical images and detector predictions; only reviewed annotation mappings change.',
        decisionRule='Keep ambiguous labels unavailable. Annotation corrections do not prove model improvement.',
        nextActionByOutcome=dict(supported='Qualify complete training coverage and prepare a matched training comparison.',contradicted='Record unresolved classes and preserve prior annotations.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');r=evaluate(q.load(checked(spec['inputs'][0])))
    q.save(OUT/'benchmark_summary.json',r);q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
