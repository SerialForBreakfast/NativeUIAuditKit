import copy
import unittest
from focus_representative_report import errors
from test_focus_representative_validation import sample


class ReportTests(unittest.TestCase):
    def test_deterministic_error_selection_preserves_rows(self):
        rows=[dict(sample(i,'listRow',i!=2),image={'path':'original'},
                   crop={'path':'crop'},bounds=[1,2,3,4]) for i in range(4)]
        before=copy.deepcopy(rows)
        scores=[dict(id=str(i),probability=p) for i,p in enumerate((.1,.1,.99,.9))]
        report=errors(rows,scores)
        self.assertEqual([x['id'] for x in report],['2','0','1'])
        self.assertEqual(report,errors(rows,scores));self.assertEqual(rows,before)

    def test_missing_scores_not_silently_omitted(self):
        with self.assertRaises(ValueError):errors([sample(0,'listRow',1)],[])

    def test_empty_population(self):
        self.assertEqual(errors([],[]),[])


if __name__=='__main__':unittest.main()
