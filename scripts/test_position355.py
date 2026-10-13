import unittest
import numpy as np
from PIL import Image
from position355 import translate,positions,key
import position355 as p
from unittest.mock import patch
from pathlib import Path


class Tests(unittest.TestCase):
    def images(self):
        a=Image.new('RGB',(12,10),(20,20,25));a.paste((200,0,0),(2,2,4,4))
        b=a.copy();b.paste((0,200,0),(2,2,4,4))
        return [a,b]

    def test_corners_preserve_pixel_changes(self):
        for cell in range(9):
            original=self.images();out,(dx,dy)=translate(original,[[2,2,2,2]],cell)
            self.assertEqual(int(np.any(np.asarray(out[0])!=np.asarray(out[1]),axis=2).sum()),4)
            self.assertEqual(out[0].getpixel((2+dx,2+dy)),(200,0,0))
            self.assertEqual(original[0].getpixel((2,2)),(200,0,0))

    def test_rejects_unmodeled_context(self):
        images=self.images();images[0].putpixel((9,9),(255,255,255))
        with self.assertRaisesRegex(ValueError,'nonuniform_context'):translate(images,[[2,2,2,2]],0)

    def test_rejects_clipping(self):
        with self.assertRaisesRegex(ValueError,'patch_bounds'):translate(self.images(),[[10,8,4,4]],0)

    def test_no_change_stays_identical(self):
        a=self.images()[0];out,_=translate([a,a],[[2,2,2,2]],8)
        self.assertTrue(np.array_equal(out[0],out[1]))

    def test_position_has_no_label_or_order_dependency(self):
        row=dict(group='g',sizePixels=3,widthPixels=1,contrast=.25,separationPixels=32,corner=0,patchBounds=[])
        other=dict(row,changed=1,reverse=True)
        self.assertEqual(key(row),key(other));self.assertEqual(positions([row,other]),positions([other,row]))

    def report(self,count,lost=0):
        rows=[dict(job=f'focus355-position-case{i}-movement',counts=dict(lost=lost if i==0 else 0,gained=1)) for i in range(count)]
        dep=dict(job='chunk',result=dict(path='result',sha256='x'),outputs=[dict(path='summary',sha256='x')])
        def load(path):return [dep] if path.name=='dependencies.json' else {'summaryRows':rows}
        with patch.object(p,'OUT',Path('.build')),patch.object(p.q,'load',side_effect=load),\
                patch.object(p.q,'digest',return_value='x'),patch.object(p.q,'save') as save:
            p.collect();return save.call_args.args[1]

    def test_incomplete_comparisons_cannot_pass(self):
        self.assertFalse(self.report(23)['decisions']['position']['passesDevelopmentRule'])

    def test_lost_success_rejects_candidate(self):
        result=self.report(24,1)
        self.assertFalse(result['decisions']['position']['passesDevelopmentRule'])
        self.assertFalse(result['modelAccepted'])

    def test_development_pass_does_not_promote(self):
        result=self.report(24)
        self.assertTrue(result['decisions']['position']['passesDevelopmentRule'])
        self.assertFalse(result['modelAccepted'])
