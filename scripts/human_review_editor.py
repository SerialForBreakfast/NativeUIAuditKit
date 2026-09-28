"""Version-pinned launcher for stock Labelme; all application settings stay local."""
import argparse
import importlib.metadata
import os
import sys

from human_annotation_review import (EDITOR, FRAME_FLAGS, SHAPE_FLAGS, ROOT, local,
                                     require, review_labels, validate_batch)


def configure(runtime):
    runtime = local(runtime)
    require(runtime.is_relative_to(ROOT/".build") or runtime.is_relative_to(ROOT/"reports/work"),
            "invalid_editor_runtime")
    require(importlib.metadata.version("labelme") == EDITOR, "unsupported_editor_version")
    for name, env in (("tmp", "TMPDIR"), ("matplotlib", "MPLCONFIGDIR"), ("cache", "XDG_CACHE_HOME")):
        path = runtime/name
        path.mkdir(parents=True, exist_ok=True)
        os.environ[env] = str(path)
    os.environ["QT_API"] = "pyqt5"
    from qtpy import QtCore
    import PyQt5
    from pathlib import Path
    # The macOS wheel's compiled prefix is not this dedicated venv.
    QtCore.QCoreApplication.setLibraryPaths([str(Path(PyQt5.__file__).parent/"Qt5/plugins")])
    settings = runtime/"settings"
    settings.mkdir(parents=True, exist_ok=True)
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
    QtCore.QSettings.setPath(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, str(settings))
    QtCore.QSettings.setPath(QtCore.QSettings.IniFormat, QtCore.QSettings.SystemScope, str(settings))
    return runtime


def configuration():
    import labelme
    import yaml
    from pathlib import Path
    # Stock get_config writes ~/.labelmerc even with an explicit config. Bypass
    # that function, not the editor, using its pinned complete bundled defaults.
    config = yaml.safe_load((Path(labelme.__file__).parent/"config/default_config.yaml").read_text())
    config.update(store_data=False, auto_save=False, keep_prev=False,
                  labels=review_labels(), validate_label="exact", flags=list(FRAME_FLAGS),
                  label_flags={".*": list(SHAPE_FLAGS)})
    for key in ("create_polygon", "create_circle", "create_line", "create_point", "create_linestrip"):
        config["shortcuts"][key] = None
    config["shortcuts"]["create_rectangle"] = ["R", "Ctrl+R"]
    config["shortcuts"]["edit_polygon"] = ["E", "Ctrl+J"]
    config["shortcuts"]["open_next"] = ["D", "Ctrl+Right"]
    config["shortcuts"]["open_prev"] = ["A", "Ctrl+Left"]
    return config


