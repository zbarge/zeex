"""
MIT License

Copyright (c) 2016 Zeke Barge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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