"""Receive the named TTR archive offer. Do not admit data or run received code."""
import shutil
from pathlib import Path
import research_queue as q
import shared_transfer as transfer
from synth05_receive import receive as receive_archives


def run():
    transfer.mounted()
    root=q.ROOT/'reports/work/FOCUS372/intake-20261013'
    root.mkdir(parents=True,exist_ok=True)
    q.require(shutil.disk_usage(root).free>6_000_000_000,'intake_storage_reserve')
    offer=dict(file='tvtestrig/transfer-focus372-20261013-v1.json',bytes=1422,
               sha256='31172d48df1c1b14284ea3998e8a0e58f1ecd727c42be8fcc61d9eed898e7633')
    receipts=[]
    def receive(item):
        tx=dict(version=1,requestID='focus372-20261013-v1',sharedPath=item['file'],
                localPath=q.relative(root/Path(item['file']).name),bytes=item['bytes'],sha256=item['sha256'],receiptPath=None)
        path=root/(Path(item['file']).name+'.transaction.json')
        if path.exists():q.require(q.load(path)==tx,'transaction_changed')
        else:q.save(path,tx)
        result=transfer.run(path,'receive',True)
        receipts.append(result['receiverReceipt'])
        print('Verified',Path(item['file']).name,item['bytes'],flush=True)
        return root/Path(item['file']).name
    op=receive(offer);doc=transfer.document(op)
    q.require(doc['version']==2 and doc['transfer_id']=='focus372-20261013-v1' and len(doc['files'])==7,'offer_identity')
    q.require(sum(x['bytes'] for x in doc['files'])<500_000_000,'transfer_budget')
    for item in doc['files']:
        q.require(item['file'].startswith('tvtestrig/focus372-20261013-v1-'),'offer_member')
        receive(item)
    entries=[(Path(x['file']).name,x['bytes'],x['sha256']) for x in doc['files'] if x['file'].endswith('.tar.gz')]
    receive_archives(transfer.SHARE/'tvtestrig',root,entries)
    extraction=q.load(root/'receipt.json')
    receipt=dict(version=1,transferID=doc['transfer_id'],receiver='research-host-NUIAK',
                 state='copied_and_verified',receipts=receipts,extraction=extraction,
                 trainingEligible=False,intake='Native semantics and capture-time build evidence remain separate checks.',
                 senderAction='Verify these receipts before removing only the named shared copies. Preserve originals.')
    rp=root/'handoff-receipt.json';q.save(rp,receipt)
    print('Local receipt:',q.relative(rp),flush=True)

if __name__=='__main__':run()
