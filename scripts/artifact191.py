"""Read-only tar audit for ART191; never extracts, follows links or admits data."""
import collections
import hashlib
import json
from pathlib import PurePosixPath
import tarfile
import time
import human_annotation_review as h
from focus_surface_intake import safe_members

OUT = h.ROOT/'reports/work/ART-INTAKE-191/artifacts'
EXPECTED = '4dd9c8459958aedf36526c0699703585a4c874c1e1343abc40cae84cb40fe9ce'
KEEP = {'handoff/manifest.json', 'handoff/evidence/acceptance.json',
        'handoff/compatibility/vectors.json', 'handoff/source-review/handoff.json'}


def headers(members):
    rows=[]; seen=set(); total=0
    for m in members:
        h.require(len(rows)<1000, 'header_count')
        path=PurePosixPath(m.name)
        h.require(not path.is_absolute() and path.parts and '..' not in path.parts
                  and '\\' not in m.name and '\0' not in m.name, 'unsafe_header_path')
        key=str(path).casefold();h.require(key not in seen, 'duplicate_header_path');seen.add(key)
        h.require(0<=m.size<=64*1024**2, 'audit_member_size')
        total+=m.size;h.require(total<=2*1024**3, 'audit_expanded_size')
        kind='file' if m.isfile() else 'directory' if m.isdir() else 'hardlink' if m.islnk() else 'other'
        try: safe_members([m]); error=None
        except ValueError as exc: error=str(exc)
        rows.append(dict(path=m.name, kind=kind, bytes=m.size, extractionError=error))
    return rows


def selection(doc, manifest):
    h.require(doc.get('version')==1 and isinstance(doc.get('cases'),list), 'selection_version')
    seen=set();counts=collections.Counter()
    for row in doc['cases']:
        key=row['metadata'];h.require(key not in seen, 'duplicate_selection');seen.add(key)
        h.require(key in manifest and manifest[key]['sha256']==row['metadata_sha256'], 'selection_hash')
        h.require(row['training_admission']=='pending', 'unexpected_admission')
        counts[row['disposition']]+=1
    h.require(len(seen)==28 and counts['pilot_review_accepted']==15 and
              counts['retained_geometry_calibration']==5 and counts['superseded_render_review']==5
              and counts['superseded_baseline_geometry']==3, 'selection_counts')
    return dict(counts)


def run():
    dest=OUT/'audit.json';h.require(not dest.exists(),'output_collision')
    source=OUT/'feedback.tar.gz';h.require(h.sha(source)==EXPECTED,'archive_hash')
    started=time.monotonic()
    with tarfile.open(source) as archive: rows=headers(archive)
    hashes={}; retained={}
    with tarfile.open(source, 'r|gz') as archive:
        for member in archive:
            if not member.isfile():continue  # In particular, never dereference a tar link.
            digest=hashlib.sha256(); raw=bytearray(); remaining=member.size
            stream=archive.extractfile(member)
            while remaining:
                data=stream.read(min(1024**2,remaining));h.require(data,'truncated_member')
                remaining-=len(data);digest.update(data)
                if member.name in KEEP:
                    h.require(len(raw)+len(data)<=2*1024**2,'metadata_budget');raw.extend(data)
            h.require(not stream.read(1),'member_grew')
            hashes[member.name]=dict(bytes=member.size,sha256=digest.hexdigest())
            if member.name in KEEP:
                def unique(pairs):
                    result={}
                    for k,v in pairs:h.require(k not in result,'duplicate_json_key');result[k]=v
                    return result
                retained[member.name]=json.loads(raw,object_pairs_hook=unique)
    h.require(set(retained)==KEEP,'missing_regular_metadata')
    manifest=retained['handoff/manifest.json'];h.require(manifest['version']==1,'manifest_version')
    files={}
    for row in manifest['files']:
        h.require(row['path'] not in files,'duplicate_manifest');files[row['path']]=row
    expected={r['path'].removeprefix('handoff/') for r in rows if r['kind']!='directory'}-{'manifest.json'}
    h.require(set(files)==expected,'manifest_membership')
    verified=[];unverified=[]
    for name,row in files.items():
        actual=hashes.get('handoff/'+name)
        if actual is None:unverified.append(name);continue
        h.require(all(actual[k]==row[k] for k in ('bytes','sha256')),'member_hash')
        verified.append(name)
    accepted=retained['handoff/evidence/acceptance.json']
    counts=selection(accepted,files)
    h.require(h.sha(source)==EXPECTED,'archive_changed')
    h.write(dest,dict(archive=h.ref(source),members=rows,regularVerified=verified,
        unresolvedLinks=unverified,selection=counts,selectionEvidence='manifest-linked producer decisions, not consumer admission',
        metadata=retained,seconds=time.monotonic()-started,extractionPerformed=False,
        extractionEligible=all(r['extractionError'] is None for r in rows),trainingEligible=False),sealed=True)
    print(dict(headers=len(rows),regularVerified=len(verified),unresolvedLinks=len(unverified),selection=counts),flush=True)


if __name__=='__main__':run()
