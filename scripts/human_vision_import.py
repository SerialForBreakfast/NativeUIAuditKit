"""Optional source-bound TTR Vision proposals; no capture, inference or annotation writes."""
import hashlib
import json
import math
from PIL import Image
from human_annotation_review import local, require
from human_auto_boxes import overlap

CONVENTION='top_left_normalized_xywh; pixels=normalized*per_frame_dimensions'
INTERPRETATION='proposals_only; no_focus_identity_or_cross_frame_correspondence; native_annotations_unchanged'


def pairs(items):
    result={}
    for k,v in items:
        require(k not in result,'duplicate_json_key');result[k]=v
    return result


def load(path,image_path,existing=(),limit=100):
    path=local(path);image_path=local(image_path)
    require(path.is_file() and path.stat().st_size<=2_097_152,'invalid_vision_sidecar_size')
    raw=path.read_bytes();doc=json.loads(raw,object_pairs_hook=pairs)
    require(isinstance(doc,dict) and doc.get('schemaVersion')==1 and
            doc.get('kind')=='vision_pair_preprocessing' and
            doc.get('coordinateConvention')==CONVENTION and doc.get('interpretation')==INTERPRETATION,
            'unsupported_vision_sidecar')
    frames=doc.get('frames');require(isinstance(frames,list) and len(frames)==2,'invalid_vision_frames')
    require(all(isinstance(f,dict) for f in frames) and {f.get('role') for f in frames}=={'before','after'},'invalid_frame_roles')
    require(image_path.stat().st_size<=33_554_432,'image_too_large')
    image_sha=hashlib.sha256(image_path.read_bytes()).hexdigest()
    with Image.open(image_path) as im:
        im.load();dimensions=im.size
    matches=[f for f in frames if f.get('sha256')==image_sha]
    require(matches,'vision_image_hash_mismatch')
    require(all((f.get('width'),f.get('height'))==dimensions for f in matches),'vision_dimensions_mismatch')
    require(all(f.get('features')==matches[0].get('features') for f in matches),'ambiguous_same_image_features')
    features=matches[0].get('features');require(isinstance(features,dict),'invalid_features')
    for key in ('ocrRevision','rectangleRevision'):
        require(type(features.get(key)) is int and features[key]>0,'missing_request_revision')
    require(type(features.get('textTruncated')) is bool,'missing_truncation_status')
    regions=[]
    for kind,key,cap in (('rectangle','rectangles',128),('ocr','text',512)):
        values=features.get(key);require(isinstance(values,list) and len(values)<=cap,'invalid_region_count')
        for value in values:
            require(isinstance(value,dict),'invalid_region')
            confidence=value.get('confidence');bounds=value.get('bounds')
            require(type(confidence) in (int,float) and math.isfinite(confidence) and 0<=confidence<=1,'invalid_confidence')
            require(isinstance(bounds,dict) and set(bounds)=={'x','y','width','height'},'invalid_bounds')
            x,y,w,h=[bounds[k] for k in ('x','y','width','height')]
            require(all(type(v) in (int,float) and math.isfinite(v) for v in (x,y,w,h)) and
                    x>=0 and y>=0 and w>0 and h>0 and x+w<=1 and y+h<=1,'invalid_bounds')
            text=value.get('text','')
            require(kind!='ocr' or isinstance(text,str) and 0<len(text)<=512,'invalid_ocr_text')
            width,height=dimensions;points=[[x*width,y*height],[(x+w)*width,(y+h)*height]]
            # Preserve OCR as a separate kind, not a rectangle/class/focus agreement.
            if any(overlap(points,box)>=.95 for box in existing):continue
            if any(r['kind']==kind and overlap(points,r['points'])>=.95 for r in regions):continue
            regions.append(dict(points=points,kind=kind,text=text,confidence=confidence))
    return dict(regions=regions,limit=max(0,min(100,limit)),textTruncated=features['textTruncated'],
        provenance=dict(sidecarSHA256=hashlib.sha256(raw).hexdigest(),imageSHA256=image_sha,
                        ocrRevision=features['ocrRevision'],rectangleRevision=features['rectangleRevision']))
