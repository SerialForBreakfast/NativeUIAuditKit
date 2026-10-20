import unittest
from research_repair_handoff478 import tasks, render


class RepairHandoffTests(unittest.TestCase):
    def review(self, reason='producer_requires_review:producer:failed', jobs=('a','b')):
        return dict(rows=[dict(job=job,blockers=[dict(owner='Maximum-mini-NUIAK',
            requirement=reason,action='Preserve the failed attempt and repair the producer.')]) for job in jobs])

    def test_consumers_share_one_repair(self):
        records=tasks([self.review()])
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['jobs'],['a','b'])
        self.assertEqual(records[0]['priority'],0)
        self.assertFalse(records[0]['executionAuthorized'])

    def test_restart_preserves_task_identity_and_text(self):
        records=tasks([self.review()])
        first=render('# Tasks\n\n- Keep human task.\n',records)
        self.assertEqual(first,render(first,tasks([self.review()])))
        self.assertIn('- Keep human task.',first)

    def test_distinct_producers_remain_distinct(self):
        self.assertEqual(len(tasks([self.review(),self.review('producer_requires_review:other:failed')])),2)

    def test_normal_dependency_wait_is_not_repair(self):
        self.assertEqual(tasks([dict(rows=[dict(job='a',blockers=[],waits=['dependency_incomplete:b'])])]),[])

    def test_resolved_repairs_leave_active_section(self):
        text=render('# Tasks',tasks([self.review()]))
        cleared=render(text,[])
        self.assertNotIn('- [ ] **REPAIR-',cleared)
        self.assertIn('no implementation blockers',cleared)

    def test_hostile_or_private_error_stays_out_of_public_tasks(self):
        text=render('# Tasks',tasks([self.review('<script>alert(1)</script> /Users/private/token')]))
        self.assertNotIn('<script>',text)
        self.assertNotIn('/Users/private',text)
        self.assertIn('input_validation_failure',text)

    def test_bad_owner_and_damaged_markers_fail(self):
        review=self.review()
        review['rows'][0]['blockers'][0]['owner']='unknown'
        with self.assertRaisesRegex(ValueError,'owner_unknown'):
            tasks([review])
        with self.assertRaisesRegex(ValueError,'markers'):
            render('<!-- FLOW478-REPAIRS:BEGIN -->',[])


if __name__=='__main__':
    unittest.main()
