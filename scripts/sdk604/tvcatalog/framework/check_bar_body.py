"""Validate the floating TVCatalog tab strip on a retained development packet.

Keep the producer artifact immutable. A reference from pixels must agree with one
distinct SDK rectangle in both layout samples before writing a diagnostic tensor.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import cv2
import framework_projection604 as projection
import detector_training419 as writer
from milestone_readback604 import decode_batch
from qpacket_import604 import _iou_edge, geometry_in_tolerance
from ttr_detector_ingest604 import ingest_framework_frame


def painted_reference(pixels):
    """Find the closed wide outer strip in the top band, excluding the smaller focused item."""
    height, width = pixels.shape
    refs = []
    for low, high in ((24, 48), (40, 90)):
        band = cv2.Canny(pixels[:height // 5], low, high)
        contours, _ = cv2.findContours(band, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        plausible = set()
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if (width*.25 < w < width*.85 and height*.025 < h < height*.12
                    and abs(x+w/2-width/2) < width*.08
                    and cv2.contourArea(contour) > .85*w*h):
                plausible.add((x, y, w, h))
        if not plausible:
            raise ValueError('no closed painted strip')
        refs.append(max(plausible, key=lambda b: b[2]*b[3]))
    if refs[0] != refs[1]:
        raise ValueError('contrast-sensitive contour')
    return list(refs[0])


def native_candidates(snapshot, transform, raw, reference):
    layout = snapshot['layout']
    if layout['coordinateSpace'] != 'window_points':
        raise ValueError('unexpected layout space')
    geometry = layout['captureGeometry']
    if geometry['toScreenPoints'] != [1, 0, 0, 1, 0, 0]:
        raise ValueError('unsupported window transform')
    sx, shear_y, shear_x, sy, tx, ty = transform
    if min(sx, sy) <= 0 or shear_x or shear_y:
        raise ValueError('unsupported screenshot transform')
    nodes = {n['id']: n for n in layout['nodes']}
    def bounds(node):
        b = node.get('clippedBounds')
        if b:
            return (b['x']*sx+tx, b['y']*sy+ty, b['width']*sx, b['height']*sy)
    found = defaultdict(list)
    for node in nodes.values():
        b = bounds(node)
        if node.get('hidden') or b is None or not geometry_in_tolerance(reference, *_iou_edge(b,reference)):
            continue
        parent = node.get('parent')
        seen = set()
        while parent in nodes and parent not in seen:
            seen.add(parent)
            ancestor = nodes[parent]
            if bounds(ancestor) == tuple(raw):
                found[b].append(node['id'])
                break
            parent = ancestor.get('parent')
    if len(found) != 1:
        raise ValueError('missing or ambiguous SDK strip rectangle')
    return next(iter(found)), next(iter(found.values()))


def verify(packet, work):
    read = lambda name: json.loads((packet/name).read_text())
    image = packet/'frame.png'
    side = packet/'frame.tvos-framework-frame-v1.json'
    evidence = read('evidence.json')
    frame = read(side.name)['frame']
    sha = hashlib.sha256(image.read_bytes()).hexdigest()
    if sha != frame['screenshot_sha256'] or sha != evidence['imageSHA256']:
        raise ValueError('image mismatch')
    row, proj = ingest_framework_frame(side, image, 'tvcatalog-development', row_id='bar-check')
    if row is None:
        raise ValueError(proj['reasons'])
    bar, = [c for c in row['controls'] if c['objectId']=='navigation.tabbar' and c['class']=='bar']
    raw = list(bar['bounds'])
    ref = painted_reference(cv2.imread(str(image), cv2.IMREAD_GRAYSCALE))
    obs = [native_candidates(evidence[k],frame['screen_to_image'],raw,ref) for k in ('before','after')]
    if obs[0][0] != obs[1][0]:
        raise ValueError('strip moved during capture')
    body = list(obs[0][0])
    bar['bounds'] = body
    names = projection.tvos_classes()
    doc = dict(version=writer.TRAIN_ONLY_VERSION,trainingAdmitted=True,
               calibrationPolicy='none-fixed-last-training-diagnostics', names=names, rows=[row])
    # Scratch loader fixture only. Do not register the diagnostic membership with the runner.
    dataset, _ = writer.prepare(doc,work)
    decoded = decode_batch(dataset,names)[row['id']]['boxes']
    assert len(decoded)==len(row['controls'])
    remaining = list(decoded)
    for c in row['controls']:
        best = max((d for d in remaining if d['cls']==c['class']),key=lambda d:_iou_edge(c['bounds'],d['box_src_px'])[0])
        assert _iou_edge(c['bounds'],best['box_src_px'])[1] < .1
        remaining.remove(best)
    decoded_bar, = [d['box_src_px'] for d in decoded if d['cls']=='bar']
    iou, edge = _iou_edge(decoded_bar,ref)
    assert geometry_in_tolerance(ref,iou,edge)
    return dict(role='development-only',trainingAdmission=False,imageSHA256=sha,
                frameworkLayout=raw,paintedReference=ref,nativeStrip=body,
                beforeNodes=obs[0][1],afterNodes=obs[1][1],decodedBar=decoded_bar,
                edgePx=edge,iou=iou,focus=proj['focus_id'],decodedTargets=decoded,
                exactScope='strip reference only; other boxes checked for serialization')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('packet','work','output'):
        p.add_argument(name,type=Path)
    a=p.parse_args()
    a.output.write_text(json.dumps(verify(a.packet.resolve(),a.work.resolve()),indent=2))
