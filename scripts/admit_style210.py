"""Reviewed style210 training admission; preserve all aliases and original pixels."""
import hashlib
from pathlib import Path
from PIL import Image
import roi196 as r
from audit_style210 import audit
from placement172 import annotation_identity

h,p=r.h,r.p
ROOT=h.ROOT/'reports/work/IOS-STYLE-210/artifacts'


def choose(rows, forbidden):
    seen={};accepted=[];aliases=[]
    for row in sorted(rows,key=lambda x:x['id']):
        h.require(row['pixelSHA256'] not in forbidden,'prior_pixel_overlap')
        old=seen.get(row['pixelSHA256'])
        if old:
            h.require(old['annotationIdentity']==row['annotationIdentity'] and old['group']==row['group'],'duplicate_conflict')
            aliases.append(dict(id=row['id'],retainedID=old['id'],pixelSHA256=row['pixelSHA256']))
        else:
            seen[row['pixelSHA256']]=row;accepted.append(row)
    return accepted,aliases


def main():
    out=ROOT/'admission01.json';h.require(not out.exists(),'output_collision')
    catalog_path=ROOT/'catalog.json';capture=ROOT/'capture01'
    checked=audit(capture,catalog_path);catalog=h.read(catalog_path)
    basepath=h.ROOT/'reports/work/IOS-PLACEMENT-173/artifacts/membership.json'
    base=p.sealed(basepath);h.require(len(base['rows'])==20004,'base_count')
    prior=h.ROOT/'reports/work/IOS-NATIVE-PAGE-150/artifacts'
    development=h.read(prior/'compose155-audit/report.json')
    freeze=h.read(prior/'page156-freeze.json')
    h.require(freeze['auditSHA256']==h.sha(prior/'compose155-audit/report.json'),'development_changed')
    forbidden={v['pixelSHA256'] for v in base['rows']}
    native_pixels={v['decodedSHA256'] for v in development['rows']}
    parents={Path(v['id']).stem:v['family'] for v in base['rows'] if 'family' in v}
    families=set()
    for v in base['rows']:
        family=v.get('family') or parents.get(v.get('group'))
        h.require(isinstance(family,str) and family,'unresolved_prior_ancestry')
        families.add(family)
    families.update(('reader-footer','gallery-inspector','PageComposition155'))
    rows=[]
    for recipe in catalog['members']:
        image=capture/(recipe['id']+'.png');annotation=capture/(recipe['id']+'.json');a=h.read(annotation)
        h.require(recipe['family'] not in families and a['generatorProfile']['templateFamily']==recipe['family'] and
                  a['generatorProfile']['seed']==recipe['seed'] and a['imageSHA256']==h.sha(image),'source_identity')
        with Image.open(image) as im:
            rgb=im.convert('RGB');raw=rgb.tobytes()
            pixel=hashlib.sha256(str(rgb.size).encode()+raw).hexdigest()
            h.require(hashlib.sha256(raw).hexdigest() not in native_pixels,'development_pixel_overlap')
        rows.append(dict(id=recipe['id'],group=recipe['group'],split='train',family=recipe['family'],
            image=h.ref(image),annotation=h.ref(annotation),pixelSHA256=pixel,annotationIdentity=annotation_identity(a)))
    accepted,aliases=choose(rows,forbidden)
    h.require(len(accepted)==96 and len(aliases)==48 and not checked['crossGroupDuplicates'],'accounting')
    h.write(out,dict(version='native-style210-admission-v1',eligible=True,role='train',rows=accepted,aliases=aliases,
        catalog=h.ref(catalog_path),receipt=h.ref(capture/'receipt.json'),base=h.ref(basepath),
        developmentAudit=h.ref(prior/'compose155-audit/report.json'),source=h.ref(__file__),
        excludedFromFinalGroups=sorted({x['group'] for x in rows}),
        review='Native source,144full-frame visible/hidden geometry checks, representative images018and125; not real-world qualification'),sealed=True)
    print('Admitted96unique training images;48aliases retained;18groups excluded from final evaluation')


if __name__=='__main__':main()
