"""Offline human review inventory and role proposal; no models or admission writes."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
import human_annotation_review as h
from human_review_audit import audit, groups
from focus_representative_validation import stratum

PROTOCOLS = {
    'photos': 'HUMAN-REVIEW-04/protocol.json',
    'batch01': 'FOCUS-TTR-TEST-CYCLE-01/batch01-protocol.json',
    'batch02': 'FOCUS-TTR-TEST-CYCLE-01/batch02-protocol.json',
    'batch03': 'FOCUS-TTR-TEST-CYCLE-01/batch03-protocol.json',
    'supplement': 'HUMAN-BENCHMARK-02/protocol.json',
}


def latest_revisions(records):
    """Reject ambiguous latest timestamps; software tests never become human data."""
    by_batch = defaultdict(list)
    for record in records:
        if record['reviewer']['kind'] == 'human':
            h.require(record['reviewer']['confirmedBatch'] is True, 'unconfirmed_revision')
            by_batch[record['batch']['path']].append(record)
    selected = []
    for rows in by_batch.values():
        rows.sort(key=lambda r: datetime.fromisoformat(r['reviewer']['completedAt']))
        h.require(len(rows) == 1 or datetime.fromisoformat(rows[-1]['reviewer']['completedAt']) != datetime.fromisoformat(rows[-2]['reviewer']['completedAt']),
                  'ambiguous_latest_revision')
        selected.append(rows[-1]['reference']['path'])
    return sorted(selected)


def components(frames):
    """Same session/family or exact pixels link whole frames, never crop splits."""
    parents = {f['id']: f['id'] for f in frames}
    def root(k):
        while parents[k] != k:
            k = parents[k]
        return k
    seen = {}
    for frame in sorted(frames, key=lambda f: f['id']):
        for key in [('session', frame['sessionID']), ('family', frame['family']), ('pixels', frame['pixelSHA256'])]:
            if key[1] in ('unknown', None, ''):
                continue
            if key in seen:
                parents[root(frame['id'])] = root(seen[key])
            else:
                seen[key] = frame['id']
    result = defaultdict(list)
    for f in frames:
        result[root(f['id'])].append(f['id'])
    return sorted(sorted(v) for v in result.values())


def metadata_hashes(value):
    """Inspect metadata only, without following paths or opening protected pixels."""
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('sha256', 'pixelSHA256', 'imageSHA256') and isinstance(item, str):
                found.add(item)
            found.update(metadata_hashes(item))
    elif isinstance(value, list):
        for item in value:
            found.update(metadata_hashes(item))
    return found


def run(output):
    output = h.fresh(output)
    inputs = {}
    def pin(path):
        ref = h.ref(path); h.checked(h.ROOT, ref); inputs[ref['path']] = ref
        return ref
    records = []
    for path in sorted((h.ROOT/'reports/work').rglob('revision.json')):
        if 'received' in path.parts:
            continue
        doc = h.read(path)
        if doc.get('version') not in (h.REVISION, h.FOCUS_REVISION):
            continue
        doc = h.read_revision(path)
        records.append(dict(reference=pin(path), reviewer=doc['reviewer'], batch=doc['batch'],
                            frames=doc['frameCounts'], controls=doc['controlCounts']))
    latest = latest_revisions(records)
    assembly_path = h.ROOT/'reports/work/FOCUS-CONTROL32-ADMIT-01/assembly.json'
    assembly = h.read(assembly_path); pin(assembly_path)
    content = dict(assembly); seal = content.pop('assemblySHA256')
    h.require(h.digest(content) == seal, 'changed_assembly')
    selection = {r['id']: r for r in assembly['samples'] if r['use'] == 'representative-selection'}
    exclusions = {r['id']: r for r in assembly['excludedSelection']}
    frames, controls, batches, audited = [], [], [], []
    prior_protocols = []
    for run_id in ('FDR-015', 'FDR-016'):
        prior_path = h.ROOT/'reports/work'/run_id/'protocol-ready.json'
        prior = h.read(prior_path); pin(prior_path)
        prior_content = dict(prior); prior_seal = prior_content.pop('protocolSHA256')
        h.require(h.digest(prior_content) == prior_seal, 'changed_prior_protocol')
        prior_protocols.append(dict(runID=run_id, reference=h.ref(prior_path),
            trainingIDs=[r['id'] for r in prior['samples'] if r['use'] == 'train-candidate'],
            selectionIDs=[r['id'] for r in prior['samples'] if r['use'] == 'representative-selection'],
            trainingLabelSources=dict(Counter(r['labelSource'] for r in prior['samples'] if r['use'] == 'train-candidate'))))
    for name, rel in PROTOCOLS.items():
        path = h.ROOT/'reports/work'/rel; pin(path); protocol = h.read(path)
        revision_path = h.checked(h.ROOT, protocol['revision']); crops_path = h.checked(h.ROOT, protocol['crops'])
        reviewed = audit(revision_path, crops_path)
        revision = h.read_revision(revision_path); audited.append(str(revision_path.relative_to(h.ROOT)))
        batch = h.validate_batch(h.checked(h.ROOT, revision['batch']))
        for ref in reviewed['inputs']:
            pin(h.checked(h.ROOT, ref))
        batches.append(dict(name=name, revision=protocol['revision'], cropQA=protocol['crops'],
                            sessionID=batch['sessionID'], counts=reviewed['counts']))
        frame_rows = {f['id']: f for f in reviewed['frames']}
        for f in reviewed['frames']:
            source = next(b for b in batch['frames'] if b['id'] == f['id'])
            policy = next(p for p in assembly['selection']['framePolicy']['frames'] if p['id'] == name+':'+f['id'])
            frames.append(dict(id=name+':'+f['id'], batch=name, originalID=f['id'], screen=f['screen'],
                family=f['screen'], sessionID=batch['sessionID'], sourceDeviceID=batch['sourceDeviceID'],
                image=f['image'], pixelSHA256=f['pixelSHA256'], controls=f['controls'], revision=protocol['revision'],
                originalCoverage=policy, observationID=source.get('observationID'),
                capture=source.get('recordingEvent', {}), sourceIndependence='unknown',
                proposedRole='development', priorUse='model-development-selection'))
        for sample in reviewed['samples']:
            sid = name+':'+sample['id']; h.require(sid in selection or sid in exclusions, 'unaccounted_control')
            active = selection.get(sid)
            if active:
                h.require(active['image'] == frame_rows[sample['frameID']]['image'] and
                          active['crop'] == sample['crop'] and active['state'] == sample['state'] and
                          active['bounds'] == sample['bounds'], 'changed_selection_annotation')
            controls.append(dict(id=sid, frameID=name+':'+sample['frameID'], state=sample['state'],
                bounds=sample['bounds'], detectorClass=sample['class'], focusRole=sample.get('focusRole'),
                stratum=stratum(active) if active else 'excluded', crop=sample['crop'],
                pixelSHA256=sample['pixelSHA256'], revision=protocol['revision'],
                priorUse='representative-selection' if active else 'excluded-selection',
                exclusion=exclusions.get(sid), proposalEligible=bool(active),
                trainingApproved=False, pairedTransitionEligible=False))
    h.require(sorted(audited) == latest, 'unaccounted_latest_human_revision')
    h.require({r['id'] for r in controls} == set(selection) | set(exclusions), 'selection_inventory_mismatch')
    # Native/synthetic source images are read for exact/similarity checks; protected pixels are never read.
    training, thumbnails, protected = [], {}, []
    def thumbnail(ref):
        if ref['sha256'] not in thumbnails:
            p = h.checked(h.ROOT, ref); pin(p)
            with Image.open(p) as im:
                thumbnails[ref['sha256']] = im.convert('RGB').resize((64, 36), Image.Resampling.BILINEAR)
        return thumbnails[ref['sha256']]
    for f in frames:
        thumbnail(f['image'])
    for row in assembly['samples']:
        if row['use'] not in ('train-candidate', 'retention-validation'):
            continue
        for key in ('frame', 'crop'):
            pin(h.checked(h.ROOT, row[key]))
            h.require(h.pixel_digest(h.ROOT, row[key]) == row[key]['pixelSHA256'], 'changed_training_pixels')
        thumbnail(row['frame'])
        training.append(dict(id=row['id'], use=row['use'], sourceID=row['sourceID'],
            sourceKind=row['sourceKind'], labelSource=row['labelSource'], group=row['relatedGroup'],
            frame=row['frame'], crop=row['crop']))
    exact = []
    for f in frames:
        for r in training:
            if f['pixelSHA256'] == r['frame']['pixelSHA256']:
                exact.append(dict(frameID=f['id'], sampleID=r['id'], kind='frame'))
    by_pixel = defaultdict(list)
    for r in training:
        by_pixel[r['crop']['pixelSHA256']].append(r['id'])
    for c in controls:
        for sid in by_pixel[c['pixelSHA256']]:
            exact.append(dict(controlID=c['id'], sampleID=sid, kind='crop'))
    near = []
    training_frames = {r['frame']['sha256']: r['frame'] for r in training}
    comparisons = 0
    for i, f in enumerate(frames):
        targets = [(g['id'], g['image']) for g in frames[i+1:]] + list(training_frames.items())
        for identity, ref in targets:
            comparisons += 1
            difference = sum(ImageStat.Stat(ImageChops.difference(thumbnail(f['image']), thumbnail(ref))).mean)/3
            if difference <= 2:
                near.append(dict(frameID=f['id'], other=identity, otherImage=ref, meanAbsoluteRGB=difference))
    for key in ('protectedMetadata', 'reservedPixels'):
        path = h.checked(h.ROOT, assembly[key]); pin(path); doc = h.read(path)
        hashes = metadata_hashes(doc)
        protected.append(dict(kind=key, reference=assembly[key], keys=sorted(doc),
            matchingHumanFrames=[f['id'] for f in frames if f['pixelSHA256'] in hashes or f['image']['sha256'] in hashes],
            matchingHumanControls=[c['id'] for c in controls if c['pixelSHA256'] in hashes or c['crop']['sha256'] in hashes],
            pixelsRead=False, absenceDoesNotProveIndependence=True))
    amendment_path = h.ROOT/'reports/work/FOCUS-INTEGRATION-03/policy-amendment.json'
    pin(amendment_path); amendment = h.read(amendment_path)
    amended_content = dict(amendment); amended_seal = amended_content.pop('amendmentSHA256')
    h.require(h.digest(amended_content) == amended_seal, 'changed_policy_amendment')
    pin(h.checked(h.ROOT, amendment['confirmation']))
    pin(h.ROOT/'reports/work/HUMAN-BENCHMARK-02/source-reservation.json')
    # Human group alternatives are proposals only. Entire session/family component moves, not individual crops.
    connected = components(frames)
    candidate_group = next(g for g in connected if 'supplement:recorded-875' in g)
    candidate = [c['id'] for c in controls if c['frameID'] in candidate_group and c['proposalEligible']]
    validation = [c['id'] for c in controls if c['frameID'] not in candidate_group and c['proposalEligible']]
    h.require(set(candidate).isdisjoint(validation), 'proposal_overlap')
    proposal = dict(version='human-corpus-role-proposal-v1', trainingApproved=False, executionAuthorized=False,
        defaultRoles={f['id']:'development' for f in frames}, groups=connected,
        alternative=dict(requiresExplicitReassignment=True, trainingFrames=candidate_group,
            trainingControls=candidate, developmentControls=validation,
            heldControls=[c['id'] for c in controls if not c['proposalEligible']],
            untouchedHumanTestFrames=[], independence='not_established',
            retireValidationForWholeTrainingGroup=True), protectedReferences=[p['reference'] for p in protected])
    legacy = []
    for rel in ['PER-DATA/manifest.json', 'FOCUS-VISUAL-02/manifest.json']:
        p=h.ROOT/'reports/work'/rel; pin(p); d=h.read(p)
        legacy.append(dict(reference=h.ref(p), cases=len(d['cases']),
            reviewers=sorted({r['reviewer'] for r in d['cases']}), humanConfirmation=False))
    for ref in inputs.values():
        h.checked(h.ROOT, ref)
    report = dict(version='human-corpus-inventory-v1', trainingApproved=False, modelExecution=False,
        revisions=records, latestRevisions=latest, batches=batches, frames=frames, controls=controls,
        counts=dict(frames=len(frames), controls=len(controls), distinctFramePixels=len({f['pixelSHA256'] for f in frames}),
            distinctCropPixels=len({c['pixelSHA256'] for c in controls}), eligibleSelection=len(selection),
            excludedSelection=len(exclusions), sessions=len({f['sessionID'] for f in frames})),
        frameDuplicates=groups((f['id'],f['pixelSHA256']) for f in frames),
        cropDuplicates=groups((c['id'],c['pixelSHA256']) for c in controls),
        exactTrainingOverlap=exact, similarity=dict(method='64x36 RGB bilinear mean absolute difference <=2/255',
            comparisons=comparisons, matches=near, independenceProof=False), training=training,
        protectedMetadata=protected, legacyAgentReviews=legacy, priorProtocols=prior_protocols,
        framePolicyAmendment=dict(reference=h.ref(amendment_path), priorSupported=amendment['priorSupported'],
            amendedSupported=amendment['amendedSupported'], changedFrameIDs=amendment['changedFrameIDs']),
        selectionStrata=dict(Counter(c['stratum'] for c in controls if c['proposalEligible'])),
        selectionStates=dict(Counter(c['state'] for c in controls if c['proposalEligible'])),
        limitations=['No native transition labels inferred from human boxes or action intent.',
            'Training ancestry before recorded assemblies is not exhaustively reconstructed.',
            'All human data is development-exposed; no untouched real-world test set.'])
    output.mkdir(parents=True)
    h.write(output/'inventory.json', report); h.write(output/'membership-proposal.json', proposal)
    h.write(output/'inputs.json', list(inputs.values()))
    return report, proposal


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report,proposal=run(args.output)
    print(report['counts']);print('group sizes',[len(g) for g in proposal['groups']])
    print('conditional training controls',len(proposal['alternative']['trainingControls']))
