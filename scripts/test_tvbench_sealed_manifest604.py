"""Tests for exposure-separated sealed vs development-regression manifests (`tvbench_sealed_manifest604.py`)."""
import tempfile
import unittest
from pathlib import Path
from PIL import Image

import real_app_review554 as rev554
import research_queue as q
import tvbench_sealed_manifest604 as sm


class TVBenchSealedManifestTests(unittest.TestCase):
    def test_separates_previously_inspected_from_uninspected_sealed(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build') as td:
            root = Path(td)
            rev_dir = root / 'review-sealed-v2'
            out_dir = root / 'out'
            (rev_dir / 'labels').mkdir(parents=True)
            (rev_dir / 'drafts').mkdir(parents=True)
            out_dir.mkdir(parents=True)

            img1 = root / 'a.png'
            img2 = root / 'b.png'
            img3 = root / 'c.png'
            Image.new('RGB', (120, 80), (10, 20, 30)).save(img1)
            Image.new('RGB', (120, 80), (40, 50, 60)).save(img2)
            Image.new('RGB', (120, 80), (70, 80, 90)).save(img3)
            sha1, sha2, sha3 = q.digest(img1), q.digest(img2), q.digest(img3)

            q.save(rev_dir / 'cases.json', dict(
                version='realapp554-review-v1',
                classes=rev554.CLASSES,
                cases=[
                    dict(id='reg1', app='office.kanopy', flow='f1', exposure='previously-inspected-development',
                         image=str(img1), sha256=sha1, width=120, height=80),
                    dict(id='seal1', app='com.example.TVCatalog', flow='f2', exposure='uninspected-candidate',
                         image=str(img2), sha256=sha2, width=120, height=80),
                    dict(id='pend1', app='com.apple.TVSettings', flow='f3', exposure='uninspected-candidate',
                         image=str(img3), sha256=sha3, width=120, height=80),
                ],
            ))
            for cid, sha in (('reg1', sha1), ('seal1', sha2)):
                q.save(rev_dir / f'labels/{cid}.json', {
                    'imageSHA256': sha,
                    'complete': True,
                    'objects': [
                        {'id': 'o1', 'class': 'secondaryButton', 'box': [10, 10, 30, 15], 'visibility': 'visible', 'provenance': 'reviewer:missing', 'flag': 'missing'},
                    ],
                    'focus': {'state': 'focused', 'box': [10, 10, 30, 15]},
                    'review': {'blinded': True, 'reviewer': 'Joe', 'status': 'accepted'},
                })
            q.save(rev_dir / 'drafts/pend1.json', {
                'imageSHA256': sha3,
                'complete': False,
                'objects': [],
                'focus': {'state': 'unknown', 'box': None},
                'review': {'blinded': True, 'reviewer': '', 'status': 'pending'},
            })

            res = sm.build_sealed_manifest(review_dir=rev_dir, out_dir=out_dir, version_tag='v2')
            self.assertEqual(res['sealedSummary']['acceptedFrames'], 1)
            self.assertEqual(res['regressionSummary']['acceptedFrames'], 1)
            sealed = q.load(out_dir / 'sealed-manifest-v2.json')
            reg = q.load(out_dir / 'dev-regression-manifest-v2.json')
            self.assertTrue(sealed['sealed'])
            self.assertEqual(sealed['split'], 'sealed-test')
            self.assertEqual([c['id'] for c in sealed['cases']], ['seal1'])
            self.assertFalse(reg['sealed'])
            self.assertEqual(reg['split'], 'development-regression')
            self.assertEqual([c['id'] for c in reg['cases']], ['reg1'])


if __name__ == '__main__':
    unittest.main()
