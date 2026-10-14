"""Check original-view preservation and content matching."""
import unittest
import numpy as np
import additive341 as a


class AddedTests(unittest.TestCase):
    def test_identical_has_no_added_window(self):
        self.assertEqual(a.added_windows(a.t.zeros(1,6,128,192)),[None])

    def test_match_is_exact_after_rounding(self):
        before=np.zeros((20,20,3),np.uint8);after=np.full_like(before,200)
        result=a.match_content(before,after,120000)
        self.assertIsNotNone(result)
        self.assertLessEqual(result[0],.1)
        self.assertEqual(result[3],a.magnitude(before,result[1]))

    def test_unreachable_is_gap(self):
        before=np.zeros((20,20,3),np.uint8)
        self.assertIsNone(a.match_content(before,before,10))

    def test_zero_target_rejected(self):
        with self.assertRaises(ValueError):a.match_content(np.zeros((1,1,3)),np.zeros((1,1,3)),0)

    def test_initial_parity_and_original_branch(self):
        import copy
        a.t.set_num_threads(2)
        old=a.e.extend(a.r.extend(a.r.s.c.model.extend(a.b.worker.make_model(a.t,paired_context=True)),2))
        new=copy.deepcopy(old);new.change=a.AddedChange(new.change)
        x=a.t.rand(2,24,128,192)
        with a.t.inference_mode():
            self.assertTrue(a.t.equal(old.change(x[:,:18]),new.change(x)))
        for key,value in old.change.state_dict().items():
            self.assertTrue(a.t.equal(value,new.change.whole.state_dict()[key]))

    def test_extra_crop_does_not_overlap_originals(self):
        x=a.t.rand(2,6,128,192)
        for old,extra in zip(a.r.windows(x),a.added_windows(x)):
            self.assertIsNotNone(extra)
            ex,ey=extra
            for ox,oy in old:
                self.assertFalse(ex<ox+32 and ex+32>ox and ey<oy+32 and ey+32>oy)

    def test_identical_extra_pixels_are_zero(self):
        x=np.zeros((2,6,128,192),np.float32)
        self.assertFalse(np.any(a.added_details(x,[None,None])))

    def test_added_training_keeps_original_weights(self):
        import copy
        old=a.e.extend(a.r.extend(a.r.s.c.model.extend(a.b.worker.make_model(a.t,paired_context=True)),2))
        old.change=a.AddedChange(old.change)
        before=copy.deepcopy(old.change.whole.state_dict())
        config=dict(epochs=1,batch=2,lr=.0001,seed=42,threads=2,detailOnly=True,addedBoundary341=True)
        trained,_=a.b.trainer.fit(old,a.t.rand(2,6,128,192),a.t.tensor([0.,1.]),config,
                                 detail_inputs=a.t.rand(2,18,128,192))
        for key,value in before.items():self.assertTrue(a.t.equal(value,trained.change.whole.state_dict()[key]))


if __name__=='__main__':unittest.main()
