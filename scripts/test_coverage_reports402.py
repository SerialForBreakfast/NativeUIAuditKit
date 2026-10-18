"""Check both native rectangle encodings and reject invalid geometry."""
import unittest
from coverage_reports402 import rectangle


class GeometryTests(unittest.TestCase):
    def test_array_and_object_are_equal(self):
        expected=dict(x=10,y=20,width=30,height=40)
        self.assertEqual(rectangle([10,20,30,40]),expected)
        self.assertEqual(rectangle(expected),expected)

    def test_invalid_shapes_fail(self):
        for value in ([1,2,3],[0,0,0,1],[0,0,float('nan'),1],dict(x=1),[True,0,1,1]):
            with self.assertRaises(ValueError):rectangle(value)



class CaptureVersionTests(unittest.TestCase):
    def test_report_accepts_both_validated_capture_versions(self):
        import coverage_reports402 as reports, native_coverage402 as coverage
        self.assertEqual(reports.CAPTURE_VERSIONS, ('native-hcf402-v1', coverage.CONTROLS_VERSION))


if __name__=='__main__':unittest.main()
