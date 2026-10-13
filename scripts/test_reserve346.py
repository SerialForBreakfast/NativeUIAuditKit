import unittest
import reserve346 as r


class ReserveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r.a.t.set_num_threads(2)
        cls.x=r.a.t.rand(2,18,128,192)*.6+.2

    def test_all_transforms(self):
        original=self.x.clone()
        self.assertEqual(len({v[0] for v in r.TESTS}),25)
        for mode,_,_ in r.TESTS:
            y=r.transform(self.x,mode)
            self.assertEqual(y.shape,self.x.shape)
            self.assertTrue(r.a.t.isfinite(y).all())
            self.assertTrue(((y>=0)&(y<=1)).all())
        self.assertTrue(r.a.t.equal(self.x,original))

    def test_noise_batch_parity(self):
        full=r.transform(self.x,'12-common-noise')
        split=r.a.t.cat([r.transform(self.x[:1],'12-common-noise'),r.transform(self.x[1:],'12-common-noise',1)])
        self.assertTrue(r.a.t.equal(full,split))
        delta=full-self.x
        self.assertTrue(r.a.t.allclose(delta[:,:3],delta[:,3:6],atol=1e-7))

    def test_selective_changes(self):
        for mode in ['18-context-position','19-padding']:
            self.assertTrue(r.a.t.equal(r.transform(self.x,mode)[:,6:],self.x[:,6:]))
        y=r.transform(self.x,'22-first-stale')
        self.assertTrue(r.a.t.equal(y[:,9:12],self.x[:,6:9]))
        self.assertTrue(r.a.t.equal(y[:,12:],self.x[:,12:]))

    def test_counts_and_rejections(self):
        rows=[dict(changed=1,sourceDomain='authored',condition='movement',group='a')]
        counts=r.count(rows,[.1],[.9])['authored/movement/a']
        self.assertEqual(counts['lost'],1)
        self.assertEqual(counts['missedChange'],1)
        for values in [[],[float('nan')],[1.1]]:
            with self.assertRaises(ValueError):r.count(rows,values,[.9])
        with self.assertRaises(ValueError):r.transform(self.x,'unknown')

    def test_actual_model_all_modes(self):
        net=r.a.e.load_candidate(r.q.ROOT/'reports/work/FOCUS-329/run/last.pt')
        with r.a.t.inference_mode():
            for mode,_,_ in r.TESTS:
                values=r.logits(net,r.transform(self.x,mode),mode)
                self.assertEqual(tuple(values.shape),(2,))
                self.assertTrue(r.a.t.isfinite(values).all())


if __name__=='__main__':unittest.main()
