from core.ui.basic.line_edit_ui import Ui_LineEditDialog
from core.compat import QtGui, QtCore
import os
from core.utility.ostools import path_incremented


class LineEditDialog(QtGui.QDialog, Ui_LineEditDialog):
    def __init__(self, *args, **kwargs):
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.execute)

    def configure(self):
        raise NotImplementedError("Child classes must implement this method.")

    def execute(self):
        raise NotImplementedError("Child classes must implement this method.")


class FilePathRenameDialog(LineEditDialog):
    """
    Simple LineEditDialog for renaming a filepath.
    """
    def __init__(self, original_path, default_rename=None, parent=None):
        LineEditDialog.__init__(self, parent=parent)
        self.original_path = original_path
        self.default_rename = (original_path if not default_rename else original_path)
        self.configure()

    def configure(self):
        orig_base = os.path.basename(self.original_path)
        new_base = os.path.basename(self.default_rename)
        self.setWindowTitle("Rename {}".format(orig_base))
        self.label.setText("New Name:")
        self.lineEdit.setText(new_base)

    def execute(self):
        new_name = self.lineEdit.text()
        new_path = os.path.join(os.path.dirname(self.original_path), new_name)
        if os.path.exists(new_path):
            new_path = path_incremented(new_path, overwrite=False)
        os.rename(self.original_path, new_path)


class DirectoryPathCreateDialog(LineEditDialog):
    def __init__(self, treeview:QtGui.QTreeView=None, base_dirname=None, parent=None):
        LineEditDialog.__init__(self, parent=parent)
        self.treeview = treeview
        self.base_dirname = base_dirname
        self.configure()

    def configure(self):
        self.setWindowTitle("Add Folder")
        self.label.setText("Folder Name:")

    def set_treeview(self, treeview):
        self.treeview = treeview

    def set_base_dirname(self, dirname):
        self.base_dirname = dirname

    def execute(self):
        b = self.base_dirname
        if self.treeview is not None:
            selected = self.treeview.selectedIndexes()
            if selected:
                idx = selected[0]
                b = self.treeview.model().filePath(idx)
        assert b is not None, "No base directory or selected treeview path found."
        if os.path.isfile(b):
            b = os.path.dirname(b)
        dirname = os.path.join(b, self.lineEdit.text())
        os.mkdir(dirname)