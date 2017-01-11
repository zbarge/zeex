# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 11:04:32 2016

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

from zeex.core.compat import QtGui, QtCore


class FileTreeModel(QtGui.QFileSystemModel):
    def __init__(self, parent=None, root_dir=None):
        QtGui.QFileSystemModel.__init__(self, parent)
        self._root_dir = root_dir
        self.setRootPath(self._root_dir)

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        print(mimedata)
        print(action)
        print(row)
        print(column)
        print(parentIndex)

    def mimeData(self, indexes):
        print("MimeData")
        index = indexes[0]
        mimedata = QtCore.QMimeData()
        mimedata.setData(u'filepath', QtCore.QByteArray(u'testtest'))
        return mimedata

    def setData(self, index, value, role):
        super(FileTreeModel, self).setData(index, value, role)


