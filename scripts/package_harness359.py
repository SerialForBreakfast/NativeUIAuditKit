"""Package named, retained Fixture evidence for the existing TTR integration."""
import tarfile
import shutil
import research_queue as q


def main():
    root=q.ROOT/'reports/work/FOCUS359';dest=root/'nuiak-harness359-size-pilot.tar.gz'
    q.require(not dest.exists(),'output_collision')
    job=q.QUEUE/'jobs/generation354b-size-capture';attempt=job/'attempts/1'
    result=q.load(attempt/'result.json')
    q.require(result['status']=='complete' and q.outputs_intact(attempt,result),'pilot_integrity')
    files=[q.ROOT/'scripts'/n for n in ('research_queue.py','test_research_queue.py','generation352.py','dataset351.py','compare351.py','research_readiness.py')]
    files += [job/'spec.json',attempt/'result.json',q.QUEUE/'jobs/generation352-01-movement/spec.json',
        q.QUEUE/'jobs/generation352-00-capture/spec.json',q.QUEUE/'jobs/generation352-00-capture/attempts/1/result.json',root/'HarnessHandoff.md']
    files += sorted((attempt/'out/capture').iterdir())
    q.require(all(p.is_file() and not p.is_symlink() for p in files),'member_type')
    total=sum(p.stat().st_size for p in files)
    q.require(total<100_000_000 and shutil.disk_usage(root).free>total*2+q.STORAGE_MARGIN,'package_space')
    manifest=dict(version=1,request='ttr-unify-nuiak-round1-20261012-v1',trainingEligible=False,
        members=[dict(path=q.relative(p),bytes=p.stat().st_size,sha256=q.digest(p)) for p in files])
    q.save(root/'members.json',manifest)
    with tarfile.open(dest,'w:gz') as out:
        for p in files:out.add(p,arcname=q.relative(p),recursive=False)
        out.add(root/'members.json',arcname='members.json',recursive=False)
    with tarfile.open(dest) as inp:
        import hashlib
        for item in manifest['members']:
            member=inp.getmember(item['path'])
            q.require(member.isfile() and member.size==item['bytes'],'archive_member')
            q.require(hashlib.sha256(inp.extractfile(member).read()).hexdigest()==item['sha256'],'archive_hash')
    q.save(root/'package.json',dict(path=q.relative(dest),bytes=dest.stat().st_size,sha256=q.digest(dest),members=len(files),verified=True))


if __name__=='__main__':main()
