"""Test equal update schedules and preserve source evidence."""
import copy
import unittest
import numpy as np
import condition291 as run
import report291


class ConditionTests(unittest.TestCase):
    def setUp(self):
        self.membership=dict(replayLabels=[0,1],selected=[0,1,2,3],
            rows=[dict(id=str(i),group='a' if i<2 else 'b',role='train',changed=i%2) for i in range(4)])
        self.added=[dict(group=r['group'],role='train',changed=r['changed']) for r in self.membership['rows']]
        self.labels=np.array([0,1,0,1,0,1,0,1,0,1],np.float32)
        self.weights=np.array([1,1,2,3,4,5,2,3,4,5],np.float32)

    def test_control_order_and_weight_totals(self):
        controls=run.select_controls(self.membership,self.added)
        self.assertEqual(controls.tolist(),[2,3,4,5])
        labels,weights,totals=run.balanced_weights(self.weights,self.labels,self.membership,self.added,controls)
        self.assertEqual(len(labels),18)
        self.assertTrue(np.array_equal(labels[-4:],labels[-8:-4]))
        self.assertTrue(np.array_equal(weights[:2],self.weights[:2]))
        for item in totals:self.assertAlmostEqual(item['before'],item['after'],places=6)
        self.assertTrue(np.all(weights>0))

    def test_missing_group_and_exhausted_support(self):
        for added in (self.added+self.added,[dict(role='train',group='missing',changed=1)]):
            with self.assertRaisesRegex(ValueError,'control_support'):run.select_controls(self.membership,added)

    def test_roles_and_label_mismatch(self):
        added=copy.deepcopy(self.added);added[0]['role']='reserved'
        with self.assertRaisesRegex(ValueError,'added_role'):run.select_controls(self.membership,added)
        with self.assertRaisesRegex(ValueError,'control_labels'):
            run.balanced_weights(self.weights,self.labels,self.membership,self.added,np.array([3,2,4,5]))

    def test_conflicting_observation(self):
        state=dict(role='train',settled=True,image={'sha256':'image'},focusID='a',runID='run',recipeHash='recipe')
        scene=dict(is_settled=True,focused_element_id='a',fixture_run_id='run',recipe={'recipe_hash':'recipe'})
        doc=dict(unfocused_sha256='image',focused_sha256='other',baseline_scene=scene,
                 focused_scene=scene,recipe={'recipe_hash':'recipe'})
        run.verify_state(state,doc)
        bad=copy.deepcopy(doc);bad['baseline_scene']['focused_element_id']='b'
        with self.assertRaisesRegex(ValueError,'state_observation'):run.verify_state(state,bad)
        bad=copy.deepcopy(doc);bad['unfocused_sha256']='unknown'
        with self.assertRaisesRegex(ValueError,'state_image_binding'):run.verify_state(state,bad)

    def test_invalid_weights(self):
        values=self.weights.copy();values[0]=float('nan')
        with self.assertRaisesRegex(ValueError,'base_weights'):
            run.balanced_weights(values,self.labels,self.membership,self.added,np.array([2,3,4,5]))

    def test_case_report_keeps_losses_and_roles(self):
        before=dict(conditions={'native.npy':dict(probabilities=[.1,.9])})
        after=dict(conditions={'native.npy':dict(probabilities=[.9,.5])})
        membership=dict(rows=[dict(id='a',group='g',role='reserved',changed=0),
                              dict(id='b',group='g',role='train',changed=1)])
        report,cases=report291.summarize_comparison(before,after,membership)
        self.assertEqual(report['native.npy']['lostCorrect'],2)
        self.assertEqual(report['native.npy']['gainedCorrect'],0)
        self.assertEqual([r['role'] for r in cases],['reserved','train'])
        self.assertEqual(cases[1]['candidateDecision'],-1)

    def test_control_choice_uses_sorted_ids(self):
        membership=copy.deepcopy(self.membership)
        membership['rows'][0]['id']='z'
        membership['rows'].append(dict(id='a',group='a',role='train',changed=0))
        membership['selected'].append(4)
        controls=run.select_controls(membership,[self.added[0]])
        self.assertEqual(controls.tolist(),[6])

    def test_added_report_separates_identity_from_focus(self):
        registration=dict(addedRows=[dict(changed=1,condition='focus'),dict(changed=0,condition='identity')])
        results={'model':dict(addedFit=dict(probabilities=[.5,.01]))}
        report=report291.added_condition_results(registration,results)['model']
        self.assertEqual(report['focus']['abstentions'],1)
        self.assertEqual(report['identity']['correct'],1)
        results['model']['addedFit']['probabilities']=[.5]
        with self.assertRaisesRegex(ValueError,'added_score_shape'):
            report291.added_condition_results(registration,results)


if __name__=='__main__':unittest.main()
