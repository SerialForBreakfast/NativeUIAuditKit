"""Offline matched-plan/report/deadline tests. No model execution."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import mps_batch_comparison as c
import mps_training_diagnostic as d


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=d.ROOT/'.build/debug-output');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def plans(self):
        a={key:[] for key in ('members','weights','taxonomy','sources','versions','limits')}
        a['settings']=dict(batch=8,seed=42);b=copy.deepcopy(a);b['settings']['batch']=16
        return [a,b]

    def test_matching_rejects_confounded_inputs(self):
        c.matching(self.plans())
        for key in ('members','weights','taxonomy','sources','versions','limits'):
            plans=self.plans();plans[1][key]=['different']
            with self.assertRaisesRegex(ValueError,'unmatched'):c.matching(plans)
        plans=self.plans();plans[1]['settings']['seed']=1
        with self.assertRaisesRegex(ValueError,'unmatched'):c.matching(plans)

    def test_summary_requires_all_repeats(self):
        trials=[dict(batch=b,epoch1_training_seconds=t) for b,t in zip(c.ORDER,[80,60,64,84])]
        report=c.summarize(trials)
        self.assertAlmostEqual(report['batch16_speed_ratio'],82/62)
        with self.assertRaisesRegex(ValueError,'incomplete'):c.summarize(trials[:-1])

    def test_actual_timing_reader_rejects_missing_runtime_and_nan(self):
        folder=self.root/'run';out=folder/'runs/diagnostic-only';out.mkdir(parents=True)
        receipt=dict(outcome='completed',returncode=0,elapsed_seconds=200,resource_samples=[dict(available_bytes=8*2**30)])
        d.write(folder/'receipt.json',receipt)
        meta=dict(kind='metadata',device='mps',workers=0,batch_size=16,rect=True,amp=False)
        stages={k:dict(calls=32 if k=='batch_interval' else 1,seconds=v,errors=0)
                for k,v in [('batch_interval',60),('inter_batch_gap',5),('epoch_total',70),('optimizer_step',10)]}
        rows=[meta,*[dict(kind='epoch',epoch=i,intervals=copy.deepcopy(stages)) for i in (0,1)],dict(kind='terminal',outcome='completed')]
        path=out/'host-timing-test.jsonl'
        def save():path.write_text('\n'.join(json.dumps(r) for r in rows))
        save();self.assertEqual(c.trial_metrics(folder,16)['epoch1_training_seconds'],65)
        rows[0]['batch_size']=8;save()
        with self.assertRaisesRegex(ValueError,'runtime'):c.trial_metrics(folder,16)
        rows[0]['batch_size']=16;rows[1]['intervals']['batch_interval']['calls']=31;save()
        with self.assertRaisesRegex(ValueError,'batches'):c.trial_metrics(folder,16)
        rows[1]['intervals']['batch_interval']['calls']=32;rows[1]['intervals']['batch_interval']['seconds']=float('nan');save()
        with self.assertRaisesRegex(ValueError,'timing'):c.trial_metrics(folder,16)

    def test_execute_stops_after_blocked_trial_no_retry(self):
        records=[dict(path='fake8',sha256='8'),dict(path='fake16',sha256='16')]
        bundle=dict(schema='mps-batch-comparison-v1',plans=records,order=c.ORDER,max_seconds=1800,quality_eligible=False,source={})
        path=self.root/'plan.json';d.write(path,bundle)
        with patch.object(d,'verified'),patch.object(d,'load_plan',side_effect=self.plans()), \
             patch.object(d,'execute',return_value=dict(outcome='blocked',reason='memory')) as execute:
            result=c.execute(path,d.digest(path))
        self.assertEqual(result['outcome'],'blocked');self.assertIsNone(result['summary']);self.assertEqual(execute.call_count,1)
        self.assertIn('deadline',execute.call_args.kwargs)

    def test_v1_does_not_allow_batch16_and_deadline_cannot_expand(self):
        plan=dict(schema='mps-host-diagnostic-v1',limits=d.LIMITS,quality_eligible=False,
                  settings=dict(device='mps',batch=16,imgsz=640,epochs=2,workers=0,seed=42))
        path=self.root/'plan.json';d.write(path,plan)
        with self.assertRaisesRegex(ValueError,'incompatible'):d.load_plan(path,d.digest(path))
        for seconds in (0,1801):
            with self.assertRaisesRegex(ValueError,'deadline'):d.supervise([],self.root,{},max_seconds=seconds)


if __name__=='__main__':unittest.main()
