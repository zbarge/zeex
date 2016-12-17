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


class FileViewModel(QtGui.QStandardItemModel):

    def __init__(self, models=None):
        QtGui.QStandardItemModel.__init__(self)
        self._df_models = {}
        if models is not None:
            [self.append_df_model(m) for m in models]

    def append_df_model(self, model):
        file_path = model.filePath
        f = QtGui.QStandardItem(file_path)
        c = QtGui.QStandardItem(str(model.dataFrame().index.size))
        row = self.rowCount()
        self.setItem(row, 0, f)
        self.setItem(row, 1, c)





