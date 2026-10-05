"""Scoped larger numerical-return adapter; original receiver limits unchanged."""
from pathlib import PurePosixPath
import synth05_receive as receiver
from focus_surface_intake import safe_members,require


def bounded_members(archive):
    result=[];seen=set();total=0;root=False
    for m in archive:
        if m.name in ('.','./'):
            require(m.isdir() and m.size==0 and not root,'unsafe_archive_root');root=True;continue
        require(len(result)<2000,'archive_member_limit')
        validated,size=safe_members([m])
        key=str(PurePosixPath(m.name)).casefold();require(key not in seen,'duplicate_archive_destination')
        seen.add(key);total+=size;require(total<=80_000_000,'archive_size_limit');result.extend(validated)
    return result,total


def receive(share,root,entries):
    original=receiver.bounded_members
    try:
        receiver.bounded_members=bounded_members
        return receiver.receive(share,root,entries)
    finally:receiver.bounded_members=original
