"""Prepare blinded review directory for the 8 RC561 development diagnostic frames.
No model predictions are included. All initial drafts are unreviewed and pending human confirmation.
Follows ModelQualificationRecovery20261103 Step 4.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CAPTURES_DIR = ROOT / 'reports/work/RC561/captures'
REVIEW_DIR = ROOT / 'reports/work/RC561/review'
DRAFTS_DIR = REVIEW_DIR / 'drafts'
LABELS_DIR = REVIEW_DIR / 'labels'

APP_MAP = {
    'plozz-screen-01.png': ('com.thatcube.Plozz', 'plozz-home', 'Plozz Jellyfin server connect screen'),
    'strimr-screen-01.png': ('org.nuiak.rc561.strimr', 'strimr-home', 'Strimr Jellyfin server connect screen'),
    'swiftfin-screen-01.png': ('org.jellyfin.swiftfin', 'swiftfin-home', 'Swiftfin Jellyfin server connect screen'),
    'tvcatalog-screen-01.png': ('com.example.apple-samplecode.TVCatalog', 'tvcatalog-stack', 'TVCatalog StackView flow screen'),
    'tvcatalog-buttons.png': ('com.example.apple-samplecode.TVCatalog', 'tvcatalog-buttons', 'TVCatalog Buttons tab screen'),
    'tvcatalog-description.png': ('com.example.apple-samplecode.TVCatalog', 'tvcatalog-description', 'TVCatalog Description tab screen'),
    'tvcatalog-search.png': ('com.example.apple-samplecode.TVCatalog', 'tvcatalog-search', 'TVCatalog Search tab screen'),
    'tvcatalog-sidebar.png': ('com.example.apple-samplecode.TVCatalog', 'tvcatalog-sidebar', 'TVCatalog Sidebar tab screen'),
}

CLASSES = [
    'actionSheet', 'activityIndicator', 'alert', 'cancelAction', 'collectionItem',
    'colorWell', 'contextMenu', 'destructiveButton', 'disclosureGroup', 'dynamicIsland',
    'homeIndicator', 'imageView', 'label', 'link', 'listRow', 'mapView', 'menuButton',
    'navigationBar', 'pageControl', 'picker', 'popover', 'primaryButton', 'progressView',
    'refreshControl', 'scrollIndicator', 'searchField', 'secondaryButton', 'secureField',
    'segmentedControl', 'sheet', 'sidebar', 'slider', 'statusBar', 'stepperControl',
    'tabBar', 'textField', 'toggle', 'toolbar', 'tooltip', 'unknown', 'webContent'
]

def main():
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_DIR.mkdir(parents=True, exist_ok=True)

    cases = []
    for filename, (app, flow, desc) in sorted(APP_MAP.items()):
        img_path = CAPTURES_DIR / filename
        assert img_path.exists(), f"Missing capture: {img_path}"

        with Image.open(img_path) as im:
            w, h = im.size
            im_bytes = im.convert('RGB').tobytes()
            pix_sha = hashlib.sha256(im_bytes).hexdigest()

        file_sha = hashlib.sha256(img_path.read_bytes()).hexdigest()
        case_id = f"rc561-{filename.replace('.png', '')}"

        case_entry = {
            'id': case_id,
            'app': app,
            'flow': flow,
            'image': str(img_path.resolve()),
            'sha256': file_sha,
            'pixelSHA256': pix_sha,
            'width': w,
            'height': h,
            'plannedFocus': None,
            'expectedScreen': desc,
            'duplicates': [],
            'dataRole': 'diagnostic-development-evidence'
        }
        cases.append(case_entry)

        draft = {
            'imageSHA256': file_sha,
            'complete': False,
            'objects': [],
            'focus': {
                'state': 'unknown',
                'box': None
            },
            'review': {
                'blinded': True,
                'reviewer': '',
                'status': 'pending'
            }
        }

        draft_file = DRAFTS_DIR / f"{case_id}.json"
        draft_file.write_text(json.dumps(draft, indent=2) + '\n')

    cases_doc = {
        'version': 'rc561-review-v1',
        'authority': 'ModelQualificationRecovery20261103:Step4',
        'classes': CLASSES,
        'note': 'Blinded: no model predictions. The 8 screens are diagnostic development evidence, not a qualification holdout.',
        'cases': cases
    }

    cases_file = REVIEW_DIR / 'cases.json'
    cases_file.write_text(json.dumps(cases_doc, indent=2) + '\n')
    print(f"Prepared {len(cases)} cases in {REVIEW_DIR}")

if __name__ == '__main__':
    main()
