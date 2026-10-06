import copy
import unittest
import roi194 as r


class Tests(unittest.TestCase):
    def fixture(self):
        base=[dict(imageID='source',width=100,height=200,status='ok',detections=[dict(classID=0,score=.7,xyxyPixels=[40,90,60,110])])]
        records=[dict(imageID='source',proposals=[dict(id='crop',proposalIndex=0,window=[25,75,75,125])])]
        crops=[dict(imageID='crop',width=50,height=50,status='ok',detections=[dict(classID=0,score=.8,xyxyPixels=[16,16,34,34])])]
        return base,records,crops

    def test_real_merge_conservation(self):
        b,p,c=self.fixture();before=copy.deepcopy(b)
        result=r.merge(b,p,c,0)
        self.assertEqual(result['results'][0]['detections'],[dict(classID=0,score=.7,xyxyPixels=[41,91,59,109])])
        self.assertEqual(b,before)

    def test_missing_extra_duplicate_crop(self):
        for variant in ('missing','extra','duplicate'):
            b,p,c=self.fixture()
            if variant=='missing':c=[]
            elif variant=='extra':c.append(dict(c[0],imageID='extra'))
            else:c.append(c[0])
            with self.assertRaisesRegex(Exception,'crop_membership'):r.merge(b,p,c,0)

    def test_geometry_and_failed_inference(self):
        for key,value in [('width',51),('status','failed')]:
            b,p,c=self.fixture();c[0][key]=value
            with self.assertRaises(Exception):r.merge(b,p,c,0)
        b,p,c=self.fixture();p[0]['proposals'][0]['window']=[0,0,50,50]
        with self.assertRaises(Exception):r.merge(b,p,c,0)

    def test_no_proposal_preserves_original(self):
        b,p,c=self.fixture();b[0]['detections'][0]['score']=.1;p[0]['proposals']=[]
        self.assertEqual(r.merge(b,p,[],0)['results'],b)

    def test_duplicate_proposal_and_original(self):
        b,p,c=self.fixture();p[0]['proposals'].append(p[0]['proposals'][0])
        with self.assertRaises(Exception):r.merge(b,p,c,0)
        b,p,c=self.fixture()
        with self.assertRaises(Exception):r.merge(b,p+p,c,0)


if __name__=='__main__':unittest.main()
