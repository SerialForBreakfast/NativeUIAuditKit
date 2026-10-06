import unittest
from fullframe_replay_audit import select


class SelectionTests(unittest.TestCase):
    def test_deterministic_unique_groups_and_cap(self):
        rows=[dict(id=str(i),group=str(i//2),classes=[i%3]) for i in range(120)]
        selected,gaps=select(rows,4,12)
        self.assertEqual((selected,gaps),select(list(reversed(rows)),4,12))
        self.assertEqual(len(selected),len({r['group'] for r in selected}))
        self.assertLessEqual(len(selected),12);self.assertFalse(any(gaps.values()))

    def test_report_gaps_not_automatic_expansion(self):
        rows=[dict(id=str(i),group=str(i),classes=[0]) for i in range(50)]
        selected,gaps=select(rows,16,3)
        self.assertEqual(len(selected),3);self.assertEqual(gaps,{0:13})
        with self.assertRaisesRegex(ValueError,'duplicate_id'):select(rows+rows[:1])


if __name__=='__main__':unittest.main()
