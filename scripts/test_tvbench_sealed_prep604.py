"""Tests for TVBench sealed review-pack prep (`tvbench_sealed_prep604.py`)."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageDraw

import tvbench_sealed_prep604 as sp


def _make_png(path, color, box=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (192, 108), color)
    if box is not None:
        draw = ImageDraw.Draw(img)
        draw.rectangle(box, fill=(240, 240, 240))
    img.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TVBenchSealedPrepTests(unittest.TestCase):
    def test_app_split_and_office_dedupe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sp_orig_root = sp.q.ROOT
            try:
                sp.q.ROOT = root
                # Existing dev manifest already owns Swiftfin frame dev-001
                dev_img = root / 'dev/sf0.png'
                dev_sha = _make_png(dev_img, (10, 10, 10))
                dev_manifest = root / 'dev-manifest.json'
                dev_manifest.write_text(json.dumps({
                    'apps': [{'id': 'org.jellyfin.swiftfin', 'split': 'dev', 'sealed': False}],
                    'cases': [{'id': 'dev-001', 'app': 'org.jellyfin.swiftfin', 'image': {'sha256': dev_sha}}],
                }))

                # Office dir: 2 nearly identical settled frames, 1 clearly different standalone, 1 unsettled quarantine
                office_dir = root / 'office'
                f0 = office_dir / 'images/f0.png'
                f1 = office_dir / 'images/f1.png'
                f2 = office_dir / 'images/f2.png'
                f3_bad = office_dir / 'images/f3_bad.png'
                s0 = _make_png(f0, (20, 20, 20))
                s1 = _make_png(f1, (21, 21, 21))
                s2 = _make_png(f2, (20, 20, 20), box=(20, 20, 160, 90))
                s3 = _make_png(f3_bad, (200, 10, 10))
                (office_dir / 'capture-events.jsonl').write_text('\n'.join(json.dumps(x) for x in [
                    {'payload_sha256': s0, 'role': 'postInputSettled', 'event_id': 'ev0', 'case_id': 'c0', 'capture_sequence': 2},
                    {'payload_sha256': s1, 'role': 'postInputSettled', 'event_id': 'ev1', 'case_id': 'c0', 'capture_sequence': 3},
                    {'payload_sha256': s2, 'role': 'standalone', 'event_id': 'ev2', 'case_id': 'c0', 'capture_sequence': 4},
                    {'payload_sha256': s3, 'role': 'postInputUnverified', 'event_id': 'ev3', 'case_id': 'c0', 'capture_sequence': 5},
                ]) + '\n')
                (office_dir / 'pilot-press-index.tsv').write_text('\n'.join([
                    'Press\tCommand\tOutcome\tAfter frame status\tFrame ID\tRecorded SHA256',
                    f'1\tright\tcompleted\tpostInputSettled\tev0\t{s0}',
                    f'2\tdown\tcompleted\tpostInputSettled\tev1\t{s1}',
                ]) + '\n')

                # RC561 holdout: 1 swiftfin (goes to dev-extra) + 1 strimr (goes to sealed)
                sf_extra = root / 'rc561/sf1.png'
                sf_extra_sha = _make_png(sf_extra, (50, 50, 50))
                strimr = root / 'rc561/strimr.png'
                strimr_sha = _make_png(strimr, (90, 90, 90))
                rc561_manifest = root / 'rc561.json'
                rc561_manifest.write_text(json.dumps({
                    'cases': [
                        {'case_id': 'rc561-swiftfin-screen-01', 'image': 'rc561/sf1.png', 'sha256': sf_extra_sha},
                        {'case_id': 'rc561-strimr-screen-01', 'image': 'rc561/strimr.png', 'sha256': strimr_sha},
                    ]
                }))

                # Extra swiftfin-2 folder (1 already in dev, 1 genuinely new)
                sf2_dup = root / 'sf2/dup.png'
                _make_png(sf2_dup, (10, 10, 10))
                sf2_new = root / 'sf2/new.png'
                _make_png(sf2_new, (130, 30, 30))

                # Sealed system capture manifest (1 TVSettings screen)
                sys_img = root / 'sealed-captures/tvos-system/s0.png'
                sys_sha = _make_png(sys_img, (180, 180, 180))
                sc_manifest = root / 'sealed-captures/manifest.json'
                sc_manifest.parent.mkdir(parents=True, exist_ok=True)
                sc_manifest.write_text(json.dumps({
                    'cases': [{
                        'id': 'tvos-system-000',
                        'app': 'com.apple.TVSettings',
                        'flow': 'settings-root',
                        'image': 'sealed-captures/tvos-system/s0.png',
                        'sha256': sys_sha,
                    }]
                }))

                out = root / 'tvbench-v1'
                plan = sp.build_packs(
                    out_dir=out,
                    dev_manifest_path=dev_manifest,
                    office_dir=office_dir,
                    rc561_holdout_path=rc561_manifest,
                    sealed_captures_path=sc_manifest,
                    swiftfin_extra_dir=root / 'sf2',
                    diff_threshold=2.0,
                    version_tag='v2',
                )
                self.assertEqual(plan['officeCleanRawCount'], 3)
                self.assertEqual(plan['officeDedupedCount'], 2)
                self.assertEqual(plan['officeQuarantinedCount'], 1)
                self.assertEqual(plan['freshSealedUninspectedCount'], 1)
                self.assertEqual(plan['previouslyInspectedQueuedCount'], 3)
                self.assertEqual(plan['sealedQueuedTotal'], 4)  # 2 office + 1 strimr + 1 system
                self.assertEqual(plan['devExtraQueuedCount'], 2)  # 1 rc561 swiftfin + 1 sf2 new
                self.assertNotIn('org.jellyfin.swiftfin', plan['sealedByApp'])

                sealed_cases = json.loads((out / 'review-sealed-v2/cases.json').read_text())
                self.assertEqual(len(sealed_cases['cases']), 4)
                by_id = {c['id']: c for c in sealed_cases['cases']}
                self.assertEqual(by_id['tvos-system-000']['exposure'], 'uninspected-candidate')
                self.assertEqual(by_id['rc561-strimr-screen-01']['exposure'], 'previously-inspected-development')
                self.assertEqual(by_id['office603-000']['command'], 'right')
                first_draft = json.loads((out / f"review-sealed-v2/drafts/{sealed_cases['cases'][0]['id']}.json").read_text())
                self.assertEqual(first_draft['objects'], [])
                self.assertTrue(first_draft['review']['blinded'])
                self.assertEqual(first_draft['review']['status'], 'pending')
            finally:
                sp.q.ROOT = sp_orig_root


if __name__ == '__main__':
    unittest.main()
