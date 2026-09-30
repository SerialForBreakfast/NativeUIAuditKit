"""Offline, immutable coverage campaign. No models, capture, training or admission."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import shutil

from focus_dataset_contract import ROOT, digest, local, image, pixel_digest
from focus_mixed_assembly import reference, checked
from focus_surface_intake import require, fresh, write
from harvest_sidecar_v2 import recipe_hash

VERSION = 'focus-production-campaign-v1'
QUOTAS = dict(gridMatrix=2000, mediaShelf=1500, settingsList=1000,
              actionDialog=500, heroCarousel=500, focusMaze=500)
ARCHETYPES = dict(gridMatrix='grid_matrix', mediaShelf='media_shelf', settingsList='settings_list',
                  actionDialog='action_dialog', heroCarousel='hero_carousel', focusMaze='focus_maze')
COUNTS = dict(gridMatrix=(8,12,16), mediaShelf=(6,9,12), settingsList=(6,8,10),
              actionDialog=(2,4,6), heroCarousel=(4,6,8), focusMaze=(4,9,16))
THEMES = ('light','high_contrast','dark')


def inventory(rows):
    require(len({r['id'] for r in rows}) == len(rows), 'duplicate_member')
    pairs=defaultdict(list)
    for row in rows:
        require(row.get('split') in ('train','validation','development','test'), 'unknown_partition')
        pairs[row['sourceID'],row['pairID']].append(row)
    counts=Counter(); styles=Counter(); roles=Counter(); groups=Counter(); controls=Counter()
    seen={}; labels={}; pixels={}
    for key, members in sorted(pairs.items()):
        require(sorted(r['label'] for r in members)==[0,1], 'incomplete_pair')
        require(len({r['split'] for r in members})==1, 'pair_split_conflict')
        require(len({(r['scene'],r['style'],r['relatedGroup']) for r in members})==1, 'pair_metadata_conflict')
        positive=next(r for r in members if r['label']==1)
        role=positive['split']; roles[role]+=1
        sig=tuple(r['crop']['pixelSHA256'] for r in sorted(members,key=lambda r:r['label']))
        require(sig[0]!=sig[1], 'contradictory_pair')
        require(sig not in seen, 'duplicate_pair')
        seen[sig]=key
        for r in members:
            h=r['crop']['pixelSHA256']
            require(h not in labels or labels[h]==r['label'], 'contradictory_labels')
            labels[h]=r['label']
            for kind in ('frame','crop'):
                h=r[kind]['pixelSHA256']
                require(h not in pixels or pixels[h]==role, 'cross_partition_pixels')
                pixels[h]=role
        if role=='train':
            counts[positive['scene']]+=1; styles[positive['style']]+=1
            groups[positive['relatedGroup']]+=1;controls[positive['control']]+=1
    quota={scene:dict(required=n,retained=counts[scene],remaining=max(0,n-counts[scene])) for scene,n in QUOTAS.items()}
    return dict(pairsByPartition=dict(roles),trainingScenes=dict(counts),trainingStyles=dict(styles),
                trainingGroups=dict(groups),trainingControls=dict(controls),sceneQuota=quota,
                canonicalAdditionalPairs=sum(q['remaining'] for q in quota.values()),
                nonQuotaTrainingPairs=sum(v for k,v in counts.items() if k not in QUOTAS),
                independence='Not established by scene, seed, or source-name counts.')


def schedule(coverage):
    """Targets are native eligible pairs, not promises that every requested item exports."""
    jobs=[]
    for scene in QUOTAS:
        remaining=coverage['sceneQuota'][scene]['remaining']; n=0
        while remaining>0:
            theme=THEMES[n%3]; count=COUNTS[scene][(n//3)%3]
            recipe=dict(schema_version=1,archetype=ARCHETYPES[scene],element_count=count,
                        theme=theme,density=('compact','regular','spacious')[(n//9)%3],
                        seed=510000+len(jobs),step_index=0)
            # Plain source-defined archetypes only. Artwork-library calibration
            # motifs and custom canvas families are NOT silently moved to training.
            target=min(count,remaining)
            jobs.append(dict(id=f'{scene}-{n+1:04d}',scene=scene,role='train-candidate',
                relatedSourceGroup='fixture-procedural-development',recipe=recipe,
                recipeSHA256=recipe_hash(recipe),collectionTarget=target,
                requestedElements=count,admittedPairs=0,
                state='requires-archetype-native-pair-pilot' if n<3 else 'awaits-pilot-and-authorized-window',
                targetSemantics='Requested elements may be offscreen, disabled or rejected; only accepted native pairs count.'))
            remaining-=target;n+=1
    return jobs


def reserve(entries):
    groups={};members={}
    for e in entries:
        require(e['role'] in ('train-candidate','development-evaluation','protected-challenge'), 'unknown_role')
        for group in e['groups']:
            require(group not in groups or groups[group]==e['role'], 'cross_role_source_group')
            groups[group]=e['role']
        for member in e['members']:
            require(member not in members, 'duplicate_reserved_member')
            members[member]=e['role']
    return dict(groups=groups,members=members)


def build(candidate, protocol, comparison, real, contract, output):
    output=fresh(output)
    paths=[local(p) for p in (candidate,protocol,comparison,real,contract)]
    refs=[reference(p) for p in paths]
    doc,p,c,r=[json.loads(x.read_text()) for x in paths[:4]]
    content=dict(doc);seal=content.pop('protocolSHA256',None)
    require(doc['version']=='focus-training-extension-v1' and digest(content)==seal,'changed_candidate')
    content=dict(p);seal=content.pop('seal',None)
    require(digest(content)==seal and p['role']=='development-diagnostics' and
            p['trainingEligible'] is False and p['finalChallengeScored'] is False,'invalid_evaluation_role')
    require(c['protocol']==refs[1] and set(c['results'])=={'shipped','fdr010'},'incompatible_comparison')
    for result in c['results'].values():
        require(result['state']=='complete' and result['scored']==result['expected']==len(p['samples'])
                and not result['unscored'] and not result['invalidPredictions'],'incomplete_comparison')
    # Validate actual original/crop bytes and decoded identity, not only metadata.
    verified=set()
    for row in doc['samples']:
        for kind in ('frame','crop'):
            value=row[kind];ref={k:value[k] for k in ('path','sha256')}
            key=(value['path'],value['sha256'],value['pixelSHA256'])
            if key in verified:continue
            checked(ref);image(ROOT,ref,(256,256) if kind=='crop' else None)
            require(pixel_digest(ROOT,ref)==value['pixelSHA256'],'changed_decoded_pixels')
            verified.add(key)
    coverage=inventory(doc['samples']);jobs=schedule(coverage)
    # These are exact existing membership reservations, NOT independence claims.
    reservations=[dict(role='train-candidate',groups=['retained-training-membership'],
                       members=[row['id'] for row in doc['samples'] if row['split']=='train']),
                  dict(role='development-evaluation',groups=['retained-retention-membership'],
                       members=[row['id'] for row in doc['samples'] if row['split']!='train']),
                  dict(role='development-evaluation',groups=['synth05-calibration-membership'],
                       members=['synth05:'+row['id'] for row in p['samples']])]
    for entry in r['inputs']:
        source=json.loads(checked(entry['protocol']).read_text())
        reservations.append(dict(role='development-evaluation',groups=['real:'+entry['name']],
            members=['real:'+entry['name']+':'+row['id'] for row in source['samples']]))
    reservation=reserve(reservations)
    # Measure retained SYNTH05 byte sizes once per source file. Scale is only an
    # estimate; campaign may render much larger/more detailed frames.
    frame_paths={checked(row['image']) for row in p['samples']}
    crop_paths={checked(row['crop']) for row in p['samples']}
    pilot_bytes=sum(x.stat().st_size for x in frame_paths|crop_paths)
    estimated=math.ceil(pilot_bytes/50*coverage['canonicalAdditionalPairs']*1.5)
    free=shutil.disk_usage(ROOT).free
    result=dict(version=VERSION,inputs=refs,code=reference(Path(__file__)),coverage=coverage,
        jobs=jobs,reservations=reservation,readinessBlockers=doc['readinessBlockers'],
        samplingPreserved=doc['sampling'],selectionPreserved=doc['selection'],
        storage=dict(freeBytesAtPlanning=free,pilotBytes=pilot_bytes,pilotPairs=50,
            estimatedAdditionalBytesWith50PercentMargin=estimated,workingReserveBytes=10*1024**3,
            estimatedFits=free>=estimated+10*1024**3,
            caveat='Estimate excludes new archive duplicates and model outputs; recheck before every wave. No cleanup authorized.'),
        themeTargets=dict(lightFraction=.2,highContrastFraction=.2,scope='gridMatrix + mediaShelf'),
        hardNegativeGate=dict(minimum=100,roles=['held-out'],themes=['light','highContrast'],
            controls=['imageView','collectionItem'],everyCrossProductCellNonempty=True,maximumFPR=.005),
        executionAuthorized=False,trainingAdmission=False,independentEvaluationEligible=False,
        releaseEligible=False,notes=[
            'Jobs use source-defined recipe fields, but current runtime and per-archetype pairing must be qualified before dispatch.',
            'Seeds provide variation, not independent sources. Related recipe/asset/ancestry groups stay in one role.',
            'Current SYNTH05 calibration and all reviewed real screens stay development-evaluation.',
            'Prior nine retention pairs and all existing sampling/selection references remain unchanged.',
            'Reserve new independent validation and challenge sources before capture; no challenge images are opened here.',
            'Plain archetypes meet volume scheduling only; failed artwork and real-transfer requirements need the separately detailed priority assignment.',
            'Count only deduplicated accepted pairs; rejected/offscreen/unsettled members remain deficits, never silent replacements.'])
    result['seal']=digest(result)
    output.mkdir(parents=True);(output/'recipes').mkdir()
    for job in jobs:write(output/'recipes'/(job['id']+'.json'),job['recipe'])
    write(output/'campaign.json',result)
    # Read-back source references after work; no source mutation is permitted.
    for ref in refs:checked(ref)
    print(json.dumps(dict(jobs=len(jobs),additionalPairs=coverage['canonicalAdditionalPairs'],storage=result['storage'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('candidate','protocol','comparison','real','contract','output'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();build(**vars(args))
