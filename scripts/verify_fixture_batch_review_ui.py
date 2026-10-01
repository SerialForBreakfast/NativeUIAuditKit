"""Offscreen smoke of native proposals through the installed annotation editor."""
import argparse
import os
from pathlib import Path

import fixture_batch_review as native
import human_annotation_review as h
import human_review_editor as editor
from test_fixture_batch_review import ReviewTests


def verify(output):
    output=h.fresh(output); output.mkdir(parents=True)
    fixture=ReviewTests(); fixture.setUp(); previous=Path.cwd()
    try:
        fixture.attach()
        native.prepare([fixture.bundle],output/'qa',fixture.protected,count=1,exception_limit=0)
        os.environ['QT_QPA_PLATFORM']='offscreen'
        editor.configure(output/'runtime')
        from qtpy import QtWidgets
        app=QtWidgets.QApplication([])
        window=editor.window(output/'qa/audit/review/batch.json',output/'runtime',output/'qa/audit/combined-queue.json',1)
        window.show(); app.processEvents()
        assert len(window.imageList)==1
        window.loadFile(window.imageList[0]); app.processEvents()
        assert len(window.canvas.shapes)==1
        assert window.canvas.shapes[0].shape_type=='rectangle'
        assert not window.canvas.shapes[0].flags['confirmed'] and not window.dirty
        window.close()
        h.write(output/'result.json',dict(passed=True,checks=['native-batch-dispatch','sample-filter','prefilled-rectangle','approval-reset','clean-load']))
    finally:
        os.chdir(previous); fixture.tearDown()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('output')
    verify(p.parse_args().output)
