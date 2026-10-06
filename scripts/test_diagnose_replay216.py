import unittest
from diagnose_replay216 import operating_matches, size_bin, compare_cases
from test_eval_run013 import Run013Tests


class MatchingTests(unittest.TestCase):
    def test_threshold_duplicate_and_tie(self):
        box=(0,0,10,10)
        self.assertEqual(operating_matches([box,box],[(.25,box)]),({1},[]))
        self.assertEqual(operating_matches([box],[(.24,box),(.9,box),(.8,box)]),({0},[2]))
        self.assertEqual(operating_matches([],[(.8,box)]),(set(),[0]))

    def test_size_boundaries_and_letterbox(self):
        for n,label in [(15,'lt16'),(16,'16to32'),(32,'32to64'),(64,'ge64')]:
            self.assertEqual(size_bin((0,0,n,n),640,640),label)
            self.assertEqual(size_bin((0,0,2*n,2*n),1280,720),label)

    def test_empty_case_accounting_and_missing(self):
        fixture=Run013Tests();fixture.setUp()
        try:
            request=fixture.request;image=request.images[0]
            doc=dict(results=[dict(imageID=image.image_id,detections=[])])
            report=compare_cases(request,doc,doc,['a']*41)
            self.assertEqual(report['totals']['control'],report['totals']['treatment'])
            self.assertEqual(sum(r['support'] for r in report['bins']),sum(r['fn'] for r in report['totals']['control']))
            with self.assertRaisesRegex(ValueError,'case_membership'):
                compare_cases(request,doc,dict(results=[]),['a']*41)
        finally:fixture.tearDown()


if __name__=='__main__':unittest.main()
