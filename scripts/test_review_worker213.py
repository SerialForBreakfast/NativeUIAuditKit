import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import review_worker213 as r


def epochs(slots):
    batches=(slots+3)//4
    return [dict(epoch=i,batches=batches,
                 updates=((i+1)*batches)//16-(i*batches)//16,
                 order=[f'/worker/images/{j:04d}.png' for j in range(slots)],
                 losses=[1.]*batches) for i in range(10)]


class WorkerReviewTests(unittest.TestCase):
    def test_compact217_order(self):
        data=epochs(1758);order=data[0]['order']
        digest=r.hashlib.sha256(json.dumps(order,separators=(',',':')).encode()).hexdigest()
        for row in data:
            row.pop('order');row.update(order_count=1758,order_sha256=digest)
        self.assertEqual(r.check_epochs(data,1758,order),(4400,275))
        for field,value in [('order_count',1757),('order_sha256','bad')]:
            bad=copy.deepcopy(data);bad[0][field]=value
            with self.assertRaisesRegex(ValueError,'compact_order_integrity'):r.check_epochs(bad,1758,order)
        with self.assertRaisesRegex(ValueError,'slot_order'):r.check_epochs(data,1758,list(reversed(order)))
        with self.assertRaises(KeyError):r.check_epochs(data,1758)
    def test_explicit_training_record_budget_preserves_default(self):
        parent=r.ROOT/'.build/debug-output';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            path=Path(tmp)/'large.json';path.write_text('"'+'a'*(4*1024**2)+'"')
            with self.assertRaisesRegex(ValueError,'inventory_size'):r.inventory_metadata(path)
            self.assertEqual(len(r.inventory_metadata(path,max_bytes=8*1024**2)),4*1024**2)
            for budget in (True,0,8*1024**2+1):
                with self.assertRaisesRegex(ValueError,'inventory_budget'):r.inventory_metadata(path,max_bytes=budget)
            path.write_text(json.dumps([0]*100001))
            with self.assertRaisesRegex(ValueError,'inventory_complexity'):r.inventory_metadata(path)
            self.assertEqual(len(r.inventory_metadata(path,max_nodes=150000)),100001)
            with self.assertRaisesRegex(ValueError,'inventory_node_budget'):r.inventory_metadata(path,max_nodes=150001)
    def test_profiles_and_continuous_accumulation(self):
        self.assertEqual(r.check_epochs(epochs(572),572),(1430,89))
        self.assertEqual(r.check_epochs(epochs(1569),1569),(3930,245))

    def test_missing_epoch_partial_batch_and_reset_accumulation(self):
        original=epochs(1569)
        mutations=[lambda x:x.pop(),lambda x:x[0].update(batches=392),
                   lambda x:x[1].update(updates=24)]
        for mutate in mutations:
            data=copy.deepcopy(original);mutate(data)
            with self.assertRaises(ValueError):r.check_epochs(data,1569)

    def test_slot_order_and_loss_integrity(self):
        for mutate in [lambda x:x[0]['order'].reverse(),
                       lambda x:x[0]['losses'].pop(),
                       lambda x:x[0]['losses'].__setitem__(0,float('nan'))]:
            data=epochs(1569);mutate(data)
            with self.assertRaises(ValueError):r.check_epochs(data,1569)

    def test_entrypoint_rejects_changed_source_before_output(self):
        parent=r.ROOT/'.build/debug-output';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            out=Path(tmp)/'review.json'
            with patch.object(r,'sha',return_value='changed'):
                with self.assertRaisesRegex(ValueError,'source_changed'):
                    r.run(base=Path(tmp),out=out,profile='216')
            self.assertFalse(out.exists())
            with self.assertRaisesRegex(ValueError,'output_collision'):
                r.run(base=Path(tmp),out=Path(tmp),profile='216')

    def test_complete216_report_and_corrupt_evaluation(self):
        parent=r.ROOT/'.build/debug-output';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            base=Path(tmp)
            for folder in ('evidence','checkpoints','predictions'):(base/folder).mkdir()
            config=dict(batch=4,epochs=10,nbs=64,imgsz=640,optimizer='AdamW',lr0=.0001,
                        lrf=1.,warmup_epochs=0,seed=42,amp=False,resume=False,workers=0,device='0')
            config.update({k:0 for k in ('mosaic','mixup','cutmix','copy_paste','hsv_h','hsv_s',
                'hsv_v','degrees','translate','scale','shear','perspective','flipud','fliplr','erasing','multi_scale')})
            training=[];evaluations=[]
            for arm,run in [('control','031'),('treatment','032')]:
                (base/arm).mkdir();cp=base/arm/'last.pt';cp.write_bytes(arm.encode())
                training.append(dict(arm=arm,run=run,results=[dict(effective_config=config,
                    epochs=epochs(1569),validations=[dict(images=512,batches=64)]*11,
                    checkpoints={'run'+run+'/weights/last.pt':r.sha(cp)},total_seconds=1.)]))
                for part,count in dict(validation=24,test=12,fit=135,page=37,combined=413).items():
                    pred=base/'predictions'/(arm+'-'+part+'.json');pred.write_text('{}')
                    evaluations.append(dict(arm=arm,partition=part,count=count,prediction=pred.name,
                        bytes=pred.stat().st_size,sha256=r.sha(pred),checkpointSHA256=r.sha(cp)))
            (base/'evidence/training-results.json').write_text(json.dumps(training))
            ep=base/'evidence/evaluation-results.json';ep.write_text(json.dumps(evaluations))
            real_sha=r.sha
            pins={'worker198_full_trainer.py':'07f226e011278d03640d65eab2778af5ca472260b625e70b2440524a307ad11f',
                  'worker216_replay.py':'966c1dd311e0f26477a0fe44c05dde49a277fb72d6126267e3e79ddc448ffec6'}
            def digest(p):return pins[p.name] if p.parent.name=='scripts' else real_sha(p)
            with patch.object(r,'sha',side_effect=digest):
                r.run(base,base/'review.json','216')
                self.assertEqual(json.loads((base/'review.json').read_text())['results'][0]['updates'],245)
                evaluations[-1]=evaluations[0];ep.write_text(json.dumps(evaluations))
                with self.assertRaisesRegex(ValueError,'duplicate_evaluation'):
                    r.run(base,base/'bad.json','216')
                self.assertFalse((base/'bad.json').exists())


if __name__=='__main__':unittest.main()
