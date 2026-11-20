"""Tests for deterministic non-model Vision geometry draft proposer (`vision_geometry_drafts604.py`)."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

import real_app_benchmark543 as r543
import real_app_review554 as rev554
import research_queue as q
import vision_geometry_drafts604 as vg


class VisionGeometryDraftsTests(unittest.TestCase):
    def test_propose_for_frame_and_validate_labels_compatibility(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build') as td:
            root = Path(td)
            img_path = root / 'frame.png'
            im = Image.new('RGB', (1920, 1080), (18, 22, 30))
            draw = ImageDraw.Draw(im)
            # Dark unfocused button pill and bright focused button pill
            draw.rounded_rectangle([120, 120, 420, 190], radius=18, fill=(45, 52, 68))
            draw.rounded_rectangle([480, 120, 780, 190], radius=18, fill=(242, 245, 250), outline=(255, 255, 255), width=6)
            im.save(img_path)

            probe = {
                'path': str(img_path),
                'width': 1920,
                'height': 1080,
                'rects': [
                    {'xyxy': [120.0, 120.0, 420.0, 190.0], 'confidence': 0.9},
                    {'xyxy': [480.0, 120.0, 780.0, 190.0], 'confidence': 0.95},
                ],
                'texts': [
                    {'text': 'Browse', 'xyxy': [170.0, 140.0, 350.0, 170.0], 'confidence': 0.98},
                    {'text': 'Featured', 'xyxy': [530.0, 140.0, 720.0, 170.0], 'confidence': 0.98},
                ],
            }
            res = vg.propose_for_frame(img_path, probe, app='com.example.apple-samplecode.TVCatalog')
            self.assertEqual(len(res['objects']), 2)
            self.assertEqual(res['focusCandidates'][0]['box'], [480.0, 120.0, 300.0, 70.0])

            sha = hashlib.sha256(img_path.read_bytes()).hexdigest()
            label_doc = {
                'imageSHA256': sha,
                'complete': True,
                'objects': res['objects'],
                'focus': {'state': 'focused', 'box': res['focusCandidates'][0]['box']},
                'review': {'blinded': True, 'reviewer': 'Joe', 'status': 'accepted'},
            }
            case_meta = {
                'id': 'c1',
                'image': {'sha256': sha},
                'sha256': sha,
                'width': 1920,
                'height': 1080,
            }
            rev554.check(label_doc, case_meta)
            r543.validate_labels(label_doc, case_meta, rev554.CLASSES)


if __name__ == '__main__':
    unittest.main()
