import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import placement173 as p


class CandidateTests(unittest.TestCase):
    def test_actual_evaluation_entrypoint_records_only_completed_export_timing(self):
        import eval_placement173 as ev
        for fail in (False,True):
            with tempfile.TemporaryDirectory(dir=p.h.ROOT/'.build') as folder:
                out=Path(folder)/'evaluation'
                with patch.object(ev,'OUT',out),patch.object(p,'ready',return_value=(Path(folder)/'last.pt',[Path(folder)/str(i) for i in range(4)])), \
                     patch.object(p,'sealed',return_value={'controlPredictions':[]}),patch.object(ev.h,'ref',side_effect=lambda x:{'path':str(x)}), \
                     patch.object(ev.h,'write') as writer,patch.object(ev.e,'export_predictions',side_effect=ValueError('failed_inference') if fail else None) as exporter, \
                     patch.object(ev.time,'perf_counter',side_effect=[1,3,10,15]):
                    if fail:
                        with self.assertRaisesRegex(ValueError,'failed_inference'):ev.infer()
                        self.assertEqual(writer.call_count,1)  # Protocol only, never a success timing.
                    else:
                        ev.infer();self.assertEqual(exporter.call_count,2)
                        records=[call.args[1] for call in writer.call_args_list[1:]]
                        self.assertEqual([r['seconds'] for r in records],[2,5])
                        self.assertTrue(all(not r['controlTimingComparable'] for r in records))
                        self.assertTrue(all(call.kwargs['discard_degenerate'] for call in exporter.call_args_list))

    def test_development_success_does_not_hide_precision_or_ap_loss(self):
        from eval_placement173 import assess
        import copy
        result={'combined':{arm:dict(metrics=dict(map50=.8),perClass=[dict(**{'class':name},fp=1) for name in ('cancelAction','mapView')]) for arm in ('017','019')}}
        page={arm:dict(strata={key:dict(tp=0 if arm=='017' else 1) for key in ('left=True','native=True')}) for arm in ('017','019')}
        self.assertTrue(assess(result,page)['developmentSuccess'])
        fp=copy.deepcopy(result);fp['combined']['019']['perClass'][0]['fp']=2
        self.assertFalse(assess(fp,page)['developmentSuccess'])
        ap=copy.deepcopy(result);ap['combined']['019']['metrics']['map50']=.79
        self.assertFalse(assess(ap,page)['developmentSuccess'])
        nohit=copy.deepcopy(page);nohit['019']['strata']['left=True']['tp']=0
        self.assertFalse(assess(result,nohit)['developmentSuccess'])
        self.assertFalse(assess(result,page)['productionEligible'])

    def test_membership_and_failure_boundaries(self):
        base=[dict(id=f'{split}/img_{i:06}.png',split=split,pixelSHA256=f'{split}-{i}')
            for split,count in [('train',14540),('val',2800),('test',2400)] for i in range(count)]
        added=[dict(id=f'new-{i}',group=f'img_{i:06}',split='train',pixelSHA256=f'new-{i}') for i in range(264)]
        reused=[dict(id=f'reused-{i}') for i in range(24)]
        p.check_membership(base,added,reused)
        for key,value in [('split','test'),('group','missing'),('pixelSHA256','test-0'),('id','reused-0')]:
            altered=[dict(r) for r in added];altered[0][key]=value
            with self.subTest(key=key),self.assertRaises(Exception):p.check_membership(base,altered,reused)
        with self.assertRaises(Exception):p.check_membership(base,added[:-1],reused)

    def test_terminal_requires_exact_budget_and_unchanged_augmentation(self):
        old=dict(translate=0,epochs=5,name='old',data='old',warmup_bias_lr=.0001)
        args=dict(old,name=p.RUN.name,data=str(p.OUT/'dataset/dataset.yaml'))
        fields=('time','train/box_loss','train/cls_loss','train/dfl_loss','val/box_loss','val/cls_loss','val/dfl_loss','metrics/mAP50(B)','metrics/mAP50-95(B)')
        rows=[dict(dict.fromkeys(fields,'1'),epoch=str(i)) for i in range(1,6)]
        p.check_terminal(args,old,rows)
        for key,value in [('translate',.35),('epochs',30),('warmup_bias_lr',.1)]:
            with self.subTest(key=key),self.assertRaisesRegex(Exception,'nonmatched_settings'):
                p.check_terminal(dict(args,**{key:value}),old,rows)
        with self.assertRaisesRegex(Exception,'epoch_count'):p.check_terminal(args,old,rows[:-1])
        with self.assertRaisesRegex(Exception,'nonfinite_or_missing_epochs'):
            p.check_terminal(args,old,[dict(r,time='nan') for r in rows])

    def test_preparation_collision_precedes_input_or_subprocess(self):
        with patch.object(p,'OUT',p.h.ROOT),patch.object(p.subprocess,'run') as command:
            with self.assertRaisesRegex(Exception,'output_collision'):p.prepare()
            command.assert_not_called()


if __name__=='__main__':unittest.main()
