import unittest
from unittest.mock import patch
import numpy as np
import train_fullscreen_focus as runner
from reference_benchmark45 import prepare_environment


class AugmentationTests(unittest.TestCase):
    def test_closed_contract_preserves_defaults(self):
        self.assertEqual(runner.augmentation_options({'version':'fullscreen-focus-run-v2'}),{'translate':0.,'scale':0.})
        good=dict(version='fullscreen-focus-run-v2',augmentation=dict(version=1,translate=.05,scale=.2))
        self.assertEqual(runner.augmentation_options(good),dict(translate=.05,scale=.2))
        for v in [dict(version=1,translate=True,scale=0),dict(version=1,translate=.2,scale=0),
                  dict(version=1,translate=.05,scale=float('nan')),dict(version=1,translate=.05,scale=.2,flip=True)]:
            with self.assertRaises(ValueError):runner.augmentation_options(dict(good,augmentation=v))
        with self.assertRaises(ValueError):runner.augmentation_options(dict(good,version='fullscreen-focus-run-v1'))

    def labels(self,box):
        from ultralytics.utils.instance import Instances
        img=np.zeros((100,100,3),dtype=np.uint8)
        img[20:40,20:40]=255
        return dict(img=img,cls=np.array([[0]],dtype=np.float32),
            instances=Instances(np.array([box],dtype=np.float32),segments=np.zeros((0,1000,2),dtype=np.float32),bbox_format='xyxy',normalized=False))

    def test_actual_transform_moves_pixels_and_boxes(self):
        prepare_environment()
        from ultralytics.data.augment import RandomPerspective
        t=RandomPerspective(degrees=0,translate=.05,scale=0,shear=0,perspective=0)
        matrix=np.array([[1,0,5],[0,1,-5],[0,0,1]],dtype=np.float32)
        with patch.object(t,'_compute_affine_matrix',return_value=(matrix,1.)):
            result=t(self.labels([20,20,40,40]))
        np.testing.assert_allclose(result['instances'].bboxes,[[25,15,45,35]])
        self.assertEqual(int(result['img'][16,26,0]),255)

    def test_actual_transform_clips_and_removes_offscreen_boxes(self):
        prepare_environment()
        from ultralytics.data.augment import RandomPerspective
        t=RandomPerspective(degrees=0,translate=.05,scale=.2,shear=0,perspective=0)
        matrix=np.array([[1,0,10],[0,1,0],[0,0,1]],dtype=np.float32)
        with patch.object(t,'_compute_affine_matrix',return_value=(matrix,1.)):
            clipped=t(self.labels([80,20,98,40]));removed=t(self.labels([95,20,100,40]))
        np.testing.assert_allclose(clipped['instances'].bboxes,[[90,20,100,40]])
        self.assertEqual(len(removed['cls']),0)

    def test_actual_scale_about_center(self):
        prepare_environment()
        from ultralytics.data.augment import RandomPerspective
        t=RandomPerspective(degrees=0,translate=.05,scale=.2,shear=0,perspective=0)
        matrix=np.array([[1.2,0,-10],[0,1.2,-10],[0,0,1]],dtype=np.float32)
        with patch.object(t,'_compute_affine_matrix',return_value=(matrix,1.2)):
            result=t(self.labels([20,20,40,40]))
        np.testing.assert_allclose(result['instances'].bboxes,[[14,14,38,38]],atol=1e-5)


if __name__=='__main__':unittest.main()
