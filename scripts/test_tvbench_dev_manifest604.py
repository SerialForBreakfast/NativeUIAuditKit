"""Tests for RESET604 T1.2 TVBench v1 development manifest builder."""
import tempfile
import unittest
from PIL import Image
import framework_projection604 as projection
from pathlib import Path

import real_app_benchmark543 as r543
import research_queue as q
import tvbench_dev_manifest604 as tdm


class TVBenchDevManifestTests(unittest.TestCase):
    def test_normalize_label_preserves_flags_and_forces_incomplete(self):
        raw = dict(
            imageSHA256='abc123',
            complete=True,
            review=dict(blinded=True, reviewer='Joe', status='accepted'),
            objects=[
                dict(id='o1', **{'class': 'button'}, box=[10, 10, 20, 20], provenance='sdk-draft:b1', visibility='unknown'),
                dict(id='o2', **{'class': 'button'}, box=[40, 40, 20, 20], provenance='sdk-draft:b2', flag='not-control', visibility='unknown'),
                dict(id='o3', **{'class': 'label'}, box=[80, 80, 20, 20], provenance='sdk-draft:b3', flag='wrong-class', visibility='visible'),
                dict(id='o4', **{'class': 'cell'}, box=[120, 120, 20, 20], provenance='sdk-draft:b4', flag='wrong-box', visibility='visible'),
            ],
            focus=dict(state='no_focus', box=None),
        )
        norm = tdm.normalize_label(raw, 'abc123')
        self.assertFalse(norm['complete'])
        self.assertEqual(norm['review']['unresolvedCount'], 3)
        self.assertEqual(norm['review']['unflaggedUnknownPromotedCount'], 1)
        self.assertEqual(len(norm['objects']), 4)
        by_id = {o['id']: o for o in norm['objects']}
        self.assertEqual(by_id['o1']['class'], 'button')
        self.assertEqual(by_id['o1']['visibility'], 'visible')
        self.assertEqual(by_id['o1']['sourceVisibility'], 'unknown')
        self.assertEqual(by_id['o1']['provenance'], 'sdk-draft:b1')
        self.assertIsNone(by_id['o1']['sourceFlag'])
        self.assertIsNone(by_id['o2']['class'])
        self.assertEqual(by_id['o2']['sourceFlag'], 'not-control')
        self.assertIsNone(by_id['o3']['class'])
        self.assertEqual(by_id['o3']['sourceClass'], 'label')
        self.assertEqual(by_id['o3']['sourceFlag'], 'wrong-class')
        self.assertIsNone(by_id['o4']['class'])
        self.assertEqual(by_id['o4']['sourceFlag'], 'wrong-box')

    def test_ax_development_requires_review_and_freezes_separate_references(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build') as work:
            pack = Path(work)
            (pack / 'labels').mkdir()
            image = pack / 'qa.png'
            Image.new('RGB', (32, 32)).save(image)
            sha = q.digest(image)
            case = dict(id='qa', app='com.apple.TVSettings', flow='qa', width=32, height=32,
                        image=str(image), sha256=sha)
            doc = dict(version='tvbench-ax-review-v1', labelMode='contract', classes=projection.tvos_classes(),
                       focusStates=['focused', 'known_no_focus', 'unknown'], cases=[case])
            q.save(pack / 'cases.json', doc)
            dest = pack / 'snapshot'
            with self.assertRaisesRegex(ValueError, 'no_accepted'):
                tdm.freeze_ax_development(pack, dest)
            self.assertFalse(dest.exists())
            obj = dict(id='a', box=[1, 2, 10, 12], visibility='unknown', provenance='human',
                       **{'class': 'button'})
            label = dict(imageSHA256=sha, complete=True, review=dict(blinded=True, reviewer='test', status='accepted'),
                         objects=[obj, dict(obj, id='b', flag='not-control')],
                         focus=dict(state='known_no_focus', box=None))
            q.save(pack / 'labels/qa.json', label)
            out = q.load(tdm.freeze_ax_development(pack, dest, {'qa': 'qa-layout'}))
            c = out['cases'][0]
            frozen = q.load(q.ROOT / c['labels']['path'])
            self.assertEqual(c['independentLayoutId'], 'qa-layout')
            self.assertEqual(c['labels']['sha256'], q.digest(q.ROOT / c['labels']['path']))
            self.assertEqual([o['id'] for o in frozen['objects']], ['a'])
            self.assertEqual(frozen['focus']['state'], 'known_no_focus')
            self.assertFalse(out['trainingEligible'])
            self.assertFalse(out['sealed'])
            case['app'] = 'com.jordankoch.NewsTV'
            q.save(pack / 'cases.json', doc, replace=True)
            with self.assertRaisesRegex(ValueError, 'case_or_app'):
                tdm.freeze_ax_development(pack, pack / 'other')
            # Joe added the media benchmark apps on 2026-11-25.
            case['app'] = 'org.jellyfin.swiftfin'
            q.save(pack / 'cases.json', doc, replace=True)
            media = q.load(tdm.freeze_ax_development(pack, pack / 'media', {'qa': 'qa-layout'}))
            self.assertEqual(media['cases'][0]['app'], 'org.jellyfin.swiftfin')

    def test_v2_dev_manifest_validates_with_zero_duplicates(self):
        m = q.load(q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest-v2.json')
        self.assertEqual(m['split'], 'development')
        self.assertFalse(m['sealed'])
        self.assertFalse(m['trainingEligible'])
        self.assertEqual(len(m['cases']), 42)
        shas = [c['image']['sha256'] for c in m['cases']]
        self.assertEqual(len(shas), len(set(shas)))
        for c in m['cases']:
            lbl = q.load(q.ROOT / c['labels']['path'])
            r543.validate_labels(lbl, c, m['classes'])
            self.assertEqual(c['labels']['sha256'], q.digest(q.ROOT / c['labels']['path']))


if __name__ == '__main__':
    unittest.main()
