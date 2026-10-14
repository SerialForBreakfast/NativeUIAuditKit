"""Use resident preparation, training, and scoring functions without new science code."""
import time
from pathlib import Path
import shutil
import research_queue as q
from template_inputs398 import checked
import experiment_steps393 as steps

OUT=None


def contract():
    from template_adapters395 import resolve_inputs
    value=q.load(OUT.parents[2]/'spec.json')['template']
    return dict(value,inputs=resolve_inputs(value,OUT))


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=p.name,sha256=q.digest(p)) for p in sorted(OUT.iterdir()) if p.is_file()]))


def execute(function):
    start=time.monotonic()
    try:
        function()
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',modelAccepted=False,code=str(error)[:500],
                                             seconds=time.monotonic()-start))
        raise


def score():
    def work():
        cfg=contract();inputs=cfg['inputs']
        steps.score_at(dict(manifest=inputs['manifest'],model=inputs['model'],batchSize=cfg['parameters']['batchSize']),
                       checked(inputs['prepared']),checked(inputs['tensors']),OUT)
    execute(work)


def report():
    def work():
        steps.report_at(checked(contract()['inputs']['predictions']),OUT);receipt()
    execute(work)


def native():
    def work():
        cfg=contract()
        for ref in cfg['inputs'].values():checked(ref)
        if cfg['id']=='T06':
            import hcf_factor_train376 as adapter
            import hcf_study371 as study
            study.OUT=OUT
            membership,=study.dependency('crops.json')
            declared=q.load(checked(cfg['inputs']['membership']))
            if declared.get('version')=='crop-membership-plan-v1':
                fields=('id','role','profile','group','label')
                q.require([{k:r[k] for k in fields} for r in membership['rows']]==declared['rows'],
                          'training_membership_mismatch')
            else:q.require(membership==declared,'training_membership_mismatch')
            adapter.OUT=OUT;adapter.train()
        else:
            import hcf_study371 as adapter
            adapter.OUT=OUT
            (adapter.admit if cfg['id']=='T04' else adapter.prepare_crops)()
        refs=[r for dep in q.load(OUT/'dependencies.json') for r in dep['outputs']]
        for ref in refs:checked(ref)
        q.save(OUT/'sources.json',refs)
    execute(work)


def capture():
    def work():
        cfg=contract()
        if 'staging' in cfg['inputs']:
            import direct_tvos_capture as capture
            stage=q.load(checked(cfg['inputs']['staging']))
            q.require(stage.get('version')=='simulator-staging-v1','staging_version')
            root=Path(stage['projectRoot']);folder=Path(stage['directory'])
            q.require(root.is_absolute() and root.name=='NativeUIAuditKit' and root.is_dir(),'staging_project')
            q.require(folder==root/'.build/debug-output/native-screenshots' and
                      not any(p.is_symlink() for p in (folder,*folder.parents)),'staging_path')
            q.require(shutil.disk_usage(root).free>100_000_000,'staging_space')
            capture.SCREENSHOT_STAGING=folder
            # Fail before changing the OS setting if the actual writer cannot save.
            from native343 import TARGET
            capture.capture_screenshot(TARGET,OUT/'writer-probe.png')
        import generation352
        generation352.OUT=OUT;generation352.run()
        artifact=q.load(OUT/'artifact.json')
        source=Path(artifact['path'])
        q.require(q.digest(source)==artifact['sha256'],'capture_receipt_changed')
        doc=q.load(source)
        q.require(doc.get('complete') is True and doc.get('cleanup') is True,'capture_incomplete')
        images=[];total=0
        folder=OUT/'verified-images';folder.mkdir()
        for index,frame in enumerate(doc['frames']):
            path=q.local_path(source.parent,frame['path'])
            q.require(q.digest(path)==frame['sha256'],'capture_image_changed')
            total+=path.stat().st_size
            q.require(total<=90_000_000,'capture_copy_budget')
            target=folder/f'{index}.png';shutil.copyfile(path,target)
            images.append(dict(path=str(target.relative_to(OUT)),sha256=q.digest(target)))
        q.save(OUT/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=images,
            cleanup=True,modelAccepted=False))
    execute(work)
