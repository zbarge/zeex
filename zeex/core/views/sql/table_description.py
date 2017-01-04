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

from zeex.core.ctrls.sql import AlchemyConnection
from zeex.core.ui.sql.table_description_ui import Ui_AlchemyTableDescriptionDialog
from zeex.core.compat import QtGui
import zeex.core.utility.widgets as widgets


class AlchemyTableDescriptionDialog(QtGui.QDialog, Ui_AlchemyTableDescriptionDialog):
    def __init__(self, con:AlchemyConnection, **kwargs):
        QtGui.QDialog.__init__(self, **kwargs)
        self._con = con
        self._query = None
        self._sess = None
        self._col_model = None
        self._rows_delete = []
        self.configure()

    @property
    def con(self) -> AlchemyConnection:
        return self._con

    def configure(self):
        self.setupUi(self)
        self.btnDeleteColumn.clicked.connect(self.append_delete_row)
        self.btnAddColumn.clicked.connect(self.append_model_row)

    def set_table(self, table_name):
        Table = self.con.meta.tables[table_name]
        data = [[c.name, c.type] for c in Table.columns]
        data = [[widgets.create_standard_item(str(c), editable=True) for c in x] for x in data]
        model = QtGui.QStandardItemModel()
        [model.appendRow(r) for r in data]

        if self._sess is not None:
            self._sess.close()
        self._sess = self._con.Session()
        self._query = self._sess.query(Table)
        self._col_model = model
        self.labelTableNameValue.setText(table_name)
        self.labelRowCountValue.setText(str(self._query.count()))
        self.labelColumnCountValue.setText(str(len(self.con.get_column_names(table_name))))
        self.labelDatabaseValue.setText("{}: {}".format(self.con.engine.name, self.con.name))
        self.tableView.setModel(self._col_model)
        self._col_model.setHorizontalHeaderLabels(['Column Name', 'Data Type'])

    def append_delete_row(self):
        idx = self.tableView.selectedIndexes()[0]
        items = [self._col_model.takeItem(idx.row(), r)
                 for r in range(self._col_model.columnCount())]
        self._col_model.takeRow(idx.row())
        self._rows_delete.append(items)

    def append_model_row(self):
        data = ['COLUMN_NAME', 'COLUMN_DTYPE']
        data = [widgets.create_standard_item(d, editable=True, checkable=False) for d in data]
        self._col_model.insertRow(self._col_model.rowCount(), data)


    def save(self):
        Table = self.con.meta.tables[self.labelTableNameValue.text()]
        for i in self._col_model.rowCount():
            old, new, dtype = [self._col_model.item(i, r)
                               for r in self._col_model.rowCount()]


