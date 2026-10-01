"""Offline native-artwork acceptance and non-executable matched-data preflight."""
import argparse
from collections import Counter, defaultdict
import math
import re

import numpy as np
from PIL import Image
import human_annotation_review as h
import focus_native_body_assembly as native
from human_corpus_inventory import metadata_hashes

VERSION = 'focus-artwork-readiness-v1'
ARM = 'artwork-readiness'
RULE = 'central192-minRGBgt220-rangeLT25-fractionGT0.65-v1'


def baseline(path):
    doc=h.read(path,limit=32*1024**2)
    h.require(doc.get('version')=='focus-visual-experiment-v1' and
              doc.get('protocolSHA256')==h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}),
              'changed_or_unsupported_baseline')
    rows=doc['samples'];allowed={('train','train-candidate'),('train','human-static-auxiliary'),
        ('validation','representative-selection'),('validation','retention-validation')}
    h.require(rows and len({r['id'] for r in rows})==len(rows) and all(
        (r['split'],r['use']) in allowed and type(r['label']) is int and r['label'] in (0,1) for r in rows),
        'protected_or_invalid_baseline_membership')
    for row in rows:
        for key in ('crop','frame','image'):
            if row.get(key):h.checked(h.ROOT,row[key])
    h.checked(h.ROOT,doc['representation']['weights'])  # hash only; never deserialize
    native.continuous_weights(doc,[])  # verifies complete positive training mass
    return doc


def white_fraction(ref):
    with Image.open(h.checked(h.ROOT,ref)) as im:
        h.require(im.size==(256,256),'production_crop_size')
        pixels=np.asarray(im.convert('RGB').crop((32,32,224,224)),dtype=np.int16)
    return float(((pixels.min(axis=2)>220)&(pixels.max(axis=2)-pixels.min(axis=2)<25)).mean())


def content(row):
    """Bound producer declaration, not OCR or a claim that pixels contain a logo."""
    appearance=row['recipe'].get('appearance') or {};comp=appearance.get('composition')
    if not comp:
        # Existing competitor-v3 canvas is independently supported. Do not require
        # composition-v1 (which currently cannot declare competitor pairing).
        if not appearance.get('canvas') or row['recipe'].get('seed') is None:return None
        value=dict(recipeSeed=row['recipe']['seed'],target=row['sourceElementID'],
                   preset=appearance.get('preset'),artwork=appearance.get('artwork'),
                   recipeHash=row['recipe']['recipe_hash'])
        return dict(id=row['sourceElementID'],declaration=value,sha256=h.digest(value),
                    semantics='recipe_target_binding_only_logo_or_blank_unverified')
    matches=[i for region in comp['regions'] for i in region['items'] if i['id']==row['sourceElementID']]
    h.require(len(matches)==1,'content_target_membership')
    item=matches[0];value=comp['contents'][item['content']]
    return dict(id=item['content'],declaration=value,sha256=h.digest(value),
                semantics='logo_or_blank_not_established_by_declaration')


def summarize(rows, links, fractions):
    """No first-seen label wins; duplicates remain explicit and never count twice."""
    h.require(len({r['id'] for r in rows})==len(rows),'duplicate_candidate_id')
    by_key={(r['batchID'],r['frameID'],r['controlID']):r for r in rows}
    h.require(len(by_key)==len(rows),'duplicate_control_key')
    h.require(set(fractions)=={r['id'] for r in rows} and all(type(v) in (int,float)
        and math.isfinite(v) and 0<=v<=1 for v in fractions.values()),'appearance_membership')
    frames=defaultdict(list)
    for row in rows:frames[row['batchID'],row['frameID']].append(row)
    pairs=[];seen=set();white_pairs=set();eligible_ids=set()
    for link in sorted(links,key=lambda x:(x['batchID'],x['id'])):
        key=(link['batchID'],link['id']);h.require(key not in seen,'duplicate_pair');seen.add(key)
        h.require(len(link['frames'])==2 and len(set(link['frames']))==2,'pair_frame_membership')
        members=[by_key.get((link['batchID'],fid,link['controlID'])) for fid in link['frames']]
        h.require(all(members),'missing_pair_control')
        f,u=members
        h.require([f['label'],u['label']]==[1,0] and f['sourceElementID']==u['sourceElementID'] and
            f['sourceID']==u['sourceID'] and f['sourcePairID']==u['sourcePairID']==link['sourcePairID'] and
            f['recipe']==u['recipe'] and f['control']==u['control'],'unmatched_focus_pair')
        if f['control']!='collectionItem':continue
        declarations=[content(r) for r in members]
        h.require(declarations[0]==declarations[1],'pair_content_changed')
        competitors=all(any(r['controlID']!=target['controlID'] and r['label']==1-target['label']
            for r in frames[target['batchID'],target['frameID']]) for target in members)
        pixel_key=tuple(r['crop']['pixelSHA256'] for r in members)
        both_white=all(fractions[r['id']]>.65 for r in members)
        reasons=sorted({reason for r in members for reason in r['reasons'] if reason!='duplicate_crop'})
        if not competitors:reasons.append('focused_competitor_missing_in_negative_frame')
        if declarations[0] is None:reasons.append('asset_binding_unknown')
        if not reasons:
            eligible_ids.update(r.get('duplicateOf') or r['id'] for r in members)
            if both_white:white_pairs.add(pixel_key)
        pairs.append(dict(id=link['id'],batchID=link['batchID'],members=[r['id'] for r in members],
            target=f['sourceElementID'],content=declarations[0],visibleCompetitors=competitors,
            whiteFractions=[fractions[r['id']] for r in members],bothWhite=both_white,
            cropPixelIdentities=list(pixel_key),reasons=reasons,
            growth=[f['bounds'][i]/u['bounds'][i] for i in (2,3)]))
    groups=defaultdict(lambda:dict(observations=0,whiteObservations=0,pixels=set(),whitePixels=set()))
    for r in rows:
        g=groups[r['control']+':'+str(r['label'])];px=r['crop']['pixelSHA256'];g['observations']+=1;g['pixels'].add(px)
        if fractions[r['id']]>.65:g['whiteObservations']+=1;g['whitePixels'].add(px)
    for g in groups.values():
        g['uniqueCropPixels']=len(g.pop('pixels'));g['uniqueWhiteCropPixels']=len(g.pop('whitePixels'))
    return dict(groups=dict(groups),artworkPairs=pairs,distinctSupportedWhitePairs=len(white_pairs),
                proposedIDs=sorted(eligible_ids),logoAndBlankCoverage='unknown_requires_asset_evidence_or_review')


