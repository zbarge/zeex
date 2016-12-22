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
from qtpandas.models.DataFrameModel import DataFrameModel


class ColumnsModel(QtGui.QStandardItemModel):
    def __init__(self, df_model: DataFrameModel=None):
        QtGui.QStandardItemModel.__init__(self)
        self.df_model = None
        if df_model is not None:
            self.set_df_model(df_model)

    def set_df_model(self, df_model):
        df_model.dataChanged.connect(self.sync_columns)
        self.df_model = df_model
        self.sync_columns()

    @property
    def df(self):
        return self.df_model.dataFrame()

    def get_dtype(self, col):
        return self.df[col].dtype

    def sync_columns(self):
        current_items = [i.text() for i in self.get_items()]
        current_checked = [i.text() for i in self.get_items_checked()]
        checkstates = {c:(True if c in current_checked else False) for c in current_items}
        self.clear()
        cols = [str(c) for c in self.df.columns]
        cols = [QtGui.QStandardItem(c) for c in sorted(cols)]
        for c in cols:
            checked = checkstates.get(c.text(), False)
            if not checked:
                checkstate = QtCore.Qt.Unchecked
            else:
                checkstate = QtCore.Qt.Checked

            c.setCheckable(True)
            c.setEditable(False)
            c.setCheckState(checkstate)
            self.appendRow(c)

    def get_items_checked(self):
        return [i for i in self.get_items() if i.checkState() is QtCore.Qt.Checked]

    def get_items(self):
        return [self.item(i) for i in range(self.rowCount())]

