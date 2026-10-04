import tempfile
import unittest
from pathlib import Path
import numpy as np
import focus_metric_reference as m
import evaluate_metric108 as e
from audit_representation107 import nearest


class MetricTests(unittest.TestCase):
    def bank(self):
        data=np.random.default_rng(42).random((1040,m.WIDTH),dtype=np.float32)
        members=[dict(frameID=str(i//2),candidateID=str(i),role='train',
                      ancestry='fixture-family',positive=bool(i%2)) for i in range(len(data))]
        return data,members

    def test_exact_naive_and_permutation(self):
        data,members=self.bank(); scorer=m.ReferenceScorer(data,members)
        actual=scorer.score(data[:4],[v['frameID'] for v in members[:4]],exclude_same_frame=True)
        frames=[v['frameID'] for v in members]
        pos=nearest(data,range(4),[i for i,v in enumerate(members) if v['positive']],frames)
        neg=nearest(data,range(4),[i for i,v in enumerate(members) if not v['positive']],frames)
        self.assertEqual([v['score'] for v in actual],[b['rms']-a['rms'] for a,b in zip(pos,neg)])
        other=m.ReferenceScorer(data[::-1],members[::-1])
        self.assertEqual(actual,other.score(data[:4],frames[:4],exclude_same_frame=True))

    def test_tiny_distance_and_ties(self):
        x=np.full((3,m.WIDTH),.5,dtype=np.float32); x[1,0]=np.nextafter(np.float32(.5),np.float32(1))
        members=[dict(frameID=str(i),candidateID='x',role='train',ancestry='a',positive=i>0) for i in range(3)]
        scorer=m.ReferenceScorer(x,members)
        score=scorer.score(x[:1],['2'],exclude_same_frame=True)[0]
        self.assertLess(score['score'],0)
        self.assertGreater(score['positiveRMS'],0)
        x[1]=x[0]; scorer=m.ReferenceScorer(x,members)
        self.assertEqual(scorer.score(x[:1],['query'])[0]['positiveReference'],1)

    def test_roles_provenance_duplicates(self):
        data,members=self.bank()
        for key,value in [('role','development'),('ancestry',''),('positive',1),('frameID','')]:
            changed=[dict(v) for v in members]; changed[0][key]=value
            with self.assertRaises(ValueError): m.ReferenceScorer(data,changed)
        members[1]=members[0]
        with self.assertRaises(ValueError): m.ReferenceScorer(data,members)

    def test_bounds_nonfinite_and_no_reference(self):
        data,members=self.bank(); scorer=m.ReferenceScorer(data,members)
        with self.assertRaises(ValueError): scorer.score(data[:81],['q']*81)
        bad=data[:1].copy(); bad[0,0]=np.nan
        with self.assertRaises(ValueError): scorer.score(bad,['q'])
        with self.assertRaises(ValueError): scorer.score(data[:1].astype(np.float64),['q'])
        with self.assertRaises(ValueError): scorer.score(data[:1],[])
        members=[dict(v,frameID='one') for v in members]
        scorer=m.ReferenceScorer(data,members)
        with self.assertRaises(ValueError): scorer.score(data[:1],['one'],exclude_same_frame=True)

    def test_manifest_hash_version_and_provenance(self):
        data,members=self.bank()
        with tempfile.TemporaryDirectory(dir=e.h.ROOT/'.build') as name:
            root=Path(name); np.save(root/'bank.npy',data,allow_pickle=False)
            doc=dict(version=m.VERSION,**e.h.FLAGS,sources={'test':'source'},members=members,
                     tensor=e.h.ref(root/'bank.npy'),implementation=e.h.ref(Path(m.__file__)),
                     encoding='production-crop256-rgb16-bilinear-normalized-size-v1')
            e.h.write(root/'bank.json',doc,sealed=True)
            e.load_bank(root/'bank.json',doc['sources'],members)
            with self.assertRaises(Exception): e.load_bank(root/'bank.json',{'test':'wrong'},members)
            with (root/'bank.npy').open('ab') as stream: stream.write(b'changed')
            with self.assertRaises(Exception): e.load_bank(root/'bank.json',doc['sources'],members)
            doc['version']='unknown'; e.h.write(root/'unsupported.json',doc,sealed=True)
            with self.assertRaises(Exception): e.load_bank(root/'unsupported.json',doc['sources'],members)


if __name__=='__main__': unittest.main()
