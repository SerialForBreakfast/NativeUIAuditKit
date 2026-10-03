import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from PIL import Image
import page_regeneration41 as p


class PageRepairTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(dir=p.h.ROOT/'.build/debug-output',prefix='page-qa-'))
        self.image=self.root/'img_000001.png';Image.new('RGB',(200,100),'black').save(self.image)
        self.ann=self.image.with_suffix('.json')
        self.recipe=dict(seed=1,family='ProgressActivity',width=200,height=100,scale=2)
        self.data=dict(imageSHA256=p.h.sha(self.image),generatorProfile=dict(seed=1,templateFamily='ProgressActivity'),
            image=dict(pixelWidth=200,pixelHeight=100,scale=2),elements=[dict(id='pageControl_0',elementType='pageControl',
                boundsPoints=dict(x=20,y=10,width=25,height=10),boundsPixels=dict(x=40,y=20,width=50,height=20),
                boundsVisionNormalized=dict(x=.2,y=.6,width=.25,height=.2))])

    def tearDown(self):shutil.rmtree(self.root)
    def check(self):
        self.ann.write_text(json.dumps(self.data));return p.checked_annotation(self.recipe,self.image,self.ann)
    def test_valid_render(self):self.assertEqual(self.check()[1]['width'],25)
    def test_old_whole_row_box_rejected(self):
        self.data['elements'][0]['boundsPoints']['width']=100
        with self.assertRaisesRegex(ValueError,'not_intrinsic'):self.check()
    def test_wrong_normalized_coordinates(self):
        self.data['elements'][0]['boundsVisionNormalized']['y']=.2
        with self.assertRaisesRegex(ValueError,'conversion_mismatch'):self.check()
    def test_duplicate_ids(self):
        self.data['elements'].append(copy.deepcopy(self.data['elements'][0]))
        with self.assertRaisesRegex(ValueError,'page_dot_missing'):self.check()
    def test_identity_changed(self):
        self.data['generatorProfile']['seed']=2
        with self.assertRaisesRegex(ValueError,'regenerated_identity'):self.check()
    def test_offscreen_dots(self):
        self.data['elements'][0]['boundsPoints']['x']=99
        with self.assertRaisesRegex(ValueError,'outside_image'):self.check()

    def test_export_truncated_membership(self):
        rows=[dict(id=str(i)) for i in range(666)]
        with self.assertRaisesRegex(ValueError,'membership_count'):
            list(p.checked_export_rows(rows,rows[:-1]))

    def test_export_reordered_membership(self):
        rows=[dict(id=str(i)) for i in range(666)]
        with self.assertRaisesRegex(ValueError,'recipe_order'):
            list(p.checked_export_rows(rows,list(reversed(rows))))

    def test_export_preserves_all_labels(self):
        categories={'pageControl':1,'label':2}
        self.data['elements'].append({**copy.deepcopy(self.data['elements'][0]),'elementType':'label'})
        text='1 0.325000 0.300000 0.250000 0.200000\n2 0.325000 0.300000 0.250000 0.200000\n'
        p.checked_export_labels(self.data,text,categories)
        with self.assertRaisesRegex(ValueError,'labels_mismatch'):
            p.checked_export_labels(self.data,text.splitlines()[0]+'\n',categories)

    def test_export_changed_class_rejected(self):
        with self.assertRaisesRegex(ValueError,'labels_mismatch'):
            p.checked_export_labels(self.data,'2 0.325000 0.300000 0.250000 0.200000\n',{'pageControl':1})


if __name__=='__main__':unittest.main()
