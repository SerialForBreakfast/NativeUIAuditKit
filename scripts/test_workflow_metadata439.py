import json
import tempfile
import unittest
from pathlib import Path
import research_queue as q
from workflow_metadata439 import enrich,digest


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def job(self,ident,state='blocked',seconds=None,inputs=None):
        spec=dict(id=ident,owner='Maximum-mini-NUIAK',conditions=[dict(job='decision',output='gate.json',outcome='supported')],inputs=inputs or [])
        folder=self.root/'jobs'/ident;folder.mkdir(parents=True)
        (folder/'spec.json').write_text(json.dumps(spec))
        return dict(job=ident,state=state,wallSeconds=seconds,specSHA256=digest(spec))
    def test_verified_metadata_and_exact_history(self):
        snapshot=dict(jobs=[self.job('old','complete',12),self.job('new')])
        result=enrich(snapshot,self.root)
        row=result['jobs'][1]
        self.assertEqual(row['owner'],'Maximum-mini-NUIAK');self.assertEqual(row['conditions'][0]['outcome'],'supported')
        self.assertEqual(row['workflowDuration']['samples'],1);self.assertEqual(row['workflowDuration']['low'],12)
        self.assertNotIn('owner',snapshot['jobs'][1])
    def test_changed_inputs_have_no_history(self):
        result=enrich(dict(jobs=[self.job('old','complete',12),self.job('new',inputs=[{'different':'input'}])]),self.root)
        self.assertIsNone(result['jobs'][1]['workflowDuration'])
    def test_different_producers_are_not_comparable(self):
        rows=[self.job('old','complete',12),self.job('new')]
        for row in rows:
            path=self.root/'jobs'/row['job']/'spec.json';spec=json.loads(path.read_text())
            spec['dependencies']=[{'job':row['job']+'-producer','specSHA256':'different','outputs':['data.json']}]
            path.write_text(json.dumps(spec));row['specSHA256']=digest(spec)
        self.assertIsNone(enrich(dict(jobs=rows),self.root)['jobs'][1]['workflowDuration'])
    def test_changed_hash_and_traversal_are_explicit(self):
        row=self.job('new');row['specSHA256']='wrong'
        result=enrich(dict(jobs=[row,dict(job='../outside')]),self.root)
        self.assertTrue(all(not r['metadataVerified'] for r in result['jobs']))
    def test_failed_and_nonfinite_times_are_not_samples(self):
        result=enrich(dict(jobs=[self.job('failed','failed',12),self.job('nan','complete',float('nan')),self.job('new')]),self.root)
        self.assertIsNone(result['jobs'][-1]['workflowDuration'])


if __name__=='__main__':unittest.main()
