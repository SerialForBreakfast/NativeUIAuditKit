import copy
import unittest
from unittest.mock import patch
import ios_repair165 as r
from train_ios_model import full_frame_finetune_kwargs

class RepairComparisonTests(unittest.TestCase):
    def test_page_geometry_separates_missing_and_low_confidence(self):
        from types import SimpleNamespace as S
        from eval_repair165 import page_geometry
        image=S(image_id='a',width=100,height=100,label_path=S(read_text=lambda:'18 .5 .5 .2 .1'))
        request=S(images=[image])
        doc={'results':[dict(imageID='a',detections=[dict(classID=18,score=.1,xyxyPixels=[40,45,60,55])])]}
        result=page_geometry(doc,request,18)['populations']
        self.assertEqual(result['export']['medianWidthRatio'],1)
        self.assertAlmostEqual(result['export']['cases'][0]['geometry']['iou'],1)
        self.assertEqual(result['operational']['missingCandidates'],1)
        self.assertIsNone(result['operational']['medianWidthRatio'])
        doc['results'][0]['detections'].append(dict(classID=18,score=.9,xyxyPixels=[30,45,70,55]))
        result=page_geometry(doc,request,18)['populations']
        self.assertAlmostEqual(result['operational']['medianWidthRatio'],2)
        self.assertEqual(result['export']['medianWidthRatio'],1)
        image.label_path=S(read_text=lambda:'18 .5 .5 .2 .1\n18 .2 .2 .1 .1')
        with self.assertRaisesRegex(ValueError,'page_single_target_required'):page_geometry(doc,request,18)

    def setUp(self):
        self.old=[];self.new=[]
        for split,count in [('train',14540),('val',2800),('test',2400)]:
            for i in range(count):
                name=f'{i:06}.png';a=dict(split=split,image=dict(path=split+'/'+name,sha256='old'),label=dict(path=split+'/'+name+'.txt',sha256='old'))
                b=copy.deepcopy(a);b.update(id=split+'/'+name,replaced=split=='train' and i<900)
                if b['replaced']:b['image']['sha256']='new';b['label']['sha256']='new'
                self.old.append(a);self.new.append(b)
    def test_full_membership(self):self.assertEqual(len(r.compare_membership(self.old,self.new)),900)
    def test_evaluation_change_rejected(self):
        self.new[-1]['image']['sha256']='altered'
        with self.assertRaisesRegex(ValueError,'evaluation_or_unplanned_change'):r.compare_membership(self.old,self.new)
    def test_reorder_and_missing_rejected(self):
        self.new[0],self.new[1]=self.new[1],self.new[0]
        with self.assertRaisesRegex(ValueError,'membership_identity'):r.compare_membership(self.old,self.new)
        with self.assertRaisesRegex(ValueError,'membership_count'):r.compare_membership(self.old,self.new[:-1])
    def test_profile_preserves_evidence(self):
        config=full_frame_finetune_kwargs()
        self.assertEqual(config['warmup_bias_lr'],config['lr0'])
        for k in ('hsv_h','hsv_s','hsv_v','translate','scale','fliplr','flipud','degrees','mosaic','mixup','copy_paste'):
            self.assertEqual(config[k],0)
        self.assertFalse(config['amp']);self.assertFalse(config['exist_ok']);self.assertEqual(config['fraction'],1)
    def test_evaluation_rejects_incomplete_or_unbound_runs(self):
        import eval_repair165 as ev
        with self.assertRaisesRegex(ValueError,'arm'):ev.ready('arbitrary')
        launch={'evaluation':[]};launch['seal']=r.h.digest(launch)
        receipt={'exitCode':1};receipt['seal']=r.h.digest(receipt)
        with patch.object(ev.h,'read',side_effect=[launch,receipt]):
            with self.assertRaisesRegex(ValueError,'incomplete_training'):ev.ready('r016-prior')
        with patch.object(ev.h,'read',return_value={'seal':'invalid'}):
            with self.assertRaisesRegex(ValueError,'launch_seal'):ev.ready('r017-repaired')
        with self.assertRaisesRegex(ValueError,'arm'):ev.ready('r014-prior')

    def test_terminal_evidence_binds_arm_epochs_and_profile(self):
        import eval_repair165 as ev
        arm='r016-prior';checkpoint=r.h.ROOT/'NativeUITrainer/yolo_runs/repair165-r016-prior/weights/last.pt'
        launch=dict(configs={arm:{'path':'example/dataset.yaml'}},initializer={'path':'example/best.pt'})
        args=dict(full_frame_finetune_kwargs(),epochs=5,imgsz=640,batch=8,workers=0,device='mps',resume=False,
            optimizer='AdamW',cos_lr=True,seed=42,name='repair165-'+arm,
            data=str(r.h.ROOT/'example/dataset.yaml'),model='example/best.pt')
        fields=['time','train/box_loss','train/cls_loss','train/dfl_loss','val/box_loss','val/cls_loss','val/dfl_loss','metrics/mAP50(B)','metrics/mAP50-95(B)']
        rows=[dict({k:'0.1' for k in fields},epoch=str(i)) for i in range(1,6)]
        ev.terminal_contract(arm,launch,checkpoint,args,rows)
        with self.assertRaisesRegex(ValueError,'training_settings_mismatch'):
            ev.terminal_contract(arm,launch,checkpoint,dict(args,warmup_bias_lr=.1),rows)
        with self.assertRaisesRegex(ValueError,'wrong_arm_or_checkpoint'):
            ev.terminal_contract(arm,launch,checkpoint.with_name('best.pt'),args,rows)
        with self.assertRaisesRegex(ValueError,'training_settings_mismatch'):
            ev.terminal_contract(arm,launch,checkpoint,dict(args,mosaic=1),rows)
        with self.assertRaisesRegex(ValueError,'epoch_accounting'):
            ev.terminal_contract(arm,launch,checkpoint,args,rows[:-1])
        bad=copy.deepcopy(rows);bad[0]['train/box_loss']='nan'
        with self.assertRaisesRegex(ValueError,'nonfinite_epoch_evidence'):
            ev.terminal_contract(arm,launch,checkpoint,args,bad)

if __name__=='__main__':unittest.main()
