import copy
import unittest
import research_queue as q
from register_hcf367_captures import fit_regions


class RegionTests(unittest.TestCase):
    def test_large_control_fits_without_moving_origins(self):
        plan=q.load(q.ROOT/'Research/ResearchSpecs/HCF362/large-dark-plan.json')
        before=copy.deepcopy(plan)
        fit_regions(plan)
        regions=plan['recipe']['appearance']['composition']['regions']
        old=before['recipe']['appearance']['composition']['regions']
        self.assertEqual([r['frame'][:2] for r in regions],[r['frame'][:2] for r in old])
        self.assertTrue(all(r['frame'][2:]==[320,320] for r in regions))

    def test_outside_screen_fails(self):
        plan=q.load(q.ROOT/'Research/ResearchSpecs/HCF362/large-dark-plan.json')
        plan['recipe']['appearance']['composition']['regions'][0]['frame'][0]=1900
        with self.assertRaisesRegex(ValueError,'outside_screen'):fit_regions(plan)


if __name__=='__main__':unittest.main()
