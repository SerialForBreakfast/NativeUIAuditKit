"""Check paired scene scaling and preserved roles."""
import unittest
import numpy as np
from PIL import Image
import scale311 as s


class ScaleTests(unittest.TestCase):
    def test_same_transform_and_reversal(self):
        a=Image.new('RGB',(100,80),'red');b=Image.new('RGB',(100,80),'blue')
        result,ratios=s.scale_pair([a,b],.3)
        reverse,_=s.scale_pair([b,a],.3)
        self.assertEqual(ratios,(.3,.3))
        self.assertEqual(result[0].tobytes(),reverse[1].tobytes())
        self.assertEqual(result[0].getpixel((0,0)),(0,0,0))
        self.assertEqual(result[0].getpixel((50,40)),(255,0,0))

    def test_identity_and_invalid_factors(self):
        a=Image.new('RGB',(100,80),'red');out,_=s.scale_pair([a,a],1)
        self.assertEqual(out[0].tobytes(),a.tobytes())
        self.assertEqual(out[0].tobytes(),out[1].tobytes())
        for factor in (0,-1,1.1,float('nan')):
            with self.assertRaises(ValueError):s.scale_pair([a,a],factor)

    def test_assignment_ignores_labels_and_order(self):
        row=dict(role='train',changed=0,images=[dict(sha256='a'),dict(sha256='b')])
        original=s.target(row);row['changed']=1;row['images'].reverse()
        self.assertEqual(original,s.target(row))
        row['role']='reserved'
        with self.assertRaises(ValueError):s.target(row)

    def test_identical_detail_stays_identical(self):
        a=Image.new('RGB',(384,216),'red');images,_=s.scale_pair([a,a],.2)
        value=s.s.encoded(*images,(192,128))[0]
        result=s.detail(value,images)
        self.assertTrue(np.array_equal(result[:3],result[3:]))

    def test_protected_groups_fail_before_image_reads(self):
        values=np.zeros((1,6,128,192),dtype=np.float32)
        for role,group in [('reserved','other'),('train','protected')]:
            with self.assertRaisesRegex(ValueError,'protected_group'):
                s.prepare_training(values,[dict(role=role,group=group)],np.ones(1),
                                   dict(groups={'protected'},frames=set()))

    def test_different_frame_sizes_fail(self):
        with self.assertRaisesRegex(ValueError,'scale_inputs'):
            s.scale_pair([Image.new('RGB',(100,80)),Image.new('RGB',(80,100))],.5)


if __name__=='__main__':unittest.main()
