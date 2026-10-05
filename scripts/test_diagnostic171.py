import copy
import unittest
from unittest.mock import patch

import diagnostic171 as d


def detection(box, score=.8):
    return dict(xyxyPixels=box, score=score)


def source():
    rows=[]
    for family,count in [('UIKitControls',700),('KitchenSink',200)]:
        for i in range(count):
            rows.append(dict(id=f'{family}-{i:04}',family=family,
                scale=2 if i%2 else 3,colorScheme='light' if i%2 else 'dark'))
    return dict(version='native-page-repair-v1',target=d.native.TARGET,split='train',members=rows)


class DiagnosticTests(unittest.TestCase):
    def test_dispositions_and_operating_threshold(self):
        box=[0,0,10,10]
        for predictions,expected in [([], 'absent'),
                ([detection([20,20,30,30])],'localization-miss'),
                ([detection(box,.249)],'low-confidence-match'),
                ([detection(box,.25)],'operating-hit')]:
            with self.subTest(expected=expected):
                self.assertEqual(d.classify(box,predictions)['disposition'],expected)

    def test_one_to_one_and_empty_truth(self):
        box=[0,0,10,10]
        predictions=[detection(box),detection(box,.7),detection(box,.1)]
        self.assertEqual(d.matches([box],predictions),dict(support=1,tp=1,fp=1,fn=0))
        self.assertEqual(d.matches([],predictions),dict(support=0,tp=0,fp=2,fn=0))
        self.assertEqual(d.matches([box],[]),dict(support=1,tp=0,fp=0,fn=1))

    def test_catalog_determinism_ancestry_and_complete_variants(self):
        doc=source(); plan=d.catalog(doc)
        reversed_doc=copy.deepcopy(doc);reversed_doc['members'].reverse()
        self.assertEqual(plan,d.catalog(reversed_doc))
        self.assertEqual(len(plan['rows']),288)
        groups={r['group'] for r in plan['rows']}
        self.assertEqual(len(groups),48)
        for group in groups:
            rows=[r for r in plan['rows'] if r['group']==group]
            self.assertEqual(len({(r['placement'],r['tint']) for r in rows}),6)
            self.assertTrue(all(r['split']=='train' and r['recipe']['id']==group for r in rows))
        for key in ('executionReady','trainingEligible','independentEvaluation'):
            self.assertFalse(plan[key])
        self.assertTrue(plan['coverageLimitations'])

    def test_catalog_rejects_changed_roles_membership_and_strata(self):
        for mutation in ('role','duplicate','theme','missing'):
            doc=source()
            if mutation=='role':doc['split']='test'
            elif mutation=='duplicate':doc['members'][0]['id']=doc['members'][1]['id']
            elif mutation=='theme':doc['members'][0]['colorScheme']='unknown'
            else:del doc['members'][0]['colorScheme']
            with self.subTest(mutation=mutation),self.assertRaises(Exception):d.catalog(doc)

    def test_entrypoint_collision_precedes_input_reads(self):
        with patch.object(d,'OUT',d.h.ROOT),patch.object(d.h,'read') as reader:
            with self.assertRaisesRegex(Exception,'output_collision'):d.run()
            reader.assert_not_called()

    def test_entrypoint_rejects_modified_report_before_inputs(self):
        with patch.object(d,'OUT') as out,patch.object(d.h,'read',return_value={'seal':'changed'}),patch.object(d.t,'ready') as ready:
            out.exists.return_value=False
            with self.assertRaisesRegex(Exception,'report_seal'):d.run()
            ready.assert_not_called()

    def test_entrypoint_rejects_changed_prediction_before_inputs(self):
        report={'predictions':[{'path':'missing-prediction','sha256':'invalid'}]}
        report['seal']=d.h.digest(report)
        with patch.object(d,'OUT') as out,patch.object(d.h,'read',return_value=report),patch.object(d.t,'ready') as ready:
            out.exists.return_value=False
            with self.assertRaises(Exception):d.run()
            ready.assert_not_called()


if __name__=='__main__':unittest.main()
