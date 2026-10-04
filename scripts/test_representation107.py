import unittest
import numpy as np
from audit_representation107 import collisions,nearest


class RepresentationAuditTests(unittest.TestCase):
    def test_exact_conflict_requires_opposite_labels(self):
        x=np.array([[1,2],[1,2],[3,4]],dtype=np.float32)
        self.assertEqual(collisions(x,[True,True,False],range(3)),[])
        groups=collisions(x,[True,False,False],range(3))
        self.assertEqual(len(groups),1);self.assertEqual(groups[0]['indices'],[0,1])
        self.assertEqual((groups[0]['positive'],groups[0]['negative']),(1,1))

    def test_training_only_collision_does_not_admit_development(self):
        x=np.ones((3,2),dtype=np.float32);labels=[True,True,False]
        self.assertEqual(collisions(x,labels,[0,1]),[])
        self.assertEqual(len(collisions(x,labels,[0,1,2])),1)

    def test_size_can_distinguish_identical_pixels(self):
        x=np.ones((2,3),dtype=np.float32)
        self.assertEqual(len(collisions(x,[True,False],[0,1])),1)
        x=np.concatenate((x,np.array([[.1,.2],[.3,.4]],dtype=np.float32)),axis=1)
        self.assertEqual(collisions(x,[True,False],[0,1]),[])

    def test_nearest_excludes_same_frame_and_uses_reference_only(self):
        x=np.array([[0,0],[0,0],[.3,.4],[.01,0]],dtype=np.float32)
        result=nearest(x,[0],[0,1,2],['a','a','b','development'])
        self.assertEqual(result[0]['neighbor'],2)
        self.assertAlmostEqual(result[0]['rms'],np.sqrt(.125),places=6)

    def test_tie_is_deterministic_and_source_order_explicit(self):
        x=np.array([[0],[1],[-1]],dtype=np.float32)
        self.assertEqual(nearest(x,[0],[1,2],['a','b','c'])[0]['neighbor'],1)
        self.assertEqual(nearest(x,[0],[2,1],['a','b','c'])[0]['neighbor'],2)

    def test_missing_independent_frame_is_not_a_zero_distance(self):
        with self.assertRaisesRegex(ValueError,'no_other_frame_reference'):
            nearest(np.zeros((2,2)),[0],[1],['same','same'])


if __name__=='__main__':unittest.main()
