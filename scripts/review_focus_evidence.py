"""Pinned cached-result intake for EVIDENCE223. Does not execute worker code/models."""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from collections import Counter
import focus_evidence as e

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    e.require(path.stat().st_size<=32*1024*1024,'input_size')
    def pairs(items):
        result={}
        for k,v in items:
            e.require(k not in result,'duplicate_key');result[k]=v
        return result
    return json.loads(path.read_text(),object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite')))


def load_inputs(manifest):
    e.require(manifest.get('version')=='evidence223-inputs-v1','input_version')
    docs={}
    for key,ref in manifest['inputs'].items():
        path=ROOT/ref['path']
        e.require(path.resolve().is_relative_to(ROOT) and path.is_file(),'input_boundary')
        e.require(hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],'input_hash:'+key)
        docs[key]=read(path)
    e.require(set(docs)=={'endpoint','union','native','bd14','bd27','ios'},'input_membership')
    return docs


def temporal(doc,kind,pin):
    frames=doc['frames'];results={};comparisons={}
    methods={'whole':'whole','tile':'tile'} if kind=='bd27' else {
        'whole':'whole_frame_difference','oracle':'foreground_oracle_difference'}
    for threshold in (.001,.005,.01,.02):
        arms={}
        for method,key in methods.items():
            rows=[]
            for r in frames:
                value=r[key];truth=r['foreground_stable']
                e.require(value is None or (type(value) in (int,float) and math.isfinite(value)
                                           and 0<=value<=1),'invalid_measurement')
                e.require(truth is None or type(truth) is bool,'invalid_stability_truth')
                rows.append(dict(id=(r['episode'] if kind=='bd27' else r['episode_id'])+':'+
                    str(r['t'] if kind=='bd27' else r['frame']),
                    group=r['family'] if kind=='bd27' else r['group'],role=r['role'],
                    condition=r['condition'],truth=None if truth is None else not truth,
                    decision=None if value is None else value>threshold,authority='authored'))
            context=dict(source=pin,domain='procedural',model={'baseline':method},
                preprocessing={'threshold':threshold,'truth':'three-frame authored foreground equality',
                               'oracle':method=='oracle'})
            results[f'{method}:{threshold}']=e.report(rows,task='temporal-instability',context=context)
            arms[method]=rows
        other='tile' if kind=='bd27' else 'oracle'
        comparisons[str(threshold)]=e.paired_groups(arms['whole'],arms[other])
    return dict(reports=results,pairedComparisons=comparisons,
                thresholdSelected=False,nativeEfficacy=None,
                comparisonScope='All arms score authored foreground stability; BD14 legacy whole-frame scores used a different full-frame target. Do not equate those denominators.')


def native(doc,pin):
    e.require(doc.get('id')=='bd12-13-native48-report01','native_version')
    rows={};audit=[]
    for r in doc['cases']:
        e.require(r['reported_focus_change_expectation'] in ('change','no-change'),'native_expectation')
        flags=r['flags']
        audit.append(dict(id=r['stableID'],flags=flags,
            disposition='unresolved-source-binding',
            secondaryDisposition='unsupported-semantics' if 'unsupported_crop_metadata' in flags else None,
            needed=['capture-era source/build binding','independent observed-focus/geometry qualification'],
            frames=r['frames'],cropChecks=r['crop_checks']))
        for model,decision in r['dispositions'].items():
            e.require(decision in ('change','no-change','abstain'),'native_decision')
            rows.setdefault(model,[]).append(dict(id=r['stableID'],group='native48-unresolved-ancestry',
                role='calibration-inspection',condition=r['reported_condition'],authority='producer-reported',
                truth=r['reported_focus_change_expectation']=='change',
                decision=None if decision=='abstain' else decision=='change'))
    return dict(cases=audit,duplicates=doc['duplicates'],dataEligible=False,
        reports={model:e.report(values,task='focus-change',context=dict(source=pin,
            domain='native-fixture',model={'name':model,**doc['models'][model]},
            preprocessing={'identity':'retained report; no new inference','qualified':False}))
            for model,values in rows.items()},missingEvidence=doc['missing_fields'])


def ios_qa(doc):
    e.require(doc.get('schema')=='worker218-retention-v1','ios_version')
    ranked=[];geometry=[];ids=[];missing=0
    for case in doc['cases']:
        ident=case['partition']+':'+case['imageID'];ids.append(ident)
        for box in case['FP']:
            if box['reason']!='unmatched_FP':continue
            score=box.get('score')
            if score is None:missing+=1;continue
            e.require(type(score) in (float,int) and math.isfinite(score) and 0<=score<=1,'qa_score')
            ranked.append(dict(case=ident,group=case['group'],proposal=box,
                               disposition='review-needed-not-label-error'))
        for box in case['GT']:
            if any('localization' in state for state in box['states'].values()):
                geometry.append(dict(case=ident,group=case['group'],annotation=box,
                                     disposition='review-needed-not-correction'))
    e.require(len(ids)==len(set(ids)),'duplicate_ios_case')
    ranked.sort(key=lambda r:(-r['proposal']['score'],r['proposal']['stableID']))
    sample=sorted(ids,key=lambda x:hashlib.sha256(('223:'+x).encode()).hexdigest())[:math.ceil(len(ids)*.1)]
    return dict(cases=len(ids),rankedUnmatched=ranked,geometryReview=geometry,randomCaseSample=sample,
        randomSampleSeed=223,unrankableMissingScore=missing,automaticCorrections=0,
        limitation='Reviewer queue only; archived matching/label policy may explain unmatched predictions.')


def run(manifest):
    start=time.monotonic();docs=load_inputs(manifest)
    from harvest_schema4_review import compare_geometry
    result=dict(version='evidence223-review-v1',inputs=manifest['inputs'],
        crop=dict(endpoint=e.schema4_report(docs['endpoint']),union=e.schema4_report(docs['union']),
                  comparison=compare_geometry(docs['endpoint'],docs['union'])),
        native=native(docs['native'],manifest['inputs']['native']),
        temporal={k:temporal(docs[k],k,manifest['inputs'][k]) for k in ('bd14','bd27')},
        ios=ios_qa(docs['ios']),
        gaps=['qualified native source/labels','independent real-app audit groups',
              'native settledness sequence truth','fixed-box focus identity contrast in authored benchmark',
              'deployable regional similarity baseline on qualified native sequences'],
        outcomes=dict(dataEligible=False,integrationQualified=False,modelGatePassed=None),
        elapsedSeconds=time.monotonic()-start)
    result['art191TruthAudit']=[dict(id=p['path'],disposition='unresolved-source-binding',
        clipped=p['clipped'],note='clipping is not itself label error; body/effect geometry differ')
        for p in docs['endpoint']['pairs']]
    # Re-read hashes at completion; changed inputs invalidate the attempt.
    load_inputs(manifest)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        out=args.output.absolute()
        e.require(out.resolve().is_relative_to(ROOT) and not out.exists(),'output_collision_or_boundary')
        result=run(read(args.inputs))
        out.mkdir(parents=True)
        with (out/'report.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
        print(json.dumps(dict(output=str(out),nativeCases=len(result['native']['cases']),
            iosCases=result['ios']['cases'],randomReview=len(result['ios']['randomCaseSample']),
            elapsedSeconds=result['elapsedSeconds'])))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(json.dumps({'error':str(exc)}));return 2


if __name__=='__main__':raise SystemExit(main())
