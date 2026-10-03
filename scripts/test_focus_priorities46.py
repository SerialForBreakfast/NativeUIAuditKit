import unittest
import numpy as np
from focus_priorities46 import choose_native, square_content, place, measure, summarize
from focus_alignment46 import aligned


class PriorityTests(unittest.TestCase):
    def test_stride_aligned_controls_preserve_phase_and_pixels(self):
        content=np.zeros((360,640,3),dtype=np.uint8);content[:,:,1]=73
        for delta,y in [(-128,12),(128,268)]:
            canvas,controls,offset=aligned(content,(1,1),[dict(id='a',state='focused',bounds=[20,40,50,60])],delta)
            self.assertEqual(offset,y);self.assertEqual(offset%32,140%32)
            np.testing.assert_array_equal(canvas[y:y+360],content)
            self.assertEqual(controls[0]['bounds'],[20,40+y,50,60])
        with self.assertRaisesRegex(ValueError,'aligned_offset'):aligned(content,(1,1),[],140)

    def test_identical_pixels_at_every_position_and_exact_bounds(self):
        content=np.arange(6*12*3,dtype=np.uint8).reshape(6,12,3)
        controls=[dict(id='a',state='focused',bounds=[2,1,4,3])]
        for position,y in [('top',0),('center',3),('bottom',6)]:
            canvas,moved,offset=place(content,(2,2),controls,position,12)
            np.testing.assert_array_equal(canvas[y:y+6],content)
            self.assertEqual(offset,y);self.assertEqual(moved[0]['bounds'],[4,2+y,8,6])
            self.assertEqual(controls[0]['bounds'],[2,1,4,3])

    def test_resize_scales_and_orientation(self):
        image=np.zeros((20,40,3),dtype=np.uint8);image[:10,:,0]=255
        content,scales=square_content(image,80)
        self.assertEqual(content.shape,(40,80,3));self.assertEqual(scales,(2,2))
        self.assertGreater(content[0,0,0],content[-1,0,0])
        with self.assertRaisesRegex(ValueError,'landscape'):square_content(image.transpose(1,0,2),80)

    def test_sample_balances_labels_without_reading_predictions(self):
        frames=[];annotations={}
        for slot in range(3):
            for index in range(3):
                key=f'{slot}-{index}'
                frames.append(dict(id=key,split='evaluation',image={'sha256':key}))
                annotations[key]={'controls':[dict(id=f'item-{slot}',state='focused')]}
        sample=choose_native(list(reversed(frames)),annotations,2)
        self.assertEqual([f['id'] for f in sample],['0-0','0-1','1-0','1-1','2-0','2-1'])
        with self.assertRaisesRegex(ValueError,'slot_support'):choose_native(frames,annotations,4)

    def test_fixed_geometry_and_threshold(self):
        controls=[dict(id='a',bounds=[0,0,10,10],state='focused'),dict(id='b',bounds=[20,0,10,10],state='unfocused')]
        r=measure({},controls,[dict(box=[0,0,10,10],score=.2),dict(box=[20,0,30,10],score=.5)])
        self.assertFalse(r['localized']['0.5']);self.assertEqual(r['bestFocusScore'],.2)
        self.assertTrue(r['unfocusedOutranksFocus']);self.assertEqual(r['selection'],'known_unfocused')
        rows=[dict(family='native26',focusSlot='a',arm='one-top',measure=r,seconds=1)]
        groups=summarize(rows)
        self.assertEqual(len(groups),2);self.assertEqual(groups[0]['candidateLocalized001'],1)


if __name__=='__main__':unittest.main()
