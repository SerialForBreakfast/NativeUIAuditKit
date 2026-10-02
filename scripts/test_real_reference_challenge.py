import unittest
from real_reference_challenge import summarize
from real_reference_inventory import candidates,iou


class ChallengeTests(unittest.TestCase):
    def test_correct(self):
        r=summarize([.1,.9]);self.assertEqual(r['advisoryCorrect'],2)
        self.assertEqual(r['correctAt085'],2)

    def test_wrong_and_uncertain(self):
        r=summarize([.9,.4]);self.assertEqual(r['advisoryWrong'],1)
        self.assertEqual(r['advisoryUncertain'],1)
        self.assertFalse(r['ordered'])

    def test_boundaries(self):
        self.assertEqual(summarize([.15,.85])['advisoryCorrect'],2)

    def test_invalid(self):
        for x in ([float('nan'),.5],[-1,.5],[True,.5],[.2]):
            with self.assertRaises(Exception):summarize(x)

    def test_overlap(self):
        self.assertEqual(iou([0,0,10,10],[0,0,10,10]),1)
        self.assertEqual(iou([0,0,10,10],[20,0,10,10]),0)

    def test_candidate_not_identity(self):
        def f(state,screen='home'):
            return dict(screen=screen,controls=[dict(id=state,state=state,**{'class':'collectionItem'},bounds=[0,0,10,10])])
        truth={'a':f('focused'),'b':f('unfocused'),'c':f('unfocused','other')}
        found=candidates(truth);self.assertEqual(len(found),1)
        self.assertEqual(found[0]['identity'],'unverified')
        self.assertEqual(found[0]['referenceImage'],'b')


if __name__=='__main__':unittest.main()
