"""Admit source-qualified UIKit training groups without changing original manifests."""
import hashlib
from PIL import Image
import research_queue as q
from experiment_templates import checked, pin
from ios_annotation_contract478 import review
from detector_native_inputs import bounds


def prepare(sources, exclusion, names):
    """Check every group and pixel against retained data before returning membership."""
    inventory = q.load(checked(exclusion))
    q.require(inventory.get('integrityPassed') and not inventory.get('errors'),
              'ios_training_exclusion_integrity')
    previous = inventory['members']
    groups = {(r['family'], r['seed']) for r in previous}
    pixels = {r['pixelSHA256'] for r in previous}
    encoded = {r['imageSHA256'] for r in previous}
    rows, lineage, rejected = [], [], []
    for source in sources:
        manifest_path, summary_path = checked(source['manifest']), checked(source['summary'])
        qualified = review(manifest_path, summary_path)
        q.require(qualified['annotationContractPassed'], 'ios_training_annotation_contract')
        doc = q.load(manifest_path)
        for row in doc['rows']:
            q.require((row['family'], row['seed']) not in groups, 'ios_training_reserved_group')
            image = q.local_path(manifest_path.parent, row['image']['path'])
            side = q.load(q.local_path(manifest_path.parent, row['sidecar']['path']))
            q.require(side['imageSHA256'] == row['image']['sha256'], 'ios_training_sidecar_image')
            with Image.open(image) as decoded:
                width, height = decoded.size
                pixel = hashlib.sha256(str(decoded.size).encode() + decoded.convert('RGBA').tobytes()).hexdigest()
            q.require(pixel not in pixels and row['image']['sha256'] not in encoded,
                      'ios_training_reserved_pixels')
            uncertain = [e['id'] for e in side['elements'] if not e.get('excluded') and
                         (e.get('knownIssues') or e.get('occluded'))]
            if uncertain:
                # Reject the whole frame. Dropping only its label would train a false background.
                rejected.append(dict(id=row['id'], group=row['group'],
                    reason='uncertain_or_occluded_element', elements=uncertain,
                    originalManifest=source['manifest']))
                continue
            controls = []
            for element in side['elements']:
                if element.get('excluded'):
                    continue
                q.require(not element.get('knownIssues') and not element.get('occluded'),
                          'ios_training_uncertain_element')
                kind = element['elementType']
                q.require(kind in names and kind != 'unknown', 'ios_training_unknown_class')
                box = element['boundsPixels']
                controls.append(dict(id=element['id'], **{'class': kind},
                    bounds=bounds([box[k] for k in ('x', 'y', 'width', 'height')], width, height)))
            q.require(len(controls) == row['labels'], 'ios_training_label_count')
            rows.append(dict(id=row['id'], group=row['group'], role='train', trainingEligible=True,
                labelsComplete=True, image=pin(image), width=width, height=height, controls=controls))
            lineage.append(dict(id=row['id'], originalManifest=source['manifest'],
                originalEligibility=False, decodedPixelSHA256=pixel))
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'ios_training_duplicate_identity')
    # Trainer preparation also verifies duplicate image groups and label consistency.
    return dict(version='detector-training-membership-v2', trainingAdmitted=True,
        calibrationPolicy='none-fixed-last-training-diagnostics', names=names, rows=rows,
        exclusion=exclusion, lineage=lineage, rejectedFrames=rejected, modelAccepted=False,
        limitation='Training admission only. Native source classes follow the frozen taxonomy. No model promotion.')
