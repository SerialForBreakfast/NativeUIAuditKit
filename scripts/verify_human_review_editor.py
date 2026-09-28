"""Exercise the installed stock Qt editor on an isolated copy, never human-label it."""
import argparse
import json
import os
from pathlib import Path
import shutil

import human_annotation_review as h
import human_review_editor as launcher


def verify(batch_path, output):
    batch_path, output = h.local(batch_path), h.fresh(output)
    batch = h.validate_batch(batch_path)
    before = {p: h.sha(p) for p in (batch_path.parent/"editor").iterdir()}
    output.mkdir(parents=True)
    shutil.copyfile(batch_path, output/"batch.json")
    shutil.copytree(batch_path.parent/"editor", output/"editor")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    launcher.configure(output/"runtime")
    from qtpy import QtCore, QtWidgets, QtTest
    app = QtWidgets.QApplication([])
    window = launcher.window(output/"batch.json", output/"runtime")
    window.resize(1400, 850); window.show(); app.processEvents()
    assert len(window.imageList) == sum(f["disposition"] == "imported" for f in batch["frames"])
    results, edited = [], False
    for frame in batch["frames"]:
        if frame["disposition"] != "imported": continue
        path = output/"editor"/(frame["editorStem"]+".json")
        original = h.read(path)
        window.loadFile(str(path.with_suffix(".png"))); app.processEvents()
        assert window.image.width() == frame["size"][0]
        assert window.image.height() == frame["size"][1]
        assert len(window.canvas.shapes) == len(original["shapes"])
        if window.canvas.shapes and not edited:
            first = window.canvas.shapes[0]
            first.points[0] = QtCore.QPointF(first.points[0].x()+.25, first.points[0].y()+.5)
            for i, shape in enumerate(window.canvas.shapes):
                def edit_dialog(i=i):
                    dialog = window.labelDialog
                    targets = dict(focused=i == 0, unfocused=i != 0, confirmed=True, flagged=False, rejected=False)
                    for j in range(dialog.flagsLayout.count()):
                        checkbox = dialog.flagsLayout.itemAt(j).widget()
                        if checkbox.isChecked() != targets[checkbox.text()]:
                            QtTest.QTest.mouseClick(checkbox, QtCore.Qt.LeftButton,
                                                   pos=QtCore.QPoint(8, checkbox.height()//2))
                    if i == 0:
                        assert dialog.grab().save(str(output/"label-dialog-software-test.png"))
                    QtTest.QTest.mouseClick(dialog.buttonBox.button(QtWidgets.QDialogButtonBox.Ok), QtCore.Qt.LeftButton)
                QtCore.QTimer.singleShot(0, edit_dialog)
                window.editLabel(window.labelList.findItemByShape(shape))
                assert shape.flags["focused"] == (i == 0) and shape.flags["confirmed"] is True, shape.flags
            for i in range(window.flag_widget.count()):
                window.flag_widget.item(i).setCheckState(QtCore.Qt.Checked)
            window.setDirty()
            app.processEvents()
            assert window.grab().save(str(output/"editor-software-test.png"))
            edited = True
            edited_id = frame["id"]
        assert window.saveLabels(str(path))
        window.setClean()
        result = h.read(path)
        assert result["nuiak"] == original["nuiak"]
        assert result["imagePath"] == original["imagePath"]
        if frame["id"] == (edited_id if edited else None):
            assert result["shapes"][0]["points"][0] == [original["shapes"][0]["points"][0][0]+.25,
                                                        original["shapes"][0]["points"][0][1]+.5]
            assert result["shapes"][0]["flags"]["focused"] is True
        else:
            assert [s["points"] for s in result["shapes"]] == [s["points"] for s in original["shapes"]]
        assert [s["group_id"] for s in result["shapes"]] == [s["group_id"] for s in original["shapes"]]
        h.parse_editor(batch, frame, path)
        results.append(dict(id=frame["id"], savedSHA256=h.sha(path)))
    assert edited, "need at least one proposed box for real edit test"
    window.close(); app.processEvents()
    # New stock window instance, same persisted workspace/settings, all files reopened.
    reopened = launcher.window(output/"batch.json", output/"runtime")
    app.processEvents()
    for frame, result in zip([f for f in batch["frames"] if f["disposition"] == "imported"], results):
        path = output/"editor"/(frame["editorStem"]+".json")
        reopened.loadFile(str(path.with_suffix(".png"))); app.processEvents()
        assert len(reopened.canvas.shapes) == len(h.read(path)["shapes"])
        assert h.sha(path) == result["savedSHA256"]
    reopened.close(); app.processEvents()
    revision = h.finish(output/"batch.json", output/"revision", reviewer="automated-stock-editor-test",
                        reference="verify_human_review_editor.py; NOT human confirmation",
                        reviewer_kind="software-test", confirm_batch=True)
    assert revision["controlCounts"].get("reviewed", 0) == 0
    crops = h.crop_qa(output/"batch.json", output/"crops", output/"revision/revision.json")
    assert before == {p: h.sha(p) for p in before}
    report = dict(version="human-review-editor-verification-v1", **h.FLAGS, editorVersion=h.EDITOR,
                  backend="Qt offscreen stock MainWindow", loadedSavedReopened=results,
                  editedFrame=edited_id, fractionalEdit=[.25,.5], unchangedGeometryExact=True,
                  focusEditedThroughStockDialog=True,
                  originalsUnchanged=True, humanReviewPerformed=False,
                  revision=h.ref(output/"revision/revision.json"), crops=crops["completed"])
    h.write(output/"verification.json", report, sealed=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch"); parser.add_argument("output")
    args = parser.parse_args()
    result = verify(args.batch, args.output)
    print(json.dumps({"loadedSavedReopened":len(result["loadedSavedReopened"]),
                      "crops":result["crops"],"humanReviewPerformed":False}))
