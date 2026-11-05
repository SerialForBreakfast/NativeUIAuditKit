import tempfile
import unittest
from pathlib import Path
import research_queue as q
import research_approval as approval
from template_inputs398 import pin
from focus_receipt568 import normalize,compile_successors
from focus_replay568 import history_entry
from research_trust import check_training_report

class ReceiptTests(unittest.TestCase):
    def test_loss_normalization_is_exact_and_rejects_invalid_data(self):
        rows=[dict(epoch=1,loss=.25),dict(epoch=2,loss=.1)]
        mapped=normalize(rows,2)
        self.assertEqual([r['trainLoss'] for r in mapped],[.25,.1]);self.assertNotIn('trainLoss',rows[0])
        with self.assertRaisesRegex(ValueError,'history_epochs'):normalize(rows,3)
        with self.assertRaisesRegex(ValueError,'history_loss'):normalize([dict(epoch=1,loss=float('nan'))],1)

    def test_new_writer_passes_canonical_receipt_validator(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='history568-') as temp:
            root=Path(temp);q.save(root/'history.json',[history_entry(i,.1) for i in range(1,31)]);q.save(root/'fit.json',dict(epochs=30))
            self.assertIsNone(check_training_report(root,dict(history='history.json',trainingReport='fit.json'),30))

    def test_successor_queue_recovers_real_completed_weights_without_training(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='recover568-') as temp:
            root=Path(temp);source=q.load(q.ROOT/'reports/work/FOCUS568/ready/compiled.json')
            manifest=compile_successors(source,root/'compiled',q.ROOT/'reports/work/FOCUS568/failed-source/focus_replay568.py')
            self.assertEqual(len(manifest['jobs']),8)
            specs=[q.load(q.ROOT/r['spec']['path']) for r in manifest['jobs']]
            self.assertEqual(sum(s['authority']=='training' for s in specs),1)
            spec=specs[0];queue=root/'queue';q.submit(root/'compiled'/(spec['id']+'.json'),queue)
            approval.approve(queue,spec['id'],'test','CPU receipt qualification only. No training or inference.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[spec['id']]),[(spec['id'],'complete')])
            out=queue/'jobs'/spec['id']/'attempts/1/out';report=q.load(out/'benchmark_summary.json')
            self.assertFalse(report['additionalTraining']);self.assertTrue(report['weightsUnchanged'])
            original=q.QUEUE/'jobs/focus568-control-train/attempts/1/out/final.pt'
            self.assertEqual(q.load(out/'model.json')['checkpoint']['sha256'],q.digest(original))
            self.assertEqual(q.load(q.QUEUE/'jobs/focus568-control-train/attempts/1/result.json')['status'],'failed')
