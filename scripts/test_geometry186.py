import copy
import unittest
from unittest.mock import patch
import geometry186 as g


class Tests(unittest.TestCase):
    def fixture(self):
        c=dict(rows=[dict(id=str(i)) for i in range(432)],initializer={'sha':'w'},membership={'sha':'m'},schedule=g.r.schedule(54,10,.25),args=dict(box=7.5,epochs=10,batch=8))
        p=dict(version='geometry185-proposal-v1',rows=c['rows'],initializer=c['initializer'],membership=c['membership'],schedule=c['schedule'],config=dict(c['args'],box=15.))
        return copy.deepcopy(p),copy.deepcopy(c)

    def test_exact_treatment(self):
        p,c=self.fixture();g.compatible(p,c)
        for field in ('version','rows','initializer','membership','schedule','config'):
            p,c=self.fixture();p[field]={}
            with self.subTest(field=field),self.assertRaises(Exception):g.compatible(p,c)
        p,c=self.fixture();p['config']['epochs']=20
        with self.assertRaisesRegex(Exception,'not_single_treatment'):g.compatible(p,c)

    def test_collision_before_input(self):
        with patch.object(g,'BASE',g.h.ROOT),patch.object(g.p,'sealed') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):g.prepare()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
