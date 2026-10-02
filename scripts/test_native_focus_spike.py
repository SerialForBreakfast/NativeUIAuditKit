import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import native_focus_spike as n
import native_focus_spike_model as model
import native_focus_spike_report as report


class NativeSpikeTests(unittest.TestCase):
    def test_model_wall_budget(self):
        with patch.object(model.time,'time',return_value=100):
            self.assertEqual(model.remaining(200),100)
            with self.assertRaisesRegex(ValueError,'model_tranche_wall_budget_exhausted'):
                model.remaining(100)
    def test_report_timing_preserves_unknowns(self):
        self.assertEqual(report.distribution([None,None])['count'],0)
        self.assertEqual(report.distribution([1,2,None,3])['total'],6)
        with self.assertRaisesRegex(ValueError,'invalid_timing'):
            report.distribution([float('nan')])

    def test_paired_representation_comparison(self):
        def arm(name,values):
            return dict(predictions=[dict(id=f'n26-g08-v{case:03d}-{label}-{name}',
                label=label,probability=value) for case,vs in enumerate(values) for label,value in enumerate(vs)])
        a=arm('normalized',[(.1,.9),(.1,.2),(.9,.9)])
        b=arm('common',[(.1,.2),(.1,.9),(.9,.2)])
        r=report.paired_comparison(a,b)
        self.assertEqual(r['controls'],dict(bothCorrect=2,normalizedOnly=2,commonOnly=1,bothWrong=1))
        self.assertEqual(r['pairs'],dict(bothCorrect=0,normalizedOnly=1,commonOnly=1,bothWrong=1))
        b['predictions'][0]['label']=1
        with self.assertRaisesRegex(ValueError,'comparison_label'):report.paired_comparison(a,b)
        b['predictions'].pop()
        with self.assertRaisesRegex(ValueError,'comparison_membership'):report.paired_comparison(a,b)

    def test_producer_partial_failure_is_terminal(self):
        self.assertIn('completed_with_failures',n.TERMINAL)
    def test_pair_metrics_and_incomplete_pairs(self):
        rows=[dict(caseID='a',label=0),dict(caseID='a',label=1),
              dict(caseID='b',label=0),dict(caseID='b',label=1)]
        r=model.metric(rows,[.1,.9,.9,.2],.85)
        self.assertEqual((r['tp'],r['tn'],r['fp'],r['fn'],r['bothCorrectPairs']),(1,1,1,1,1))
        with self.assertRaisesRegex(ValueError,'incomplete_scored_pair'):
            model.metric(rows[:1],[.1],.85)
        with self.assertRaisesRegex(ValueError,'invalid_probability'):
            model.metric(rows,[float('nan'),.9,.9,.2],.85)

    def test_model_membership_preflight(self):
        members=[dict(caseID=str(i),role='train' if i<1000 else 'evaluation',configurationGroup=i//125)
                 for i in range(1250)]
        rows=[dict(m,id=f"{m['caseID']}-{label}",label=label,arm='common',
            sha256=f"{int(m['caseID'])*2+label:064x}") for m in members for label in (0,1)]
        model.validate_samples(rows,dict(members=members),'native26-common')
        rows[0]['role']='evaluation'
        with self.assertRaisesRegex(ValueError,'arm_split_or_label'):
            model.validate_samples(rows,dict(members=members),'native26-common')
        rows[0]['role']='train';rows[0]['label']=1
        with self.assertRaisesRegex(ValueError,'arm_pair_balance'):
            model.validate_samples(rows,dict(members=members),'native26-common')
        rows[0]['label']=0;rows[0]['sha256']=rows[1]['sha256']
        with self.assertRaisesRegex(ValueError,'ambiguous_crop_pixels_or_split_overlap'):
            model.validate_samples(rows,dict(members=members),'native26-common')

    def test_external_runtime_root_boundary(self):
        import focus_runtime
        with patch.object(focus_runtime,'identity',return_value={}):
            with self.assertRaisesRegex(ValueError,'invalid_image_root'):
                focus_runtime.invoke([dict(path=str(n.ROOT/'Package.swift'))],image_root='/')
            with self.assertRaisesRegex(ValueError,'image_outside_authorized_root'):
                focus_runtime.invoke([dict(path='/etc/hosts')],image_root=n.ROOT)
    def test_common_window_uses_before_scale(self):
        b=[200,200,100,80];v=n.common_window(b)
        self.assertAlmostEqual(v[2]*1.32,140)
        self.assertAlmostEqual(v[3]*1.32,112)
        self.assertAlmostEqual(v[0]+v[2]/2,250)
        self.assertEqual(n.overlap([0,0,10,10],[10,0,10,10]),0)

    def test_plan_partition_and_hashes(self):
        composition=dict(version=3,background=dict(colors=[0,1],locations=[0,1],
            direction='horizontal',interpolation='linear'),
            definitions=dict(target=dict(kind='home_icon',style='main',width=220,height=260)),
            styles=dict(main=dict(foreground=0xffffff,background=0,fontSize=24,cornerRadius=12,
                opacity=1,blur=False,focus=dict(kind='native_image',version=1))),
            contents={f'item-{i}':dict(title='Test',seed=i,preset='artwork') for i in range(3)},
            regions=[dict(id='main',axis='row',frame=[180,180,1560,580],gap=90,
                items=[dict(id=f'item-{i}',component='target',content=f'item-{i}',selected=False) for i in range(3)])])
        recipe=dict(schema_version=1,archetype='grid_matrix',density='regular',theme='dark',
            element_count=3,step_index=0,seed=1,
            appearance=dict(version=1,preset='artwork',layout='standard',composition=composition))
        manifest=dict(cases=[dict(recipe=recipe,split_group='validation')])
        temp=n.ROOT/'.build/debug-output/native26-tests';temp.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp) as d:
            d=Path(d);(d/'base.json').write_text(json.dumps(manifest));(d/'helper').write_bytes(b'fixture')
            doc=n.plan(d/'base.json',d/'helper',d/'plan.json')
            self.assertEqual(len(doc['members']),1250)
            self.assertEqual(sum(r['role']=='train' for r in doc['members']),1000)
            for field in ('layoutFamily','artworkFamily','seed','recipeSHA256','configurationGroup'):
                a={r[field] for r in doc['members'] if r['role']=='train'}
                b={r[field] for r in doc['members'] if r['role']=='evaluation'}
                self.assertFalse(a & b,field)
            for chunk in doc['chunks']:
                self.assertEqual(len(chunk['cases']),25)
                for case in chunk['cases']:
                    self.assertEqual(n.recipe_hash(case['recipe']),case['recipe']['recipe_hash'])
            with self.assertRaisesRegex(ValueError,'plan_exists'):
                n.plan(d/'base.json',d/'helper',d/'plan.json')

    def test_missing_mount(self):
        with patch.object(Path,'is_mount',return_value=False):
            with self.assertRaisesRegex(ValueError,'external_volume_not_mounted'):n.mounted()

    def test_real_pair_observation_and_recipe_rejection(self):
        p=n.USB/'qualification-ebfd748d/splits/validation/home_icon-dark-dark-p0-s260001'
        if not p.exists():self.skipTest('retained qualification unavailable')
        c=n.validate_bundle(p)['usableRows'][0]
        member=dict(caseID='qualification',target='item-0',recipeSHA256=n.recipe_hash(c['recipe']))
        result=n.inspect(p,member)
        self.assertGreater(min(result['growth']),1.1)
        self.assertEqual([f['label'] for f in result['frames']],[0,1])
        member['recipeSHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'recipe_membership'):n.inspect(p,member)


if __name__=='__main__':unittest.main()
