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


if __name__ == '__main__':
    unittest.main()
