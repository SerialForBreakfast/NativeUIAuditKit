"""Resumable local delivery-to-review orchestration. No capture, inference or admission."""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import shutil
import uuid

from PIL import Image, ImageDraw
import human_annotation_review as h
import fixture_batch_review as batch
from fixture_recipe_coverage import map_catalog

VERSION='fixture-offline-plan-v1'


def catalog_review(path, root):
    """Keep producer ancestry; structural signatures describe diversity, not independence."""
    path=h.local(path); root=h.local(root); doc=h.read(path)
    refs=[]
    def check(record):
        p=h.local(root/record['path'])
        h.require(p.is_relative_to(root) and not p.is_symlink(),'unsafe_catalog_member')
        h.require(h.sha(p)==record['sha256'],'changed_catalog_member')
        if 'bytes' in record: h.require(p.stat().st_size==record['bytes'],'changed_catalog_size')
        refs.append(h.ref(p))
        return h.read(p) if p.suffix=='.json' else None
    coverage=map_catalog(doc,check)
    groups=defaultdict(list); structures=defaultdict(list); signatures={}
    for record in doc['recipes']:
        # Deliberately remove only appearance/seed; preserve layout/content choices.
        recipe=json.loads(json.dumps(record['recipe']))
        for key in ('seed','step_index','theme','recipe_hash'): recipe.pop(key,None)
        appearance=recipe.get('appearance',{}); appearance.pop('family_id',None)
        appearance.get('canvas',{}).pop('backgroundRGB',None)
        signature=h.digest(recipe)
        signatures[record['path']]=signature
        group=record.get('shared_source_group')
        h.require(isinstance(group,str) and group.strip(),'unknown_source_group')
        groups[group].append(record['path']); structures[signature].append(record['path'])
    # Exact same recipe bytes must join even differently named producer groups.
    parent={g:g for g in groups}
    def find(x):
        while parent[x]!=x: x=parent[x]
        return x
    owners={}
    for r in doc['recipes']:
        g=r['shared_source_group']
        for key in (('bytes',r['sha256']),('structure',signatures[r['path']])):
            if key in owners: parent[find(g)]=find(owners[key])
            else: owners[key]=g
    connected=defaultdict(list)
    for g,members in groups.items(): connected[find(g)].extend(members)
    return dict(version='fixture-source-role-review-v1',**h.FLAGS,catalog=h.ref(path),files=refs,
        coverage=coverage,structures=[dict(signature=k,recipes=sorted(v)) for k,v in sorted(structures.items())],
        groups=[dict(id=k,recipes=sorted(v),proposedRole='training_candidate_only_if_later_admitted',
                     roleReserved=None) for k,v in sorted(connected.items())],
        independentValidationGroupsEstablished=0,
        missingEvidence=['Reviewed structural/content ancestry against retained corpus.',
            'Separate validation source/layout/content group; theme or seed changes are insufficient.',
            'Rendered variation and body geometry qualification; source signatures are not pixel proof.'])


def geometry_review(batch_path, output):
    """Review all eligible frames; distinguish annotation rectangles from measured layout."""
    doc=batch.validate(batch_path); output=h.fresh(output); output.mkdir(parents=True)
    rows=[]; md=['# Geometry review — diagnostic only','',
        'Blue: native wrapper/layout. Orange: proposed annotation.',
        ('Measured rendered-body v1 is mapped; full/clipped bounds and provenance stay in the batch.'
         if doc['version']==batch.BODY_VERSION else 'Legacy wrapper proposals: rendered-body geometry is unavailable.'),
        '**Training hold:** verify solid-body enlargement, excluding shadow/glow. No automatic approval.','']
    for frame in doc['frames']:
        if frame['disposition']!='imported': continue
        source=h.checked(h.ROOT,frame['image'])
        with Image.open(source) as im:
            im.load(); im=im.convert('RGB'); im.thumbnail((1200,900))
            sx,sy=im.width/frame['size'][0],im.height/frame['size'][1]
            layout=im.copy(); annotation=im.copy()
            for c in frame['proposals']:
                x,y,w,ht=c['bounds']; rect=(x*sx,y*sy,(x+w)*sx,(y+ht)*sy)
                lx,ly,lw,lh=c.get('layoutWrapperBounds',c['bounds'])
                ImageDraw.Draw(layout).rectangle((lx*sx,ly*sy,(lx+lw)*sx,(ly+lh)*sy),outline='#00bfff',width=2)
                draw=ImageDraw.Draw(annotation); draw.rectangle(rect,outline='#ff9d00',width=2)
                draw.text((x*sx+3,y*sy+3),c['id']+(' FOCUS' if c['state']=='focused' else ''),fill='#ff9d00')
            canvas=Image.new('RGB',(im.width*2,im.height+30),'#202020')
            canvas.paste(layout,(0,30)); canvas.paste(annotation,(im.width,30))
            draw=ImageDraw.Draw(canvas);draw.text((5,8),'Native wrapper/layout',fill='#00bfff')
            draw.text((im.width+5,8),'Annotation proposal - body alignment unverified',fill='#ff9d00')
            dest=output/(frame['editorStem']+'.png');canvas.save(dest)
        sizes={(c['bounds'][2],c['bounds'][3]) for c in frame['proposals']}
        row=dict(frameID=frame['id'],source=frame['image'],overlay=h.ref(dest),
            wrapperRole='control_wrapper',annotationRole=('rendered_control_body' if doc['version']==batch.BODY_VERSION else 'control_wrapper_proposal'),
            renderedBody=('measured' if doc['version']==batch.BODY_VERSION else 'unavailable_unbound_schema'),visualAlignment='human_verification_required',
            uniformSizes=len(sizes)==1,duplicateOf=frame['duplicateOf'],trainingEligible=False)
        rows.append(row)
        md.extend([f'## {frame["number"]:03d} {frame["id"]}','',
            f'![Layout and annotation proposals]({dest})','',
            'Uniform bounds: '+str(row['uniformSizes'])+'. This alone does not prove a defect.',''])
    result=dict(version='fixture-geometry-review-v1',**h.FLAGS,batch=h.ref(batch_path),frames=rows,
        gate='held_pending_rendered_body_alignment',automatedGeometryAcceptance=False)
    h.write(output/'geometry.json',result,sealed=True)
    (output/'review.md').write_text('\n'.join(md))
    return result


