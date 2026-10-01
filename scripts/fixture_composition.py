"""Closed TTR composition-v1/v2 consumer; design frames are never annotation truth."""
import base64
import copy
import hashlib
import math
import re
import json
from harvest_artwork import swift_json


def owned_artwork(value, require):
    """Exact delivered OwnedArtwork v1 specification; no file/URL dereferencing."""
    keys={'version','id','family','structural_family','origin','width','height','background','primitives'}
    integer=lambda v,lo,hi:type(v) is int and lo<=v<=hi
    require(isinstance(value,dict) and set(value)==keys,'owned_artwork_fields')
    require(type(value['version']) is int and value['version']==1 and
            type(value['width']) is int and value['width']==256 and
            type(value['height']) is int and value['height']==160 and
            value['origin']=='original_repository_geometry','owned_artwork_version_origin_size')
    require(all(isinstance(value[k],str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,96}',value[k])
                for k in ('id','family','structural_family')),'owned_artwork_identity')
    require(integer(value['background'],0,0xffffff) and isinstance(value['primitives'],list)
            and len(value['primitives'])<=32,'owned_artwork_budget_color')
    for p in value['primitives']:
        require(isinstance(p,dict) and set(p)=={'shape','rect','color'},'owned_primitive_fields')
        require(p['shape'] in ('rect','ellipse','diamond','triangle') and
                integer(p['color'],0,0xffffff),'owned_primitive_shape_color')
        r=p['rect']
        require(isinstance(r,list) and len(r)==4 and all(type(n) is int for n in r) and
                0<=r[0]<256 and 0<=r[1]<160 and r[2]>0 and r[3]>0 and
                r[0]+r[2]<=256 and r[1]+r[3]<=160,'owned_primitive_bounds')
    return 'owned-artwork@1:'+hashlib.sha256(swift_json(value)).hexdigest()


