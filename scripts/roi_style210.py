"""Prepare native style coverage with the existing ROI cropper; no training."""
import hashlib
import shutil
from pathlib import Path
from PIL import Image
import roi196 as previous
from export_coco import vision_to_yolo, bounds_vision, element_type

h,p,e,r=previous.h,previous.p,previous.e,previous.r
OUT=h.ROOT/'reports/work/IOS-STYLE-210/artifacts/roi04'


def precise_labels(annotation,names,exported):
    lines=[]
    for element in annotation['elements']:
        values=vision_to_yolo(bounds_vision(element))
        h.require(values is not None and element_type(element) in names,'annotation_mapping')
        lines.append(str(names.index(element_type(element)))+' '+' '.join(f'{v:.15f}' for v in values))
    expected=sorted(exported.splitlines());actual=sorted(lines)
    h.require(len(actual)==len(expected),'label_count')
    for a,b in zip(actual,expected):
        av,bv=a.split(),b.split()
        h.require(av[0]==bv[0] and all(abs(float(x)-float(y))<=0.000000501 for x,y in zip(av[1:],bv[1:])),'export_correspondence')
    return '\n'.join(lines)+'\n'


def paired_slots(old_ids,new_ids):
    h.require(old_ids and new_ids and len(set(old_ids))==len(old_ids) and
              len(set(new_ids))==len(new_ids) and not set(old_ids)&set(new_ids),'slot_membership')
    order=sorted(old_ids,key=lambda k:(hashlib.sha256(k.encode()).hexdigest(),k))
    repeats=[order[i%len(order)] for i in range(len(new_ids))]
    return dict(control=list(old_ids)+repeats,treatment=list(old_ids)+list(new_ids))


def prepare():
    old=p.sealed(previous.OUT/'proposal.json')
    source=h.ROOT/'reports/work/IOS-STYLE-210/artifacts/export01/membership.json'
    doc=p.sealed(source);admission=p.sealed(h.checked(h.ROOT,doc['admission']))
    h.require(doc['role']=='train' and admission['eligible'] and len(doc['rows'])==96,'admission')
    h.require(all(v['split']=='train' for v in doc['rows']),'role')
    old_req=e.load_request(h.checked(h.ROOT,old['membership']),41)
    h.require(len(old_req.images)==1173 and not OUT.exists(),'count_or_collision')
    h.require(shutil.disk_usage(h.ROOT).free>4*1024**3,'storage_reserve')
    # Every non-fit retained plan is independently revalidated before crop writes.
    forbidden=set()
    for kind,plan in old['evaluation'].items():
        if kind=='fit':continue
        req=e.load_request(h.checked(h.ROOT,plan['manifest']),41)
        for im in req.images:
            with Image.open(im.image_path) as image:
                forbidden.add(hashlib.sha256(image.convert('RGB').tobytes()).hexdigest())
    seen={};old_entries=[]
    for im in old_req.images:
        with Image.open(im.image_path) as image:digest=hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
        canonical=tuple(sorted(im.label_path.read_text().splitlines()))
        h.require(digest not in forbidden and r.duplicate(seen,digest,canonical) is None,'old_overlap')
        seen[digest]=dict(id=im.image_id,labels=canonical)
        old_entries.append(dict(id=im.image_id,image=h.ref(im.image_path),label=h.ref(im.label_path)))
    entries=[]
    for row in doc['rows']:
        image=h.checked(h.ROOT,row['image']);label=h.checked(h.ROOT,row['label'])
        entries.append(dict(imageID=row['id'],imagePath=str(image),labelPath=str(label),
            imageSHA256=row['image']['sha256'],labelSHA256=row['label']['sha256']))
    OUT.mkdir(parents=True)
    staging=OUT/'sources';staging.mkdir()
    for entry,row in zip(entries,doc['rows']):
        link=staging/(entry['imageID']+'.png');link.symlink_to(entry['imagePath'])
        label=staging/(entry['imageID']+'.txt')
        text=precise_labels(h.read(h.checked(h.ROOT,row['annotation'])),e.load_names(),Path(entry['labelPath']).read_text())
        with label.open('x') as stream:stream.write(text)
        entry.update(imagePath=str(link.relative_to(OUT)),labelPath=str(label.relative_to(OUT)),labelSHA256=h.sha(label))
    h.write(OUT/'source.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='style210-training',images=entries))
    req=e.load_request(OUT/'source.json',41);cid=e.load_names().index('pageControl')
    meta={x['id']:x for x in doc['rows']};crops=[];aliases=[];lineage=[];rejected=[]
    for im in req.images:
        truths=r.c.g.r.f.d.prior.truth(im,cid);h.require(len(truths)==1,'one_page_required');windows=set()
        for variant,shift in enumerate(r.JITTER):
            roi=r.window(im.width,im.height,truths[0],shift)
            if tuple(roi) in windows:continue
            windows.add(tuple(roi));key=im.image_id+f'-roi{variant}'
            ancestry=dict(id=key,parent=im.image_id,group=meta[im.image_id]['group'],window=roi)
            _,dispositions=r.labels(im,roi)
            if any(x['disposition']!='retained' for x in dispositions if x['classID']==cid):
                rejected.append(dict(ancestry,reason='page_clipped',dispositions=dispositions));continue
            digest,canonical=r.signature(im,roi);h.require(digest not in forbidden,'evaluation_overlap')
            duplicate=r.duplicate(seen,digest,canonical)
            if duplicate is not None:
                aliases.append(dict(ancestry,canonical=duplicate));continue
            saved=r.OUT
            try:
                r.OUT=OUT;entry,detail=r.save_crop(im,roi,OUT/'crops',key)
            finally:r.OUT=saved
            h.require(all(x['disposition']=='retained' for x in detail['dispositions'] if x['classID']==cid),'page_clipped')
            crops.append(entry);lineage.append(dict(ancestry,**detail));seen[digest]=dict(id=key,labels=canonical)
    h.require(crops and {x['parent'] for x in lineage+aliases}==set(meta),'missing_parent_coverage')
    h.write(OUT/'crops.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='style210-roi-training',images=crops))
    e.load_request(OUT/'crops.json',41)
    slots=paired_slots([x['id'] for x in old_entries],[x['imageID'] for x in crops])
    h.write(OUT/'comparison.json',dict(source=h.ref(source),admission=doc['admission'],
        oldProposal=h.ref(previous.OUT/'proposal.json'),oldMembership=old['membership'],
        cropMembership=h.ref(OUT/'crops.json'),oldEntries=old_entries,lineage=lineage,aliases=aliases,rejected=rejected,
        slots=slots,evaluation=old['evaluation'],initializer=old['initializer'],
        sources=[h.ref(__file__),h.ref(r.__file__)],role='train',evaluationChanged=False,
        uniqueOld=len(old_entries),uniqueNew=len(crops),slotsPerArm=len(slots['control']),
        trainingLaunched=False,modelGatePassed=False),sealed=True)
    print(f'{len(crops)} unique new crops; {len(aliases)} aliases; {len(rejected)} clipped windows rejected; {len(slots["control"])} slots per arm')


if __name__=='__main__':prepare()