def tree_refs(root):
    """Freeze generated outputs, but allow human edits/revisions in the review copy."""
    refs=[]
    for p in sorted(root.rglob('*')):
        h.require(not p.is_symlink(),'output_symlink')
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if 'review-revisions' in rel.parts: continue
        if rel.parts[:3]==('audit','review','editor') and p.suffix=='.json': continue
        refs.append(h.ref(p))
    return refs


def source_markdown(review):
    lines=['# Source-role proposal — no reservations','',
        f'{review["coverage"]["recipeCount"]} recipes; {len(review["structures"])} theme/seed-normalized layout/content signatures; '
        f'{len(review["groups"])} conservative connected source groups.','',
        'Keep each connected group together on the training-candidate side only, subject to later admission. '
        'Do not fill training and independent validation slots with variants of the same group. '
        'A shared renderer is a conservative grouping constraint, not proof of identical screenshots.','']
    for group in review['groups']:
        lines.extend(['## '+group['id'],'','Proposed role: training candidate only. Actual reservation: none.',''])
        lines.extend('- `'+p+'`' for p in group['recipes'])
    lines.extend(['','## Still needed','']+['- '+s for s in review['missingEvidence']])
    return '\n'.join(lines)+'\n'


def fingerprint(plan):
    protected=h.ref(h.local(plan['protectedMetadata']))
    roots=[]
    for item in plan['bundles']:
        root=h.local(item['path']); refs=[]
        h.require(root.is_dir(),'bundle_missing')
        members=sorted(root.iterdir()); h.require(len(members)<=1024,'member_limit')
        for p in members:
            h.require(p.is_file() and not p.is_symlink(),'nonflat_bundle')
            h.require(p.stat().st_size<=32*1024*1024,'member_size_limit')
            refs.append(h.ref(p))
        roots.append(dict(id=item['id'],root=str(root),files=refs))
    result=dict(protected=protected,bundles=roots)
    if plan.get('catalog'):
        result['catalog']=catalog_review(plan['catalog']['path'],plan['catalog']['root'])
    return result


