"""Explicit local Vision integration check; not part of offline unit discovery."""
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw
from perception_benchmark import _iou


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'reports/work/VISION-ANNOTATION-COMPARE-01/native-check'
    output.mkdir(exist_ok=False)
    path = output / 'asymmetric.png'
    image = Image.new('RGB', (800, 600), 'black')
    ImageDraw.Draw(image).rectangle((80, 60, 380, 180), fill='white')
    image.save(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    frame = {'id': 'asymmetric', 'path': str(path), 'sha256': digest}
    request = {'version': 1, 'root': str(root), 'frames': [frame]}
    tool = root / '.build/debug-output/vision-annotation/probe'
    valid = subprocess.run([str(tool)], input=json.dumps(request), text=True,
                           capture_output=True, timeout=60)
    (output / 'valid.json').write_text(valid.stdout)
    assert valid.returncode == 0, valid.stderr
    result = json.loads(valid.stdout)['results'][0]
    assert not result['errors'], result['errors']
    overlap = max(_iou(p['bounds'], [80, 60, 300, 120]) for p in result['rectangles'])
    assert overlap > .95, overlap
    frame['sha256'] = '0' * 64
    invalid = subprocess.run([str(tool)], input=json.dumps(request), text=True,
                             capture_output=True, timeout=60)
    (output / 'invalid.stdout').write_text(invalid.stdout)
    (output / 'invalid.stderr').write_text(invalid.stderr)
    # A rejected image may be an explicit per-frame error or a failed invocation.
    rejected = invalid.returncode != 0 or bool(json.loads(invalid.stdout)['results'][0]['errors'])
    assert rejected
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    report = {'coordinateCheckIoU': overlap, 'changedHashRejected': rejected,
              'fixturePreserved': True}
    (output / 'result.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
