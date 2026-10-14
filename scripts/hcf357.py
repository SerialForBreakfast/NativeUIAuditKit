"""Inspect the retained HCF diagnostic without executing producer code."""
import hashlib
from pathlib import PurePosixPath
import shutil
import tarfile
from PIL import Image
import research_queue as q
from focus_surface_intake import safe_members
OUT = None


def unpack(archive, destination):
    q.require(not destination.exists(), 'output_collision')
    with tarfile.open(archive) as stream:
        # A root directory entry names no payload. All other entries use existing checks.
        raw = stream.getmembers()
        q.require(len(raw) <= 1000, 'archive_member_limit')
        members, total = safe_members(m for m in raw if not (m.isdir() and m.name in ('.', './')))
        q.require(total <= 100_000_000, 'expanded_budget')
        q.require(shutil.disk_usage(destination.parent).free >= total + q.STORAGE_MARGIN, 'storage_insufficient')
        destination.mkdir()
        for member in members:
            target = destination / str(PurePosixPath(member.name))
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with stream.extractfile(member) as source, target.open('xb') as output:
                    shutil.copyfileobj(source, output)
    return dict(members=len(members), expandedBytes=total)


def inspect(root):
    root = root.absolute()
    verified = []
    for line in (root/'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split(None, 1)
        name = name.strip(); path = PurePosixPath(name)
        q.require(not path.is_absolute() and path.parts and '..' not in path.parts, 'manifest_path')
        q.require(q.HASH.fullmatch(digest) and q.digest(root/name) == digest, 'member_hash')
        verified.append(name)
    images = {}
    for path in sorted(root.rglob('*.png')):
        with Image.open(path) as image:
            image.load(); rgb = image.convert('RGB')
            images[str(path.relative_to(root))] = dict(size=list(image.size), sha256=q.digest(path),
                decodedSHA256=hashlib.sha256(rgb.tobytes()).hexdigest())
    same = all(images['standard/synth-0_'+state+'.png']['decodedSHA256'] ==
               images['hcf/synth-0_'+state+'.png']['decodedSHA256'] for state in ('focused', 'unfocused'))
    from harvest_schema4_review import pair
    reviews = []
    for folder in ('standard', 'hcf', 'hcf_card_unmatched'):
        try:
            reviews.append(pair(root, folder+'/synth-0_metadata.json'))
        except (ValueError, OSError, KeyError, TypeError) as error:
            reviews.append(dict(path=folder, state='rejected', reason=str(error)))
    return dict(verifiedMembers=len(verified), images=images, sourceReviews=reviews, matchedProfilePixelsIdentical=same,
        trainingEligible=False, positiveVisibleHCFQualified=False,
        limitation='Matched button profiles have identical pixels. The artwork case lacks a Standard counterpart.')


def run():
    config = q.load(OUT/'config.json'); ref = config['archive']
    archive = q.ROOT/ref['path']; q.require(q.digest(archive) == ref['sha256'], 'archive_changed')
    root = OUT/'extracted'
    extraction = unpack(archive, root)
    q.save(OUT/'inspection.json', dict(extraction=extraction, **inspect(root)))
