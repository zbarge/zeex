import os

from core.compat import QtGui, QtCore
from core.ui.basic.directory_ui import Ui_DirectoryViewDialog
from core.views.basic.line_edit import DirectoryPathCreateDialog
from icons import Icons


class DirectoryViewDialog(QtGui.QDialog, Ui_DirectoryViewDialog):
    signalDownloadReady = QtCore.Signal()
    def __init__(self, source_view=None, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self._source_view = source_view
        self.setupUi(self)
        self.icons = Icons()

    def configure(self):
        self.btnDelete.clicked.connect(self.delete)
        self.btnDownload.clicked.connect(self.download)
        self.btnRefresh.clicked.connect(self.refresh)
        self.btnUpload.clicked.connect(self.upload)
        self.btnAddFolder.clicked.connect(self.add_folder)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def upload(self):
        pass

    def download(self):
        pass

    def delete(self):
        pass

    def refresh(self):
        pass

    def add_folder(self):
        pass

    @property
    def source_view(self):
        return self._source_view

    def set_source_view(self, tree_view):
        self._source_view = tree_view


from core.utility.qtdropbox import QtDropBox


class DropBoxViewDialog(DirectoryViewDialog):
    def __init__(self, source_view, parent):
        DirectoryViewDialog.__init__(self, source_view=source_view, parent=parent)
        self.dropbox = QtDropBox()
        self.dialog_add_folder = DropBoxDirectoryPathCreateDialog(self.dropbox, treeview=self.treeView,
                                                                  base_dirname="/", parent=self)
        self.configure()

    def configure(self):
        self.setWindowIcon(self.icons['dropbox'])
        self.setWindowTitle("DropBox")
        self.dialog_add_folder.setWindowTitle("Add DropBox Folder")
        self.dialog_add_folder.signalDirectoryCreated.connect(self.refresh)
        super(DropBoxViewDialog, self).configure()

    def upload(self):
        indexes = self.source_view.selectedIndexes()
        paths = list(set([self.source_view.model().filePath(i) for i in indexes]))
        to = self.treeView.model().directory(self.treeView.selectedIndexes()[0])
        for p in paths:
            self.dropbox.upload_file(p, to)
            print("DropBox - Uploaded {} to {}".format(p, to))

    def download(self):
        index = self.source_view.selectedIndexes()[0]
        to = self.source_view.model().filePath(index)
        from_idx = self.treeView.selectedIndexes()[0]
        from_path = self.treeView.model().filePath(from_idx)

        if os.path.isfile(to):
            to = os.path.dirname(to)
        to = os.path.join(to, os.path.basename(from_path))
        self.dropbox.download_file(from_path, to)
        print("DropBox - Downloaded {} to {}".format(from_path, to))

    def refresh(self):
        self.treeView.setModel(self.dropbox.get_filesystem_model(update=True))

    def delete(self):
        from_idx = self.treeView.selectedIndexes()[0]
        from_path = self.treeView.model().filePath(from_idx)
        # Don't delete if there are children.
        child = from_idx.child(0, 0)
        if child.row() >= 0:
            # Way too easy to make a big mistake otherwise
            raise Exception("Can't delete folder that is not empty.")
        self.dropbox.con.files_delete(from_path)
        print("DropBox - Deleted {}".format(from_path))
        self.refresh()

    def show(self, *args, **kwargs):
        self.refresh()
        super(DirectoryViewDialog, self).show(*args, **kwargs)

    def add_folder(self):
        self.dialog_add_folder.show()


class DropBoxDirectoryPathCreateDialog(DirectoryPathCreateDialog):

    def __init__(self, qtdropbox:QtDropBox, **kwargs):
        DirectoryPathCreateDialog.__init__(self, **kwargs)
        self.dropbox = qtdropbox
        self.autorename = False

    def execute(self):
        model = self.treeview.model()
        b = self.base_dirname

        try:
            idx = self.treeview.selectedIndexes()[0]
            b = model.directory(idx)
            if '.' in b[-5:]:
                b = model.directory(idx.parent())
        except (IndexError, Exception) as e:
            assert b is not None, "Unable to verify base directory, error: {}".format(e)
        if b.endswith("/"):
            b = b[:-1]
        directory = b + self.lineEdit.text()
        self.dropbox.con.files_create_folder(directory, autorename=self.autorename)
        self.signalDirectoryCreated.emit(directory)