def mass(rows,weights):
    result=defaultdict(float)
    for r in rows:
        if r['split']=='train':result[r.get('sourceKind','unspecified')+':'+r['use']+':'+str(r['label'])]+=weights[r['id']]
    return dict(sorted(result.items()))


def comparison(base, additions):
    """Hypothetical weights only; additions are not admitted by this operation."""
    proposed=[dict(r,split='train',use='train-candidate') for r in additions]
    weights=native.continuous_weights(base,proposed)
    evaluation=[r for r in base['samples'] if r['split']!='train']
    train=[r for r in base['samples'] if r['split']=='train']
    return dict(controlTrainingIDs=[r['id'] for r in train],proposedAdditionIDs=[r['id'] for r in proposed],
        evaluationMembershipSHA256=h.digest(evaluation),evaluationIDs=[r['id'] for r in evaluation],
        selectionSHA256=h.digest(base['selection']),baselineWeights=base['fullFit']['weights'],
        hypotheticalAdditionWeights=weights,weightPolicy=native.CONTINUITY_POLICY,
        baselineSourceLabelMass=mass(train,base['fullFit']['weights']),
        proposedSourceLabelMass=mass(train+proposed,weights),
        configuration=base['configuration'],fullFit={k:v for k,v in base['fullFit'].items() if k!='weights'},
        representation=base['representation'],arms=['matched-partial-detail-control','matched-partial-detail-added-data'],
        modelPolicy=dict(input='production-detail-only',frozenPrefix='features[:9]',trainableTail='features[9:]',
                         batchNorm='frozen',head='1152-64-1; context columns zeroed',optimizer='AdamW'),
        onlyChange='admitted training examples; fixture label mass redistributed, OS/human members unchanged',
        evaluationRole='development-exposed and retention; not independent release qualification',
        executor='existing focus_visual_experiment partial-detail path; future exact-data adapter/envelope required',
        executionAuthorized=False)


def conditional_owned_comparison(base, rows, coverage):
    """Plan exact unique owned-target additions, without clearing any blocking reason."""
    pending={'screenshot_time_hash_binding_unqualified','pair_index_recipe_file_hash_mismatch','duplicate_crop'}
    by_id={r['id']:r for r in rows};eligible=set();pairs=[]
    for p in coverage['artworkPairs']:
        declaration=(p.get('content') or {}).get('declaration',{})
        if not declaration.get('owned_artwork') or not p['bothWhite'] or not p['visibleCompetitors']:continue
        if set(p['reasons'])-pending:continue
        pairs.append(p['id']);eligible.update(p['members'])
    owners={};aliases={}
    for rid in sorted(eligible):
        r=by_id[rid];key=r['crop']['pixelSHA256']
        if key in owners:aliases[rid]=owners[key]['id']
        else:owners[key]=r
    additions=list(owners.values())
    return dict(purpose='conditional evidence-resolution proposal only; no reasons removed or admission',
        pairIDs=sorted(pairs),duplicateAliases=aliases,
        unresolvedReasons=sorted({reason for r in additions for reason in r['reasons']}),
        comparison=comparison(base,additions),trainingEligible=False,executionAuthorized=False)