def window(batch_path, runtime, queue_path=None, batch_index=None):
    batch_path = local(batch_path)
    batch = validate_batch(batch_path)
    queue_path = local(queue_path) if queue_path else None
    from human_regression_review import queue_scope
    require(queue_path is not None or batch_index is None, 'batch_index_requires_queue')
    scope = queue_scope(local(queue_path), batch_path, batch_index) if queue_path else None
    require(scope is None or bool(scope), 'empty_review_queue')
    runtime = configure(runtime)
    from qtpy import QtCore, QtGui, QtWidgets
    from labelme.app import MainWindow
    from labelme.widgets.label_dialog import LabelDialog

    class FocusLabelDialog(LabelDialog):
        def setFlags(self, flags):
            super().setFlags({k: bool(flags.get(k, False)) for k in SHAPE_FLAGS if k != 'unfocused'})
            for i in range(self.flagsLayout.count()):
                self.flagsLayout.itemAt(i).widget().installEventFilter(self)

        def getFlags(self):
            flags = super().getFlags()
            flags['unfocused'] = not flags.get('focused', False)
            return flags

        def validate(self):
            if self.edit.text().strip() in review_labels():
                self.edit.setText(self.edit.text().strip())
                super().validate()

        def eventFilter(self, watched, event):
            if event.type() == QtCore.QEvent.KeyPress and event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self.validate()
                return True
            return super().eventFilter(watched, event)

    class RectangleReviewWindow(MainWindow):
        """Constrain the pinned editor's drawing entrypoint, not its geometry."""
        def refreshFocusList(self, pinned=True):
            import html
            if not hasattr(self, 'labelList') or not hasattr(self, 'canvas'):
                return
            model = self.labelList.model()
            role = QtCore.Qt.UserRole + 17
            focused = 0
            previous = model.blockSignals(True)
            try:
                for index, shape in enumerate(self.canvas.shapes):
                    try:
                        item = self.labelList.findItemByShape(shape)
                    except ValueError:
                        continue
                    flags = shape.flags or {}
                    active = bool(flags.get('focused')) and not flags.get('rejected')
                    focused += active
                    if flags.get('rejected'):
                        state, color = 'EXCLUDED', '#999999'
                    elif flags.get('focused') and flags.get('unfocused'):
                        state, color = '! CONFLICT', '#e69f00'
                    elif active:
                        state, color = '● FOCUSED', '#009e73'
                    elif flags.get('unfocused'):
                        state, color = '○ unfocused', '#999999'
                    else:
                        state, color = '○ unfocused (default)', '#999999'
                    label = html.escape(shape.label)
                    identity = f' ({shape.group_id})' if shape.group_id is not None else ''
                    symbol = '×' if flags.get('rejected') else '⚠' if flags.get('focused') and flags.get('unfocused') else '●' if active else '○'
                    item.setText(f'<font color="{color}">{symbol}</font> {label}{identity}')
                    item.setToolTip(f'{state}: {shape.label}{identity}. Checkbox controls visibility, not focus.')
                    item.setData((0 if active or not pinned else 1)*1000000 + index, role)
            finally:
                model.blockSignals(previous)
            model.setSortRole(role)
            model.sort(0)
            self.labelList.viewport().update()
            if hasattr(self, 'shape_dock'):
                message = 'none marked' if not focused else '1 focused' if focused == 1 else f'⚠ {focused} focused — review'
                self.shape_dock.setWindowTitle('Control boxes — '+message)

        def setDirty(self):
            super().setDirty()
            self.refreshFocusList()

        def saveLabels(self, filename):
            # Stock serialization iterates the list, not canvas stacking order.
            # Temporarily restore original order; pinning is presentation only.
            self.refreshFocusList(pinned=False)
            try:
                return super().saveLabels(filename)
            finally:
                self.refreshFocusList()

        def loadShapes(self, shapes, replace=True):
            super().loadShapes(shapes, replace=replace)
            self.refreshFocusList()

        def importDirImages(self, *args, **kwargs):
            if getattr(self, '_frozenReviewQueue', False):
                return
            return super().importDirImages(*args, **kwargs)

        def importDroppedImageFiles(self, *args, **kwargs):
            if getattr(self, '_frozenReviewQueue', False):
                return
            return super().importDroppedImageFiles(*args, **kwargs)

        def openFile(self, *args, **kwargs):
            if getattr(self, '_frozenReviewQueue', False):
                return
            return super().openFile(*args, **kwargs)

        def toggleDrawMode(self, edit=True, createMode="rectangle"):
            require(edit or createMode == "rectangle", "rectangle_only_review")
            return super().toggleDrawMode(edit, createMode="rectangle")

        def refreshFrameFlags(self, *_):
            if not hasattr(self, "frameFlagsButton"):
                return
            items = [self.flag_widget.item(i) for i in range(self.flag_widget.count())]
            enabled = bool(self.imagePath) and {item.text() for item in items} == set(FRAME_FLAGS)
            all_on = bool(items) and all(item.checkState() == QtCore.Qt.Checked for item in items)
            caption = "All frame flags off" if all_on else "All frame flags on"
            self.frameFlagsButton.setText(caption)
            self.frameFlagsButton.setEnabled(enabled)
            self.actions.toggleFrameFlags.setText(caption)
            self.actions.toggleFrameFlags.setEnabled(enabled)

        def toggleFrameFlags(self):
            items = [self.flag_widget.item(i) for i in range(self.flag_widget.count())]
            if not self.imagePath or {item.text() for item in items} != set(FRAME_FLAGS):
                return
            state = QtCore.Qt.Unchecked if all(item.checkState() == QtCore.Qt.Checked for item in items) else QtCore.Qt.Checked
            for item in items:
                item.setCheckState(state)
            self.refreshFrameFlags()

        def loadFile(self, filename=None):
            if filename is not None:
                # Finish review opens absolute paths; stock navigation indexes
                # filename verbatim against the short relative file-list entries.
                filename = next((entry for entry in getattr(self, "imageList", [])
                                 if os.path.abspath(entry) == os.path.abspath(filename)), filename)
            result = super().loadFile(filename)
            self.refreshFrameFlags()
            self.refreshFocusList()
            return result

        def resetState(self):
            super().resetState()
            self.refreshFrameFlags()

        def finishReview(self):
            import human_review_finish as bulk
            from datetime import datetime, timezone
            from uuid import uuid4
            if self.dirty:
                answer = QtWidgets.QMessageBox.question(
                    self, "Save before review", "Save the current frame before checking the batch?",
                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
                if answer != QtWidgets.QMessageBox.Save:
                    return
                self.saveFile()
                if self.dirty:
                    return
            try:
                if queue_path:
                    require(queue_scope(queue_path, batch_path, batch_index) == scope, 'queue_changed')
                plan = bulk.preview(batch_path, scope)
            except (ValueError, OSError, KeyError, TypeError) as error:
                QtWidgets.QMessageBox.warning(self, "Review blocked", str(error))
                return
            ready = [r for r in plan["frames"] if r["ready"]]
            displayed = [r for r in plan['frames'] if r['id'] in plan['selectedFrames']]
            dialog = QtWidgets.QDialog(self)
            dialog.setObjectName("finishReviewDialog")
            dialog.setWindowTitle("Finish review — confirm ready frames")
            dialog.resize(850, 560)
            layout = QtWidgets.QVBoxLayout(dialog)
            summary = QtWidgets.QLabel(
                f"{len(ready)} ready frames / {sum(r['boxes'] for r in ready)} boxes; "
                f"{len(displayed)-len(ready)} displayed frames need attention.\n"
                "Only Ready frames will be confirmed. Pending frames remain untouched.\n"
                "Missing local IDs are assigned automatically. Unchecked Focused means unfocused on confirmation; conflicts still require review.")
            summary.setWordWrap(True)
            layout.addWidget(summary)
            tree = QtWidgets.QTreeWidget()
            tree.setObjectName("reviewFrames")
            tree.setHeaderLabels(["Frame", "Screen", "Boxes", "Status"])
            for row in displayed:
                item = QtWidgets.QTreeWidgetItem([row["id"], row["screen"], str(row["boxes"]),
                    f"Ready (+{len(row['assignedIDs'])} local IDs)" if row["ready"] else "Needs attention"])
                item.setData(0, QtCore.Qt.UserRole, row)
                tree.addTopLevelItem(item)
            layout.addWidget(tree)
            details = QtWidgets.QPlainTextEdit()
            details.setObjectName("reviewExceptions")
            details.setReadOnly(True)
            details.setMaximumHeight(115)
            layout.addWidget(details)
            open_frame = QtWidgets.QPushButton("Open selected frame to fix/check")
            open_frame.setObjectName("openReviewFrame")
            layout.addWidget(open_frame)
            def selected():
                item = tree.currentItem()
                row = item.data(0, QtCore.Qt.UserRole) if item else {}
                details.setPlainText("\n".join(row.get("issues", [])) or "Ready for your explicit confirmation.")
                open_frame.setEnabled(bool(row.get("imagePath")))
            tree.itemSelectionChanged.connect(selected)
            def navigate():
                row = tree.currentItem().data(0, QtCore.Qt.UserRole)
                dialog.reject()
                self.loadFile(row["imagePath"])
            open_frame.clicked.connect(navigate)
            tree.setCurrentItem(tree.topLevelItem(0))
            reviewer = QtWidgets.QLineEdit()
            reviewer.setObjectName("bulkReviewer")
            reviewer.setPlaceholderText("Reviewer name (required)")
            layout.addWidget(reviewer)
            consent = QtWidgets.QCheckBox(
                "I reviewed bounds, classes and focus states for ALL Ready frames;\n"
                "those frames are settled and their content is approved.")
            consent.setObjectName("bulkAttestation")
            layout.addWidget(consent)
            completeness = QtWidgets.QCheckBox(
                'Also confirm: ALL visible focusable controls are included in every Ready frame.\n'
                'Optional — leave unchecked if anything is missing or uncertain.')
            completeness.setObjectName('completeFrameAttestation')
            layout.addWidget(completeness)
            buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
            confirm = buttons.addButton("Confirm ready frames and finish", QtWidgets.QDialogButtonBox.AcceptRole)
            confirm.setObjectName("confirmReadyFrames")
            confirm.setEnabled(False)
            def enable_confirm():
                confirm.setEnabled(bool(ready) and bool(reviewer.text().strip()) and consent.isChecked())
            reviewer.textChanged.connect(enable_confirm)
            consent.toggled.connect(enable_confirm)
            buttons.rejected.connect(dialog.reject)
            buttons.accepted.connect(dialog.accept)
            layout.addWidget(buttons)
            if dialog.exec_() != QtWidgets.QDialog.Accepted:
                return
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            output = batch_path.parent / "review-revisions" / (stamp+"-"+uuid4().hex[:8])
            current_image = self.imagePath
            try:
                receipt = bulk.apply_preview(plan, output, reviewer=reviewer.text(), attested=consent.isChecked(),
                                             complete_frames=completeness.isChecked())
            except (ValueError, OSError, KeyError, TypeError) as error:
                if output.exists() and current_image:
                    # Current edits were saved before preview; refresh any partial
                    # applied flags so a later Save cannot overwrite them silently.
                    self.loadFile(current_image)
                QtWidgets.QMessageBox.warning(self, "Finish review blocked",
                    f"{error}\nIf an update started, backups and recovery details are in:\n{output}")
                return
            self.loadFile(current_image)
            QtWidgets.QMessageBox.information(self, "Review revision saved",
                f"Confirmed {len(receipt['appliedFrames'])} ready frames. Pending frames remain blocked.\n"
                f"Saved diagnostic-only revision:\n{output / 'revision/revision.json'}\n"
                "No training admission or model inference. Production crop QA is a separate next step.")

        def reviewContext(self):
            from pathlib import Path
            stem = Path(self.imagePath).stem if self.imagePath else None
            frame = next((f for f in batch["frames"] if f.get("editorStem") == stem), None)
            return (frame["screen"], self.image.width(), self.image.height()) if frame else None

        def saveBoxPreset(self):
            import human_review_presets as presets
            if not self.imagePath:
                return
            shapes = self.canvas.selectedShapes or self.canvas.shapes
            name, ok = QtWidgets.QInputDialog.getText(self, 'Save rectangle preset',
                'Name (for example Home grid or Settings navigation):')
            if not ok:
                return
            try:
                require(all(s.shape_type == 'rectangle' and len(s.points) == 2 for s in shapes), 'rectangles_only')
                boxes = [dict(label=s.label, points=[
                    [min(p.x() for p in s.points), min(p.y() for p in s.points)],
                    [max(p.x() for p in s.points), max(p.y() for p in s.points)]]) for s in shapes]
                presets.save(name.strip(), (self.image.width(), self.image.height()), boxes)
                self.status(f'Saved preset {name}: {len(boxes)} boxes, no focus or approval flags.', 15000)
            except (ValueError, OSError, KeyError, TypeError) as error:
                self.clipboardWarning(str(error))

        def loadBoxPreset(self):
            import human_review_presets as presets
            from labelme.shape import Shape
            if not self.imagePath:
                return
            paths = sorted(presets.DIRECTORY.glob('*.json'))
            if not paths:
                self.clipboardWarning('No presets yet. Draw or select boxes, then Save preset.')
                return
            name, ok = QtWidgets.QInputDialog.getItem(self, 'Load rectangle preset',
                'Choose a compatible layout. Boxes are added; adjust geometry and focus afterward.',
                [p.stem for p in paths], 0, False)
            if not ok:
                return
            try:
                boxes = presets.load(next(p for p in paths if p.stem == name),
                                     (self.image.width(), self.image.height()))
                require(len(self.canvas.shapes) + len(boxes) <= 100, 'too_many_boxes')
                used = {s.group_id for s in self.canvas.shapes}
                ids = iter(i for i in range(1, 100001) if i not in used)
                shapes = []
                for box in boxes:
                    shape = Shape(label=box['label'], shape_type='rectangle', group_id=next(ids),
                                  flags={key: False for key in SHAPE_FLAGS})
                    for x, y in box['points']:
                        shape.addPoint(QtCore.QPointF(x, y))
                    shape.close()
                    shapes.append(shape)
                self.toggleDrawMode(True)
                self.loadShapes(shapes, replace=False)
                for i in range(self.flag_widget.count()):
                    item = self.flag_widget.item(i)
                    if item.text() == 'reviewed':
                        item.setCheckState(QtCore.Qt.Unchecked)
                self.shapeSelectionChanged(shapes)
                self.canvas.update()
                self.setDirty()
                self.status(f'Loaded {len(shapes)} unconfirmed boxes. Adjust bounds and set focus states.', 15000)
            except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
                self.clipboardWarning(str(error))

        def clipboardWarning(self, message):
            QtWidgets.QMessageBox.warning(self, "Box copy/paste", message)

        def selectAllBoxes(self):
            if self.imagePath:
                self.toggleDrawMode(True)
                self.shapeSelectionChanged(list(self.canvas.shapes))
                self.canvas.setFocus()
                self.canvas.update()
                self.status(f"Selected {len(self.canvas.selectedShapes)} boxes; Copy boxes next.")

        def copySelectedShape(self):
            selected = list(self.canvas.selectedShapes)
            if not selected or self.reviewContext() is None:
                self.clipboardWarning("Select boxes first, or use Select all boxes.")
                return
            if any(s.shape_type != "rectangle" or len(s.points) != 2 for s in selected):
                self.clipboardWarning("Only two-corner rectangles can be copied.")
                return
            ids = [s.group_id for s in self.canvas.shapes if s.group_id is not None]
            if any(type(i) is not int or not 0 < i <= 100000 for i in ids) or len(ids) != len(set(ids)):
                self.clipboardWarning("Fix invalid or duplicate Group IDs before copying.")
                return
            # Allocate local review identities only; never infer native identity.
            used = set(ids)
            available = iter(i for i in range(1, 100001) if i not in used)
            missing = [s for s in selected if s.group_id is None]
            if len(missing) > 100000 - len(ids):
                self.clipboardWarning("No unused review IDs remain.")
                return
            for shape in missing:
                shape.group_id = next(available)
                self.labelList.findItemByShape(shape).setText(f"{shape.label} ({shape.group_id})")
            if missing:
                self.setDirty()
            self._copied_shapes = [s.copy() for s in selected]
            self._copy_context = self.reviewContext()
            self.actions.paste.setEnabled(True)
            self.status(f"Copied {len(selected)} boxes; assigned {len(missing)} local IDs. Save before switching frames.", 15000)

        def pasteSelectedShape(self):
            if not self._copied_shapes:
                self.clipboardWarning("Copy boxes in this editor window first.")
                return
            if self.reviewContext() != self._copy_context:
                self.clipboardWarning("Paste requires the same screen type and image dimensions. No boxes changed.")
                return
            existing = {s.group_id for s in self.canvas.shapes}
            if any(s.group_id in existing for s in self._copied_shapes):
                self.clipboardWarning("These control IDs already exist here. Paste will not overwrite or duplicate boxes; use an unannotated frame or copy only missing controls.")
                return
            shapes = [s.copy() for s in self._copied_shapes]
            for shape in shapes:
                shape.flags = {k: bool(shape.flags.get(k, False)) for k in SHAPE_FLAGS}
                shape.flags["confirmed"] = False
            self.toggleDrawMode(True)
            self.loadShapes(shapes, replace=False)
            for i in range(self.flag_widget.count()):
                item = self.flag_widget.item(i)
                if item.text() == "reviewed":
                    item.setCheckState(QtCore.Qt.Unchecked)
            self.shapeSelectionChanged(shapes)
            self.canvas.update()
            self.setDirty()
            self.status(f"Pasted {len(shapes)} proposals. Adjust bounds/focus, then confirm each box and review this frame.", 15000)

    # QSettings(org, app) ignores setDefaultFormat on macOS. Scope this
    # constructor injection tightly; the stock window retains the real object.
    settings_type = QtCore.QSettings
    settings = settings_type(str(runtime/"settings/labelme.ini"), settings_type.IniFormat)
    settings.setFallbacksEnabled(False)
    require(local(settings.fileName()).is_relative_to(runtime), "external_qt_settings")
    # Stock file-list entries retain their path. A local working directory keeps
    # the numbered filenames visible instead of clipping a long absolute prefix.
    os.chdir(batch_path.parent)
    QtCore.QSettings = lambda *args, **kwargs: settings
    try:
        result = RectangleReviewWindow(config=configuration(), filename="editor")
    finally:
        QtCore.QSettings = settings_type
    require(local(result.settings.fileName()).is_relative_to(runtime), "external_qt_settings")
    old_dialog = result.labelDialog
    config = result._config
    result.labelDialog = FocusLabelDialog(parent=result, labels=config['labels'],
        sort_labels=config['sort_labels'], show_text_field=config['show_label_text_field'],
        completion=config['label_completion'], fit_to_content=config['fit_to_content'], flags=config['label_flags'])
    old_dialog.deleteLater()
    dialog = result.labelDialog
    dialog.editDescription.setPlaceholderText('Optional note — normally leave blank')
    dialog.edit.setToolTip('Detector class, or focus:tabItem / focus:otherFocusable for focus-only annotation')
    dialog.labelList.setToolTip('focus: roles do not add detector classes. Tab bar means the container, not its items.')
    for widget in [dialog, *dialog.findChildren(QtWidgets.QWidget)]:
        widget.installEventFilter(dialog)
    dialog.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setDefault(True)
    dialog.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setAutoDefault(False)
    if scope is not None:
        # Keep the stock navigation and visible list backed by the same membership.
        paths = {f['id']: 'editor/'+f['editorStem']+'.png' for f in batch['frames'] if f['disposition'] == 'imported'}
        items = {result.fileListWidget.item(i).text(): result.fileListWidget.item(i).clone()
                 for i in range(result.fileListWidget.count())}
        result.fileListWidget.blockSignals(True)
        result.fileListWidget.clear()
        for frame_id in scope:
            result.fileListWidget.addItem(items[paths[frame_id]])
        result.fileListWidget.blockSignals(False)
        result.loadFile(paths[scope[0]])
        result._frozenReviewQueue = True
        result.fileSearch.setEnabled(False)
        result.fileSearch.setPlaceholderText('Frozen review batch — use Next/Previous')
        result.actions.open.setEnabled(False)
        result.setAcceptDrops(False)

    class RectangleDoubleClick(QtCore.QObject):
        def eventFilter(self, watched, event):
            canvas = result.canvas
            if (event.type() == QtCore.QEvent.MouseButtonDblClick and
                    event.button() == QtCore.Qt.LeftButton and canvas.editing()):
                point = canvas.transformPos(event.localPos())
                for shape in reversed(canvas.shapes):
                    if shape.shape_type == 'rectangle' and canvas.isVisible(shape) and shape.containsPoint(point):
                        canvas.selectShapes([shape])
                        result.editLabel(result.labelList.findItemByShape(shape))
                        event.accept()
                        return True
            return False
    result.rectangleDoubleClick = RectangleDoubleClick(result.canvas)
    result.canvas.installEventFilter(result.rectangleDoubleClick)
    forbidden = [getattr(result.actions, name) for name in
                 ("createMode", "createCircleMode", "createLineMode", "createPointMode", "createLineStripMode")]
    for action in forbidden:
        action.setVisible(False)
        action.setShortcuts([])
    # Rectangles have exactly two corners; polygon vertex removal is not useful.
    result.actions.removePoint.setVisible(False)
    result.actions.removePoint.setShortcuts([])
    result.actions.tool = tuple(result.actions.createRectangleMode if a is result.actions.createMode else a
                                for a in result.actions.tool if a not in forbidden[1:])
    result.actions.menu = tuple(a for a in result.actions.menu if a not in forbidden)
    select_all = QtWidgets.QAction("Select all boxes", result)
    select_all.setIconText("Select all\nboxes")
    select_all.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.SelectAll))
    select_all.triggered.connect(result.selectAllBoxes)
    result.actions.selectAllBoxes = select_all
    result.actions.copy.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Copy))
    result.actions.paste.setShortcuts(QtGui.QKeySequence.keyBindings(QtGui.QKeySequence.Paste))
    clipboard_actions = (select_all, result.actions.copy, result.actions.paste)
    # Stock copy/paste live only in a canvas context menu. Register them in the
    # main menu too so keyboard shortcuts do not depend on opening that menu.
    result.actions.editMenu = clipboard_actions + (None,) + result.actions.editMenu
    preset_actions = []
    for caption, callback in [('Save preset…', result.saveBoxPreset), ('Load preset…', result.loadBoxPreset)]:
        action = QtWidgets.QAction(caption, result)
        action.triggered.connect(callback)
        preset_actions.append(action)
    result.actions.editMenu = tuple(preset_actions) + (None,) + result.actions.editMenu
    result.actions.tool = tuple(preset_actions) + result.actions.tool
    toolbar = list(result.actions.tool)
    toolbar.insert(toolbar.index(result.actions.copy), select_all)
    result.actions.tool = tuple(toolbar)
    toggle_flags = QtWidgets.QAction("All frame flags on", result)
    toggle_flags.triggered.connect(result.toggleFrameFlags)
    result.actions.toggleFrameFlags = toggle_flags
    result.actions.editMenu = (toggle_flags, None) + result.actions.editMenu
    flag_panel = QtWidgets.QWidget()
    flag_layout = QtWidgets.QVBoxLayout(flag_panel)
    flag_layout.setContentsMargins(4, 4, 4, 4)
    result.frameFlagsButton = QtWidgets.QPushButton("All frame flags on")
    result.frameFlagsButton.setObjectName("toggleAllFrameFlags")
    result.frameFlagsButton.setToolTip(
        "Current image only: Reviewed, Settled, Content approved.\n"
        "Turn on only after checking all three. Does not change box focus or confirmation flags.")
    result.frameFlagsButton.clicked.connect(result.toggleFrameFlags)
    flag_layout.addWidget(result.frameFlagsButton)
    flag_layout.addWidget(result.flag_widget)
    result.flag_dock.setWidget(flag_panel)
    result.flag_widget.itemChanged.connect(result.refreshFrameFlags)
    result.refreshFrameFlags()
    result.actions.openNextImg.setToolTip("Next image: Command+Right (macOS), Ctrl+Right (other platforms), or D")
    result.actions.openPrevImg.setToolTip("Previous image: Command+Left (macOS), Ctrl+Left (other platforms), or A")
    finish_review = QtWidgets.QAction("Finish review…", result)
    finish_review.setIconText("Finish\nreview")
    finish_review.setToolTip("Check the whole batch, resolve exceptions, then explicitly confirm ready frames")
    finish_review.triggered.connect(result.finishReview)
    result.actions.finishReview = finish_review
    result.actions.editMenu = (finish_review, None) + result.actions.editMenu
    toolbar = list(result.actions.tool)
    toolbar.insert(toolbar.index(result.actions.save)+1, finish_review)
    result.actions.tool = tuple(toolbar)
    result.actions.editMode.setText("Edit rectangles")
    result.actions.editMode.setToolTip("Move boxes or drag corners; E")
    result.actions.createRectangleMode.setText("Create rectangle")
    result.actions.createRectangleMode.setToolTip("Draw an axis-aligned box; R")
    for name, caption in (("editMode", "Edit rectangles"), ("createRectangleMode", "Create rectangle"),
                          ("duplicate", "Duplicate boxes"), ("copy", "Copy boxes"),
                          ("paste", "Paste boxes"), ("delete", "Delete boxes")):
        action = getattr(result.actions, name)
        action.setText(caption)
        action.setIconText(caption.replace(" ", "\n", 1))
    result.labelList.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
    result.refreshFocusList()
    result.populateModeActions()
    result.toggleDrawMode(True)
    result.setWindowTitle("NUIAK diagnostic review — save edits, then Finish batch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch")
    parser.add_argument("--frame", help="Start at an exact imported frame ID")
    parser.add_argument('--queue', help='Frozen diagnostic regression queue')
    parser.add_argument('--batch-index', type=int, help='One-based eight-frame queue slice')
    parser.add_argument("--runtime", default=str(ROOT/"reports/work/HUMAN-REVIEW-01/runtime"))
    args = parser.parse_args()
    configure(args.runtime)
    from qtpy import QtWidgets
    app = QtWidgets.QApplication([sys.argv[0]])
    widget = window(args.batch, args.runtime, args.queue, args.batch_index)
    widget.show()
    if args.frame:
        # window() changes cwd for short numbered file-list entries.
        batch = validate_batch(os.path.join(os.getcwd(), "batch.json"))
        frame = next((f for f in batch["frames"] if f["id"] == args.frame and f["disposition"] == "imported"), None)
        require(frame is not None, "unknown_start_frame")
        require('editor/'+frame['editorStem']+'.png' in widget.imageList, 'start_frame_outside_queue')
        app.processEvents()
        widget.loadFile("editor/"+frame["editorStem"]+".png")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
