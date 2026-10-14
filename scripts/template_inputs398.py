"""Stable input checks shared by template execution, independent of authoring."""
from pathlib import Path
import research_queue as q


def pin(path):
    path=Path(path)
    return dict(path=q.relative(path),sha256=q.digest(path))


def checked(ref):
    q.check_pin(ref)
    path=q.local_path(q.ROOT,ref['path'])
    q.require(path.is_file(),'input_missing:'+ref['path'])
    q.require(q.digest(path)==ref['sha256'],'input_changed:'+ref['path'])
    return path
