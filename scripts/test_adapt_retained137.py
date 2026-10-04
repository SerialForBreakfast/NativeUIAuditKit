import copy
import unittest
from unittest.mock import Mock, patch
import numpy as np
import adapt_retained137 as a


def fixture():
    families=['within_screen']*4+['within_screen_with_content_change']+['screen_transition']*2+['identical_control']*2
    pairs=[dict(source='s',before=i,after=i+1,changed=f!='identical_control',family=f) for i,f in enumerate(families)]
    peer=[dict(id=f'op:{i}:{i+1}',nativeHint=f!='identical_control') for i,f in enumerate(families)]
    peer += [dict(id=f'op:{i}:{i+1}',nativeHint=None) for i in (9,10)]
    admission=dict(version='retained-change-admission-v1',decision='approved_for_next_pinned_change_only_development_fit',
        effectiveRole='train',independentEvaluationEligible=False,bodyGeometryEligible=False,
        sourceBundles=dict(s=dict(operation='op')),pairs=pairs,
        excluded=[dict(source='s',before=i,after=i+1) for i in (9,10)])
    return admission,peer


class AdmissionTests(unittest.TestCase):
    def test_changed_admission_fails_before_source_access(self):
        path=Mock();path.read_bytes.return_value=b'changed admission'
        with patch.object(a,'ADMISSION',path),self.assertRaisesRegex(ValueError,'admission_changed'):
            a.load()

    def test_equal_family_weights(self):
        doc,peer=fixture();order,y,families=a.reviewed_indices(doc,peer)
        self.assertEqual(len(order),30);self.assertEqual(len(set(order)),9)
        for ids in families.values():self.assertEqual(sum(order.count(i) for i in ids),10)
        self.assertEqual(y.sum(),20)
        self.assertFalse({9,10}&set(order))

    def test_bad_roles_unknown_labels_overlap_and_identity(self):
        doc,peer=fixture()
        for key,value in [('effectiveRole','evaluation'),('bodyGeometryEligible',True),('independentEvaluationEligible',True),('version','new')]:
            bad=copy.deepcopy(doc);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):a.reviewed_indices(bad,peer)
        for mutate in (lambda v:v['pairs'].append(v['pairs'][0]),
                       lambda v:v['pairs'][0].update(changed=None),
                       lambda v:v['pairs'][0].update(changed=False),
                       lambda v:v['pairs'][0].update(family='unknown'),
                       lambda v:v['excluded'].pop(),
                       lambda v:v['pairs'][0].update(before=99)):
            bad=copy.deepcopy(doc);mutate(bad)
            with self.assertRaises(ValueError):a.reviewed_indices(bad,peer)
        peer[-1]['id']=peer[0]['id']
        with self.assertRaises(ValueError):a.reviewed_indices(doc,peer)

    def test_retention_constraint_and_materialized_update(self):
        torch=a.d.a.r.d.torch_runtime();torch.set_num_threads(2)
        x=np.zeros((2,1153),np.float32);x[:,0]=[3,-3];x[:,1]=[1,-1]
        net=a.t.retention.constrained_model(x,np.array([1,0],np.float32))
        # A large adverse correction must be bounded; identical residuals never change.
        net.change.linear.weight.data.fill_(-100)
        with torch.no_grad():
            out=net.change(torch.from_numpy(x)).flatten().numpy()
            self.assertGreater(out[0],a.t.retention.FLOOR);self.assertLess(out[1],-a.t.retention.FLOOR)
            identity=x.copy();identity[:,1:]=0
            np.testing.assert_array_equal(net.change(torch.from_numpy(identity)).flatten().numpy(),identity[:,0])
        self.assertNotIn('originalGroupCount',a.configuration())


if __name__=='__main__':unittest.main()
