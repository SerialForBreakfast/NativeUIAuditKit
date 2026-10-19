"""Kill only owned qualification processes around approval-store replacement."""
import json
import os
import subprocess
import sys
import threading
import unittest

import research_queue as q
import research_approval as approval
import workflow_transaction441 as transaction
from test_workflow_transaction441 import TransactionTests


CHILD = '''
import json, os, sys, time
from pathlib import Path
import research_queue as q
import workflow_transaction441 as transaction
queue, modules, entries, phase = sys.argv[1:]
replace=q.os.replace
def boundary(src,dst):
    if phase=='after':replace(src,dst)
    print('AT_BOUNDARY',flush=True)
    time.sleep(60)
    if phase=='before':replace(src,dst)
q.os.replace=boundary
transaction.qualify(Path(queue),json.loads(entries),Path(modules))
'''


class RecoveryTests(unittest.TestCase):
    setUp=TransactionTests.setUp
    pin=TransactionTests.pin
    spec=TransactionTests.spec
    entries=TransactionTests.entries

    def crash(self,phase):
        rows=self.entries()
        q.save(approval.path(self.queue),dict(version=approval.VERSION,jobs={},events=[]))
        original=approval.path(self.queue).read_bytes()
        env=dict(os.environ,PYTHONPATH=str(q.MODULES),PYTHONDONTWRITEBYTECODE='1')
        child=subprocess.Popen([sys.executable,'-B','-c',CHILD,str(self.queue),str(self.modules),json.dumps(rows),phase],
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
        timer=threading.Timer(20,child.kill);timer.start()
        try:
            self.assertEqual(child.stdout.readline().strip(),'AT_BOUNDARY')
            child.kill();child.communicate(timeout=10)
        finally:
            timer.cancel()
            if child.poll() is None:child.kill();child.communicate(timeout=10)
        self.assertLess(child.returncode,0)
        if phase=='before':self.assertEqual(approval.path(self.queue).read_bytes(),original)
        else:self.assertEqual(len(approval.load(self.queue)['events']),5)
        result=transaction.qualify(self.queue,rows,self.modules)
        self.assertEqual(result['storeWrites'],1 if phase=='before' else 0)
        self.assertEqual(len(approval.load(self.queue)['events']),5)
        self.assertEqual(len(approval.load(self.queue)['jobs']),5)

    def test_kill_before_atomic_replace(self):self.crash('before')
    def test_kill_after_atomic_replace_before_receipt(self):self.crash('after')


if __name__=='__main__':unittest.main()
