"""Tests for RESET604 T4.2 Arm B comparative focus selector."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import comparative_focus604 as cf
import research_queue as q


class ComparativeFocus604Tests(unittest.TestCase):
    def test_synthetic_bright_ring_separates_focused_from_no_focus(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='armb-test-') as tmp:
            root = Path(tmp)
            screens = []
            for idx in range(12):
                im = Image.new('RGB', (320, 180), (30, 30, 35))
                draw = ImageDraw.Draw(im)
                boxes = [[20, 40, 80, 60], [120, 40, 80, 60], [220, 40, 80, 60]]
                for b in boxes:
                    draw.rectangle([b[0], b[1], b[0] + b[2], b[1] + b[3]], fill=(70, 75, 85))
                gt_idx = idx % 3
                is_nf = idx >= 9
                if not is_nf:
                    fb = boxes[gt_idx]
                    draw.rectangle([fb[0] - 3, fb[1] - 3, fb[0] + fb[2] + 3, fb[1] + fb[3] + 3], outline=(250, 250, 255), width=4)
                raw = cf.extract_candidate_raw_features(np.asarray(im), boxes)
                comp = cf.build_comparative_features(raw)
                screens.append(dict(
                    id=f's{idx}', role='train', sourceRole='test',
                    focusState='no_focus' if is_nf else 'focused',
                    gtIndex=-1 if is_nf else gt_idx,
                    features=comp,
                ))
            bundle = cf.fit_comparative_selector(screens, epochs=25, lr=0.05)
            # Verify prediction on fresh focused + no_focus synthetic frame
            p_im = Image.new('RGB', (320, 180), (30, 30, 35))
            d = ImageDraw.Draw(p_im)
            boxes = [[20, 40, 80, 60], [120, 40, 80, 60], [220, 40, 80, 60]]
            for b in boxes:
                d.rectangle([b[0], b[1], b[0] + b[2], b[1] + b[3]], fill=(70, 75, 85))
            foc_path = root / 'foc.png'
            nf_path = root / 'nf.png'
            p_im.save(nf_path)
            fb = boxes[1]
            d.rectangle([fb[0] - 3, fb[1] - 3, fb[0] + fb[2] + 3, fb[1] + fb[3] + 3], outline=(250, 250, 255), width=4)
            p_im.save(foc_path)

            cases = [
                dict(id='foc', status='captured', image=dict(path=str(foc_path.relative_to(q.ROOT)), sha256=q.digest(foc_path))),
                dict(id='nf', status='captured', image=dict(path=str(nf_path.relative_to(q.ROOT)), sha256=q.digest(nf_path))),
            ]
            dets = {
                'foc': [dict(cls='cell', box=b, score=0.9) for b in boxes],
                'nf': [dict(cls='cell', box=b, score=0.9) for b in boxes],
            }
            preds = cf.predict_comparative_on_detections(bundle, cases, dets, class_names=['cell'], use_gate=True)
            self.assertEqual(preds['foc']['focusBox'], boxes[1])
            self.assertIsNone(preds['nf']['focusBox'])

            coreml_paths = cf.export_comparative_coreml(bundle, out_dir=root / 'coreml')
            preds_ml = cf.predict_comparative_on_detections(
                bundle, cases, dets, class_names=['cell'], use_gate=True, coreml_paths=coreml_paths,
            )
            self.assertEqual(preds_ml['foc']['focusBox'], boxes[1])
            self.assertIsNone(preds_ml['nf']['focusBox'])
            for k in ('foc', 'nf'):
                self.assertAlmostEqual(
                    preds['foc']['focusExecution']['hasFocusGateProb'],
                    preds_ml['foc']['focusExecution']['hasFocusGateProb'],
                    places=3,
                )


if __name__ == '__main__':
    unittest.main()
