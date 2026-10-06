"""Prepare the frozen split-aware ARTWORK204 native campaign; no simulator mutation."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
from PIL import Image
from artwork200_campaign import TARGET, sha, write
from shared_transfer import document, require
from generator_asset_plan import inventory_metadata


def recipes():
    rows = []
    for subject in range(8):
        for theme in ('light', 'dark'):
            for density in ('low', 'high'):
                for condition in ('procedural', 't1', 't2'):
                    r = dict(id=f'art204-s{subject}-{theme}-{density}-{condition}', layout='grid',
                             theme=theme, density=density, seed=20400+subject, condition=condition,
                             family=f'artwork204-family-r1-s{subject}',
                             dataRole='train' if subject < 5 else 'validation' if subject < 7 else 'test')
                    if condition != 'procedural': r['assetID'] = f'artwork204-r1-s{subject}-v0-{condition}'
                    rows.append(r)
    return rows


def check(plan, catalog, inputs):
    require(set(plan) == {'schemaVersion','target','catalogSHA256','recipes'} and
            plan['schemaVersion'] == 'ios-artwork-campaign-v2' and plan['target'] == TARGET and
            plan['recipes'] == recipes() and plan['catalogSHA256'] == sha(inputs/'catalog.json'), 'split_plan')
    require(set(catalog) == {'schemaVersion','assets'} and
            catalog['schemaVersion'] == 'ios-generator-artwork-v2', 'split_catalog')
    assets = {a['id']: a for a in catalog['assets']}
    require(len(assets) == len(catalog['assets']) == 16 and
            set(assets) == {r['assetID'] for r in recipes() if 'assetID' in r}, 'split_assets')
    require(len({a['sha256'] for a in assets.values()}) == 16, 'duplicate_asset')
    for r in recipes():
        if 'assetID' not in r: continue
        a = assets[r['assetID']]
        require(a['ancestryGroup'] == r['family'] and a['dataRole'] == r['dataRole'] and
                a['rightsStatus'] == a['reviewStatus'] == 'verified' and
                a['rightsEvidence'] and a['reviewEvidence'], 'split_asset_role')
        require(a['path'] == a['id']+'.png', 'asset_path')
        p = inputs/a['path']
        require(p.resolve() == p.absolute() and p.is_file() and p.stat().st_size == a['bytes'] and
                sha(p) == a['sha256'], 'asset_bytes')
        with Image.open(p) as im:
            require(im.format == 'PNG' and im.size == (a['width'],a['height']) == (1216,832), 'asset_dimensions')
            im.load()
    return plan


def prepare(inventory, source, out):
    inventory, source, out = Path(inventory), Path(source), Path(out)
    require(not out.exists(), 'output_collision')
    data = inventory_metadata(inventory)
    wanted = {r['assetID']:r for r in recipes() if 'assetID' in r}
    selected = [a for a in data['resources'] if a['id'] in wanted]
    require(len(selected) == len({a['id'] for a in selected}) == 16, 'missing_assets')
    entries = []
    for a in sorted(selected,key=lambda a:a['id']):
        r = wanted[a['id']]
        require(a['dataRole'] == r['dataRole'] and a['ancestryGroups'] == [r['family']] and
                a['reviewStatus'] == a['rightsStatus'] == 'verified' and
                a['rightsEvidence'] and a['reviewEvidence'], 'unreviewed_asset')
        p = source/(a['id']+'.png')
        require(p.resolve() == p.absolute() and p.is_file() and p.stat().st_size == a['bytes'] and
                sha(p) == a['sha256'], 'source_bytes')
        with Image.open(p) as im:
            require(im.format == 'PNG' and im.size == (1216,832), 'source_dimensions'); im.load()
        entries.append(dict(id=a['id'],path=p.name,sha256=a['sha256'],bytes=a['bytes'],width=1216,height=832,
                            ancestryGroup=r['family'],dataRole=r['dataRole'],rightsStatus='verified',
                            reviewStatus='verified',rightsEvidence=a['rightsEvidence'],reviewEvidence=a['reviewEvidence']))
    out.mkdir(parents=True)
    for a in entries: shutil.copyfile(source/a['path'],out/a['path'])
    write(out/'catalog.json',dict(schemaVersion='ios-generator-artwork-v2',assets=entries))
    write(out/'campaign.json',dict(schemaVersion='ios-artwork-campaign-v2',target=TARGET,
                                 catalogSHA256=sha(out/'catalog.json'),recipes=recipes()))
    check(document(out/'campaign.json'),document(out/'catalog.json'),out)
    return dict(frames=96,roles=dict(Counter(r['dataRole'] for r in recipes())),
                inventorySHA256=sha(inventory),planSHA256=sha(out/'campaign.json'))


def completed_shard(work, native_output, inputs, shard):
    """A terminal test plus sealed bytes permits skipping, never ambiguous retry."""
    import continue_ios_reconstruction as native
    result=document(work/f'shard-{shard}-result.json')
    require(result.get('exitCode')==0 and not result.get('timeout') and
            sha(work/f'shard-{shard}.log')==result['logSHA256'],'prior_shard_failed')
    native.require_test_pass(work/f'shard-{shard}.log','testArtworkCampaign')
    receipt=document(native_output/f'shard-{shard}.json')
    require(receipt.get('complete') is True and receipt['schemaVersion']=='ios-artwork-shard-v2' and
            receipt['shard']==shard and receipt['planSHA256']==sha(inputs/'campaign.json') and
            len(receipt['frames'])==48,'prior_shard_partial')
    for r,record in zip(recipes()[shard*48:(shard+1)*48],receipt['frames']):
        require(record==document(native_output/(r['id']+'.record.json')) and record['recipe']==r and
                record['dataRole']==r['dataRole'] and record['planSHA256']==sha(inputs/'campaign.json') and
                record['imageSHA256']==sha(native_output/(r['id']+'.png')) and
                record['sidecarSHA256']==sha(native_output/(r['id']+'.json')),'prior_shard_changed')


def execute(inputs, work, resume=False):
    """Assigned exact-target capture; reuse the qualified native runner and r6 I/O."""
    import plistlib
    import continue_ios_reconstruction as native
    from artwork200_campaign import validate
    inputs,work=native.local(inputs),native.local(work)
    check(document(inputs/'campaign.json'),document(inputs/'catalog.json'),inputs)
    require(work.is_dir() if resume else not work.exists(),'execution_collision')
    devices=json.loads(native.command(['xcrun','simctl','list','devices','available','-j']))
    selected=[(runtime,d) for runtime,ds in devices['devices'].items() for d in ds if d['udid']==TARGET]
    require(len(selected)==1 and selected[0][1]['state']=='Booted' and
            'iOS-26-5' in selected[0][0], 'wrong_or_unready_runtime')
    require(shutil.disk_usage(native.ROOT).free >= 20*1024**3,'storage_reserve')
    products=native.ROOT/'.build/asset200-ios/Build/Products'
    base=products/'GeneratorRunnerTests_iphonesimulator27.0-arm64-x86_64.xctestrun'
    app=products/'Debug-iphonesimulator/GeneratorRunner.app'
    require(plistlib.loads((app/'Info.plist').read_bytes())['CFBundleIdentifier']==native.BUNDLE,'app_identity')
    run=plistlib.loads(base.read_bytes())
    pins={str(p.relative_to(app)):sha(p) for p in app.rglob('*') if p.is_file()}
    staged='art204_'+work.name+'_input';output='art204_'+work.name+'_output'
    if resume:
        old=document(work/'preflight.json')
        require(old['buildHashes']==pins and old['sourceHashes']==native.sources() and
                old['planSHA256']==sha(inputs/'campaign.json'),'resume_pins_changed')
        prior=document(work/'staging.json')
        require(prior['input']==staged and prior['output']==output,'resume_staging_changed')
    else:
        work.mkdir(parents=True);(work/'tmp').mkdir()
        write(work/'preflight.json',dict(target=selected[0],xcode=native.command(['xcodebuild','-version']),
            sourceHashes=native.sources(),buildHashes=pins,planSHA256=sha(inputs/'campaign.json'),
            storageBudgetBytes=20*1024**3))
        native.command(['xcrun','simctl','install',TARGET,str(app)],120)
        before=native.container()
        require(not (before/'Documents'/output).exists(),'native_output_collision')
        native.copy_new(inputs,before/'Documents'/staged)
        write(work/'staging.json',dict(container=str(before),input=staged,output=output))
    for shard in (0,1):
        before=native.container()
        current=Path(native.command(['xcrun','simctl','get_app_container',TARGET,native.BUNDLE,'app']))
        require(all(sha(current/name)==digest for name,digest in pins.items()),'installed_build_changed')
        require(all(sha(before/'Documents'/staged/p.name)==sha(p) for p in inputs.iterdir()),'staged_input_changed')
        if (work/f'shard-{shard}-result.json').exists():
            require(resume,'unexpected_existing_result')
            completed_shard(work,before/'Documents'/output,inputs,shard)
            continue
        require(not (work/f'shard-{shard}.log').exists() and
                not (before/'Documents'/output/f'shard-{shard}.json').exists(),'ambiguous_prior_attempt')
        target=run['GeneratorRunnerTests']
        target['OnlyTestIdentifiers']=['GenerateDatasetTests/testArtworkCampaign']
        target.setdefault('EnvironmentVariables',{}).update(NUIAK_ARTWORK200_CAMPAIGN=staged,
            NUIAK_ARTWORK200_OUTPUT=output,NUIAK_ARTWORK200_SHARD=str(shard))
        config=products/f'art204-{work.name}-{shard}.xctestrun'
        with config.open('xb') as f:plistlib.dump(run,f)
        log=native.run_logged(['xcodebuild','test-without-building','-xctestrun',str(config),
            '-destination','platform=iOS Simulator,id='+TARGET,'-parallel-testing-enabled','NO',
            '-only-testing:GeneratorRunnerTests/GenerateDatasetTests/testArtworkCampaign',
            '-resultBundlePath',str(work/f'shard-{shard}.xcresult')],work,f'shard-{shard}',240)
        native.require_test_pass(log,'testArtworkCampaign')
    after=native.container()  # Never reuse the pre-install container UUID for retrieval.
    native.copy_new(after/'Documents'/output,work/'frames')
    result=validate(work/'frames',inputs)
    write(work/'validation.json',result)
    write(work/'retrieval.json',dict(container=str(after),frames=96,hashVerified=True,
        cleanup='test-owned windows released; no status overrides; native originals retained',
        modelGate='not_assessed',trainingAdmission='pending semantic review'))


def qualify(frames, inputs, out):
    from artwork200_campaign import validate
    from annotation_schema_validation import validate_sidecar_structure
    from validate_reconstructed_corpus import check_schema
    result=validate(frames,inputs)
    require(result['dataRole']=='recipe_bound','wrong_qualification_lane')
    for r in result['rows']:
        a=document(Path(frames)/(r['id']+'.json'))
        schema=document(validate_sidecar_structure(a));check_schema(a,schema,schema)
        require(a['generatorProfile']['generatorVersion']=='asset204-campaign-v2' and
                a['generatorProfile']['templateFamily']=='MediaCardGrid' and
                a['generatorProfile']['seed']==r['seed'],'generator_identity')
        require(a['image']['scale']==3 and a['image']['platform']=='iOS','platform_scale')
        for e in a['elements']:
            p=e['boundsPixels'];q=e['boundsPoints']
            require(all(abs(p[k]-3*q[k])<=1 for k in ('x','y','width','height')),'coordinate_scale')
    result['sidecarSchemasVerified']=96
    result['roles']=dict(Counter(r['dataRole'] for r in result['rows']))
    result['trainingAdmission']='awaiting visual review; test role is development diagnostic, not final holdout'
    write(out,result)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    commands=p.add_subparsers(dest='command',required=True)
    prep=commands.add_parser('prepare');prep.add_argument('inventory',type=Path)
    prep.add_argument('source',type=Path);prep.add_argument('out',type=Path)
    run=commands.add_parser('execute');run.add_argument('inputs',type=Path);run.add_argument('out',type=Path)
    run.add_argument('--resume',action='store_true',help='Verify and skip completed shards; never retry a failed or ambiguous shard')
    q=commands.add_parser('qualify');q.add_argument('frames',type=Path);q.add_argument('inputs',type=Path);q.add_argument('out',type=Path)
    rv=commands.add_parser('review');rv.add_argument('frames',type=Path);rv.add_argument('out',type=Path)
    a=p.parse_args()
    if a.command=='execute':execute(a.inputs,a.out,a.resume)
    elif a.command=='qualify':qualify(a.frames,a.inputs,a.out)
    elif a.command=='review':
        from artwork200_campaign import review_sheet
        selected=[r for r in recipes() if r['theme']==('light' if r['seed']%2==0 else 'dark') and
                  r['density']==('low' if r['seed']%4<2 else 'high') and r['condition']==('t1' if r['seed']%2==0 else 't2')]
        review_sheet(a.frames,a.out,selected)
    else:print(json.dumps(prepare(a.inventory,a.source,a.out),indent=2))
