"""Scoring-only geometry decomposition; never supplies model inputs or boxes."""
import numpy as np
import focus_direct_transition as d
import focus_spatial_transition as spatial
from focus_recorded_transition_eval import iou


def overflow(box,size):
    x,y,w,h=box;W,H=size
    return [max(0.,-x),max(0.,-y),max(0.,x+w-W),max(0.,y+h-H)]


def diagnose(net,encoded,row,prediction):
    torch=d.torch_runtime();x=torch.from_numpy(encoded).unsqueeze(0)
    truth=[d.target_box(b,row['size']) for b in row['boxes']]
    indices,_=spatial.targets(torch,torch.tensor([[v for b in truth for v in b]]))
    with torch.inference_mode():
        cells,geometry,_=net.fields(x);values=net(x).sigmoid()[0].tolist()
        oracle_values=geometry.flatten(3).gather(3,indices[:,:,None,None].expand(-1,-1,4,1)).squeeze(3).sigmoid()[0]
    rows=[]
    for k,endpoint in enumerate(('before','after')):
        predicted=values[k*4:k*4+4];target=truth[k];raw=d.raw_image_box(predicted,row['size'])
        target_cell=int(indices[0,k]);scores=cells[0,k].flatten();actual=prediction['boxes'][k]
        center_oracle=d.image_box([*target[:2],*predicted[2:]],row['size'])
        extent_oracle=d.image_box([*predicted[:2],*target[2:]],row['size'])
        g=oracle_values[k].tolist();cell_oracle=d.image_box([(target_cell%24+g[0])/24,(target_cell//24+g[1])/16,*g[2:]],row['size'])
        def overlap(box):return iou(box,row['boxes'][k]) if box else 0
        rows.append(dict(endpoint=endpoint,targetInputPixels=[target[2]*96,target[3]*64],
            centerErrorInputPixels=[(predicted[i]-target[i])*v for i,v in enumerate((96,64))],
            extentErrorInputPixels=[(predicted[i+2]-target[i+2])*v for i,v in enumerate((96,64))],
            predictedNormalized=predicted,truthNormalized=target,unclippedBox=raw,
            borderOverflowPixels=overflow(raw,row['size']),invalid=actual is None,actualIoU=overlap(actual),
            targetCell=target_cell,predictedCell=int(scores.argmax()),targetCellRank=int((scores>scores[target_cell]).sum())+1,
            scoringOnlyOracleIoU=dict(center=overlap(center_oracle),extent=overlap(extent_oracle),cell=overlap(cell_oracle))))
    return rows


def summarize(rows):
    endpoints=[e for row in rows for e in row['endpoints']]
    if not endpoints:return dict(endpoints=0)
    def absolute_mean(name):return np.abs([e[name] for e in endpoints]).mean(axis=0).tolist()
    dims=np.asarray([e['targetInputPixels'] for e in endpoints])
    return dict(endpoints=len(endpoints),invalid=sum(e['invalid'] for e in endpoints),
        localized=sum(e['actualIoU']>=.5 for e in endpoints),
        correctCells=sum(e['targetCell']==e['predictedCell'] for e in endpoints),
        meanAbsoluteCenterErrorInputPixels=absolute_mean('centerErrorInputPixels'),
        meanAbsoluteExtentErrorInputPixels=absolute_mean('extentErrorInputPixels'),
        targetSizeInputPixels=dict(min=dims.min(axis=0).tolist(),median=np.median(dims,axis=0).tolist(),max=dims.max(axis=0).tolist()),
        scoringOnlyOracleLocalized={key:sum(e['scoringOnlyOracleIoU'][key]>=.5 for e in endpoints) for key in ('center','extent','cell')})
