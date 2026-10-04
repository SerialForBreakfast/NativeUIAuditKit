"""Real CLI contract tests; use a caller-selected existing release tool, no capture."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / os.environ.get('TRANSITION_TEST_BASE', 'reports/work/TRANSITION-SHADOW-106/artifacts')
TOOL = ROOT / '.build/arm64-apple-macosx/release/TransitionShadowTool'


class ConsumerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = BASE / os.environ.get('TRANSITION_TEST_OUTPUT', 'contract-tests-01')
        cls.out.mkdir(exist_ok=False)
        reference = json.loads((BASE / 'parity-inputs/reference.json').read_text())
        cls.request = dict(schemaVersion=1,mode='encode',root=str(ROOT),pairs=reference['examples'][:1])
        cls.request['mode'] = 'encode'
        cls.bundle = BASE / 'bundle'
        cls.manifest = hashlib.sha256((cls.bundle / 'contract.json').read_bytes()).hexdigest()

    def run_case(self, request=None, expected=0, bundle=None, digest=None, raw=None):
        name = self.id().split('.')[-1]
        path = self.out / (name + '.json')
        path.write_text(raw if raw is not None else json.dumps(request or self.request))
        reply = self.out / (name + '-reply.json')
        run = subprocess.run([str(TOOL), '--bundle', str(bundle or self.bundle),
            '--manifest-sha256', digest or self.manifest, '--request', str(path),
            '--output', str(reply)], capture_output=True, text=True, timeout=60)
        (self.out / (name + '-execution.json')).write_text(json.dumps(
            dict(exitCode=run.returncode, stderr=run.stderr)))
        self.assertEqual(run.returncode, expected, run.stderr)
        return json.loads(reply.read_text()) if reply.exists() else None

    def changed(self):
        return copy.deepcopy(self.request)

    def test_good_encode(self):
        result = self.run_case()
        self.assertFalse(result['modelLoaded'])
        self.assertEqual(result['results'][0]['state'], 'encoded')

    def test_off_never_loads_pixels_or_model(self):
        request = self.changed(); request['mode'] = 'off'
        request['pairs'][0]['before']['path'] = str(self.out / 'absent.png')
        result = self.run_case(request, bundle=self.out / 'absent-model')
        self.assertFalse(result['modelLoaded'])
        self.assertEqual(result['results'][0]['state'], 'skipped')
        self.assertNotIn('probability', result['results'][0])

    def test_real_model_scores(self):
        request = self.changed(); request['mode'] = 'score'
        result = self.run_case(request)
        self.assertTrue(result['modelLoaded'])
        self.assertEqual(result['results'][0]['state'], 'scored')

    def test_wrong_hash(self):
        request = self.changed(); request['pairs'][0]['before']['sha256'] = '0'*64
        result = self.run_case(request, expected=1)
        self.assertEqual(result['results'][0]['error'], 'changedBytes')

    def test_missing_image(self):
        request = self.changed(); request['pairs'][0]['before']['path'] = str(self.out / 'missing.png')
        self.assertEqual(self.run_case(request, expected=1)['failed'], 1)

    def png_case(self, mode, size, expected, orientation=None):
        path = self.out / (self.id().split('.')[-1] + '.png')
        image = Image.new(mode, size)
        kwargs = {}
        if orientation:
            exif = image.getexif(); exif[274] = orientation; kwargs['exif'] = exif
        image.save(path, **kwargs)
        request = self.changed()
        request['pairs'][0]['before'] = dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        result = self.run_case(request, expected=1)
        self.assertEqual(result['results'][0]['error'], expected)

    def test_viewport_mismatch(self): self.png_case('RGB', (20,20), 'viewportChanged')
    def test_transparent_rejected(self): self.png_case('RGBA', (20,20), 'unsupportedImage')
    def test_grayscale_rejected(self): self.png_case('L', (20,20), 'unsupportedImage')
    def test_oriented_rejected(self): self.png_case('RGB', (20,20), 'unsupportedImage', 6)
    def test_oversized_dimensions(self): self.png_case('RGB', (5000,4001), 'unsupportedImage')

    def test_corrupt_png(self):
        path = self.out / 'corrupt.png'; path.write_bytes(b'\x89PNG\r\n\x1a\ninvalid')
        request = self.changed(); request['pairs'][0]['before'] = dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(self.run_case(request, expected=1)['results'][0]['error'], 'unsupportedImage')

    def test_outside_root(self):
        request = self.changed(); request['root'] = str(self.out)
        self.assertEqual(self.run_case(request, expected=1)['results'][0]['error'], 'invalidPath')

    def test_symlink_image(self):
        path = self.out / 'link.png'; path.symlink_to(self.request['pairs'][0]['before']['path'])
        request = self.changed(); request['pairs'][0]['before']['path'] = str(path)
        self.assertEqual(self.run_case(request, expected=1)['results'][0]['error'], 'invalidPath')

    def test_duplicate_pair(self):
        request = self.changed(); request['pairs'] *= 2
        self.run_case(request, expected=2)

    def test_unknown_fields(self):
        request = self.changed(); request['pairs'][0]['label'] = 'changed'
        self.run_case(request, expected=2)

    def test_unsupported_version(self):
        request = self.changed(); request['schemaVersion'] = 2
        self.run_case(request, expected=2)

    def test_unknown_backend_request(self):
        request = self.changed(); request['backend'] = 'gpu'
        self.run_case(request, expected=2)

    def test_duplicate_json_keys(self):
        self.run_case(raw='{"schemaVersion":1,"schemaVersion":1}', expected=2)

    def test_malformed_json(self): self.run_case(raw='{', expected=2)

    def test_batch_bound(self):
        request = self.changed(); request['pairs'] = [dict(request['pairs'][0], id=str(i)) for i in range(129)]
        self.run_case(request, expected=2)

    def test_wrong_manifest_hash(self):
        request = self.changed(); request['mode'] = 'score'
        self.run_case(request, expected=2, digest='0'*64)

    def test_tampered_model(self):
        bundle = self.out / 'tampered'; shutil.copytree(self.bundle, bundle)
        (bundle / 'FocusTransitionChange.mlmodelc/extra').write_bytes(b'changed')
        request = self.changed(); request['mode'] = 'score'
        self.run_case(request, expected=2, bundle=bundle)

    def test_unsupported_model_contract(self):
        bundle = self.out / 'wrong-contract'; shutil.copytree(self.bundle, bundle)
        path = bundle / 'contract.json'; contract = json.loads(path.read_text()); contract['inputEncoding'] = 'wrong'
        path.write_text(json.dumps(contract)); request = self.changed(); request['mode'] = 'score'
        self.run_case(request, expected=2, bundle=bundle, digest=hashlib.sha256(path.read_bytes()).hexdigest())

    def test_output_collision(self):
        path = self.out / (self.id().split('.')[-1] + '-reply.json'); path.write_bytes(b'preserve')
        # Fatal collision leaves the preexisting non-JSON bytes untouched.
        with self.assertRaises(json.JSONDecodeError): self.run_case(expected=2)
        self.assertEqual(path.read_bytes(), b'preserve')


if __name__ == '__main__': unittest.main()
