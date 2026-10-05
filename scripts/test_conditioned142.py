import unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import conditioned142 as f


class ConditionedTests(unittest.TestCase):
    def test_original_norm_objective_with_unequal_columns(self):
        x=np.array([[0,1,100,0],[4,0,0,0]],float)
        r,w=f.solve(x,[1,1]);self.assertTrue(r['feasibleWitness'])
        # Min max(|w1|,|w2|) is TARGET/101, not a scaled-coordinate norm.
        np.testing.assert_allclose(w[:2],f.TARGET/101,rtol=1e-6)
        self.assertEqual(w[2],0);self.assertEqual(r['zeroRows'],1)
        self.assertEqual(r['zeroColumns'],1)

    def test_zero_and_contradiction(self):
        for x,y in [([[0,1],[0,1]],[0,1]),([[0,0]],[1])]:
            r,w=f.solve(x,y);self.assertEqual(r['status'],2);self.assertIsNone(w)
        r,w=f.solve([[3,0],[-3,0]],[1,0]);self.assertTrue(r['feasibleWitness']);np.testing.assert_array_equal(w,[0])

    def test_matches_unscaled(self):
        x=np.array([[0,1,0],[0,0,-2],[3,0,0]],float)
        r,w=f.solve(x,np.ones(3));old,v=f.previous.lp.solve(x,np.ones(3))
        self.assertTrue(r['feasibleWitness']);self.assertAlmostEqual(r['objective'],old['objective'],places=6)
        self.assertTrue(np.all(x[:,0]+x[:,1:]@w>=f.TARGET-1e-6))

    def test_invalid(self):
        for x,y in [([[np.nan,1]],[1]),([[0,1]],[2]),(np.empty((0,2)),[])]:
            with self.assertRaises(ValueError):f.solve(x,y)
        for budget in [0,61,float('nan')]:
            with self.assertRaises(ValueError):f.solve([[0,1]],[1],budget)

    def test_solver_success_does_not_override_original_residual(self):
        result=SimpleNamespace(status=0,message='solver claims success',success=True,nit=1,
                               x=np.array([f.TARGET-2e-5,f.TARGET]),fun=f.TARGET)
        with patch.object(f,'linprog',return_value=result):r,w=f.solve([[0,1]],[1])
        self.assertTrue(r['solverSuccess']);self.assertFalse(r['feasibleWitness']);self.assertIsNone(w)
        self.assertGreater(r['maxViolation'],1e-6)
        self.assertEqual(len(r['candidateWeights']),1)
        self.assertEqual(r['worstRow'],0)

    def test_strict_tolerance_and_rejected_candidate_retention(self):
        result=SimpleNamespace(status=1,message='limit',success=False,nit=1,
                               x=np.array([f.TARGET,f.TARGET]),fun=f.TARGET)
        with patch.object(f,'linprog',return_value=result) as call:
            r,w=f.solve([[0,1]],[1],strict=True)
        self.assertIsNone(w);self.assertFalse(r['feasibleWitness'])
        self.assertEqual(r['candidateWeights'],[f.TARGET])
        self.assertEqual(r['originalResiduals'],[0.])
        self.assertEqual(call.call_args.kwargs['options']['primal_feasibility_tolerance'],1e-10)
        with self.assertRaises(ValueError):f.solve([[0,1]],[1],strict='yes')

    def test_preservation_scales_rhs_and_keeps_tiny_entries(self):
        from scipy.sparse import csr_matrix
        matrix=csr_matrix([[1.,1e-12],[0.,2.]]);rhs=np.array([3.,4.])
        changed,right,factor=f.preserve_coefficients(matrix,rhs)
        self.assertGreater(np.abs(changed.data).min(),1e-9)
        np.testing.assert_allclose(changed.toarray()/factor[:,None],matrix.toarray())
        np.testing.assert_allclose(right/factor,rhs)
        with self.assertRaises(ValueError):f.preserve_coefficients(csr_matrix([[1e-30]]),np.array([1.]))
        with self.assertRaises(ValueError):f.solve([[0,1]],[1],preserve=True)

    def test_preserved_original_objective(self):
        r,w=f.solve([[0,1,100,0],[4,0,0,0]],[1,1],strict=True,preserve=True)
        self.assertTrue(r['feasibleWitness']);np.testing.assert_allclose(w[:2],f.TARGET/101,rtol=1e-6)

    def test_stronger_training_margin_does_not_weaken_runtime_gate(self):
        r,w=f.solve([[0,1]],[1],strict=True,preserve=True,margin=f.TARGET+.009)
        self.assertTrue(r['feasibleWitness']);self.assertAlmostEqual(w[0],f.TARGET+.009)
        with self.assertRaises(ValueError):f.solve([[0,1]],[1],margin=f.TARGET-.001)

    def test_global_admission_rejects_scope_change_before_reading_pixels(self):
        with patch.object(f.h,'read',return_value={'version':'wrong'}):
            with self.assertRaises(ValueError):f.global_admission({})


if __name__=='__main__':unittest.main()
