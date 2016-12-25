from core.compat import QtGui, QtCore
from core.ui.directory_ui import Ui_DirectoryViewDialog
from icons import Icons
import os

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
        self.configure()

    def configure(self):
        self.setWindowIcon(self.icons['dropbox'])
        self.setWindowTitle("DropBox")
        super(DropBoxViewDialog, self).configure()

    def upload(self):
        indexes = self.source_view.selectedIndexes()
        paths = list(set([self.source_view.model().filePath(i) for i in indexes]))
        to = self.treeView.model().directory(self.treeView.selectedIndexes()[0])
        for p in paths:
            self.dropbox.upload_file(p, to)

    def download(self):
        index = self.source_view.selectedIndexes()[0]
        to = self.source_view.model().filePath(index)
        from_idx = self.treeView.selectedIndexes()[0]
        from_path = self.treeView.model().filePath(from_idx)

        if os.path.isfile(to):
            to = os.path.dirname(to)
        to = os.path.join(to, os.path.basename(from_path))
        self.dropbox.download_file(from_path, to)
        print("Directory: {}, File: {}".format(os.path.isdir(to), os.path.isfile(to)))

    def refresh(self):
        self.treeView.setModel(self.dropbox.get_filesystem_model(update=True))

    def delete(self):
        from_idx = self.treeView.selectedIndexes()[0]
        from_path = self.treeView.model().filePath(from_idx)
        res = self.dropbox.con.files_delete(from_path)
        print(res)


    def show(self, *args, **kwargs):
        self.refresh()
        super(DirectoryViewDialog, self).show(*args, **kwargs)




