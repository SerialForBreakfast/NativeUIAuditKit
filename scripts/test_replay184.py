import copy
import unittest
from unittest.mock import patch
import replay184 as r


class BindingTests(unittest.TestCase):
    def fixture(self):
        old=dict(rows=[{'id':str(i)} for i in range(432)],initializer={'sha256':'weights'})
        new=dict(version='replay181-proposal-v1',rows=old['rows'][:352]+[{'id':str(i)} for i in range(432,512)],
            addedIDs=[str(i) for i in range(432,512)],removedIDs=[str(i) for i in range(352,432)],
            initializer=old['initializer'],schedule=r.r.schedule(54,10,.25),membership={})
        return new,old

    def test_compatible_and_changed_inputs(self):
        doc,old=self.fixture();self.assertEqual(len(r.compatible(doc,old)['replayRows']),216)
        for field in ('version','initializer','schedule','fit','ids'):
            doc,old=copy.deepcopy(self.fixture())
            if field=='fit':doc['rows'][0]={'id':'other'}
            elif field=='ids':doc['addedIDs'][0]='other'
            else:doc[field]='changed'
            with self.subTest(field=field),self.assertRaises(Exception):r.compatible(doc,old)

    def test_collision_precedes_input(self):
        with patch.object(r,'BASE',r.h.ROOT),patch.object(r.r,'inputs') as read:
            with self.assertRaisesRegex(Exception,'output_collision'):r.prepare()
            read.assert_not_called()


if __name__=='__main__':unittest.main()