def resolve(value, recipe, require):
    from harvest_sidecar_v2 import focus_digest_source
    def fields(v, required, optional=()):
        require(isinstance(v, dict) and set(required)<=set(v)<=set(required)|set(optional), 'composition_fields')
    def integer(v, lo, hi): return type(v) is int and lo<=v<=hi
    def ident(v): return isinstance(v,str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,96}',v)
    def num(v): return type(v) in (float,int) and math.isfinite(v)
    fields(value, ('version','styles','definitions','contents','regions','background'))
    require(type(value['version']) is int and value['version'] in (1,2),'composition_version')
    canonical=copy.deepcopy(value)
    for key,limit in [('styles',16),('definitions',32),('contents',64)]:
        require(isinstance(value[key],dict) and 1<=len(value[key])<=limit and all(ident(k) for k in value[key]),'composition_budget')
    b=value['background'];fields(b,('colors','locations','direction','interpolation'))
    require(isinstance(b['colors'],list) and 2<=len(b['colors'])<=4 and all(integer(c,0,0xffffff) for c in b['colors']) and
            isinstance(b['locations'],list) and len(b['locations'])==len(b['colors']) and all(num(x) for x in b['locations']) and
            b['locations'][0]==0 and b['locations'][-1]==1 and all(a<b for a,b in zip(b['locations'],b['locations'][1:])) and
            b['direction'] in ('horizontal','vertical','diagonal') and b['interpolation']=='linear','composition_background')
    for k,s in value['styles'].items():
        fields(s,('foreground','background','fontSize','cornerRadius','opacity','blur','focus'))
        require(all(integer(s[c],0,0xffffff) for c in ('foreground','background')) and integer(s['fontSize'],14,80) and
                integer(s['cornerRadius'],0,32) and num(s['opacity']) and .1<=s['opacity']<=1 and type(s['blur']) is bool,'composition_style')
        canonical['styles'][k]['focus']=json.loads(base64.b64decode(focus_digest_source(s['focus']).split('@',1)[1]))
    kinds=('poster','thumbnail','button','row','tab','text','artwork')
    for d in value['definitions'].values():
        fields(d,('kind','style','width','height'))
        require(d['kind'] in kinds and isinstance(d['style'],str) and d['style'] in value['styles'] and
                integer(d['width'],40,1600) and integer(d['height'],24,900),'composition_definition')
    for k,c in value['contents'].items():
        fields(c,('title','seed','preset'),('subtitle','design')+ (('owned_artwork',) if value['version']==2 else ()))
        require(isinstance(c['title'],str) and 0<len(c['title'])<=160 and
                (c.get('subtitle') is None or isinstance(c['subtitle'],str) and len(c['subtitle'])<=240) and
                integer(c['seed'],0,2**64-1) and c['preset'] in ('artwork','bright_unfocused','gray_placeholder','blank_placeholder','high_contrast','photos_like') and
                c.get('design') in (None,'city','orbit','collage','checkerboard'),'composition_content')
        canonical['contents'][k]={a:b for a,b in canonical['contents'][k].items() if b is not None}
        if c.get('owned_artwork') is not None:
            require(c.get('design') is None,'owned_artwork_design_conflict')
            owned_artwork(c['owned_artwork'],require)
    regions=value['regions'];require(isinstance(regions,list) and 1<=len(regions)<=16,'composition_regions')
    ids={'composition.background'};occupied=[];result=[]
    for ri,r in enumerate(regions):
        fields(r,('id','axis','frame','gap','items'))
        require(ident(r['id']) and r['id'] not in ids and r['axis'] in ('row','column','shelf') and integer(r['gap'],0,120),'composition_region')
        ids.add(r['id']);f=r['frame']
        require(isinstance(f,list) and len(f)==4 and all(type(x) is int for x in f) and
                f[0]>=0 and f[1]>=0 and f[2]>0 and f[3]>0 and f[0]+f[2]<=1920 and f[1]+f[3]<=1080,'composition_frame')
        require(not any(f[0]<o[0]+o[2] and o[0]<f[0]+f[2] and f[1]<o[1]+o[3] and o[1]<f[1]+f[3] for o in occupied),'composition_overlap')
        occupied.append(f);require(isinstance(r['items'],list) and 1<=len(r['items'])<=64,'composition_items');cursor=0
        for ii,i in enumerate(r['items']):
            fields(i,('id','component','content','selected'),('style',))
            require(ident(i['id']) and i['id'] not in ids and type(i['selected']) is bool,'composition_instance')
            ids.add(i['id'])
            require(isinstance(i['component'],str) and i['component'] in value['definitions'] and isinstance(i['content'],str) and i['content'] in value['contents'],'composition_reference')
            d=value['definitions'][i['component']];c=value['contents'][i['content']];sk=d['style'] if i.get('style') is None else i['style']
            require(isinstance(sk,str) and sk in value['styles'],'composition_style_reference');s=value['styles'][sk];kind=d['kind']
            x=f[0]+(0 if r['axis']=='column' else cursor);y=f[1]+(cursor if r['axis']=='column' else 0)
            require(x+d['width']<=f[0]+f[2] and y+d['height']<=f[1]+f[3],'composition_overflow')
            require(not i['selected'] or kind=='tab','composition_selected')
            require(c.get('design') is None or kind in ('poster','thumbnail','artwork') and c['preset']=='artwork','composition_design')
            require(c.get('owned_artwork') is None or kind in ('poster','thumbnail','artwork') and c['preset']=='artwork','composition_owned_artwork_kind')
            focusable=kind not in ('text','artwork')
            require(not focusable or not s['blur'] and s['opacity']==1,'composition_control_effect')
            require(kind not in ('button','row','tab') or s['focus']['kind']=='native_button','composition_button_focus')
            require(kind not in ('poster','thumbnail') or s['focus']['kind']!='native_button' and s['cornerRadius']==(s['focus'].get('custom') or {}).get('cornerRadius',12),'composition_image_focus')
            result.append(dict(id=i['id'],parent=r['id'],kind=kind,focusable=focusable,selected=i['selected'],content=c,style=s))
            canonical['regions'][ri]['items'][ii]={a:b for a,b in i.items() if b is not None}
            cursor+=(d['height'] if r['axis']=='column' else d['width'])+r['gap']
    require(len(result)<=64 and any(i['focusable'] for i in result),'composition_count')
    require(recipe['element_count']==len(result) and recipe['theme']=='dark' and recipe['density']=='regular','composition_recipe')
    pack=recipe.get('randomization')
    if pack is not None:
        require(pack==dict(pack_id='identity',version='1',palette_name='system',typography_weight='regular',badge_count=0,
                          gradient_overlay=False,simulate_voiceover_running=False,simulate_reduce_motion=False,simulate_bold_text=False),'composition_randomization')
    # JSONEncoder emits integral Double values as integers. Preserve signed zero.
    def normalize(v):
        if isinstance(v,dict):return {k:normalize(x) for k,x in v.items()}
        if isinstance(v,list):return [normalize(x) for x in v]
        if type(v) is float and v.is_integer() and not (v==0 and math.copysign(1,v)<0):return int(v)
        return v
    encoded=swift_json(normalize(canonical)).replace(b':-0.0',b':-0').replace(b',-0.0',b',-0')
    return result,f'composition@{value["version"]}:'+hashlib.sha256(encoded).hexdigest()


def hierarchy(scene, require):
    recipe=scene['recipe'];resolved,_=resolve(recipe['appearance']['composition'],recipe,require)
    elements={e['element_id']:e for e in scene['elements']}
    require(set(elements)=={i['id'] for i in resolved},'composition_native_membership')
    taxonomy={'poster':('collectionItem',),'thumbnail':('collectionItem',),'button':('primaryButton','secondaryButton'),
              'row':('listRow',),'tab':('menuButton',),'text':('label',),'artwork':('imageView',)}
    for i in resolved:
        e=elements[i['id']]
        require(e.get('parent_element_id')==i['parent'] and e['taxonomy_class'] in taxonomy[i['kind']],'composition_native_role')
        require(('isSelected' in e.get('accessibility_traits',[]))==i['selected'],'composition_native_selected')
    require(set(scene['focus_observation']['plannedFocusIDs'])=={i['id'] for i in resolved if i['focusable']},'composition_native_plan')
