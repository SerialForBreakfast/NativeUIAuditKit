"""Isolated installed-editor rectangle controls/actual canvas interaction test."""
import argparse
import os

import human_annotation_review as h
import human_review_editor as launcher


def verify(index, output):
    output=h.fresh(output)
    batch=h.import_batch(index,output)
    original={p:h.sha(p) for p in (output/'editor').iterdir()}
    os.environ['QT_QPA_PLATFORM']='offscreen'
    launcher.configure(output/'runtime')
    from qtpy import QtWidgets,QtCore,QtTest
    app=QtWidgets.QApplication([])
    w=launcher.window(output/'batch.json',output/'runtime')
    w.resize(1400,850);w.show();app.processEvents()
    forbidden=[getattr(w.actions,n) for n in ('createMode','createCircleMode','createLineMode','createPointMode','createLineStripMode')]
    buttons=[b.defaultAction() for b in w.tools.findChildren(QtWidgets.QToolButton) if b.isVisible()]
    for a in forbidden:
        assert not a.isVisible() and not a.shortcuts()
        assert a not in buttons
    assert w.actions.createRectangleMode in buttons
    assert all('polygon' not in b.text().lower() for b in w.tools.findChildren(QtWidgets.QToolButton) if b.isVisible())
    assert w.actions.createRectangleMode.shortcuts()[0].toString()=='R'
    assert w.shape_dock.windowTitle()=='Control boxes'
    assert not w.actions.removePoint.isVisible() and not w.actions.removePoint.shortcuts()
    for mode in ('polygon','circle','point','line','linestrip'):
        try:w.toggleDrawMode(False,createMode=mode)
        except h.FocusDataError:pass
        else:raise AssertionError('nonrectangle drawing accepted')
    w.actions.createRectangleMode.trigger()
    assert w.canvas.createMode=='rectangle' and not w.canvas.editing()
    # Exercise the stock canvas' actual two-click rectangle creation. Suppress
    # only the label dialog in this generated software test; do not save a label.
    before=len(w.canvas.shapes)
    w.canvas.newShape.disconnect()
    QtTest.QTest.mouseClick(w.canvas,QtCore.Qt.LeftButton,pos=QtCore.QPoint(150,160))
    QtTest.QTest.mouseMove(w.canvas,QtCore.QPoint(300,250))
    QtTest.QTest.mouseClick(w.canvas,QtCore.Qt.LeftButton,pos=QtCore.QPoint(300,250))
    app.processEvents()
    assert len(w.canvas.shapes)==before+1
    shape=w.canvas.shapes[-1]
    assert shape.shape_type=='rectangle' and len(shape.points)==2
    assert shape.points[0].x()<shape.points[1].x() and shape.points[0].y()<shape.points[1].y()
    w.actions.editMode.trigger();assert w.canvas.editing()
    for f in batch['frames']:
        if f['disposition']=='imported':
            w.loadFile('editor/'+f['editorStem']+'.png');app.processEvents()
            assert all(not a.isVisible() and not a.shortcuts() for a in forbidden)
            w.actions.createRectangleMode.trigger();assert w.canvas.createMode=='rectangle'
            w.actions.editMode.trigger()
    w.loadFile('editor/004-frame-004.png');app.processEvents()
    assert w.grab().save(str(output/'rectangle-editor.png'))
    w.setClean();w.close();app.processEvents()
    assert original=={p:h.sha(p) for p in original}
    result=dict(version='human-review-rectangle-verification-v1',**h.FLAGS,frames=len(batch['frames']),
                toolbarRectangle=True,forbiddenDrawingModesRejected=5,twoClickRectangleCreated=True,
                sourceAndReviewFilesUnchanged=True,humanReviewPerformed=False)
    h.write(output/'rectangle-verification.json',result,sealed=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('index');p.add_argument('output');a=p.parse_args()
    print(verify(a.index,a.output))