def run(plan_path, output):
    plan_path=h.local(plan_path); plan=h.read(plan_path); output=h.local(output)
    h.require(plan.get('version')==VERSION,'unsupported_plan')
    items=plan.get('bundles'); h.require(isinstance(items,list) and 1<=len(items)<=32,'bundle_limit')
    ids=[h.identifier(item['id']) for item in items]
    h.require(len(set(ids))==len(ids),'duplicate_bundle_id')
    roots=[h.local(item['path']) for item in items]
    h.require(len(set(roots))==len(roots),'duplicate_bundle_path')
    h.require(not any(output.is_relative_to(p) or p.is_relative_to(output) for p in roots),'output_source_overlap')
    count=plan.get('sampleCount',3); exceptions=plan.get('exceptionLimit',3); seed=plan.get('seed',42)
    h.require(type(count)is int and 1<=count<=256 and type(exceptions)is int and 0<=exceptions<=256
              and type(seed)is int,'invalid_sampling_limits')
    output.mkdir(parents=True,exist_ok=True)
    lock=output/'active.lock'
    try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError: raise ValueError('pipeline_locked: reconcile active/stale owner before retry')
    os.close(fd)
    try:
        inputs=fingerprint(plan)
        dependencies=['fixture_offline_pipeline.py','fixture_batch_review.py','fixture_recipe_coverage.py',
            'human_annotation_review.py','human_intake_audit.py','harvest_bundle_validation.py',
            'harvest_sidecar_v2.py','fixture_semantic_inventory.py','fixture_rendered_body.py','harvest_artwork.py','photos_focus_pilot.py']
        identity=dict(plan=h.ref(plan_path),inputs=inputs,categoryMap=h.ref(h.CATEGORY),
            implementation=[h.ref(h.ROOT/'scripts'/name) for name in dependencies])
        identity_path=output/'identity.json'
        if identity_path.exists(): h.require(h.read(identity_path)==identity,'changed_plan_sources_or_implementation')
        else:
            h.require(set(output.iterdir())=={lock},'unrecognized_existing_output')
            h.write(identity_path,identity)
        if 'catalog' in inputs and not (output/'source-groups.json').exists():
            h.write(output/'source-groups.json',inputs['catalog'])
        if 'catalog' in inputs:
            h.require(h.read(output/'source-groups.json')==inputs['catalog'],'changed_group_report')
            (output/'source-groups.md').write_text(source_markdown(inputs['catalog']))
        statuses=[]
        for item in items:
            directory=output/item['id']; directory.mkdir(exist_ok=True)
            receipt=directory/'completed.json'
            if receipt.exists():
                done=h.read(receipt)
                for ref in done['files']:h.checked(h.ROOT,ref)
                # Revalidate immutable native projection; review edits remain untouched.
                path=h.ROOT/done['attempt']/'native-review/batch.json'
                if path.exists(): batch.validate(path)
                statuses.append(done['status']);continue
            h.require(shutil.disk_usage(h.ROOT).free>2_000_000_000,'insufficient_space')
            attempts=list(directory.glob('attempt-*')); h.require(len(attempts)<20,'attempt_limit')
            attempt=directory/f'attempt-{len(attempts)+1:03d}'
            try:
                report=batch.prepare([item['path']],attempt,plan['protectedMetadata'],seed=seed,count=count,exception_limit=exceptions)
                native=attempt/'native-review/batch.json'
                if native.exists(): geometry_review(native,attempt/'geometry')
                status=dict(id=item['id'],state='rejected' if report['counts'].get('rejected') else 'review_ready',
                    report=h.ref(attempt/'report.json'),geometryGate='held_pending_rendered_body_alignment',
                    trainingEligible=False)
                done=dict(attempt=str(attempt.relative_to(h.ROOT)),status=status,files=tree_refs(attempt))
                # Atomic completion marker; interrupted attempts never overwrite an earlier one.
                temp=directory/('completed-'+uuid.uuid4().hex+'.pending.json');h.write(temp,done);temp.replace(receipt)
                statuses.append(status)
            except (ValueError,OSError,KeyError,TypeError) as error:
                attempt.mkdir(exist_ok=True)
                h.write(attempt/'orchestration-failure.json',dict(reason=str(error),state='retryable_in_fresh_attempt'))
                statuses.append(dict(id=item['id'],state='failed',reason=str(error),trainingEligible=False))
        h.require(fingerprint(plan)==inputs,'sources_changed_during_run')
        summary=dict(version='fixture-offline-run-v1',**h.FLAGS,items=statuses,
            counts=dict(Counter(r['state'] for r in statuses)),geometryGate='held_pending_rendered_body_alignment')
        temp=output/('status-'+uuid.uuid4().hex+'.pending.json');h.write(temp,summary);temp.replace(output/'status.json')
        md=['# Offline intake status','', '**Diagnostic only. Rendered-body alignment and training admission remain blocked.**','']
        for row in statuses:
            md.append(f'- {row["id"]}: {row["state"]}')
            if row.get('report'):
                folder=(h.ROOT/row['report']['path']).parent
                if (folder/'geometry/review.md').exists():
                    md.append(f'  - [Geometry review]({folder}/geometry/review.md)')
                md.append(f'  - [Intake report]({folder}/report.json)')
        if 'catalog' in inputs:md.extend(['',f'[Source-role proposal]({output}/source-groups.md)'])
        (output/'review.md').write_text('\n'.join(md)+'\n')
        return summary
    finally: lock.unlink()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    try:
        result=run(a.plan,a.output);print(json.dumps(result['counts']))
        return 2 if result['counts'].get('failed') or result['counts'].get('rejected') else 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Offline pipeline blocked: '+str(error));return 2


if __name__=='__main__':raise SystemExit(main())
