"""Group retained triplets by shared pixels without extracting or admitting them."""
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path,PurePosixPath
import tarfile
from PIL import Image
import research_queue as q
from research_campaign340 import pin
from focus_surface_intake import safe_members

OUT=None


def connected(rows):
    parents={row['id']:row['id'] for row in rows};seen={}
    q.require(len(parents)==len(rows),'duplicate_case')
    def root(value):
        while parents[value]!=value:
            parents[value]=parents[parents[value]];value=parents[value]
        return value
    for row in rows:
        for key in row['keys']:
            if key in seen:parents[root(row['id'])]=root(seen[key])
            else:seen[key]=row['id']
    groups=defaultdict(list)
    for row in rows:groups[root(row['id'])].append(row['id'])
    return sorted((sorted(v) for v in groups.values()),key=lambda v:(-len(v),v))


def run():
    config=q.load(OUT/'config.json');ref=config['archive'];path=q.local_path(q.ROOT,ref['path'])
    q.require(q.digest(path)==ref['sha256'],'archive_hash')
    rows=[];hashes=set();labels={};metadata=[]
    with tarfile.open(path) as archive:
        members=archive.getmembers();q.require(len(members)<=2500,'archive_count')
        q.require(sum(v.size for v in members)<=100_000_000,'archive_size')
        names=set()
        for member in members:
            safe_members([member],max_member_bytes=10_000_000)
            key=str(PurePosixPath(member.name)).casefold();q.require(key not in names,'duplicate_path');names.add(key)
        manifest=json.load(archive.extractfile('bulk_crop_triplets_manifest.json'))
        q.require(len(manifest['cases'])==200,'case_count')
        for case in manifest['cases']:
            id=case['case_id'];q.require(q.ID.fullmatch(id),'case_id')
            crop=json.load(archive.extractfile(f'crops/{id}/crop_manifest.json'));keys=[]
            for role in ('anchor','positive','negative'):
                item=crop[role];q.require(item['file']==f'crop_{role}.png','crop_path')
                raw=archive.extractfile(f'crops/{id}/'+item['file']).read()
                digest=hashlib.sha256(raw).hexdigest()
                q.require(digest==item['sha256']==case[f'crop_{role}_sha256'],'crop_hash')
                with Image.open(io.BytesIO(raw)) as image:
                    q.require(image.size==(256,256),'crop_size');image.load()
                    pixel=hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
                q.require(type(item['is_focused']) is bool,'focus_label')
                q.require(labels.setdefault(pixel,item['is_focused'])==item['is_focused'],'conflicting_pixel_label')
                keys.append('pixel:'+pixel);hashes.add(pixel)
            pixelkeys=keys.copy()
            keys.extend('reported-frame:'+case[k] for k in ('focused_sha256','unfocused_sha256'))
            rows.append(dict(id=id,keys=keys,pixelKeys=pixelkeys))
            metadata.append(dict(id=id,anchorFocused=crop['anchor']['is_focused'],positiveFocused=crop['positive']['is_focused'],
                                 sameControl=crop['anchor']['node_id']==crop['positive']['node_id']))
    pixelgroups=connected([dict(id=r['id'],keys=r['pixelKeys']) for r in rows])
    allgroups=connected(rows)
    q.save(OUT/'diagnostic.json',dict(archive=ref,cases=200,crops=600,uniqueDecodedImages=len(hashes),
        pixelConnectedGroups=pixelgroups,reportedAncestryGroups=allgroups,caseSemantics=metadata,
        fullFramesPresent=False,trainingEligible=False,
        limitation='Reported frame hashes add conservative ancestry. Their source pixels are absent. No independence is established.',
        nextAction='Keep connected cases together. Verify crop mapping and source renderer before admission.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS342';id='focus342-triplet-groups'
    q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
    archive=pin(q.ROOT/'reports/work/FOCUS-341/triplets-200.tar.gz')
    config=folder/(id+'-config.json');q.save(config,dict(archive=archive))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS342',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Shared crop pixels connect apparently separate triplet cases and reduce independent support.',
        decisionRule='Report connected groups. Do not admit received crops or infer independent trials.',
        adapter=dict(type='python-callable',steps=['triplets342.run'],outputAttributes=['triplets342.OUT']),
        inputs=[pin(Path(__file__)),pin(q.ROOT/'scripts/focus_surface_intake.py'),archive],
        stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
