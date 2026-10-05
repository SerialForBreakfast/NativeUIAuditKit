"""Exercise resident augmentation pixels and labels, not an alternate transform."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['YOLO_CONFIG_DIR']=str(ROOT/'NativeUITrainer/.ultralytics')
os.environ['MPLCONFIGDIR']=str(ROOT/'NativeUITrainer/.mplconfig')
import unittest
from unittest.mock import patch
import numpy as np
from ultralytics.data.augment import RandomPerspective
from ultralytics.utils.instance import Instances
from train_ios_model import full_frame_finetune_kwargs,parse_args

class TranslationTests(unittest.TestCase):
    def test_terminal_settings_and_epoch_contract(self):
        from eval_translation170 import check_rows,t
        old=dict(translate=0,name='repair165-r017-repaired',epochs=5,warmup_bias_lr=.0001)
        new=dict(old,translate=.35,name=t.RUN.name)
        fields=('time','train/box_loss','train/cls_loss','train/dfl_loss','val/box_loss',
                'val/cls_loss','val/dfl_loss','metrics/mAP50(B)','metrics/mAP50-95(B)')
        rows=[dict(dict.fromkeys(fields,'1'),epoch=str(i)) for i in range(1,6)]
        check_rows(rows,new,old)
        for bad in (dict(new,translate=0),dict(new,warmup_bias_lr=.1)):
            with self.assertRaisesRegex(ValueError,'nonmatched_settings'):check_rows(rows,bad,old)
        with self.assertRaisesRegex(ValueError,'epoch_count'):check_rows(rows[:-1],new,old)
        with self.assertRaisesRegex(ValueError,'missing_epoch_metrics'):check_rows([dict(epoch=str(i)) for i in range(1,6)],new,old)
        with self.assertRaisesRegex(ValueError,'nonfinite_epochs'):check_rows([dict(x,loss='nan') for x in rows],new,old)

    def test_pixel_box_alignment_and_clipping(self):
        t=RandomPerspective(degrees=0,translate=.35,scale=0,shear=0,perspective=0)
        image=np.zeros((100,100,3),dtype=np.uint8);image[40:60,40:60]=255
        original=np.array([[40,40,60,60],[0,40,10,60],[90,40,100,60]],dtype=np.float32)
        labels=dict(img=image,cls=np.array([[0],[1],[2]]),
            instances=Instances(original,bbox_format='xyxy',normalized=False))
        matrix=np.eye(3,dtype=np.float32);matrix[0,2]=-35
        params=dict(M=matrix,scale=1,orig_shape=(100,100),size=(100,100))
        labels=t.apply_image(labels,params);labels=t.apply_instances(labels,params)
        np.testing.assert_allclose(labels['instances'].bboxes,[[5,40,25,60],[55,40,65,60]])
        self.assertEqual(labels['cls'].flatten().tolist(),[0,2])
        self.assertTrue(np.all(labels['img'][40:60,5:25]==255))
        # Partial survives only if standard area/size filters admit it.
        b=np.array([[90,40,100,60]],dtype=np.float32)
        labels=dict(instances=Instances(b,bbox_format='xyxy',normalized=False),cls=np.array([[2]]))
        matrix[0,2]=5
        labels=t.apply_instances(labels,params)
        np.testing.assert_allclose(labels['instances'].bboxes,[[95,40,100,60]])

    def test_real_matrix_bounds_and_defaults(self):
        t=RandomPerspective(degrees=0,translate=.35,scale=0,shear=0,perspective=0)
        import random
        random.seed(42);xs=[];ys=[]
        for _ in range(100):
            m,s=t._compute_affine_matrix(np.zeros((100,100,3),dtype=np.uint8),(100,100))
            self.assertEqual(s,1);xs.append(m[0,2]);ys.append(m[1,2])
            self.assertTrue(-35<=m[0,2]<=35 and -35<=m[1,2]<=35)
        self.assertLess(min(xs),-20);self.assertGreater(max(xs),20)
        self.assertLess(min(ys),-20);self.assertGreater(max(ys),20)
        self.assertEqual(full_frame_finetune_kwargs()['translate'],0)
        with patch('sys.argv',['train','--translation-ablation','--full-frame-finetune']):
            self.assertTrue(parse_args().translation_ablation)

if __name__=='__main__':unittest.main()
