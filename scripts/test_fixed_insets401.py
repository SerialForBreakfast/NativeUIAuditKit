"""Check fitting separation, invalid inputs, and both real queue adapters."""
import copy
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin
from fixed_insets401 import correct, compare, partition


class FixedInsetTests(unittest.TestCase):
    def inputs(self):
        rows = [dict(id=str(i), sha256=str(i)*64, group=str(i), role='development', profile='hcf',
                     family='card', outcome='miss', prediction=dict(decision='abstain', box=None, candidates=[[10,20,100,80]])) for i in range(4)]
        rows.append(dict(rows[3], id='standard', profile='standard', sha256='s'*64))
        geometry = dict(rows=[dict(r, ringInsetsPixels=[-4]*4) for r in rows])
        policy = dict(version='fixed-inset-groups-v1', fitGroups=['0','1','2'], evaluationGroups=['3'])
        return dict(rows=rows), geometry, policy

    def test_fixed_mapping_and_evaluation_independence(self):
        p, g, policy = self.inputs(); result, mapping = correct(p,g,policy)
        self.assertEqual(mapping['offsets'], [-4]*4)
        self.assertEqual(result['rows'][3]['prediction']['candidates'], [[14,24,92,72]])
        self.assertEqual(result['rows'][4], p['rows'][4])
        g['rows'][3]['ringInsetsPixels'] = [float('nan')]*4
        self.assertEqual(correct(p,g,policy)[1], mapping)
        self.assertEqual(p['rows'][0]['prediction']['candidates'], [[10,20,100,80]])

    def test_rejects_leakage_and_invalid_geometry(self):
        p,g,policy = self.inputs();bad=copy.deepcopy(policy);bad['evaluationGroups'].append('0')
        with self.assertRaisesRegex(ValueError,'overlap'):correct(p,g,bad)
        p['rows'][3]['sha256']=p['rows'][0]['sha256']
        with self.assertRaisesRegex(ValueError,'duplicate'):partition(p['rows'],policy)
        p,g,policy=self.inputs();g['rows'][0]['ringInsetsPixels']=[float('nan')]*4
        with self.assertRaisesRegex(ValueError,'invalid_insets'):correct(p,g,policy)
        p,g,policy=self.inputs();p['rows'][3]['prediction']['candidates']=[[0,0,2,2]]
        with self.assertRaisesRegex(ValueError,'collapsed'):correct(p,g,policy)
        p,g,policy=self.inputs();p['rows'][0]['role']='retained'
        with self.assertRaisesRegex(ValueError,'fit_role'):correct(p,g,policy)

    def test_partition_report(self):
        p,g,policy=self.inputs();v=compare(p,p,policy)
        self.assertEqual(v['partitions']['evaluation']['slices']['hcf']['frames'],1)
        self.assertTrue(v['standardPredictionsIdentical'])
        self.assertTrue(v['partitions']['evaluation']['previousSuccessesPreserved'])

    def test_queue_positive_and_negative(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='fixed401-') as folder:
            root=Path(folder);queue=root/'queue'
            for template in ('T31','T32'):
                for bad in (False,True):
                    p,g,policy=self.inputs();ident=template.lower()+('-bad' if bad else '-good')
                    if bad:policy['evaluationGroups'].append('0')
                    values=dict(proposals=p,geometry=g,partition=policy) if template=='T31' else dict(baseline=p,candidate=p,partition=policy)
                    inputs={}
                    for key,value in values.items():
                        path=root/(ident+'-'+key+'.json');q.save(path,value);inputs[key]=pin(path)
                    doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template=template,
                        question='Does fixed geometry preserve group separation?',decision='Reject overlapping fitting and evaluation groups.',
                        inputs=inputs,parameters={},dependencies=[])
                    templates.register(doc,queue);approval.approve(queue,ident,'test','Isolated fixed geometry qualification.')
                    self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,'failed' if bad else 'complete')])


if __name__=='__main__':unittest.main()
