import copy
import unittest
from unittest.mock import patch
import replay179 as r


class ReplayTests(unittest.TestCase):
    def test_accumulation_not_batches(self):
        a=r.schedule(27,20,.5);b=r.schedule(54,10,.25)
        self.assertEqual(a,b)
        self.assertEqual(a['batches'],540)
        self.assertLess(len(a['optimizerAt']),100)
        self.assertNotEqual(a,r.schedule(54,10,.5))

    def fixture(self):
        rows=[dict(id=str(i),split='train',pixelSHA256=str(i)) for i in range(432)]
        return dict(fitIDs=[str(i) for i in range(216)],replayRows=rows[216:]),rows,{str(i):{} for i in range(216)}

    def test_membership(self):
        d,m,meta=self.fixture();self.assertEqual(len(r.choose(d,m,meta)),432)
        for kind in ('role','duplicate','ancestry','changed','overlap','missing'):
            d,m,meta=copy.deepcopy(self.fixture())
            if kind=='role':m[0]['split']='test'
            elif kind=='duplicate':d['fitIDs'][0]=d['fitIDs'][1]
            elif kind=='ancestry':m[0]['group']='unknown'
            elif kind=='changed':d['replayRows']=copy.deepcopy(d['replayRows']);d['replayRows'][0]['extra']=True
            elif kind=='overlap':m.append(dict(id='test',split='test',pixelSHA256='0'))
            else:m.pop(0)
            with self.subTest(kind=kind),self.assertRaises(Exception):r.choose(d,m,meta)

    def test_collision_before_inputs(self):
        with patch.object(r,'OUT',r.h.ROOT),patch.object(r.p,'sealed') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):r.prepare()
            read.assert_not_called()

    def test_acceptance_and_failure(self):
        classes=[dict(**{'class':n},ap50=.9,tp=100,fp=0) for n in ('sheet','scrollIndicator','cancelAction','mapView')]
        result=dict(combined=dict(perClass=classes,metrics=dict(map50=.9)),page=dict(perClass=[dict(**{'class':'pageControl'},tp=59,fp=4)]))
        reference=dict(results=dict(combined={'019':copy.deepcopy(result['combined'])}))
        strata={s:{'operating-hit':65} for s in ('leading','center','trailing')}
        self.assertTrue(r.assess(result,strata,reference)['developmentSuccess'])
        result['combined']['perClass'][0]['ap50']=.8
        self.assertFalse(r.assess(result,strata,reference)['developmentSuccess'])
        self.assertFalse(r.assess(result,strata,reference)['productionEligible'])


if __name__=='__main__':unittest.main()
