"""Training uses the 12 h hang guard; older exact exceptions never lower it."""
import unittest
import research_execution_policy as p


class PolicyTests(unittest.TestCase):
    def test_exact_training_exception(self):
        key=next(iter(p.TRAINING_EXCEPTIONS))
        self.assertEqual(p.seconds(key,'training',800),p.TRAINING_SECONDS)
        self.assertEqual(p.seconds(key,'diagnostic',800),800)
        self.assertEqual(p.seconds('0'*64,'training',800),43200)
        self.assertEqual(p.seconds('0'*64,'capture',800),800)

if __name__=='__main__':unittest.main()
