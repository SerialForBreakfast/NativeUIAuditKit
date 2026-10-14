"""Check excluded groups and preserve unsupported geometry."""
import unittest
from ring_body399 import correct


class InsetTests(unittest.TestCase):
    def test_group_exclusion_and_standard(self):
        rows=[dict(id=str(i),role='development',profile='hcf',group=str(i),ringInsetsPixels=[-4]*4) for i in range(4)]
        rows[0]['ringInsetsPixels']=[-100]*4
        rows.append(dict(id='s',role='retained',profile='standard',group='s'))
        proposals=dict(rows=[dict(r,prediction=dict(candidates=[[20,20,100,80]])) for r in rows])
        result,fits=correct(proposals,dict(rows=rows))
        self.assertEqual(result['rows'][0]['prediction']['candidates'],[[24,24,92,72]])
        self.assertNotIn('0',fits[0]['fitGroups'])
        self.assertEqual(result['rows'][-1]['prediction']['candidates'],[[20,20,100,80]])
        self.assertEqual(proposals['rows'][0]['prediction']['candidates'],[[20,20,100,80]])
        proposals['rows'][0]['role']='audit'
        with self.assertRaisesRegex(ValueError,'identity'):correct(proposals,dict(rows=rows))


if __name__=='__main__':unittest.main()
