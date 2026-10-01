import copy
import unittest
from unittest.mock import patch

import focus_transfer_experiment as t


class TransferTests(unittest.TestCase):
    def data(self):
        rows=[dict(id=str(i),split='train',use='train-candidate',
                   sourceKind='simulatorFixture',label=i%2) for i in range(8)]
        rows += [dict(id='human',split='train',use='human-static-auxiliary',label=0),
                 dict(id='evaluation',split='validation',use='representative-selection',label=1)]
        return rows,{str(i):.1 for i in range(8)} | {'human':.2}

    def test_identity_mass_and_tenfold_relative_emphasis(self):
        rows,w=self.data(); targets={'0','1'}
        self.assertEqual(t.emphasis(rows,w,targets,1),w)
        actual=t.emphasis(rows,w,targets)
        self.assertEqual(actual['human'],w['human'])
        self.assertAlmostEqual(sum(actual.values()),1)
        for label in (0,1):
            ids=[r['id'] for r in rows[:8] if r['label']==label]
            self.assertAlmostEqual(sum(actual[i] for i in ids),.4)
        self.assertAlmostEqual(actual['0']/actual['2'],10)
        self.assertAlmostEqual(actual['1']/actual['3'],10)

    def test_invalid_targets_weights_factors_and_duplicates(self):
        rows,w=self.data()
        for targets in ({'evaluation'},{'human'},{'missing'},set()):
            with self.assertRaises(ValueError):t.emphasis(rows,w,targets)
        for factor in (0,-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):t.emphasis(rows,w,{'0'},factor)
        with self.assertRaises(ValueError):t.emphasis(rows+rows[:1],w,{'0'})
        with self.assertRaises(ValueError):t.emphasis(rows,dict(w,missing=.1),{'0'})

    def test_expected_isolates_one_variable_without_mutating_parent(self):
        rows,w=self.data()
        p=dict(samples=rows,fullFit=dict(weights=w),configuration={},counts={},
               representation={},selection={},unmetQualificationBlockers=[])
        before=copy.deepcopy(p);doc=dict(additions=rows[:2])
        self.assertEqual(t.expected(p,doc,'transfer-aspect-partial'),p)
        changed=t.expected(p,doc,'transfer-emphasis-partial')
        self.assertNotEqual(changed['fullFit'],p['fullFit'])
        changed['fullFit']=p['fullFit'];self.assertEqual(changed,p)
        self.assertEqual(p,before)

    def test_cli_routes_version_and_binds_approval(self):
        import focus_learning_experiment as cli
        from pathlib import Path
        with patch.object(cli,'local',return_value=Path('unused')), \
             patch.object(Path,'read_text',return_value='{"version":"focus-transfer-experiment-v1"}'), \
             patch.object(t,'load_protocol',return_value='routed') as loader:
            self.assertEqual(cli.load_protocol('p','a','n','approval'),'routed')
            loader.assert_called_once_with('p','a','n','approval')
        p=dict(protocolSHA256='one',authority={},arm='transfer-emphasis-partial')
        self.assertNotEqual(t.approval(p),t.approval(dict(p,protocolSHA256='two')))


if __name__=='__main__':unittest.main()
