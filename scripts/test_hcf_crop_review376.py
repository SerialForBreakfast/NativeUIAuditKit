import copy
import unittest
import hcf_crop_review376 as r


class ReviewTests(unittest.TestCase):
    def fixture(self):
        row=dict(id='a',sha256='x',group='g',role='development',profile='hcf',family='cards',outcome='miss',
                 prediction=dict(scores=[.2,.1],cropHashes=['a','b']))
        a=dict(rows=[row],proposalMode='oracle',modelSHA256='one')
        b=copy.deepcopy(a);b['modelSHA256']='two';b['rows'][0]['outcome']='correct'
        b['rows'][0]['prediction']['scores']=[.9,.1]
        return a,b

    def test_gain(self):
        a,b=self.fixture(); result=r.review(a,b,{})
        self.assertEqual((result['gains'],result['losses']),(1,0))
        self.assertIsNone(result['deploymentAccuracy'])
        self.assertAlmostEqual(result['rows'][0]['candidateMargin']['separation'],.8)

    def test_loss(self):
        a,b=self.fixture(); self.assertEqual(r.review(b,a,{})['losses'],1)

    def test_invalid_inputs(self):
        for key,value in [('role','audit'),('sha256','other'),('group','other'),('outcome','invented')]:
            a,b=self.fixture(); b['rows'][0][key]=value
            with self.assertRaises(ValueError):r.review(a,b,{})

    def test_duplicates(self):
        a,b=self.fixture();a['rows']*=2
        with self.assertRaises(ValueError):r.review(a,b,{})

    def test_nan(self):
        a,b=self.fixture();b['rows'][0]['prediction']['scores']=[float('nan'),.2]
        with self.assertRaises(ValueError):r.review(a,b,{})

    def test_crop_change(self):
        a,b=self.fixture();b['rows'][0]['prediction']['cropHashes']=['different']
        with self.assertRaises(ValueError):r.review(a,b,{})

    def test_geometry(self):
        a,b=self.fixture();g=dict(a['rows'][0],boxes={'f':[10,20,20,10]},focus='f',width=100,height=100)
        self.assertEqual(r.review(a,b,{'a':g})['rows'][0]['geometry']['region'],'0:0')

    def test_exposure(self):
        rows=[dict(role='train',profile='hcf',label=1,sha256='x',group='g')]*2
        d=r.duplicate_exposure(dict(rows=rows));self.assertEqual(d['fileIdentities'],1)

    def test_training_configuration(self):
        from hcf_factor_train376 import validate_config
        for profile in ('hcf','balanced'):
            for deduplicate in (True,False):
                validate_config(dict(profile=profile,deduplicate=deduplicate,seed=371))
        for cfg in [dict(profile='unknown',deduplicate=True,seed=371),
                    dict(profile='hcf',deduplicate='yes',seed=371),
                    dict(profile='hcf',deduplicate=True,seed=42)]:
            with self.assertRaises(ValueError):validate_config(cfg)


if __name__=='__main__': unittest.main()
