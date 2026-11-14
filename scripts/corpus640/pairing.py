"""Pair verified, observed focus states without changing source data roles."""
import hashlib
from collections import Counter
from itertools import combinations
from pathlib import Path
import numpy as np
from PIL import Image

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check_frame(frame):
    """Validate normalized adapter rows. Missing focus is not no-focus."""
    if frame.get('focusState') not in ('focused', 'no_focus', 'unknown'):
        raise ValueError('Invalid or missing focusState')
    state=frame['focusState']; focus=frame.get('focusID')
    if state=='focused':
        if not isinstance(focus,str) or not focus:raise ValueError('Focus ID conflicts with state')
    elif focus is not None:
        raise ValueError('Focus ID conflicts with state')
    controls=frame.get('controls')
    if not isinstance(controls,list) or len({c['id'] for c in controls})!=len(controls):
        raise ValueError('Invalid control identities')
    if state=='focused' and focus not in {c['id'] for c in controls}:
        raise ValueError('Focused control is missing')
    if sha(frame['image']['path'])!=frame['image']['sha256']:
        raise ValueError('Image hash mismatch')
    with Image.open(frame['image']['path']) as image:
        pixels=np.asarray(image.convert('RGB'))
    height,width=pixels.shape[:2]
    for c in controls:
        b=c['bounds']
        if len(b)!=4 or any(not isinstance(v,int) or isinstance(v,bool) for v in b):
            raise ValueError('Non-integral control geometry')
        x,y,w,h=b
        if x<0 or y<0 or w<=0 or h<=0 or x+w>width or y+h>height:
            raise ValueError('Control geometry outside image')
    return pixels

def assess(a,b,pa,pb):
    if a['group']!=b['group'] or a['role']!=b['role']:
        return {'eligible':False,'reason':'group_or_role_mismatch'}
    if not a.get('contentVariant') or not b.get('contentVariant'):
        return {'eligible':False,'reason':'missing_content_identity'}
    if a['contentVariant']!=b['contentVariant']:
        return {'eligible':False,'reason':'content_changed'}
    if a['focusState']=='unknown' or b['focusState']=='unknown':
        return {'eligible':False,'reason':'missing_focus_observation'}
    if a['focusState']!='focused' or b['focusState']!='focused':
        return {'eligible':False,'reason':'explicit_no_focus'}
    if a['focusID']==b['focusID']:
        return {'eligible':False,'reason':'same_focused_control'}
    ca={c['id']:c['bounds'] for c in a['controls']};cb={c['id']:c['bounds'] for c in b['controls']}
    if ca!=cb or pa.shape!=pb.shape:
        return {'eligible':False,'reason':'control_or_image_geometry_changed'}
    changed=np.any(pa!=pb,axis=2); mask=np.zeros(changed.shape,dtype=bool)
    changes={}
    for key in (a['focusID'],b['focusID']):
        x,y,w,h=ca[key]; mask[y:y+h,x:x+w]=True
        changes[key]=int(changed[y:y+h,x:x+w].sum())
    outside=int(changed[~mask].sum())
    if outside or any(v==0 for v in changes.values()):
        return {'eligible':False,'reason':'unmatched_pixels','outsideChanged':outside,'changedByControl':changes}
    return {'eligible':True,'reason':'matched','outsideChanged':outside,'changedByControl':changes}

def build(frames):
    ids=[f['id'] for f in frames]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate frame ID')
    counts=Counter(f['focusState'] for f in frames); pairs=[]; seen={}; duplicates=[]
    grouped={}; hash_roles={}; hash_focus={}
    for f in frames:
        grouped.setdefault((f['group'],f['role']),[]).append(f)
        hash_roles.setdefault(f['image']['sha256'],set()).add(f['role'])
        hash_focus.setdefault(f['image']['sha256'],set()).add((f['focusState'],f.get('focusID')))
    conflicts=sorted(h for h,roles in hash_roles.items() if len(roles)>1)
    focus_conflicts=sorted(h for h,labels in hash_focus.items() if len(labels)>1)
    for key,group in sorted(grouped.items()):
        pixels={f['id']:check_frame(f) for f in group}
        for a,b in combinations(sorted(group,key=lambda x:x['id']),2):
            identity=tuple(sorted((a['image']['sha256'],b['image']['sha256'])))
            entry={'ids':[a['id'],b['id']],'hashes':list(identity),'group':key[0],'role':key[1]}
            if any(h in conflicts for h in identity):
                pairs.append({**entry,'eligible':False,'reason':'cross_role_duplicate'});continue
            if any(h in focus_conflicts for h in identity):
                pairs.append({**entry,'eligible':False,'reason':'conflicting_focus_for_identical_pixels'});continue
            if identity in seen:
                duplicates.append({**entry,'duplicateOf':seen[identity]});continue
            seen[identity]=entry['ids']
            pairs.append({**entry,**assess(a,b,pixels[a['id']],pixels[b['id']])})
    return {'states':dict(counts),'crossRoleImageHashes':conflicts,'conflictingFocusImageHashes':focus_conflicts,'duplicatePairs':duplicates,'pairs':pairs}
