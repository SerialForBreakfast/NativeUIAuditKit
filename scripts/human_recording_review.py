"""Direct diagnostic subset intake from a retained schema2 recorder bundle."""
import argparse
import json
from pathlib import Path
import shutil
import human_annotation_review as h

VERSION = 'human-recording-review-batch-v1'


def events(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s]


def validate(path):
    batch = h.sealed(path, VERSION)
    for ref in batch['rawEvidence']:
        h.checked(h.ROOT, ref)
    manifest = h.read(h.checked(h.ROOT, batch['manifest']))
    h.require(manifest['schemaVersion'] == 2 and manifest['sessionID'] == batch['sessionID'] and
              manifest['targetDeviceID'] == batch['sourceDeviceID'], 'recording_binding_changed')
    h.require(h.sha(h.CATEGORY) == batch['categoryMap']['sha256'], 'taxonomy_changed')
    raw = events(h.checked(h.ROOT, batch['events']))
    frames = {d['frame']['_0']['frameID']: d['frame']['_0'] for d in raw if 'frame' in d}
    h.require(len(frames) == sum('frame' in d for d in raw), 'duplicate_frame_id')
    inventory = events(h.checked(h.ROOT, batch['inventory']))
    hashes = {v['sha256']: v for v in inventory}
    ids = [f['id'] for f in batch['frames']]
    h.require(0 < len(ids) <= 8 and len(set(ids)) == len(ids), 'invalid_review_membership')
    h.require(len({f['pixelSHA256'] for f in batch['frames']}) == len(ids), 'duplicate_review_pixels')
    h.require(not batch['pairs'] and not batch['transitions'] and not batch['completeFrameCandidates'],
              'unsupported_recording_claim')
    for f in batch['frames']:
        event = frames[f['observationID']]
        roles = ('postInputSettled', 'postInputUnverified') if batch.get('includeUnverified') is True else ('postInputSettled',)
        h.require(f['recordingEvent'] == event and event['sourceDeviceID'] == batch['sourceDeviceID'] and
                  event['role'] in roles and f['image']['sha256'] == event['sha256'], 'frame_binding_changed')
        p = h.checked(h.ROOT, f['image'])
        h.require(p.stat().st_size == hashes[event['sha256']]['bytes'], 'image_size_changed')
        h.require(list(h.image(h.ROOT, f['image'])) == f['size'] and
                  h.pixel_digest(h.ROOT, f['image']) == f['pixelSHA256'], 'pixels_changed')
        h.require(f['disposition'] == 'imported' and not f['proposals'] and not f['nativeUnresolved'], 'invalid_recording_proposals')
    return batch


def prepare(source, output, selection, *, include_unverified=False):
    source = Path(source).resolve()
    output = h.fresh(output)
    h.require(type(include_unverified) is bool, 'invalid_unverified_option')
    batch_id = 'recording-review-'+h.digest(str(output.relative_to(h.ROOT)))[:16]
    manifest = json.loads((source/'manifest.json').read_text())
    h.require(manifest['schemaVersion'] == 2, 'unsupported_recording')
    raw_events = events(source/'events.jsonl')
    frames = {d['frame']['_0']['sequenceNumber']: d['frame']['_0'] for d in raw_events if 'frame' in d}
    h.require(0 < len(selection) <= 8 and len({s[0] for s in selection}) == len(selection), 'invalid_selection')
    output.mkdir(parents=True)
    for name in ['raw', 'editor']:
        (output/name).mkdir()
    refs = {}
    for name in ['manifest.json', 'events.jsonl', 'files.jsonl', 'delivery.json', 'manifest-receipt.json']:
        original = source/name
        h.require(not original.is_symlink() and original.stat().st_size < 32*1024*1024, 'invalid_metadata')
        shutil.copyfile(original, output/'raw'/name)
        h.require(h.sha(original) == h.sha(output/'raw'/name), 'source_changed')
        refs[name] = h.ref(output/'raw'/name)
    shutil.copyfile(h.CATEGORY, output/'raw/category-map.json')
    category = h.ref(output/'raw/category-map.json')
    rows = []
    for number, (sequence, screen) in enumerate(selection, 1):
        event = frames[sequence]
        original = source/'images'/('frame-'+event['sha256']+'.png')
        h.require(original.resolve().is_relative_to(source) and not original.is_symlink() and
                  h.sha(original) == event['sha256'], 'changed_source_image')
        frame_id = f'recorded-{sequence}'
        stem = f'{number:03d}-{frame_id}'
        shutil.copyfile(original, output/'raw'/(frame_id+'.png'))
        image = h.ref(output/'raw'/(frame_id+'.png'))
        row = dict(id=frame_id, number=number, screen=screen, context='Retained TTR recording; human review pending',
                   disposition='imported', reasons=[], observationID=event['frameID'], recordingEvent=event,
                   proposals=[], nativeUnresolved=False, editorStem=stem, size=list(h.image(h.ROOT,image)),
                   image=image, pixelSHA256=h.pixel_digest(h.ROOT,image), duplicateOf=None)
        rows.append(row)
        shutil.copyfile(original, output/'editor'/(stem+'.png'))
        h.write(output/'editor'/(stem+'.json'), h.editor_document(batch_id,row))
    batch = dict(version=VERSION, **h.FLAGS, id=batch_id, includeUnverified=include_unverified,
                 manifest=refs['manifest.json'], events=refs['events.jsonl'], inventory=refs['files.jsonl'],
                 rawEvidence=list(refs.values())+[category], categoryMap=category,
                 sessionID=manifest['sessionID'], sourceDeviceID=manifest['targetDeviceID'],
                 frames=rows, pairs=[], transitions=[], counts={'imported':len(rows)},
                 completeFrameCandidates=False, selectionBasis='preparer visual diversity; original producer settlement role preserved')
    h.write(output/'batch.json',batch,sealed=True)
    validate(output/'batch.json')
    return output/'batch.json'


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source');parser.add_argument('output');parser.add_argument('--selection',required=True)
    parser.add_argument('--include-unverified', action='store_true', help='Allow diagnostic review of producer-unverified frames, never transition frames')
    args=parser.parse_args()
    selection=[(int(part.split(':',1)[0]),part.split(':',1)[1]) for part in args.selection.split(',')]
    print(prepare(args.source,args.output,selection,include_unverified=args.include_unverified))
