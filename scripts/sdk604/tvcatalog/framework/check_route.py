"""Compare TVCatalog's authenticated framework packet with its frozen development key."""
import argparse
import json
from pathlib import Path

import framework_projection604 as projection
import milestone_readback604 as readback
import research_queue as q
from ttr_detector_ingest604 import ingest_framework_frame


def verify(packet, keypath, work, output):
    key = q.load(keypath)
    side = packet / readback.SIDECAR
    image = packet / 'frame.png'
    row, projected = ingest_framework_frame(side, image, 'tvcatalog-description-development',
                                           role='review', row_id='tvcatalog-description')
    expected = {obj['id']: ('target', obj['expectedClass'], None) for obj in key['targets']}
    expected.update({i: ('owned_metadata', None, parent) for i, parent in key['ownedMetadata'].items()})
    expected.update({i: ('out_of_scope', None, None) for i in key['staticText']})
    actual = {obj['id']: (obj['disposition'], obj['class'], obj['parent_id']) for obj in projected['objects']}
    mismatches = {i: {'expected': expected.get(i), 'actual': actual.get(i)}
                  for i in sorted(set(expected) | set(actual)) if expected.get(i) != actual.get(i)}
    reasons = list(projected['reasons'])
    if mismatches:
        reasons.append('independent_object_key')
    if projected['focus_id'] != key['expectedFocus'] or projected['focus_state'] != 'focused':
        reasons.append('independent_focus_key')
    loader = None
    if row is not None:
        _, cfg = readback.loader_config()
        all_rows, _ = readback.readback([('tvcatalog-description', side, image)], work, projection.tvos_classes(), cfg)
        loader = all_rows['tvcatalog-description']
        if loader['roundtrip_errors']:
            reasons.append('loader_roundtrip')
    result = dict(sourceRole='development-regression', trainingAdmission=False, route=key['route'],
                  screenshotSHA256=q.digest(image), sidecarSHA256=q.digest(side), keySHA256=q.digest(keypath),
                  focus=projected['focus_id'], focusState=projected['focus_state'], keyTargets=len(key['targets']),
                  detectedTargets=len(projected['targets']), keyObjects=len(expected), reportedObjects=len(actual),
                  mismatches=mismatches, rawImporterEligible=row is not None, reasons=reasons,
                  independentKeyAndTensorPass=row is not None and not reasons, loader=loader,
                  independentPixelEdges='unmeasured')
    output.write_text(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('packet', type=Path)
    p.add_argument('key', type=Path)
    p.add_argument('work', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    result = verify(a.packet.resolve(), a.key, a.work.resolve(), a.output)
    print(json.dumps({k: v for k, v in result.items() if k not in ('loader', 'mismatches')}, indent=2))
    raise SystemExit(0 if result['independentKeyAndTensorPass'] else 1)
