import unittest
from unittest.mock import patch
from collections import Counter
import prepare_replay219 as p

class Replay219Tests(unittest.TestCase):
    def test_exact_schedule_and_exposure(self):
        full=[f'full-{i}' for i in range(189)];native=[f'native-{i}' for i in range(60)]
        slots=p.schedule(full,native);counts=Counter(slots)
        self.assertEqual(len(slots),1758);self.assertEqual(len(counts),249)
        self.assertEqual(slots[-60:],native)
        self.assertEqual(Counter(counts[x] for x in full),{9:186,8:3})
        self.assertTrue(all(counts[x]==1 for x in native))
        self.assertEqual(slots,p.schedule(list(reversed(full)),native))
        self.assertEqual(sum(((i+1)*440)//16-(i*440)//16 for i in range(10)),275)

    def test_bad_sources(self):
        full=[f'f{i}' for i in range(189)];native=[f'n{i}' for i in range(60)]
        for f,n in [(full[:-1],native),(full[:-1]+[full[0]],native),(full,native[:-1]),(full,[full[0]]+native[1:])]:
            with self.assertRaises(ValueError):p.schedule(f,n)

    def test_output_collision_before_inputs(self):
        with self.assertRaisesRegex(ValueError,'output_collision_boundary'):p.prepare(p.ROOT)

    def test_source_pin_failure_does_not_create_output(self):
        target=p.ROOT/'.build/replay219-invalid-source-test.json'
        self.assertFalse(target.exists())
        with patch.object(p,'sha',return_value='changed'):
            with self.assertRaisesRegex(ValueError,'parent_changed'):p.prepare(target)
        self.assertFalse(target.exists())

if __name__=='__main__':unittest.main()
