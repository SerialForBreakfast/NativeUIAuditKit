"""Measure bounded decode concurrency on verified study storage."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import plistlib
import subprocess
import time
from PIL import Image
import research_queue as q
OUT = None


def run():
    config = q.load(OUT/'config.json')
    receipt = q.load(q.ROOT/config['storage']['path'])
    q.require(q.digest(q.ROOT/config['storage']['path']) == config['storage']['sha256'], 'storage_receipt_changed')
    volume = Path(receipt['mountPoint'])
    q.require(volume == Path('/Volumes/training-drive') and volume.is_mount(), 'storage_unmounted')
    info = plistlib.loads(subprocess.check_output(['diskutil','info','-plist',str(volume)], timeout=10))
    q.require(info.get('VolumeUUID') == receipt['volumeUUID'], 'storage_identity_changed')
    workers = config['workers']; q.require(workers in (1,2,4), 'worker_count')
    paths = []
    for item in receipt['files']:
        path = Path(item['path'])
        q.require(path.resolve().is_relative_to(volume/'data/NUIAK/HCF357') and q.digest(path)==item['sha256'], 'storage_input_changed')
        paths.append(path)
    def decode(path):
        with Image.open(path) as image:
            image.load()
            return image.width * image.height
    samples = []
    for repeat in range(3):
        start = time.monotonic()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pixels = sum(pool.map(decode, paths*4))
        seconds = time.monotonic()-start
        samples.append(dict(seconds=seconds, images=len(paths)*4, pixels=pixels))
    q.save(OUT/'decode.json', dict(workers=workers, samples=samples, trainingStarted=False,
        limitation='Repeated four-image warm-cache decode. This tests decode concurrency, not cold disk bandwidth or full training throughput.'))
