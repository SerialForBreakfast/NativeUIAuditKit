import unittest
from sdk_report508 import summarize

class ReportTests(unittest.TestCase):
    def report(self,ident,loss=False):
        models={m:dict(outcome='correct-abstention') for m in ('hcf','mixed','fallback')}
        row=dict(id=ident,sha256=ident,group='related',truth=None,arms={a:dict(models=models) for a in ('known','scoped','general','union')})
        return dict(rows=[row],comparisons=[dict(id=ident,model=m,gain=False,loss=loss,newWrong=loss) for m in models])

    def test_any_regression_rejects_union(self):
        r=summarize([self.report('a'),self.report('b',True)])
        self.assertEqual(r['groups'],1)
        self.assertTrue(all(v['decision']=='reject_union' for v in r['gates'].values()))
        self.assertFalse(r['modelAccepted'])

    def test_duplicate_frames_fail(self):
        with self.assertRaisesRegex(ValueError,'sdk508_report_duplicate'):summarize([self.report('a'),self.report('a')])
