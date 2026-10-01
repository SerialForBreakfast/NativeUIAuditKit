"""Offscreen integration of the audit queue with the installed annotation app."""
import argparse
import os
from pathlib import Path

import human_annotation_review as h
import human_intake_audit as audit
import human_review_editor as editor
import test_human_annotation_review as fixtures


def verify(output):
    output = h.fresh(output)
    fixture = fixtures.ReviewTests()
    fixture.setUp()
    previous = Path.cwd()
    try:
        fixture.imported()
        report = audit.prepare(fixture.batch/'batch.json', output, count=1, exception_limit=0)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        editor.configure(output/'runtime')
        from qtpy import QtWidgets
        app = QtWidgets.QApplication([])
        window = editor.window(output/'review/batch.json', output/'runtime', output/'combined-queue.json', 1)
        window.show()
        app.processEvents()
        assert len(window.imageList) == 1
        window.loadFile(window.imageList[0])
        app.processEvents()
        assert len(window.canvas.shapes) == 1
        assert not any(s.flags.get('confirmed', False) for s in window.canvas.shapes)
        assert not window.dirty
        window.close()
        h.write(output/'ui-result.json', dict(passed=True, selected=report['selectedFrames'],
                                             checks=['queue-filter', 'prefilled-rectangle', 'approval-reset', 'clean-load']))
    finally:
        os.chdir(previous)
        fixture.tearDown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    verify(parser.parse_args().output)
