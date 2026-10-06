import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import scroll_resolution216 as s


class ScrollTests(unittest.TestCase):
    def test_selection_uses_labels_not_predictions(self):
        labels=[SimpleNamespace(read_text=lambda:'24 .5 .5 .01 .5\n'),
                SimpleNamespace(read_text=lambda:'18 .5 .5 .1 .1\n')]
        rows=[SimpleNamespace(image_id=str(i),label_path=p) for i,p in enumerate(labels)]
        self.assertEqual(s.select(SimpleNamespace(images=rows),24),rows[:1])

    def test_collision_and_changed_source_before_launch(self):
        with patch.object(s,'OUT',Path(__file__).parent),patch.object(s.subprocess,'run') as launch:
            with self.assertRaises(ValueError):s.run()
            launch.assert_not_called()
        with patch.object(s.a,'fresh'),patch.object(s.a,'sha',return_value='changed'),patch.object(s.subprocess,'run') as launch:
            with self.assertRaisesRegex(ValueError,'source_changed'):s.run()
            launch.assert_not_called()


if __name__=='__main__':unittest.main()
