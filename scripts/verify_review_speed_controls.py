"""Installed Qt frame-flag toggle and navigation tests on generated images."""
import argparse
import copy
import os

import human_annotation_review as h
import human_review_editor as launcher
import test_human_annotation_review as fixtures


def verify(output):
    output = h.fresh(output)
    output.mkdir(parents=True)
    fixture = fixtures.ReviewTests()
    fixture.setUp()
    batch = h.import_batch(fixture.input, output / "batch")
    batch_path = output / "batch/batch.json"
    paths = [output / "batch/editor" / (r["editorStem"]+".json") for r in batch["frames"]]
    before = {p: h.read(p) for p in paths}
    originals = {p: h.sha(p) for p in (output / "batch/raw").rglob("*") if p.is_file()}
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    launcher.configure(output / "runtime")
    from qtpy import QtCore, QtWidgets, QtTest, QtGui
    app = QtWidgets.QApplication([])
    # Fail boundedly if an unexpected nested stock dialog appears.
    watchdog = QtCore.QTimer()
    watchdog.setInterval(8000)
    def timeout():
        dialog = app.activeModalWidget()
        if dialog:
            print("Unexpected dialog:", dialog.windowTitle(), getattr(dialog, "text", lambda: "")(), flush=True)
            dialog.reject()
    watchdog.timeout.connect(timeout)
    watchdog.start()
    w = launcher.window(batch_path, output / "runtime")
    w.resize(1200, 800)
    w.show()
    app.processEvents()
    w.loadFile(str(paths[0].with_suffix(".png")))
    app.processEvents()
    assert w.filename in w.imageList
    flags = lambda: {w.flag_widget.item(i).text(): w.flag_widget.item(i).checkState() == QtCore.Qt.Checked
                     for i in range(w.flag_widget.count())}
    button = w.frameFlagsButton
    assert button.isVisible() and button.isEnabled()
    shape_flags = copy.deepcopy(w.canvas.shapes[0].flags)
    assert button.text() == "All frame flags on"
    QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
    assert all(flags().values()) and button.text() == "All frame flags off" and w.dirty
    assert w.canvas.shapes[0].flags == shape_flags
    assert before[paths[0]] == h.read(paths[0])  # No automatic save.
    QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
    assert not any(flags().values()) and button.text() == "All frame flags on"
    w.flag_widget.item(0).setCheckState(QtCore.Qt.Checked)
    assert button.text() == "All frame flags on"
    w.actions.toggleFrameFlags.trigger()
    assert all(flags().values()) and w.canvas.shapes[0].flags == shape_flags

    errors = []
    def dialog_button(choice):
        def respond():
            try:
                dialog = app.activeModalWidget()
                assert isinstance(dialog, QtWidgets.QMessageBox)
                print("Responding to:", dialog.windowTitle(), "with", choice, flush=True)
                dialog.button(choice).click()
            except Exception as error:
                errors.append(repr(error))
                if app.activeModalWidget():
                    app.activeModalWidget().reject()
        QtCore.QTimer.singleShot(0, respond)
    def key(sequence, target=None, response=None):
        target = target or w.canvas
        w.activateWindow()
        target.setFocus()
        app.processEvents()
        print("Key:", sequence, "current:", w.filename, flush=True)
        if response is not None:
            dialog_button(response)
        QtTest.QTest.keySequence(target, QtGui.QKeySequence(sequence))
        app.processEvents()
    key("Ctrl+Right", response=QtWidgets.QMessageBox.Cancel)
    assert w.imagePath.endswith(paths[0].with_suffix(".png").name) and w.dirty
    key("Ctrl+Right", response=QtWidgets.QMessageBox.Save)
    assert not errors, errors
    assert w.imagePath.endswith(paths[1].with_suffix(".png").name)
    assert not any(flags().values()) and button.text() == "All frame flags on"
    assert h.read(paths[0])["flags"] == {k: True for k in h.FRAME_FLAGS}
    saved_shapes = h.read(paths[0])["shapes"]
    assert len(saved_shapes) == len(before[paths[0]]["shapes"])
    for saved, original in zip(saved_shapes, before[paths[0]]["shapes"]):
        assert all(saved[k] == value for k, value in original.items())
    assert h.read(paths[1]) == before[paths[1]]
    key("Ctrl+Right")  # Last image is a boundary, not wrap-around.
    assert w.imagePath.endswith(paths[1].with_suffix(".png").name)
    key("Ctrl+Left", w.fileListWidget)
    assert w.imagePath.endswith(paths[0].with_suffix(".png").name)
    assert all(flags().values()) and button.text() == "All frame flags off"
    key("Ctrl+Left", w.fileListWidget)
    assert w.imagePath.endswith(paths[0].with_suffix(".png").name)
    key("D")
    assert w.imagePath.endswith(paths[1].with_suffix(".png").name)
    key("A")
    assert w.imagePath.endswith(paths[0].with_suffix(".png").name)
    assert not w._config["keep_prev"]  # Navigation must never propagate labels.
    assert w.grab().save(str(output / "speed-controls.png"))
    w.setClean()
    w.close()
    app.processEvents()
    reopened = launcher.window(batch_path, output / "runtime")
    reopened.loadFile(str(paths[0].with_suffix(".png")))
    app.processEvents()
    assert reopened.frameFlagsButton.text() == "All frame flags off"
    reopened.resetState()
    assert not reopened.frameFlagsButton.isEnabled()
    reopened.setClean()
    reopened.close()
    assert all(h.sha(p) == digest for p, digest in originals.items())
    result = dict(version="human-review-speed-controls-v1", **h.FLAGS,
                  allOnOffAndMixed=True, boxFlagsUnchanged=True, currentFrameOnly=True,
                  commandArrowNavigation=True, legacyADNavigation=True,
                  canvasAndFileListKeys=True, unsavedCancelAndSave=True,
                  noImplicitCopyOrWrap=True, savedReopened=True, originalsUnchanged=True,
                  generatedFixtures=True, humanReviewPerformed=False)
    h.write(output / "verification.json", result, sealed=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    args = parser.parse_args()
    print(verify(args.output))
