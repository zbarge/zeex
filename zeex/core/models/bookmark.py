# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:02:26 2016

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
from zeex.core.ctrls.bookmark import BookmarkManager
from zeex.core.compat import QtGui, QtCore

Qt = QtCore.Qt


class BookMarkModel(QtGui.QStandardItemModel):
    """
    A QStandardItemModel representing the data
    stored in a BookmarkManager.
    """
    header = ['name', 'file_path']

    def __init__(self, manager: BookmarkManager):
        QtGui.QStandardItemModel.__init__(self)
        self.manager = manager
        self.header = self.header.copy()

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.header[col]
        elif orientation == Qt.Vertical:
            return col

        return None

    def rowCount(self):
        return len(self.manager.names)

    def columnCount(self):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return None

        elif role not in (Qt.DisplayRole, Qt.EditRole):
            return None

        mark = self.manager.names[index.row()]
        row = self.manager.bookmark(mark)
        name = self.fields[index.column()]

        return str(getattr(row, name))

    def flags(self):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
