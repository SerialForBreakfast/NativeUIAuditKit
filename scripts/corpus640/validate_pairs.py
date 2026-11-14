"""Verify focus observations and strict matched pairs in a completed packet."""
import argparse
import hashlib
import json
from pathlib import Path
import pairing

ROOT=Path(__file__).resolve().parents[2]
SOURCE_SHA256='73ff3834488aae24ade150fb171eec79102181460c97ba406ee7bde46096d1d5'
ROLE='provisional train-only; all shared derivatives remain training; Q-packets stay qualification-only'
LINEAGE='CORPUS640/UIKit-native-procedural-v1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(value):
    p=(ROOT/value).resolve()
    if p==ROOT or not p.is_relative_to(ROOT):raise ValueError('Path must stay inside the project')
    return p

def validate(packet):
    casepath=packet/'cases.json';receiptpath=packet/'capture-receipt.json'
    cases=json.loads(casepath.read_text());receipt=json.loads(receiptpath.read_text())
    if len(cases)!=300 or not receipt.get('completed') or receipt.get('frames')!=300 or receipt.get('renderer')!='live simctl screenshot':raise ValueError('Incomplete or unqualified packet')
    if receipt.get('sourceSHA256')!=SOURCE_SHA256 or receipt.get('outputBytes',2_000_000_001)>2_000_000_000:raise ValueError('Source identity or output budget mismatch')
    frames=[];excluded=[];states={'focused':0,'no_focus':0,'unknown':0}
    for c in cases:
        if c['sourceLineage']!=LINEAGE or c['constructorSHA']!=SOURCE_SHA256 or c['exeSHA']!=receipt['executableSHA256']:raise ValueError('Source lineage mismatch')
        obs=c.get('focusObservation')
        valid=(isinstance(obs,dict) and obs.get('source')=='UIFocusSystem.focusedItem' and obs.get('state') in states and c.get('focusObservationAfter')==obs and c.get('nativeFocusBefore')==obs)
        if not valid:obs={'state':'unknown','id':None}
        state=obs['state'];states[state]+=1
        for k in ('image','repeatImage'):
            p=inside(c[k]['path'])
            if sha(p)!=c[k]['sha256']:raise ValueError('Image hash mismatch')
        if c.get('partialReasons'):
            excluded.append({'id':c['id'],'reason':'partial_native_targets','focusState':state});continue
        if c['image']['sha256']!=c['repeatImage']['sha256']:
            excluded.append({'id':c['id'],'reason':'repeat_pixels_unstable','focusState':state});continue
        frames.append({'id':c['id'],'group':c['layoutGroup'],'role':ROLE,'contentVariant':c.get('contentVariant'),'focusState':state,'focusID':obs.get('id'),'controls':[{'id':t['id'],'bounds':t['box_src_px']} for t in c['targets']],'image':{'path':str(inside(c['image']['path'])),'sha256':c['image']['sha256']}})
    audit=pairing.build(frames)
    return {'version':'corpus640-focus-pairs-v1','sourceCasesSHA256':sha(casepath),'captureReceiptSHA256':sha(receiptpath),'role':ROLE,'trainingAdmitted':False,'states':states,'excluded':excluded,'eligiblePairs':sum(p['eligible'] for p in audit['pairs']),'pairAudit':audit}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--packet',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();packet=inside(args.packet);output=inside(args.output)
    if output.exists():parser.error('Output exists; preserve the previous verification')
    report=validate(packet);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')
    print('Verified',len(report['pairAudit']['pairs']),'candidate pairs;',report['eligiblePairs'],'eligible')

if __name__=='__main__':main()
