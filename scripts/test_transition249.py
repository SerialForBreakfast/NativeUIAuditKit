import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import torch
import transition249_worker as w


class PackageTests(unittest.TestCase):
    def test_collision_blocks_read(self):
        with patch.object(Path,'exists',return_value=True),patch.object(w,'read_package') as read:
            with self.assertRaisesRegex(ValueError,'output_collision'):w.run(Path('.'),Path('existing'))
            read.assert_not_called()

    def test_score_batches_preserve_order(self):
        class Net:
            def change_inputs(self,x):return x
            def change(self,x):return x[:,0,0,0,None]
        x=np.arange(11,dtype=np.float32).reshape(11,1,1,1)
        np.testing.assert_allclose(w.score(Net(),x),torch.sigmoid(torch.arange(11,dtype=torch.float32)).numpy())

    def test_invalid_manifest_version(self):
        with patch.object(Path,'read_text',return_value='{"version":"unknown"}'):
            with self.assertRaisesRegex(ValueError,'version'):w.read_package(Path('.'))


if __name__=='__main__':unittest.main()