def prepare(spec):
    h.require(set(spec)=={'baseline','sources','protected'},'readiness_input_fields')
    base=baseline(h.checked(h.ROOT,spec['baseline']))
    protected=metadata_hashes(h.read(h.checked(h.ROOT,spec['protected'])))
    for r in base['samples']:
        if r['split']!='train':
            protected |= metadata_hashes([r.get(k,{}) for k in ('crop','frame','image')])
    rows,accounting,links=native.candidates(spec['sources'],protected)
    rows=native.classify(rows,base['samples'],protected)
    cache={};fractions={};producer_roles={}
    for r in rows:
        key=r['crop']['pixelSHA256']
        if key not in cache:cache[key]=white_fraction(r['crop'])
        fractions[r['id']]=cache[key]
        if r['sourceID'] not in producer_roles:
            root=h.ROOT/r['sourceID']
            if (root/'pair-index.json').is_file():
                producer_roles[r['sourceID']]={p['frame_prefix']:p['role'] for p in h.read(root/'pair-index.json')['pairs']}
            else:
                manifest=h.read(root/'manifest.json')
                producer_roles[r['sourceID']]={p['id']:p['split'] for p in manifest}
        r['producerSplit']=producer_roles[r['sourceID']][r['sourcePairID']]
    coverage=summarize(rows,links,fractions)
    proposed=[r for r in rows if r['id'] in set(coverage['proposedIDs'])]
    blockers=['human_sample_acceptance_pending','exact_training_admission_pending',
              'source_role_decision_pending','new_data_encoding_and_execution_envelope_pending',
              'logo_and_blank_asset_evidence_pending']
    if not coverage['distinctSupportedWhitePairs']:
        observed=any(p['bothWhite'] and p['visibleCompetitors'] for p in coverage['artworkPairs'])
        blockers.append('matched_white_artwork_evidence_pending' if observed else 'matched_white_artwork_coverage_absent')
    if not proposed:blockers.append('no_supported_unique_artwork_additions')
    # Composition recipes are large shared evidence, not per-control payloads.
    # Keep exact canonical identities once instead of exceeding the bounded reader.
    recipes={};compact=[]
    for row in rows:
        key=h.digest(row['recipe']);recipes[key]=row['recipe']
        compact.append({**{k:v for k,v in row.items() if k!='recipe'},'recipeSHA256':key})
    report=dict(version=VERSION,inputs=spec,configurationValid=True,launchEligible=False,
        trainingEligible=False,releaseEligible=False,modelGatePassed='not_assessed',executionAuthorized=False,
        descriptor=RULE,descriptorPurpose='coverage only; not label truth or a qualification threshold',
        coverage=coverage,comparison=comparison(base,proposed),candidates=compact,recipes=recipes,nativeAccounting=accounting,
        sourceRoles={k:dict(Counter(v.values())) for k,v in producer_roles.items()},
        counts=dict(candidates=len(rows),proposedAdditions=len(proposed),
                    dispositions=dict(Counter(r['disposition'] for r in rows))),blockers=blockers)
    if any((p.get('content') or {}).get('declaration',{}).get('owned_artwork') for p in coverage['artworkPairs']):
        report['conditionalOwnedComparison']=conditional_owned_comparison(base,rows,coverage)
    report['protocolSHA256']=h.digest(report)
    return report


def load_protocol(path,arm,run_name,approval_path=None):
    h.require(arm==ARM and approval_path is None,'readiness_not_execution_approval')
    h.require(isinstance(run_name,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name),'invalid_run_name')
    doc=h.read(h.local(path),limit=32*1024**2)
    h.require(doc.get('version')==VERSION and doc.get('protocolSHA256')==h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}),'changed_readiness')
    h.require(doc==prepare(doc['inputs']),'readiness_inputs_changed')
    return dict(formatVersion='focus-representative-preflight-v1',protocolVersion=VERSION,
        configurationValid=True,launchEligible=False,executionAuthorized=False,releaseEligible=False,
        configuration=doc['comparison']['configuration'],counts=doc['counts'],blockers=doc['blockers'],
        protocolSHA256=doc['protocolSHA256']),[]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',required=True);p.add_argument('--protected',required=True)
    p.add_argument('--source',nargs=2,action='append',required=True,metavar=('BATCH','CROP_QA'))
    p.add_argument('--output',required=True)
    args=p.parse_args()
    try:
        out=h.fresh(args.output)
        spec=dict(baseline=h.ref(h.local(args.baseline)),protected=h.ref(h.local(args.protected)),
                  sources=[dict(batch=h.ref(h.local(b)),crops=h.ref(h.local(c))) for b,c in args.source])
        report=prepare(spec);out.mkdir(parents=True)
        h.write(out/'readiness.json',report)
        print(dict(counts=report['counts'],distinctSupportedWhitePairs=report['coverage']['distinctSupportedWhitePairs'],blockers=report['blockers']))
        return 0
    except (OSError,ValueError,KeyError,TypeError) as e:p.exit(2,str(e)+'\n')


if __name__=='__main__':raise SystemExit(main())
