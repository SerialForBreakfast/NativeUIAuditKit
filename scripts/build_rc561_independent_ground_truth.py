"""Generate verified independent ground truth labels for RC561 / RA554-13 holdout.
Zero reliance on model predictions. Pure ground-truth annotations from visual verification
and source code layouts.
"""
import sys
import json
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
HOLDOUT_DIR = q.ROOT / 'reports/work/RC561/holdout'
LABELS_DIR = HOLDOUT_DIR / 'labels'
LABELS_DIR.mkdir(parents=True, exist_ok=True)

# Define independent ground truth for all 8 screens
GROUND_TRUTH = {
    'rc561-swiftfin-screen-01': {
        'image': 'reports/work/RC561/captures/swiftfin-screen-01.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'swiftfin-icon', 'class': 'picture', 'box': [1820.0, 95.0, 201.0, 204.0]},
            {'id': 'swiftfin-text-title', 'class': 'text', 'box': [1535.0, 981.0, 775.0, 165.0]},
            {'id': 'swiftfin-btn-connect', 'class': 'button', 'box': [1512.0, 1196.0, 815.0, 172.0]}
        ]
    },
    'rc561-strimr-screen-01': {
        'image': 'reports/work/RC561/captures/strimr-screen-01.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'strimr-icon', 'class': 'picture', 'box': [1824.0, 765.0, 190.0, 159.0]},
            {'id': 'strimr-text-title', 'class': 'text', 'box': [1585.0, 1005.0, 680.0, 92.0]},
            {'id': 'strimr-text-desc', 'class': 'text', 'box': [564.0, 1133.0, 2713.0, 67.0]},
            {'id': 'strimr-btn-retry', 'class': 'button', 'box': [1783.0, 1255.0, 273.0, 159.0]}
        ]
    },
    'rc561-plozz-screen-01': {
        'image': 'reports/work/RC561/captures/plozz-screen-01.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'plozz-text-clock', 'class': 'text', 'box': [3280.0, 110.0, 360.0, 95.0]},
            {'id': 'plozz-picture-logo', 'class': 'picture', 'box': [1657.0, 664.0, 566.0, 279.0]},
            {'id': 'plozz-cell-srv1', 'class': 'cell', 'box': [780.0, 1655.0, 499.0, 298.0]},
            {'id': 'plozz-cell-srv2', 'class': 'cell', 'box': [1391.0, 1664.0, 433.0, 271.0]},
            {'id': 'plozz-cell-srv3', 'class': 'cell', 'box': [1924.0, 1630.0, 585.0, 340.0]},
            {'id': 'plozz-cell-srv4', 'class': 'cell', 'box': [2562.0, 1655.0, 498.0, 290.0]}
        ]
    },
    'rc561-tvcatalog-screen-01': {
        'image': 'reports/work/RC561/captures/tvcatalog-screen-01.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'tvcatalog-tab-bar', 'class': 'bar', 'box': [1100.0, 100.0, 1650.0, 140.0]},
            {'id': 'tvcatalog-tab-stack', 'class': 'button', 'box': [1155.0, 128.0, 224.0, 75.0]},
            {'id': 'tvcatalog-tab-buttons', 'class': 'button', 'box': [1529.0, 128.0, 268.0, 75.0]},
            {'id': 'tvcatalog-tab-desc', 'class': 'button', 'box': [1936.0, 128.0, 358.0, 75.0]},
            {'id': 'tvcatalog-tab-search', 'class': 'button', 'box': [2416.0, 128.0, 288.0, 75.0]},
            {'id': 'tvcatalog-title', 'class': 'text', 'box': [161.0, 352.0, 1006.0, 112.0]},
            {'id': 'tvcatalog-hero-btn-show', 'class': 'button', 'box': [189.0, 1415.0, 217.0, 104.0]},
            {'id': 'tvcatalog-hero-btn-info', 'class': 'button', 'box': [564.0, 1413.0, 345.0, 110.0]},
            {'id': 'tvcatalog-sec-movies', 'class': 'text', 'box': [156.0, 1769.0, 307.0, 51.0]},
            {'id': 'tvcatalog-card-1', 'class': 'cell', 'box': [168.0, 1886.0, 515.0, 278.0]},
            {'id': 'tvcatalog-card-2', 'class': 'cell', 'box': [720.0, 1886.0, 515.0, 278.0]},
            {'id': 'tvcatalog-card-3', 'class': 'cell', 'box': [1272.0, 1886.0, 515.0, 278.0]},
            {'id': 'tvcatalog-card-4', 'class': 'cell', 'box': [1824.0, 1886.0, 515.0, 278.0]},
            {'id': 'tvcatalog-card-5', 'class': 'cell', 'box': [2376.0, 1886.0, 515.0, 278.0]},
            {'id': 'tvcatalog-card-6', 'class': 'cell', 'box': [2928.0, 1886.0, 515.0, 278.0]}
        ]
    },
    'rc561-tvcatalog-buttons': {
        'image': 'reports/work/RC561/captures/tvcatalog-buttons.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'tvcatalog-btn-tab-bar', 'class': 'bar', 'box': [1100.0, 100.0, 1650.0, 140.0]},
            {'id': 'tvcatalog-btn-tab-stack', 'class': 'button', 'box': [1155.0, 128.0, 224.0, 75.0]},
            {'id': 'tvcatalog-btn-tab-buttons', 'class': 'button', 'box': [1529.0, 128.0, 268.0, 75.0]},
            {'id': 'tvcatalog-btn-tab-desc', 'class': 'button', 'box': [1936.0, 128.0, 358.0, 75.0]},
            {'id': 'tvcatalog-btn-tab-search', 'class': 'button', 'box': [2416.0, 128.0, 288.0, 75.0]},
            {'id': 'tvcatalog-btn-b1', 'class': 'button', 'box': [1380.0, 325.0, 345.0, 123.0]},
            {'id': 'tvcatalog-btn-b2', 'class': 'button', 'box': [1856.0, 325.0, 345.0, 123.0]},
            {'id': 'tvcatalog-btn-b3', 'class': 'button', 'box': [2327.0, 323.0, 130.0, 124.0]},
            {'id': 'tvcatalog-btn-t1', 'class': 'button', 'box': [1250.0, 565.0, 470.0, 123.0]},
            {'id': 'tvcatalog-btn-t2', 'class': 'button', 'box': [1845.0, 565.0, 550.0, 123.0]},
            {'id': 'tvcatalog-btn-t3', 'class': 'button', 'box': [2520.0, 565.0, 130.0, 123.0]},
            {'id': 'tvcatalog-btn-p1', 'class': 'button', 'box': [1355.0, 803.0, 372.0, 134.0]},
            {'id': 'tvcatalog-btn-p2', 'class': 'button', 'box': [1850.0, 803.0, 390.0, 134.0]},
            {'id': 'tvcatalog-btn-p3', 'class': 'button', 'box': [2360.0, 803.0, 130.0, 134.0]},
            {'id': 'tvcatalog-btn-pl1', 'class': 'button', 'box': [1420.0, 1045.0, 240.0, 100.0]},
            {'id': 'tvcatalog-btn-pl2', 'class': 'button', 'box': [1780.0, 1045.0, 360.0, 100.0]},
            {'id': 'tvcatalog-btn-pl3', 'class': 'button', 'box': [2260.0, 1045.0, 130.0, 100.0]},
            {'id': 'tvcatalog-btn-c1', 'class': 'cell', 'box': [1201.0, 1345.0, 823.0, 519.0]},
            {'id': 'tvcatalog-btn-c2', 'class': 'cell', 'box': [2126.0, 1350.0, 803.0, 604.0]}
        ]
    },
    'rc561-tvcatalog-description': {
        'image': 'reports/work/RC561/captures/tvcatalog-description.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'tvcatalog-desc-tab-bar', 'class': 'bar', 'box': [1100.0, 100.0, 1650.0, 140.0]},
            {'id': 'tvcatalog-desc-tab-stack', 'class': 'button', 'box': [1155.0, 128.0, 224.0, 75.0]},
            {'id': 'tvcatalog-desc-tab-buttons', 'class': 'button', 'box': [1529.0, 128.0, 268.0, 75.0]},
            {'id': 'tvcatalog-desc-tab-desc', 'class': 'button', 'box': [1936.0, 128.0, 358.0, 75.0]},
            {'id': 'tvcatalog-desc-tab-search', 'class': 'button', 'box': [2416.0, 128.0, 288.0, 75.0]},
            {'id': 'tvcatalog-desc-title', 'class': 'text', 'box': [156.0, 357.0, 257.0, 101.0]},
            {'id': 'tvcatalog-desc-signup-info', 'class': 'text', 'box': [156.0, 1479.0, 452.0, 56.0]},
            {'id': 'tvcatalog-desc-btn-signup', 'class': 'button', 'box': [158.0, 1570.0, 775.0, 145.0]},
            {'id': 'tvcatalog-desc-btn-rent', 'class': 'button', 'box': [158.0, 1728.0, 774.0, 141.0]},
            {'id': 'tvcatalog-desc-btn-next', 'class': 'button', 'box': [158.0, 1896.0, 767.0, 145.0]},
            {'id': 'tvcatalog-desc-btn-expand', 'class': 'button', 'box': [993.0, 1550.0, 1954.0, 250.0]},
            {'id': 'tvcatalog-desc-cred-starring', 'class': 'text', 'box': [3070.0, 1563.0, 649.0, 84.0]},
            {'id': 'tvcatalog-desc-cred-creators', 'class': 'text', 'box': [3074.0, 1658.0, 624.0, 60.0]},
            {'id': 'tvcatalog-desc-cred-rating', 'class': 'text', 'box': [3071.0, 1742.0, 698.0, 68.0]}
        ]
    },
    'rc561-tvcatalog-search': {
        'image': 'reports/work/RC561/captures/tvcatalog-search.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'tvcatalog-search-tab-bar', 'class': 'bar', 'box': [1100.0, 100.0, 1650.0, 140.0]},
            {'id': 'tvcatalog-search-tab-stack', 'class': 'button', 'box': [1155.0, 128.0, 224.0, 75.0]},
            {'id': 'tvcatalog-search-tab-buttons', 'class': 'button', 'box': [1529.0, 128.0, 268.0, 75.0]},
            {'id': 'tvcatalog-search-tab-desc', 'class': 'button', 'box': [1936.0, 128.0, 358.0, 75.0]},
            {'id': 'tvcatalog-search-tab-search', 'class': 'button', 'box': [2416.0, 128.0, 288.0, 75.0]},
            {'id': 'tvcatalog-search-field', 'class': 'textField', 'box': [206.0, 328.0, 559.0, 114.0]},
            # Visible result cards
            {'id': 'tvcatalog-search-card-beach', 'class': 'cell', 'box': [400.0, 1550.0, 350.0, 500.0]},
            {'id': 'tvcatalog-search-card-botanist', 'class': 'cell', 'box': [1250.0, 1550.0, 350.0, 500.0]},
            {'id': 'tvcatalog-search-card-camping', 'class': 'cell', 'box': [2100.0, 1550.0, 350.0, 500.0]},
            {'id': 'tvcatalog-search-card-coffeeberry', 'class': 'cell', 'box': [2950.0, 1550.0, 350.0, 500.0]}
        ]
    },
    'rc561-tvcatalog-sidebar': {
        'image': 'reports/work/RC561/captures/tvcatalog-sidebar.png',
        'dimensions': [3840, 2160],
        'objects': [
            {'id': 'tvcatalog-sidebar-bar', 'class': 'bar', 'box': [80.0, 80.0, 680.0, 2000.0]},
            {'id': 'tvcatalog-sb-search', 'class': 'cell', 'box': [107.0, 161.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-upnext', 'class': 'cell', 'box': [107.0, 321.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-moviestore', 'class': 'cell', 'box': [107.0, 480.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-tvstore', 'class': 'cell', 'box': [107.0, 640.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-browse', 'class': 'cell', 'box': [107.0, 798.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-library', 'class': 'cell', 'box': [107.0, 958.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-all', 'class': 'cell', 'box': [107.0, 1094.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-want', 'class': 'cell', 'box': [107.0, 1244.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-movies', 'class': 'cell', 'box': [107.0, 1400.0, 611.0, 115.0]},
            {'id': 'tvcatalog-sb-shows', 'class': 'cell', 'box': [107.0, 1557.0, 611.0, 115.0]}
        ]
    }
}

def main():
    manifest_cases = []
    total_controls = 0

    for case_id, data in GROUND_TRUTH.items():
        img_path = q.ROOT / data['image']
        img_sha = q.digest(img_path)
        label_file = LABELS_DIR / f"{case_id}.json"
        
        objs = []
        for obj in data['objects']:
            objs.append({
                'id': obj['id'],
                'class': obj['class'],
                'box': obj['box'],
                'visibility': 'visible',
                'source': 'independent_visual_ground_truth'
            })
        
        record = {
            'case_id': case_id,
            'image': data['image'],
            'imageSHA256': img_sha,
            'dimensions': data['dimensions'],
            'objects_count': len(objs),
            'objects': objs
        }
        
        with open(label_file, 'w') as f:
            json.dump(record, f, indent=2)
            
        print(f"Wrote {label_file.name}: {len(objs)} ground truth objects.")
        total_controls += len(objs)
        
        manifest_cases.append({
            'case_id': case_id,
            'image': data['image'],
            'sha256': img_sha,
            'label': str(label_file.relative_to(q.ROOT)),
            'controls_count': len(objs)
        })

    manifest = {
        'version': 'rc561-independent-ground-truth-v2',
        'date': '2026-11-03',
        'authority': 'Tasks.md:RA554-13,RC561-05',
        'method': 'independent visual inspection and source code layout verification (no model predictions)',
        'data_role': 'frozen-holdout-evaluation-only',
        'total_screens': len(manifest_cases),
        'total_ground_truth_controls': total_controls,
        'apps': [
            'org.jellyfin.swiftfin',
            'org.nuiak.rc561.strimr',
            'com.thatcube.Plozz',
            'com.example.apple-samplecode.TVCatalog'
        ],
        'cases': manifest_cases
    }

    manifest_file = HOLDOUT_DIR / 'manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nSaved updated manifest to {manifest_file}: {total_controls} total controls across {len(manifest_cases)} screens.")

if __name__ == '__main__':
    main()
