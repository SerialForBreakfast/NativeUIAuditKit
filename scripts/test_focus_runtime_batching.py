import base64
import io
import unittest
from unittest.mock import patch
from PIL import Image
import focus_runtime as r
from focus_dataset_contract import FocusDataError


class PixelBatchTests(unittest.TestCase):
    def test_area_and_item_limits_order(self):
        items=[{'id':str(i),'path':'test-only'} for i in range(19)]
        with patch('PIL.Image.open') as opened:
            im=opened.return_value.__enter__.return_value
            im.width,im.height=3840,2160
            batches=list(r.bounded_batches(items))
            self.assertEqual([len(b) for b in batches],[9,9,1])
            self.assertEqual(sum(batches,[]),items)
            im.width,im.height=256,256
            self.assertEqual([len(b) for b in r.bounded_batches(items)],[16,3])
            im.width,im.height=10000,8001
            with self.assertRaisesRegex(FocusDataError,'runtime_pixel_limit'):
                list(r.bounded_batches(items))

    def test_real_render_and_infer_entrypoints_use_batches(self):
        items=[{'id':str(i),'path':'test-only'} for i in range(19)]
        png=io.BytesIO(); Image.new('RGB',(256,256)).save(png,format='PNG')
        encoded=base64.b64encode(png.getvalue()).decode()
        actual_open=Image.open
        def opened(path):
            if path=='test-only': return Image.new('RGB',(3840,2160))
            return actual_open(path)
        def reply(batch,*args):
            self.assertLessEqual(len(batch),9)
            return {'results':[{'id':x['id'],'png':encoded,'probability':.5} for x in batch]}
        with patch.object(r,'items_for',return_value=items), patch('PIL.Image.open',side_effect=opened), \
             patch.object(r,'invoke',side_effect=reply), patch.object(r,'identity',return_value={}), \
             patch('focus_ring_baseline.artifact_digest',return_value='hash'):
            self.assertEqual([x[0] for x in r.rendered_items({})],[i['id'] for i in items])
            result=r.infer({'runtimeCrop':{}},'test',{'artifact':{'sha256':'hash'},'protocolSHA256':'test'})
            self.assertEqual(list(result['scores']),[i['id'] for i in items])

if __name__=='__main__': unittest.main()
