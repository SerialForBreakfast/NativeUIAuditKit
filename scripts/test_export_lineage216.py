from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import export_lineage216 as exporter


class LineageTests(unittest.TestCase):
    def test_window_binding(self):
        parent=SimpleNamespace(width=100,height=200);crop=SimpleNamespace(width=50,height=50)
        exporter.check_window([0,0,50,50],parent,crop)
        for box in [[0,0,51,50],[-1,0,49,50],[60,0,110,50],[False,0,50,50]]:
            with self.assertRaises(ValueError):exporter.check_window(box,parent,crop)

    def test_collision_before_reading(self):
        with patch.object(exporter,'sha') as digest:
            with self.assertRaisesRegex(ValueError,'collision'):exporter.export(Path(__file__).absolute())
            digest.assert_not_called()


if __name__=='__main__':unittest.main()
