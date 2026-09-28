"""Exercise installed Qt selection/cross-frame clipboard on an isolated import."""
import argparse
import os

import human_annotation_review as h
import human_review_editor as launcher


def verify(index, output):
    output = h.fresh(output)
    batch = h.import_batch(index, output)
    originals = {p: h.sha(p) for p in (output / "raw").rglob("*") if p.is_file()}
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    launcher.configure(output / "runtime")
    from qtpy import QtWidgets, QtCore, QtTest, QtGui
    from labelme.shape import Shape
    app = QtWidgets.QApplication([])
    w = launcher.window(output / "batch.json", output / "runtime")
    w.resize(1400, 1000)
    w.show()
    app.processEvents()
    warnings = []
    # Only suppress blocking error dialogs in this isolated software test.
    w.clipboardWarning = warnings.append

    def load(number):
        w.setClean()
        w.loadFile(f"editor/{number:03d}-frame-{number:03d}.png")
        app.processEvents()

    def key(standard):
        w.activateWindow()
        w.canvas.setFocus()
        app.processEvents()
        QtTest.QTest.keySequence(w.canvas, QtGui.QKeySequence(standard))
        app.processEvents()

    load(7)
    assert not w.canvas.shapes
    w.pasteSelectedShape()
    assert len(warnings) == 1
    for i in range(3):
        shape = Shape(label="collectionItem", shape_type="rectangle", group_id=8 if i == 0 else None)
        shape.points = [QtCore.QPointF(100+i*250, 100), QtCore.QPointF(300+i*250, 220)]
        shape.flags = {k: k in ("confirmed", "focused") for k in h.SHAPE_FLAGS}
        w.loadShapes([shape], replace=False)
    assert not w.canvas.selectedShapes  # Checked visibility is not selection.
    for action in (w.actions.selectAllBoxes, w.actions.copy, w.actions.paste):
        assert action in w.menus.edit.actions()
        assert action in [b.defaultAction() for b in w.tools.findChildren(QtWidgets.QToolButton)]
    key(QtGui.QKeySequence.SelectAll)
    assert len(w.canvas.selectedShapes) == 3
    key(QtGui.QKeySequence.Copy)
    assert len(w._copied_shapes) == 3
    assert [s.group_id for s in w.canvas.shapes] == [8, 1, 2]
    assert all(s.flags["confirmed"] for s in w.canvas.shapes)
    source_path = output / "editor/007-frame-007.json"
    assert w.saveLabels(str(source_path))
    source_hash = h.sha(source_path)

    load(1)
    binding = dict(w.otherData)
    for i in range(w.flag_widget.count()):
        w.flag_widget.item(i).setCheckState(QtCore.Qt.Checked)
    key(QtGui.QKeySequence.Paste)
    assert len(w.canvas.shapes) == 3
    assert w.otherData == binding
    assert all(not s.flags["confirmed"] and s.flags["focused"] for s in w.canvas.shapes)
    assert next(w.flag_widget.item(i) for i in range(w.flag_widget.count())
                if w.flag_widget.item(i).text() == "reviewed").checkState() == QtCore.Qt.Unchecked
    w.canvas.shapes[0].points[0] = QtCore.QPointF(111, 112)
    w.canvas.shapes[0].flags["focused"] = False
    w.actions.paste.trigger()
    assert len(warnings) == 2 and len(w.canvas.shapes) == 3  # Atomic collision rejection.
    dest_path = output / "editor/001-frame-001.json"
    assert w.saveLabels(str(dest_path))
    dest = h.read(dest_path)
    assert dest["nuiak"] == binding["nuiak"]
    row = next(f for f in batch["frames"] if f["id"] == "frame-001")
    parsed = h.parse_editor(batch, row, dest_path)
    assert all(c["disposition"] != "reviewed" for c in parsed)

    load(2)
    # Exercise the actual toolbar button, independently of keyboard bindings.
    button = next(b for b in w.tools.findChildren(QtWidgets.QToolButton)
                  if b.defaultAction() is w.actions.paste)
    QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
    assert len(w.canvas.shapes) == 3
    assert w.canvas.shapes[0].points[0] == QtCore.QPointF(100, 100)
    assert w.canvas.shapes[0].flags["focused"]  # No clipboard alias from frame001.
    w.actions.selectAllBoxes.trigger()
    assert len(w.canvas.selectedShapes) == 3
    w.canvas.shapes[1].group_id = 8
    w.actions.copy.trigger()
    assert len(warnings) == 3  # Existing clipboard retained on invalid copy.
    load(4)
    before = len(w.canvas.shapes)
    w.actions.paste.trigger()
    assert len(warnings) == 4 and len(w.canvas.shapes) == before
    load(3)
    w._copy_context = ("home", 10, 10)
    w.actions.paste.trigger()
    assert len(warnings) == 5 and not w.canvas.shapes
    w._copy_context = ("home", 1920, 1080)
    extra = Shape(label="collectionItem", shape_type="rectangle", group_id=99)
    extra.points = [QtCore.QPointF(100, 400), QtCore.QPointF(300, 500)]
    extra.flags = {k: False for k in h.SHAPE_FLAGS}
    w.loadShapes([extra], replace=False)
    w.actions.paste.trigger()
    assert len(w.canvas.shapes) == 4 and w.canvas.shapes[0] is extra
    load(1)
    assert w.canvas.shapes[0].points[0] == QtCore.QPointF(111, 112)
    assert all(not s.flags["confirmed"] for s in w.canvas.shapes)
    assert w.grab().save(str(output / "clipboard-editor.png"))
    w.setClean()
    w.close()
    app.processEvents()
    reopened = launcher.window(output / "batch.json", output / "runtime")
    reopened.loadFile("editor/001-frame-001.png")
    app.processEvents()
    assert len(reopened.canvas.shapes) == 3
    assert reopened.canvas.shapes[0].points[0] == QtCore.QPointF(111, 112)
    assert all(not s.flags["confirmed"] for s in reopened.canvas.shapes)
    reopened.setClean()
    reopened.close()
    assert h.sha(source_path) == source_hash
    assert all(h.sha(p) == digest for p, digest in originals.items())
    result = dict(version="human-review-clipboard-verification-v1", **h.FLAGS,
                  selectAllCopyPasteKeyboard=True, toolbarPaste=True, savedReopened=True,
                  copiedBoxes=3, warningPaths=5, freshConfirmationRequired=True,
                  independentRepeatedPaste=True, originalsUnchanged=True,
                  humanReviewPerformed=False)
    h.write(output / "clipboard-verification.json", result, sealed=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index")
    parser.add_argument("output")
    args = parser.parse_args()
    print(verify(args.index, args.output))
