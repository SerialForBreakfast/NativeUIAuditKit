import copy
import unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
import diagnostic174 as d


class DiagnosticTests(unittest.TestCase):
    def sample(self):
        rows=[dict(id=str(i),split='train',image={'sha256':str(i)},group=str(i)) for i in range(264)]
        return {'rows':copy.deepcopy(rows)}, {'newTrainingRows':rows}

    def test_membership_exact_and_deterministic(self):
        m,a=self.sample();one=d.select_rows(m,a);m['rows'].reverse()
        self.assertEqual(one,d.select_rows(m,a));self.assertEqual(len(one),264)

    def test_reject_wrong_role_changed_bytes_duplicates_missing(self):
        for kind in ('role','bytes','duplicate','missing'):
            m,a=self.sample()
            if kind=='role':m['rows'][0]['split']='test'
            elif kind=='bytes':m['rows'][0]['image']['sha256']='changed'
            elif kind=='duplicate':m['rows'].append(m['rows'][0])
            else:m['rows'].pop()
            with self.subTest(kind=kind),self.assertRaises(Exception):d.select_rows(m,a)

    def test_prepare_collision_before_ready(self):
        with patch.object(d,'OUT',d.h.ROOT),patch.object(d.p,'ready') as ready:
            with self.assertRaisesRegex(Exception,'output_collision'):d.prepare()
            ready.assert_not_called()

    def test_infer_routes_both_arms_and_records_only_success(self):
        doc={'checkpoints':{'017':{},'019':{}}}
        with patch.object(d,'inputs',return_value=doc),patch.object(Path,'exists',return_value=False),patch.object(d.h,'checked',return_value=Path('weight')) as checked,patch.object(d.e,'export_predictions') as export,patch.object(d.h,'ref',return_value={}),patch.object(d.h,'write') as write:
            d.infer();self.assertEqual(export.call_count,2);self.assertEqual(write.call_count,2)
            self.assertTrue(all(c.kwargs['discard_degenerate'] for c in export.call_args_list))
            self.assertTrue(all(c.args[2]==256*1024**2 for c in checked.call_args_list))
        with patch.object(d,'inputs',return_value=doc),patch.object(Path,'exists',return_value=False),patch.object(d.h,'checked',return_value=Path('weight')),patch.object(d.e,'export_predictions',side_effect=ValueError('corrupt PNG')),patch.object(d.h,'write') as write:
            with self.assertRaisesRegex(ValueError,'corrupt'):d.infer()
            write.assert_not_called()

    def test_pages_dispositions_and_resized_dimensions(self):
        image=MagicMock(image_id='a',width=1280,height=640)
        request=MagicMock(images=[image]);meta={'a':{'placement':'leading'}}
        for det,expected in [([], 'absent'),([{'classID':1,'score':.2,'xyxyPixels':[0,0,20,10]}],'low-confidence-match')]:
            with patch.object(d.prior,'truth',return_value=[[0,0,20,10]]):
                rows=d.pages(request,{'results':[{'imageID':'a','detections':det}]},1,meta)
            self.assertEqual(rows[0]['disposition'],expected);self.assertEqual(rows[0]['resizedHeight'],5)
        with self.assertRaisesRegex(Exception,'case_membership'):d.pages(request,{'results':[]},1,meta)

    def test_changed_protocol_settings_rejected_before_hash_reads(self):
        with patch.object(d.p,'sealed',return_value={'settings':{}}),patch.object(d.h,'checked') as checked:
            with self.assertRaisesRegex(Exception,'settings_changed'):d.inputs()
            checked.assert_not_called()


if __name__=='__main__':unittest.main()
