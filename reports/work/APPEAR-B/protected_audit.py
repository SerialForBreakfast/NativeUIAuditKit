"""Keep known native and visual diagnostics protected; no new model execution."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from focus_dataset_contract import digest, image, pixel_digest
from focus_mixed_assembly import checked, reference
from focus_appearance_proposal import components

proposal=json.loads((HERE/'proposal.json').read_text())
assert proposal['proposalSHA256']==digest({k:v for k,v in proposal.items() if k!='proposalSHA256'})
spec_path=ROOT/'reports/work/OS-FOCUS-03/challenge.json'; spec=json.loads(spec_path.read_text())
path=checked(spec['manifest']); checked(spec['review']); doc=json.loads(path.read_text())
assert doc['manifestSHA256']==digest({k:v for k,v in doc.items() if k!='manifestSHA256'})
for name,sha in doc['sourceHashes'].items(): checked({'path':doc['sourceRoot']+'/'+name,'sha256':sha})
extra=[]
for pair in doc['pairs']:
    for role,label in [('focused',1),('unfocused',0)]:
        f=pair['frames'][role]
        raw={'path':doc['sourceRoot']+'/'+f['path'],'sha256':f['sha256']}
        crop={'path':str((path.parent/f['crop']).relative_to(ROOT)),'sha256':f['cropSHA256']}
        for r in (raw,crop): image(ROOT,r); r['pixelSHA256']=pixel_digest(ROOT,r)
        assert raw['pixelSHA256']==f['pixelSHA256']
        extra.append({'id':'protected-remotes:'+pair['pair_id']+':'+role,'sourceID':'remotes',
            'pairID':pair['pair_id'],'sourceKind':doc['sourceKind'],'split':'challenge',
            'relatedGroup':doc['lineage'],'intrinsicGroup':doc['lineage'],'recipeSeed':None,
            'frame':raw,'crop':crop,'label':label,'proposedRole':'known-retention-challenge'})
joined=components(proposal['samples']+extra)
known={r[k]['pixelSHA256'] for r in proposal['samples']+extra for k in ('frame','crop')}
visual=[]
source_protocol=json.loads((ROOT/'reports/work/FOCUS-VISUAL-03/protocol.json').read_text())
for surface,s in source_protocol['sources'].items():
    p=checked(s['protocol']); checked(s['referenceReport']); v=json.loads(p.read_text())
    assert v['protocolSHA256']==digest({k:x for k,x in v.items() if k!='protocolSHA256'})
    frames={x['path']:{'path':x['path'],'sha256':x['sha256']} for x in v['samples']}
    for f in frames.values(): image(ROOT,f); f['pixelSHA256']=pixel_digest(ROOT,f)
    visual.append({'surface':surface,'protocol':reference(p),'role':'known-visual-development-only',
                   'baseBoxes':sum(x['variant']=='base' for x in v['samples']),
                   'frames':list(frames.values()),'pixelOverlaps':sum(f['pixelSHA256'] in known for f in frames.values()),
                   'trainingEligible':False,'independence':'unknown-journey; previously inspected/model-scored'})
out={'version':'appearance-protected-evidence-audit-v1','proposal':reference(HERE/'proposal.json'),
     'remotesInputs':[reference(spec_path),spec['manifest'],spec['review']], 'remotesSamples':extra,
     'crossPartitionConflicts':[g for g in joined['components'] if g['crossPartitionConflict']],
     'visualDiagnostics':visual,'untouchedAppearanceValidation':[],'untouchedFinalChallenge':[],
     'trainingEligible':False,'launchEligible':False}
out['auditSHA256']=digest(out)
with (HERE/'protected-evidence.json').open('x') as f: json.dump(out,f,indent=2)
print(json.dumps({'remotesPairs':len(extra)//2,'conflicts':len(out['crossPartitionConflicts']),
                  'visual':[{k:v for k,v in r.items() if k in ('surface','baseBoxes','pixelOverlaps')} for r in visual]}))
