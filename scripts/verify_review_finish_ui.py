"""Actual Qt Finish review interaction using generated diagnostic-only fixtures."""
import argparse
import copy
import os
from unittest.mock import patch

import human_annotation_review as h
import human_review_editor as launcher
import human_review_finish as bulk
import test_human_annotation_review as fixtures


def verify(output):
    output = h.fresh(output)
    output.mkdir(parents=True)
    f = fixtures.ReviewTests()
    f.setUp()
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    launcher.configure(output / "runtime")
    from qtpy import QtWidgets, QtCore, QtTest
    app = QtWidgets.QApplication([])
    batch = h.import_batch(f.input, output / "batch")
    batch_path = output / "batch/batch.json"
    paths = [output / "batch/editor" / (row["editorStem"]+".json") for row in batch["frames"]]
    d = h.read(paths[0])
    d["shapes"][0]["flags"]["focused"] = False
    f.dump(paths[0], d)
    d = h.read(paths[1])
    extra = copy.deepcopy(d["shapes"][0])
    extra["group_id"] = None
    d["shapes"].append(extra)
    f.dump(paths[1], d)
    w = launcher.window(batch_path, output / "runtime")
    w.resize(1200, 800)
    w.show()
    app.processEvents()
    assert w.actions.finishReview in w.menus.edit.actions()
    assert w.actions.finishReview in [b.defaultAction() for b in w.tools.findChildren(QtWidgets.QToolButton)]
    before = {p: h.sha(p) for p in paths}
    errors = []
    def schedule(callback):
        def checked():
            try:
                callback(app.activeModalWidget())
            except Exception as error:
                errors.append(repr(error))
                if app.activeModalWidget():
                    app.activeModalWidget().reject()
        QtCore.QTimer.singleShot(0, checked)
    def field(dialog, kind, name):
        result = dialog.findChild(kind, name)
        assert result is not None, name
        return result
    def confirm_fields(dialog):
        assert dialog.objectName() == "finishReviewDialog"
        button = field(dialog, QtWidgets.QPushButton, "confirmReadyFrames")
        assert not button.isEnabled()
        field(dialog, QtWidgets.QLineEdit, "bulkReviewer").setText("Generated Qt software test")
        assert not button.isEnabled()
        checkbox = field(dialog, QtWidgets.QCheckBox, "bulkAttestation")
        QtTest.QTest.mouseClick(checkbox, QtCore.Qt.LeftButton, pos=QtCore.QPoint(8, checkbox.height()//2))
        assert button.isEnabled()
        return button

    def cancel(dialog):
        tree = field(dialog, QtWidgets.QTreeWidget, "reviewFrames")
        assert tree.topLevelItemCount() == 2
        assert "Needs attention" in tree.topLevelItem(0).text(3)
        assert "Ready (+1 local IDs)" == tree.topLevelItem(1).text(3)
        assert "unknown_focus" in field(dialog, QtWidgets.QPlainTextEdit, "reviewExceptions").toPlainText()
        confirm_fields(dialog)
        assert dialog.grab().save(str(output / "finish-dialog.png"))
        dialog.reject()
    schedule(cancel)
    w.actions.finishReview.trigger()
    assert not errors, errors
    assert before == {p: h.sha(p) for p in paths}

    def navigate(dialog):
        QtTest.QTest.mouseClick(field(dialog, QtWidgets.QPushButton, "openReviewFrame"), QtCore.Qt.LeftButton)
    schedule(navigate)
    w.actions.finishReview.trigger()
    assert w.imagePath.endswith(paths[0].with_suffix(".png").name)
    assert w.filename in w.imageList  # Next/previous also work after Open frame.

    def stale(dialog):
        button = confirm_fields(dialog)
        d = h.read(paths[1])
        d["shapes"][0]["description"] = "newer saved edit"
        f.dump(paths[1], d)
        def warning(message):
            assert isinstance(message, QtWidgets.QMessageBox)
            assert "stale" in message.text()
            message.accept()
        schedule(warning)
        button.click()
    schedule(stale)
    w.actions.finishReview.trigger()
    assert not (output / "batch/review-revisions").exists()

    # Explicitly cancel Save for unsaved work; never discard or auto-save it.
    w.setDirty()
    def cancel_save(dialog):
        assert isinstance(dialog, QtWidgets.QMessageBox)
        dialog.button(QtWidgets.QMessageBox.Cancel).click()
    schedule(cancel_save)
    w.actions.finishReview.trigger()
    assert w.dirty
    w.setClean()

    real_apply = bulk.apply_preview
    receipts = []
    def software_apply(*args, **kwargs):
        kwargs["reviewer_kind"] = "software-test"
        receipt = real_apply(*args, **kwargs)
        receipts.append(receipt)
        return receipt
    def approve(dialog):
        button = confirm_fields(dialog)
        def success(message):
            assert isinstance(message, QtWidgets.QMessageBox)
            assert "Confirmed 1 ready frames" in message.text()
            message.accept()
        schedule(success)
        button.click()
    schedule(approve)
    with patch.object(bulk, "apply_preview", side_effect=software_apply):
        w.actions.finishReview.trigger()
    assert not errors, errors
    assert len(receipts) == 1 and receipts[0]["frameCounts"] == {"blocked": 2}
    assert h.sha(paths[0]) == before[paths[0]]
    assert all(s["flags"]["confirmed"] for s in h.read(paths[1])["shapes"])
    revision = h.checked(h.ROOT, receipts[0]["revision"])
    assert h.read(revision)["reviewer"]["kind"] == "software-test"
    w.setClean()
    w.close()
    app.processEvents()
    result = dict(version="human-review-finish-ui-verification-v1", **h.FLAGS,
                  generatedFixtures=True, humanReviewPerformed=False, cancelUnchanged=True,
                  dirtySaveCancelPreserved=True, openExceptionFrame=True, stalePreviewRejected=True,
                  explicitAttestation=True, pendingUntouched=True, localIDsAssigned=True,
                  softwareRevision=h.ref(revision))
    h.write(output / "finish-ui-verification.json", result, sealed=True)
    # Keep source fixture references alive for reproducible retained output.
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    args = parser.parse_args()
    print(verify(args.output))
