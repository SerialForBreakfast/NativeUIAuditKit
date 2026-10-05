import copy
import unittest
from prepare_worker145 import selected


class WorkerIntakeTests(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(id=str(i),group='fixture-procedural-renderer-v1',split='train',changed=True) for i in range(113)]
        self.indices=list(range(24))+list(range(29,113))

    def test_excludes_native_settings(self):
        for i in range(24,29):self.rows[i].update(group='native-settings',split='development')
        self.assertEqual(len(selected(self.rows,self.indices)),108)

    def test_rejects_role_source_and_membership_drift(self):
        for field,value in [('group','native-settings'),('split','test'),('changed',1)]:
            rows=copy.deepcopy(self.rows);rows[0][field]=value
            with self.assertRaises(ValueError):selected(rows,self.indices)
        with self.assertRaises(ValueError):selected(self.rows,list(range(108)))
        self.rows[1]['id']='0'
        with self.assertRaises(ValueError):selected(self.rows,self.indices)


if __name__=='__main__':unittest.main()
