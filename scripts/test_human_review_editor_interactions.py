"""Actual pinned Qt editor interactions on generated, non-human fixture data."""
import os
import unittest
from unittest.mock import patch

import human_annotation_review as h
import human_regression_review as regression
import human_review_editor as editor
import test_human_annotation_review as fixtures


class EditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cwd = os.getcwd()
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        editor.configure(h.ROOT/'.build/human-review/gui-tests')
        from qtpy import QtWidgets
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.f = fixtures.ReviewTests(); self.f.setUp(); self.f.imported()
        self.queue = self.f.root/'queue.json'
        h.write(self.queue, regression.prepare(self.f.batch/'batch.json', limit=1), sealed=True)
        self.w = editor.window(self.f.batch/'batch.json', self.f.root/'runtime', self.queue, 1)
        self.w.show(); self.app.processEvents()

    def tearDown(self):
        self.w.dirty = False; self.w.close(); self.app.processEvents()
        os.chdir(self.cwd); self.f.tearDown()

    def double_click(self, x, y):
        from qtpy import QtCore, QtTest
        canvas = self.w.canvas
        point = (QtCore.QPointF(x, y) + canvas.offsetToCenter()) * canvas.scale
        QtTest.QTest.mouseDClick(canvas, QtCore.Qt.LeftButton, pos=point.toPoint())
        self.app.processEvents()

    def test_actual_double_click_edits_and_cancel_preserves(self):
        shape = self.w.canvas.shapes[0]
        points = [(p.x(), p.y()) for p in shape.points]
        self.w.canvas.scale = 2.3
        with patch.object(self.w.labelDialog, 'popUp', return_value=(None, {}, None, None)) as dialog:
            self.double_click(30, 25)
            self.assertEqual(dialog.call_count, 1)
        self.assertEqual(shape.label, 'primaryButton')
        self.assertFalse(self.w.dirty)
        with patch.object(self.w.labelDialog, 'popUp', return_value=('secondaryButton', shape.flags, shape.group_id, '')):
            self.double_click(30, 25)
        self.assertEqual(shape.label, 'secondaryButton')
        self.assertEqual([(p.x(), p.y()) for p in shape.points], points)
        self.assertTrue(self.w.dirty)
        self.w.saveFile()
        self.w.loadFile(self.w.imageList[0])
        self.assertEqual(self.w.canvas.shapes[0].label, 'secondaryButton')

    def test_optional_proposal_filter_restore_and_cancel(self):
        from qtpy import QtCore, QtWidgets
        before=list(self.w.canvas.shapes)
        proposals=[[[10,10],[50,50]],[[11,11],[51,51]],[[70,30],[71,31]]]
        def inspect(dialog):
            filtering=dialog.findChild(QtWidgets.QCheckBox,'autoDetectDeduplicate')
            listing=dialog.findChild(QtWidgets.QListWidget,'autoDetectCandidates')
            self.assertFalse(filtering.isChecked())
            filtering.setChecked(True)
            self.assertTrue(listing.item(1).isHidden())
            self.assertEqual(listing.item(1).checkState(),QtCore.Qt.Unchecked)
            toggle=dialog.findChild(QtWidgets.QPushButton,'autoDetectToggleAll')
            toggle.click();self.assertEqual(listing.item(0).checkState(),QtCore.Qt.Unchecked)
            toggle.click();self.assertEqual(listing.item(0).checkState(),QtCore.Qt.Checked)
            filtering.setChecked(False)
            self.assertFalse(listing.item(1).isHidden())
            self.assertEqual(listing.item(1).checkState(),QtCore.Qt.Checked)
            return QtWidgets.QDialog.Rejected
        with patch.object(QtWidgets.QDialog,'exec_',inspect):self.w.reviewBoxProposals(proposals)
        self.assertEqual(self.w.canvas.shapes,before)

    def test_optional_proposal_filter_invalid_geometry_does_not_escape_qt(self):
        from qtpy import QtWidgets
        before=list(self.w.canvas.shapes)
        def inspect(dialog):
            checkbox=dialog.findChild(QtWidgets.QCheckBox,'autoDetectDeduplicate')
            checkbox.setChecked(True)
            self.assertFalse(checkbox.isChecked())
            return QtWidgets.QDialog.Rejected
        with patch.object(QtWidgets.QDialog,'exec_',inspect):
            self.w.reviewBoxProposals([[[0,0],[1000,1000]]])
        self.assertEqual(self.w.canvas.shapes,before)

    def test_preset_roundtrip_and_dimension_rejection(self):
        from qtpy import QtWidgets
        import human_review_presets as presets
        directory = self.f.root/'presets'
        original = self.w.canvas.shapes[0]
        original.flags['confirmed'] = True
        original.flags['focused'] = True
        with patch.object(presets, 'DIRECTORY', directory), patch.object(
                QtWidgets.QInputDialog, 'getText', return_value=('Settings navigation', True)):
            self.w.saveBoxPreset()
        path = directory/'Settings navigation.json'
        doc = h.read(path)
        self.assertNotIn('flags', doc['boxes'][0])
        with self.assertRaises(ValueError): presets.load(path, (1920,1080))
        with self.assertRaises(ValueError): presets.save('../escape', (100,60), doc['boxes'], directory)
        with self.assertRaises(ValueError): presets.save('Settings navigation', (100,60), doc['boxes'], directory)
        with patch.object(presets, 'DIRECTORY', directory), patch.object(
                QtWidgets.QInputDialog, 'getItem', return_value=('Settings navigation', True)):
            self.w.loadBoxPreset()
        self.assertEqual(len(self.w.canvas.shapes), 2)
        added = self.w.canvas.shapes[-1]
        self.assertNotEqual(added.group_id, original.group_id)
        self.assertFalse(any(added.flags.values()))
        self.assertTrue(original.flags['confirmed'])
        self.w.saveFile()
        self.w.loadFile(self.w.imagePath)
        self.assertEqual(len(self.w.canvas.shapes), 2)

    def test_invalid_preset_does_not_change_boxes(self):
        from qtpy import QtWidgets
        import human_review_presets as presets
        directory = self.f.root/'presets'; directory.mkdir()
        h.write(directory/'Broken.json', {'version':'wrong'})
        with patch.object(presets, 'DIRECTORY', directory), patch.object(
                QtWidgets.QInputDialog, 'getItem', return_value=('Broken', True)), patch.object(
                self.w, 'clipboardWarning') as warning:
            self.w.loadBoxPreset()
            warning.assert_called_once()
        self.assertEqual(len(self.w.canvas.shapes), 1)

    def test_single_focus_and_enter_from_fields(self):
        from qtpy import QtCore, QtTest
        dialog = self.w.labelDialog
        for field in (dialog.edit, dialog.labelList, dialog.editDescription, dialog.edit_group_id):
            def accept():
                field.setFocus()
                QtTest.QTest.keyClick(field, QtCore.Qt.Key_Return)
            QtCore.QTimer.singleShot(10, accept)
            text, flags, _, _ = dialog.popUp('listRow', move=False)
            self.assertEqual(text, 'listRow')
            self.assertFalse(flags['focused'])
            self.assertTrue(flags['unfocused'])
            self.assertFalse(flags['confirmed'])
        names = [dialog.flagsLayout.itemAt(i).widget().text() for i in range(dialog.flagsLayout.count())]
        self.assertNotIn('unfocused', names)
        def focus_and_accept():
            checkbox = dialog.flagsLayout.itemAt(0).widget()
            self.assertEqual(checkbox.text(), 'focused')
            checkbox.setChecked(True)
            QtTest.QTest.keyClick(checkbox, QtCore.Qt.Key_Enter)
        QtCore.QTimer.singleShot(10, focus_and_accept)
        _, flags, _, _ = dialog.popUp('listRow', move=False)
        self.assertTrue(flags['focused']); self.assertFalse(flags['unfocused'])
        QtCore.QTimer.singleShot(10, dialog.reject)
        self.assertEqual(dialog.popUp('listRow', move=False), (None,None,None,None))

    def test_enter_does_not_accept_unknown_label(self):
        from qtpy import QtCore, QtTest, QtWidgets
        dialog = self.w.labelDialog
        def attempt():
            dialog.edit.setText('not-a-class')
            QtTest.QTest.keyClick(dialog.edit, QtCore.Qt.Key_Return)
            self.assertTrue(dialog.isVisible())
            dialog.reject()
        QtCore.QTimer.singleShot(10, attempt)
        self.assertEqual(dialog.popUp('listRow', move=False), (None,None,None,None))

    def test_focus_role_available_and_saved_as_rectangle(self):
        from qtpy import QtCore, QtTest
        dialog = self.w.labelDialog
        self.assertEqual(len(dialog.labelList.findItems('focus:tabItem', QtCore.Qt.MatchExactly)), 1)
        def accept():
            dialog.edit.setText('focus:tabItem')
            QtTest.QTest.keyClick(dialog.edit, QtCore.Qt.Key_Return)
        QtCore.QTimer.singleShot(10, accept)
        self.w.editLabel(self.w.labelList.findItemByShape(self.w.canvas.shapes[0]))
        self.assertEqual(self.w.canvas.shapes[0].label, 'focus:tabItem')
        self.w.saveFile(); self.w.loadFile(self.w.imagePath)
        self.assertEqual(self.w.canvas.shapes[0].label, 'focus:tabItem')

    def test_focus_pinning_preserves_selection_geometry_and_saved_order(self):
        first = self.w.canvas.shapes[0]
        first.flags.update(focused=False, unfocused=True)
        second = first.copy(); second.group_id = 2
        second.flags.update(focused=True, unfocused=False)
        self.w.loadShapes([second], replace=False)
        self.w.shapeSelectionChanged([first])
        self.w.refreshFocusList()
        self.assertIs(self.w.labelList[0].shape(), second)
        self.assertIn('2. primaryButton', self.w.labelList[0].text())
        self.assertIn('1. primaryButton', self.w.labelList[1].text())
        self.assertIn('●', self.w.labelList[0].text())
        self.assertNotIn('FOCUSED', self.w.labelList[0].text())
        self.assertIn('FOCUSED', self.w.labelList[0].toolTip())
        self.assertEqual(self.w.canvas.selectedShapes, [first])
        self.assertEqual(self.w.canvas.shapes, [first, second])
        self.assertEqual([item.shape() for item in self.w.labelList.selectedItems()], [first])
        self.assertIn('1 focused', self.w.shape_dock.windowTitle())
        self.w.setDirty(); self.w.saveFile()
        path = self.f.batch/'editor/001-frame-0.json'
        self.assertEqual([s['group_id'] for s in h.read(path)['shapes']], [first.group_id, 2])
        self.w.loadFile(self.w.imagePath)
        self.assertEqual(self.w.labelList[0].shape().group_id, 2)
        self.assertIn('2. primaryButton', self.w.labelList[0].text())

    def test_multiple_focus_unknown_and_excluded_indicators(self):
        first = self.w.canvas.shapes[0]
        second = first.copy(); second.group_id = 2
        self.w.loadShapes([second], replace=False)
        self.assertIn('2 focused', self.w.shape_dock.windowTitle())
        self.assertTrue(all(s.flags['focused'] for s in self.w.canvas.shapes))
        second.flags['rejected'] = True
        self.w.setDirty()
        self.assertIn('1 focused', self.w.shape_dock.windowTitle())
        self.assertIn('×', self.w.labelList[1].text())
        self.assertIn('EXCLUDED', self.w.labelList[1].toolTip())
        first.flags.update(focused=False, unfocused=False)
        self.w.setDirty()
        self.assertIn('none marked', self.w.shape_dock.windowTitle())
        self.assertIn('○', self.w.labelList[0].text())
        self.assertNotIn('unfocused', self.w.labelList[0].text())
        self.assertIn('unfocused (default)', self.w.labelList[0].toolTip())

    def test_blank_drawing_and_topmost(self):
        canvas = self.w.canvas
        second = canvas.shapes[0].copy(); second.group_id = 2
        self.w.loadShapes([second], replace=False)
        with patch.object(self.w, 'editLabel') as edit:
            self.double_click(30, 25)
            self.assertIs(edit.call_args.args[0], self.w.labelList.findItemByShape(second))
            edit.reset_mock()
            self.double_click(90, 50)
            edit.assert_not_called()
            self.w.toggleDrawMode(False, 'rectangle')
            self.double_click(30, 25)
            edit.assert_not_called()

    def test_navigation_clears_movement_and_delayed_key_release(self):
        from qtpy import QtCore, QtGui
        old = self.w.canvas.shapes[0]
        self.w.shapeSelectionChanged([old])
        self.w.canvas.movingShape = True
        self.w.loadFile('editor/002-frame-1.png')
        self.assertFalse(self.w.canvas.movingShape)
        self.assertEqual(self.w.canvas.selectedShapes, [])
        self.app.sendEvent(self.w.canvas, QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, QtCore.Qt.Key_Right, QtCore.Qt.NoModifier))
        self.assertEqual(len(self.w.canvas.shapes), 1)
        # Defensive guard also handles stale state without an intervening reset.
        self.w.canvas.selectedShapes = [old]
        self.w.canvas.movingShape = True
        self.app.sendEvent(self.w.canvas, QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, QtCore.Qt.Key_Right, QtCore.Qt.NoModifier))
        self.assertFalse(self.w.canvas.movingShape)
        self.assertEqual(self.w.canvas.selectedShapes, [])

    def test_valid_movement_release_keeps_edit_and_undo(self):
        from qtpy import QtCore, QtGui
        canvas = self.w.canvas
        shape = canvas.shapes[0]
        self.w.shapeSelectionChanged([shape])
        shape.points[0] += QtCore.QPointF(1, 0)
        canvas.movingShape = True
        count = len(canvas.shapesBackups)
        self.app.sendEvent(canvas, QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, QtCore.Qt.Key_Right, QtCore.Qt.NoModifier))
        self.assertFalse(canvas.movingShape)
        self.assertGreater(len(canvas.shapesBackups), count)
        self.assertTrue(self.w.dirty)

    def test_queue_navigation_and_finish_dialog_same_membership(self):
        from qtpy import QtCore, QtWidgets
        self.assertEqual(len(self.w.imageList), 1)
        self.w.openNextImg(); self.app.processEvents()
        self.assertIn('001-', self.w.imagePath)
        observations = []
        def inspect_dialog():
            dialog = self.w.findChild(QtWidgets.QDialog, 'finishReviewDialog')
            tree = dialog.findChild(QtWidgets.QTreeWidget, 'reviewFrames')
            check = dialog.findChild(QtWidgets.QCheckBox, 'completeFrameAttestation')
            observations.append((tree.topLevelItemCount(), check.isChecked()))
            dialog.grab().save(str(h.ROOT/'.build/human-review/gui-tests/finish-review.png'))
            dialog.reject()
        QtCore.QTimer.singleShot(10, inspect_dialog)
        self.w.finishReview()
        self.assertEqual(observations, [(1, False)])

    def test_startup_queue_excludes_directory_first_frame(self):
        # Constructor timers must not restore frame-0 after the queue is frozen.
        self.w.dirty = False
        self.w.close()
        before = {str(p): h.sha(p) for p in (self.f.batch/'editor').glob('*.json')}
        with patch('human_regression_review.queue_scope', return_value=['frame-1']):
            self.w = editor.window(self.f.batch/'batch.json', self.f.root/'runtime', self.queue, 1)
        self.w.show()
        for _ in range(3): self.app.processEvents()
        self.assertEqual(self.w.imageList, ['editor/002-frame-1.png'])
        self.assertEqual(self.w.filename, self.w.imageList[0])
        self.w.openNextImg(); self.app.processEvents()
        self.w.openPrevImg(); self.app.processEvents()
        self.assertEqual(self.w.filename, self.w.imageList[0])
        self.assertFalse(self.w.dirty)
        self.assertEqual(before, {str(p): h.sha(p) for p in (self.f.batch/'editor').glob('*.json')})

    def test_optional_click_proposal_cancel_accept_and_off(self):
        from qtpy import QtCore, QtTest
        action=self.w.actions.suggestBox
        self.assertFalse(action.isChecked())
        canvas=self.w.canvas
        location=((QtCore.QPointF(85,45)+canvas.offsetToCenter())*canvas.scale).toPoint()
        with patch('human_click_box.suggest', return_value=[[70,35],[95,55]]) as suggest:
            QtTest.QTest.mouseClick(canvas,QtCore.Qt.LeftButton,pos=location)
            suggest.assert_not_called()
            action.setChecked(True)
            with patch.object(self.w.labelDialog,'popUp',return_value=(None,None,None,None)):
                QtTest.QTest.mouseClick(canvas,QtCore.Qt.LeftButton,pos=location)
            self.assertEqual(len(canvas.shapes),1)
            with patch.object(self.w.labelDialog,'popUp',return_value=('listRow',{},None,'')):
                QtTest.QTest.mouseClick(canvas,QtCore.Qt.LeftButton,pos=location)
            self.assertEqual(len(canvas.shapes),2)
            self.assertTrue(canvas.shapes[-1].flags['unfocused'])
            self.assertFalse(canvas.shapes[-1].flags['confirmed'])
            self.assertIsNone(canvas.current)
            self.w.toggleDrawMode(False,'rectangle')
            self.assertFalse(action.isChecked())
        action.setChecked(True)
        with patch('human_click_box.suggest', return_value=None), patch.object(self.w.labelDialog,'popUp') as dialog:
            QtTest.QTest.mouseClick(canvas,QtCore.Qt.LeftButton,pos=location)
            dialog.assert_not_called()
        self.assertEqual(len(canvas.shapes),2)

    def test_suggestion_preview_clears_stale_manual_guide_not_saved_boxes(self):
        from qtpy import QtCore
        from labelme.shape import Shape
        canvas = self.w.canvas
        original = list(canvas.shapes)
        for accepted in (False, True):
            canvas.line = Shape(shape_type='rectangle')
            canvas.line.points = [QtCore.QPointF(5,5), QtCore.QPointF(60,15)]
            canvas.line.close()
            before = len(canvas.shapes)
            def inspect_preview(*args, **kwargs):
                self.assertEqual(canvas.line.points, [])
                self.assertEqual(len(canvas.shapes), before)
                self.assertEqual([(p.x(),p.y()) for p in canvas.current.points],
                                 [(70,35),(95,55)])
                self.assertFalse(canvas.grab().isNull())  # Exercise actual paintEvent.
                return ('listRow', {}, None, '') if accepted else (None,None,None,None)
            with patch('human_click_box.suggest', return_value=[[70,35],[95,55]]), \
                    patch.object(self.w.labelDialog, 'popUp', side_effect=inspect_preview):
                self.w.suggestRectangle(QtCore.QPointF(85,45))
            self.assertIsNone(canvas.current)
            self.assertEqual(len(canvas.shapes), before + int(accepted))
            self.assertIs(canvas.shapes[0], original[0])

    def test_suggestion_reuses_accepted_label_and_enter_with_fresh_flags(self):
        from qtpy import QtCore, QtTest
        dialog = self.w.labelDialog
        # An ordinary label dialog establishes the session default.
        QtCore.QTimer.singleShot(10, dialog.validate)
        self.assertEqual(dialog.popUp('listRow', move=False,
                                     flags={'focused': True, 'confirmed': True})[0], 'listRow')
        def cancel_edit():
            dialog.edit.setText('collectionItem')
            dialog.reject()
        QtCore.QTimer.singleShot(10, cancel_edit)
        self.assertIsNone(dialog.popUp(move=False)[0])
        self.assertEqual(dialog.edit.text(), 'listRow')
        observed = []
        def accept_suggestion():
            observed.append((dialog.edit.text(), dialog.getFlags()))
            QtTest.QTest.keyClick(dialog.edit, QtCore.Qt.Key_Return)
        for _ in range(2):
            QtCore.QTimer.singleShot(10, accept_suggestion)
            with patch('human_click_box.suggest', return_value=[[70,35],[95,55]]):
                self.w.suggestRectangle(QtCore.QPointF(85,45))
            self.assertEqual(self.w.canvas.shapes[-1].label, 'listRow')
            self.assertTrue(self.w.canvas.shapes[-1].flags['unfocused'])
            self.assertFalse(self.w.canvas.shapes[-1].flags['confirmed'])
        self.assertEqual([label for label, _ in observed], ['listRow', 'listRow'])
        self.assertTrue(all(not flags['focused'] and not flags['confirmed']
                            for _, flags in observed))

    def test_actual_finish_button_writes_scoped_completeness(self):
        from qtpy import QtCore, QtWidgets
        hidden = sorted((self.f.batch/'editor').glob('*.json'))[1]
        before = h.sha(hidden)
        def confirm():
            dialog = self.w.findChild(QtWidgets.QDialog, 'finishReviewDialog')
            dialog.findChild(QtWidgets.QLineEdit, 'bulkReviewer').setText('generated-fixture-only')
            dialog.findChild(QtWidgets.QCheckBox, 'bulkAttestation').setChecked(True)
            dialog.findChild(QtWidgets.QCheckBox, 'completeFrameAttestation').setChecked(True)
            dialog.findChild(QtWidgets.QPushButton, 'confirmReadyFrames').click()
        QtCore.QTimer.singleShot(10, confirm)
        with patch.object(QtWidgets.QMessageBox, 'information') as done, patch.object(QtWidgets.QMessageBox, 'warning') as warning:
            self.w.finishReview()
            warning.assert_not_called()
            done.assert_called_once()
        receipt = next((self.f.batch/'review-revisions').glob('*/completeness.json'))
        self.assertEqual(regression.checked_completeness(receipt, receipt.parent/'revision/revision.json'), {'frame-0'})
        self.assertEqual(h.sha(hidden), before)

    def test_auto_detect_preview_cancel_select_add_undo_and_reload(self):
        from qtpy import QtCore, QtWidgets
        original=self.w.canvas.shapes[0]
        original_flags=dict(original.flags)
        for i in range(self.w.flag_widget.count()):
            self.w.flag_widget.item(i).setCheckState(QtCore.Qt.Checked)
        self.w.labelDialog.edit.setText('listRow')
        proposals=[[[65,5],[95,25]],[[65,30],[95,55]]]
        def inspect(accept):
            dialog=self.w.findChild(QtWidgets.QDialog,'autoDetectDialog')
            self.assertIsNotNone(dialog)
            label=dialog.findChild(QtWidgets.QComboBox,'autoDetectLabel')
            self.assertEqual(label.currentText(),'listRow')
            listing=dialog.findChild(QtWidgets.QListWidget,'autoDetectCandidates')
            self.assertEqual(listing.count(),2)
            self.assertFalse(dialog.findChild(QtWidgets.QLabel,'autoDetectPreview').pixmap().isNull())
            toggle=dialog.findChild(QtWidgets.QPushButton,'autoDetectToggleAll')
            toggle.click()
            self.assertTrue(all(listing.item(i).checkState()==QtCore.Qt.Unchecked for i in range(2)))
            toggle.click(); listing.item(1).setCheckState(QtCore.Qt.Unchecked)
            dialog.grab().save(str(h.ROOT/'.build/human-review/gui-tests/auto-detect.png'))
            if accept: dialog.accept()
            else: dialog.reject()
        for accept in (False,True):
            # Delete the prior closed preview so lookup finds the current one.
            for dialog in self.w.findChildren(QtWidgets.QDialog,'autoDetectDialog'):
                dialog.setParent(None); dialog.deleteLater()
            QtCore.QTimer.singleShot(10,lambda accept=accept:inspect(accept))
            with patch('human_auto_boxes.detect',return_value=proposals):
                self.w.actions.autoDetectBoxes.trigger()
            self.assertEqual(len(self.w.canvas.shapes),1+int(accept))
            self.assertEqual(original.flags,original_flags)
        added=self.w.canvas.shapes[-1]
        self.assertEqual(added.label,'listRow')
        self.assertTrue(added.flags['unfocused'])
        self.assertFalse(added.flags['focused']); self.assertFalse(added.flags['confirmed'])
        self.assertNotEqual(added.group_id,original.group_id)
        frame_flags={self.w.flag_widget.item(i).text():self.w.flag_widget.item(i).checkState()==QtCore.Qt.Checked
                     for i in range(self.w.flag_widget.count())}
        self.assertFalse(frame_flags['reviewed'])
        self.assertTrue(frame_flags['settled']); self.assertTrue(frame_flags['content_approved'])
        self.w.undoShapeEdit(); self.assertEqual(len(self.w.canvas.shapes),1)
        # Add again then roundtrip without modal UI (same integrated shape path).
        for dialog in self.w.findChildren(QtWidgets.QDialog,'autoDetectDialog'):
            dialog.setParent(None); dialog.deleteLater()
        QtCore.QTimer.singleShot(10,lambda:inspect(True))
        with patch('human_auto_boxes.detect',return_value=proposals): self.w.autoDetectBoxes()
        self.w.saveFile(); self.w.loadFile(self.w.imagePath)
        self.assertEqual(len(self.w.canvas.shapes),2)
        self.assertFalse(self.w.canvas.shapes[-1].flags['confirmed'])

    def test_auto_detect_empty_failure_and_drawing_preserve_annotations(self):
        original=list(self.w.canvas.shapes)
        with patch('human_auto_boxes.detect',return_value=[]): self.w.autoDetectBoxes()
        with patch('human_auto_boxes.detect',side_effect=ValueError('test_failure')):
            self.w.autoDetectBoxes()
        self.assertEqual(self.w.canvas.shapes,original)
        self.w.toggleDrawMode(False,'rectangle')
        with patch('human_auto_boxes.detect') as detector:
            self.w.autoDetectBoxes(); detector.assert_not_called()

    def test_blank_first_batch_undo_via_action_and_save(self):
        import json
        import shutil
        from qtpy import QtCore, QtWidgets
        from test_human_vision_import import document
        image = self.f.root/'blank-annotations.png'
        shutil.copyfile(self.w.imagePath, image)
        self.w.dirty = False
        self.w.loadFile(str(image))
        self.assertEqual(self.w.canvas.shapes, [])
        self.assertEqual(self.w.canvas.shapesBackups, [])
        path = self.f.root/'blank-vision.json'
        path.write_text(json.dumps(document(image)))

        def respond(accept):
            dialog = self.w.findChild(QtWidgets.QDialog, 'autoDetectDialog')
            if accept == 'empty':
                listing = dialog.findChild(QtWidgets.QListWidget, 'autoDetectCandidates')
                for i in range(listing.count()):
                    listing.item(i).setCheckState(QtCore.Qt.Unchecked)
            dialog.accept() if accept else dialog.reject()

        def run_preview(accept, vision):
            for dialog in self.w.findChildren(QtWidgets.QDialog, 'autoDetectDialog'):
                dialog.setParent(None); dialog.deleteLater()
            QtCore.QTimer.singleShot(10, lambda: respond(accept))
            if vision:
                with patch.object(QtWidgets.QFileDialog, 'getOpenFileName', return_value=(str(path), 'JSON')):
                    self.w.actions.importVisionSuggestions.trigger()
            else:
                self.w.reviewBoxProposals([[[10, 10], [30, 30]]])

        run_preview(False, True)
        self.assertEqual(self.w.canvas.shapesBackups, [])
        run_preview('empty', True)
        self.assertEqual(self.w.canvas.shapesBackups, [])
        for vision in (True, False, True):
            run_preview(True, vision)
            self.assertEqual(len(self.w.canvas.shapes), 1)
            self.assertTrue(self.w.actions.undo.isEnabled())
            self.w.actions.undo.trigger()
            self.assertEqual(self.w.canvas.shapes, [])
            self.assertEqual(self.w.labelList.model().rowCount(), 0)
            self.assertFalse(self.w.actions.undo.isEnabled())
        with patch.object(QtWidgets.QFileDialog, 'getSaveFileName', return_value=(str(image.with_suffix('.json')), 'JSON')):
            self.w.saveFile()
        self.w.loadFile(str(image))
        self.assertEqual(self.w.canvas.shapes, [])
        self.assertEqual(json.loads(image.with_suffix('.json').read_text())['shapes'], [])

    def test_optional_vision_import_preview_cancel_add_undo_roundtrip(self):
        import json
        from pathlib import Path
        from qtpy import QtCore, QtWidgets
        from test_human_vision_import import document
        path=self.f.root/'supplied-vision.json'
        path.write_text(json.dumps(document(self.w.imagePath)))
        original=self.w.canvas.shapes[0]
        def finish(accept):
            dialog=self.w.findChild(QtWidgets.QDialog,'autoDetectDialog')
            listing=dialog.findChild(QtWidgets.QListWidget,'autoDetectCandidates')
            self.assertEqual(listing.count(),2)
            self.assertEqual(listing.item(0).checkState(),QtCore.Qt.Checked)
            self.assertEqual(listing.item(1).checkState(),QtCore.Qt.Unchecked)
            if accept:
                listing.item(1).setCheckState(QtCore.Qt.Checked)
                dialog.accept()
            else:dialog.reject()
        for accept in (False,True,True):
            if len(self.w.canvas.shapes)==3:
                self.assertTrue(self.w.actions.undo.isEnabled())
                self.w.actions.undo.trigger()
                self.assertEqual(len(self.w.canvas.shapes),1)
            for d in self.w.findChildren(QtWidgets.QDialog,'autoDetectDialog'):
                d.setParent(None);d.deleteLater()
            QtCore.QTimer.singleShot(10,lambda a=accept:finish(a))
            with patch.object(QtWidgets.QFileDialog,'getOpenFileName',return_value=(str(path),'JSON')):
                self.w.actions.importVisionSuggestions.trigger()
            self.assertEqual(len(self.w.canvas.shapes),3 if accept else 1)
        restored=self.w.canvas.shapes[0]
        self.assertEqual(restored.points,original.points)
        self.assertEqual(restored.label,original.label)
        self.assertEqual(restored.flags,original.flags)
        self.assertEqual(restored.description,original.description)
        self.assertEqual(self.w.canvas.shapes[-1].label,'label')
        self.assertIn('Search',self.w.canvas.shapes[-1].description)
        for s in self.w.canvas.shapes[1:]:
            self.assertFalse(s.flags['confirmed']);self.assertFalse(s.flags['focused'])
        self.w.saveFile();self.w.loadFile(self.w.imagePath)
        self.assertEqual(len(self.w.canvas.shapes),3)
        self.assertIn('sidecarSHA256',self.w.canvas.shapes[-1].description)


if __name__ == '__main__':
    unittest.main()
