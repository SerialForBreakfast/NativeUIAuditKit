"""Audit measured sizes and compare original detail with encoded detail."""
import argparse
from collections import Counter
from functools import lru_cache
from pathlib import Path
import time
import types
import numpy as np
from PIL import Image
import context309 as previous
from diagnose_signal95 import encoded
from detail307 import crop_pair

c=previous.c
base=c.base
torch=base.torch
OUT=base.ROOT/'reports/work/FOCUS-310'
VERSION='source310-v1'


def boxes(values):
    local=c.model.change_inputs(None,values)[:,9:].mean(1,keepdim=True)
    peak=torch.nn.functional.avg_pool2d(local,5,stride=1,padding=2).flatten(1).argmax(1)
    x=(peak%192-16).clamp(0,160); y=(peak//192-16).clamp(0,96)
    return list(zip(x.tolist(),y.tolist()))


def enlarged(values):
    """Keep square windows square inside a black letterbox."""
    base.require(values.ndim==4 and values.shape[1:]==(6,128,192),'detail_shape')
    output=torch.zeros_like(values)
    for i,(x,y) in enumerate(boxes(values)):
        if torch.equal(values[i,:3],values[i,3:]):
            output[i]=values[i]
        else:
            output[i,:, :,32:160]=torch.nn.functional.interpolate(
                values[i:i+1,:,y:y+32,x:x+32],size=(128,128),mode='bilinear',align_corners=False)[0]
    return output


class SourceChange(previous.ContextChange):
    def forward(self,images):
        base.require(images.shape[1] in (6,12),'paired_channels')
        whole=images[:,:6]
        detail=images[:,6:] if images.shape[1]==12 else enlarged(whole)
        context=self.whole[:10](c.model.change_inputs(None,whole))
        features=torch.cat((context,self.detail(c.model.change_inputs(None,detail))),1)
        return self.whole[10](context)+self.correction(features)


def extend(net):
    net.change=SourceChange(net.change,True)
    net.change_inputs=types.MethodType(previous.identity_inputs,net)
    return net


def load_candidate(path):
    saved=torch.load(path,map_location='cpu',weights_only=True)
    base.require(saved.get('representation')==VERSION,'checkpoint_version')
    net=extend(c.model.extend(base.worker.make_model(torch,paired_context=True)))
    net.load_state_dict(saved['state']); return net.eval()


@lru_cache(maxsize=64)
def image(path,digest):
    with Image.open(base.checked(dict(path=path,sha256=digest))) as opened:
        return opened.convert('RGB')


@lru_cache(maxsize=512)
def metadata(path,digest):
    return base.read(base.checked(dict(path=path,sha256=digest)))


def reverse_row(row):
    if row is None:return None
    result=dict(row)
    for key in ('images','metadata','observedIDs','focusIDs'):
        if key in result:result[key]=list(reversed(result[key]))
    return result


def schedule_rows(membership,registration,labels):
    rows=[None]*len(membership['replayLabels'])
    rows += [membership['rows'][i] for i in membership['selected']]
    pin=base.read(base.ROOT/'reports/work/TRANSITION-266/preflight.json')
    replacements=base.read(base.checked(pin['replacements']))
    for row in replacements['rows']: rows[row['trainingIndex']]=row
    rows += [reverse_row(r) for r in rows[668:1164]]
    added=[row if labels[1660+i] else rows[registration['controlIndices'][i]]
           for i,row in enumerate(registration['addedRows'])]
    rows += added+[reverse_row(r) for r in added]
    base.require(len(rows)==1820,'row_schedule')
    return rows


def measured(row,images):
    result=[]
    ids=row.get('observedIDs',row.get('focusIDs'))
    for n,(ref,meta_ref) in enumerate(zip(row['images'],row['metadata'])):
        doc=metadata(meta_ref['path'],meta_ref['sha256'])
        scenes=[doc[key] for prefix,key in [('unfocused','baseline_scene'),('focused','focused_scene')]
                if doc.get(prefix+'_sha256')==ref['sha256']]
        if not scenes:
            result.append(dict(status='missing_scene'));continue
        focus=scenes[0].get('focused_element_id')
        base.require(all(s.get('focused_element_id')==focus for s in scenes),'conflicting_focus')
        if ids is not None:base.require(ids[n]==focus,'focus_identity')
        elements=[e for e in scenes[0].get('elements',[]) if e.get('element_id')==focus]
        geometry=elements[0].get('rendered_body_geometry',{}) if len(elements)==1 else {}
        box=geometry.get('visible_pixel_bounds')
        if geometry.get('availability')!='measured' or geometry.get('coordinate_space')!='image_top_left_pixels' or not box:
            result.append(dict(status='missing_body',focusID=focus));continue
        base.require(len(box)==4 and np.isfinite(box).all() and min(box[2:])>0,'invalid_body')
        w,h=images[n].size; scale=min(192/w,128/h)
        size=[box[2]*round(w*scale)/w,box[3]*round(h*scale)/h]
        result.append(dict(status='measured',focusID=focus,sourceSize=[w,h],visibleBody=box,
                           encodedSize=size,minimumEncodedSize=min(size)))
    return result


def prepare_views(values,rows,weights=None,audit=False):
    """Select windows from pixels. Geometry serves only the size audit."""
    low=np.empty_like(values); high=np.empty_like(values); records=[]
    for start in range(0,len(values),8):
        chunk=torch.from_numpy(np.array(values[start:start+8]))
        low[start:start+len(chunk)]=enlarged(chunk).numpy()
    high[:]=low
    for i,row in enumerate(rows):
        record=dict(index=i,sourceAvailable=row is not None,
                    weight=None if weights is None else float(weights[i]))
        if row is not None:
            images=[image(r['path'],r['sha256']) for r in row['images']]
            base.require(images[0].size==images[1].size,'frame_size')
            source=encoded(*images,(192,128))[0]
            base.require(np.array_equal(source,values[i]),'source_encoding_parity')
            x,y=boxes(torch.from_numpy(values[i:i+1]))[0]
            box=[x,y,x+32,y+32]
            if not np.array_equal(values[i,:3],values[i,3:]):
                high[i]=crop_pair(images,box,preserve_padding=True)
            record.update(id=row.get('id'),role=row.get('role'),group=row.get('group'),
                          images=row['images'],window=box,changed=row.get('changed'))
            if audit:record['endpoints']=measured(row,images)
        records.append(record)
        if i and i%200==0:print('Prepared source views',i,'/',len(rows),flush=True)
    return low,high,records


def size_summary(records):
    bins=Counter(); weights=Counter(); endpoints=Counter()
    for row in records:
        measured_sizes=[e['minimumEncodedSize'] for e in row.get('endpoints',[]) if e['status']=='measured']
        endpoints.update(e['status'] for e in row.get('endpoints',[]))
        if not row['sourceAvailable']:key='encoded_only'
        elif len(measured_sizes)!=2:key='missing_body_measurement'
        else:
            size=min(measured_sizes)
            key='below4' if size<4 else '4to8' if size<8 else '8to16' if size<16 else '16plus'
        bins[key]+=1;weights[key]+=row['weight'] or 0
    return dict(scheduleEntries=dict(bins),weightTotals=dict(weights),endpoints=dict(endpoints),
                definition='Minimum visible focused-body dimension across both endpoints, in encoded pixels.',
                limitation='Missing measurements are not small controls. Repeated rows are not independent examples.')


def tiny_rows():
    values,original,pin=previous.tiny_inputs(); rows=[]
    for row in original:
        path=base.checked(row['metadata']);doc=base.read(path)
        refs=[dict(path=str((path.parent/doc[p+'_png']).relative_to(base.ROOT)),sha256=doc[p+'_sha256'])
              for p in ('unfocused','focused')]
        if row['condition']=='reverse':refs.reverse()
        if row['condition']=='same-before':refs[1]=refs[0]
        if row['condition']=='same-after':refs[0]=refs[1]
        rows.append(dict(row,images=refs,metadata=[row['metadata']]*2,role='development'))
    return values,rows,pin


def run(out):
    base.require(not out.exists(),'output_collision');torch.set_num_threads(2);started=time.monotonic()
    manifest,membership,full,labels,weights,extra,controls,_,reg=c.prepare()
    added=previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,base.reporting.reverse(added)));del full,extra,added
    parent=base.ROOT/'reports/work/TRANSITION-292/DTM085'
    base.require(base.sha(values.tobytes())==base.read(parent/'registration.json')['trainingSHA256'],'schedule_identity')
    initializer=base.checked(base.read(parent/'result.json')['model'])
    rows=schedule_rows(membership,reg,labels)
    out.mkdir(parents=True)
    config=dict(reg['configuration'],epochs=30)
    base.write(out/'registration.json',dict(version=VERSION,runner=base.ref(Path(__file__)),
        trainer=base.ref(Path(base.trainer.__file__)),evaluator=base.ref(Path(base.__file__)),
        cropper=base.ref(base.ROOT/'scripts/detail307.py'),
        initializer=base.ref(initializer),configuration=config,trainingSHA256=base.sha(values.tobytes()),
        labelsSHA256=base.sha(labels.tobytes()),weightsSHA256=base.sha(weights.tobytes()),
        membership=base.ref(base.PACKAGE/'membership.json'),parent=base.ref(parent/'registration.json'),
        hypothesis='Original detail improves tiny focus changes when full-frame context remains available.',
        matchedControl='Same 32-pixel window and architecture with enlarged encoded pixels.',
        selector='Image residual energy only; no boxes or labels select windows.',
        thresholds=[.15,.85],epochs=30,selection='fixed-last',wallTimeLimit=None,
        outputCapBytes=128*1024**2,rolesChanged=False,productionEligible=False,
        acceptance='Improve tiny changed decisions with no loss of previous correct decisions.',
        fallback='Encoded-only examples use the same enlarged view in both runs.'))
    low,high,audit=prepare_views(values,rows,weights,True)
    base.write(out/'size-audit.json',dict(rows=audit,summary=size_summary(audit)))
    base.write(out/'views.json',dict(encodedSHA256=base.sha(low.tobytes()),sourceSHA256=base.sha(high.tobytes()),
        sourceRows=sum(r is not None for r in rows),cachePersisted=False))
    native=np.load(base.PACKAGE/'native.npy',allow_pickle=False)
    _,native_high,native_audit=prepare_views(native,membership['rows'],audit=True)
    base.write(out/'native-views.json',dict(rows=native_audit,sha256=base.sha(native_high.tobytes())))
    tiny,trows,tpin=tiny_rows();tiny_low,tiny_high,taudit=prepare_views(tiny,trows,audit=True)
    base.write(out/'tiny-views.json',dict(input=tpin,rows=taudit,sha256=base.sha(tiny_high.tobytes())))
    references={'DTM085':c.model.load_candidate(initializer)}
    references['FOCUS309']=previous.load_candidate(previous.OUT/'context-detail/last.pt')
    completed={}
    for name,detail in [('encoded-control',low),('source-detail',high)]:
        folder=out/name;folder.mkdir();torch.manual_seed(42);net=extend(c.model.load_candidate(initializer))
        sanity=np.concatenate((values[:8],detail[:8]),1)
        delta=float(np.max(np.abs(base.worker.score(net,sanity)-base.worker.score(references['DTM085'],values[:8]))))
        base.require(delta<=1e-6,'initial_parity')
        base.write(folder/'registration.json',dict(parent=base.ref(out/'registration.json'),maximumInitialError=delta,
            detailSHA256=base.sha(detail.tobytes()),parameters=sum(p.numel() for p in net.parameters())))
        def progress(row):
            base.write(folder/f"epoch-{row['epoch']:04d}.json",row);print(name,row,flush=True)
        begin=time.monotonic()
        net,history=base.trainer.fit(net,torch.from_numpy(values),torch.from_numpy(labels),config,progress,
                                   torch.from_numpy(weights),detail_inputs=torch.from_numpy(detail))
        torch.save(dict(state=net.state_dict(),representation=VERSION,registration=base.ref(folder/'registration.json')),folder/'last.pt')
        restored=load_candidate(folder/'last.pt')
        base.require(np.array_equal(base.worker.score(net,sanity),base.worker.score(restored,sanity)),'reload_parity')
        base.write(folder/'fit.json',dict(history=history,seconds=time.monotonic()-begin,checkpointParity=True))
        def transform(key,x):
            if name=='source-detail' and key=='native.npy': d=native_high
            elif name=='source-detail' and key=='reverse_native.npy': d=base.reporting.reverse(native_high)
            else:return x
            return np.concatenate((x,d),1)
        evaluation=base.evaluate_full(restored,references,manifest,input_transform=transform)
        base.write(folder/'evaluation.json',evaluation)
        detail_tiny=tiny_high if name=='source-detail' else tiny_low
        scores=base.worker.score(restored,np.concatenate((tiny,detail_tiny),1))
        tiny_report=[]
        for condition in sorted({r['condition'] for r in trows}):
            ids=[i for i,r in enumerate(trows) if r['condition']==condition]
            tiny_report.append(dict(condition=condition,summary=base.trainer.w.summary(scores[ids],
                np.array([trows[i]['changed'] for i in ids])),probabilities=scores[ids].tolist()))
        base.write(folder/'tiny.json',dict(results=tiny_report,independentFinalAudit=False))
        completed[name]=dict(model=base.ref(folder/'last.pt'),regressionPassed=evaluation['regressionPassed'],tiny=tiny_report)
        if name=='encoded-control':references[name]=restored
    size=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    base.require(size<128*1024**2,'output_budget')
    base.write(out/'completion.json',dict(runs=completed,seconds=time.monotonic()-started,outputBytes=size,
        productionEligible=False,rolesChanged=False))
    print('Source detail comparison complete.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',required=True,action='store_true')
    parser.parse_args();run(OUT)
