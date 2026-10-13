import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import report_office349 as r


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=r.q.ROOT/'.build');self.root=Path(self.tmp.name)
        self.check=patch.object(r.s.m,'check_inputs');self.check.start()
    def tearDown(self):self.check.stop();self.tmp.cleanup()
    def make(self,name,score=.9):
        out=self.root/name/'out';out.mkdir(parents=True)
        models={'baseline':{'path':'model','sha256':'a'*64}}
        row=dict(id='pair',group='session',role='development',actionLinked=False)
        r.q.save(out/'config.json',dict(models=models,rows=[row],inputs=[]))
        r.q.save(out.parent/'result.json',dict(status='complete'))
        doc=dict(version='office-shadow349-v1',models=models,accuracy=None,trainingEligible=False,productionEligible=False,
                 rows=[dict(row,focusChanged=None,trainingEligible=False,probabilities={'baseline':score},
                     decisions={'baseline':r.s.decision(score)},disagreement=False)],timing={})
        path=out/'shadow.json';r.q.save(path,doc);return path
    def test_agreement_is_not_accuracy(self):
        result=r.summarize([self.make('one')]);self.assertIsNone(result['accuracy'])
        self.assertEqual(result['counts'],dict(pairs=1,groups=1,disagreements=0))
        self.assertIn('not truth',result['review'][0]['reviewReason'])
    def test_duplicate_pair_rejected(self):
        with self.assertRaisesRegex(Exception,'duplicate_pair'):r.summarize([self.make('one'),self.make('two')])
    def test_invalid_probability(self):
        with self.assertRaisesRegex(Exception,'invalid_probability'):r.summarize([self.make('one',1.1)])
    def test_incomplete_job(self):
        path=self.make('one');(path.parent.parent/'result.json').write_text('{"status":"running"}')
        with self.assertRaisesRegex(Exception,'incomplete_job'):r.summarize([path])


if __name__=='__main__':unittest.main()
