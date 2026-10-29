"""Preserve native semantics and distinguish control lifetimes without inferred labels."""
import copy
import math
import research_queue as q

OPTIONAL_FIELDS = ('accessibilityTraits', 'isAccessibilityElement', 'publicAccessibility',
                   'publicAccessibilityActionIDs', 'layoutContext', 'observedState', 'publicLabel')


def identity(value):
    q.require(isinstance(value, dict) and isinstance(value.get('id'), str) and value['id'], 'sdk529_identity')
    lifetime=value.get('lifetime'); revision=value.get('revision')
    q.require(lifetime is None or isinstance(lifetime,str) and 0<len(lifetime)<=256,'sdk529_lifetime')
    q.require(revision is None or type(revision) is int and revision>=0,'sdk529_revision')
    return dict(id=value['id'], lifetime=lifetime, revision=revision)


def semantics(element):
    ident=identity(element['identity']); result={k:copy.deepcopy(element.get(k)) for k in OPTIONAL_FIELDS}
    traits=result['accessibilityTraits']
    q.require(traits is None or type(traits) is int and 0<=traits<2**64,'sdk529_traits')
    public=result['publicAccessibility']
    q.require(public is None or isinstance(public,dict) and set(public)<= {'identifier','label','hint','value'} and
              all(v is None or isinstance(v,str) and len(v.encode())<=2048 for v in public.values()),'sdk529_public_text')
    actions=result['publicAccessibilityActionIDs']
    q.require(actions is None or isinstance(actions,list) and len(actions)<=128 and
              all(isinstance(v,str) and 0<len(v.encode())<=256 for v in actions) and len(actions)==len(set(actions)), 'sdk529_actions')
    for key in ('className','parentID'):
        v=element.get(key);q.require(v is None or isinstance(v,str) and len(v.encode())<=512,'sdk529_'+key)
    return dict(identity=ident,identityComplete=ident['lifetime'] is not None and ident['revision'] is not None,
                **result,semanticProvenance='sdk_registered_fields',
                visibilityProvenance=(element.get('observedState') or {}).get('source','unknown'),
                selectionProvenance='registration_not_verified_native_selection')


def focus_identity(frame):
    if frame.get('focusState')=='unknown' or 'focusID' not in frame:
        return None,False
    focus=frame['focusID']
    if focus is None:return None,True
    rows=[c for c in frame['controls'] if c['identity']['id']==focus]
    if len(rows)!=1:return None,False
    value=identity(rows[0]['identity'])
    return value,value['lifetime'] is not None and value['revision'] is not None


def transition(before,after):
    """Revision changes preserve lifetime. Process changes never establish continuity."""
    for key in ('appID','processID','runID'):
        if not before.get(key) or before[key]!=after.get(key):
            return dict(observed='unknown',relation='producer_changed',eligible=False)
    a,ak=focus_identity(before);b,bk=focus_identity(after)
    if not ak or not bk:return dict(observed='unknown',relation='identity_unavailable',eligible=False)
    if a is None:label,relation=('no_focus','none') if b is None else ('arrival','appeared')
    elif b is None:label,relation='departure','disappeared'
    elif a['id']!=b['id']:label,relation='move','different_control'
    elif a['lifetime']!=b['lifetime']:label,relation='move','replaced_control'
    elif b['revision']<a['revision']:return dict(observed='unknown',relation='revision_regressed',eligible=False)
    else:label,relation='unchanged','revised_control' if a['revision']!=b['revision'] else 'same_control'
    return dict(observed=label,relation=relation,eligible=True,before=a,after=b)


def transformed_bounds(bounds,matrix,viewport):
    """Use an explicit measured affine transform. Return clipped and full pixel bounds."""
    q.require(len(bounds)==4 and len(matrix)==6 and len(viewport)==2,'sdk529_transform_shape')
    q.require(all(type(v) in (int,float) and math.isfinite(v) for v in [*bounds,*matrix,*viewport]),'sdk529_transform_finite')
    x,y,w,h=bounds;a,b,c,d,tx,ty=matrix;vw,vh=viewport
    q.require(w>0 and h>0 and vw>0 and vh>0 and abs(a*d-b*c)>1e-12,'sdk529_transform_geometry')
    points=[(a*px+c*py+tx,b*px+d*py+ty) for px,py in ((x,y),(x+w,y),(x,y+h),(x+w,y+h))]
    left=min(p[0] for p in points);top=min(p[1] for p in points)
    right=max(p[0] for p in points);bottom=max(p[1] for p in points)
    full=[left,top,right-left,bottom-top]; clipped=[max(0,left),max(0,top),max(0,min(vw,right)-max(0,left)),max(0,min(vh,bottom)-max(0,top))]
    return dict(full=full,visible=clipped if clipped[2]>0 and clipped[3]>0 else None,clipped=full!=clipped)


def classify(control,rules):
    """Apply explicit reviewed conjunctive mappings. Never classify from a class name alone."""
    matches=[]
    for rule in rules:
        q.require(set(rule)=={'id','class','match','reviewer','evidence'} and rule['reviewer'] and rule['evidence'],'sdk529_mapping_review')
        m=rule['match'];q.require(isinstance(m,dict) and 2<=len(m)<=4 and set(m)<={'nativeClass','traitsAll','publicIdentifier','registeredID'},'sdk529_mapping_match')
        actual=dict(nativeClass=control.get('className'),traitsAll=control.get('accessibilityTraits'),
                    publicIdentifier=(control.get('publicAccessibility') or {}).get('identifier'),registeredID=control['identity']['id'])
        ok=True
        for key,value in m.items():
            if key=='traitsAll':
                q.require(type(value) is int and value>0,'sdk529_mapping_traits')
                ok &= type(actual[key]) is int and actual[key]&value==value
            else:
                q.require(isinstance(value,str) and value,'sdk529_mapping_value');ok &= actual[key]==value
        if ok:matches.append(rule)
    classes={r['class'] for r in matches}
    return dict(taxonomyClass=next(iter(classes)) if len(classes)==1 else None,
                state='mapped' if len(classes)==1 else 'ambiguous' if classes else 'unmapped',
                mappingIDs=[r['id'] for r in matches])
