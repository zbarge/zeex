from core.compat import QtGui, QtCore
from core.models.filetree import FileTreeModel


class FileSystemTreeView(QtGui.QTreeView):
    def __init__(self, parent=None, root_dir=None):
        QtGui.QTreeView.__init__(self, parent=parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setModel(FileTreeModel(parent=parent, root_dir=root_dir))
        self.setColumnWidth(0, 400)

    def dropEvent(self, event):
        print("dropEvent Called")
        if event.source() == self:
         QtGui.QAbstractItemView.dropEvent(self, event)

    def dropMimeData(self, parent, row, data, action):
        print("{} {} {} {}".format(parent, row, data, action))
        if action == QtCore.Qt.MoveAction:
            return self.moveSelection(parent, row)
        return False

    def mimeData(self, indexes):
        print(indexes)

    def get_selected_path(self):
        pass

    def get_selected_dataframe_model(self):
        pass