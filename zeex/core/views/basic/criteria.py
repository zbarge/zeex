# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:09:50 2016
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
from core.utility.collection import Eval
from core.compat import QtGui, QtCore
from core.ui.basic.criteria_ui import Ui_CriteriaDialog
from core.utility.widgets import create_standard_item
Qt = QtCore.Qt


class CriteriaTableModel(QtGui.QStandardItemModel):
    headers = ['group', 'field', 'condition', 'value', 'andor']

    def __init__(self):
        QtGui.QStandardItemModel.__init__(self)

    @property
    def fields(self):
        return list(self.dictionary.keys())

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.headers[col]
        elif orientation == Qt.Vertical:
            return col

        return None

    def add_criterion(self, data: (list, dict), index=None):
        if index is None:
            row = self.rowCount()
        else:
            row = index.row()

        if isinstance(data, dict):
            data = [data.get(h, None) for h in self.headers]

        if len(data) != len(self.headers):
            raise KeyError("Data and header lengths are mismatched: {} {}".format(data, self.headers))

        for i in range(len(data)):
            self.setItem(row, i, create_standard_item(data[i], editable=True, checkable=False))

    def add_criteria(self, criteria:list):
        for c in criteria:
            self.add_criterion(c)

    def add_last_criterion(self):
        self.add_criteria(self.data_list[-1])

    def get_criteria(self):
        col_range = range(len(self.headers))
        row_range = range(self.rowCount())
        return [[self.item(row, col) for col in col_range]
                for row in row_range]


class CriteriaDialog(QtGui.QDialog, Ui_CriteriaDialog):
    def __init__(self, *args, **kwargs):
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.configure()

    @property
    def criteria_table_model(self) -> CriteriaTableModel:
        return self.tableViewCriteria.model()

    @property
    def criteria_list(self) -> list:
        return self.criteria_table_model.get_criteria()

    @property
    def criteria_dict(self) -> list:
        headers = self.criteria_table_model.headers
        return [{h: d for h, d in zip(headers, c)}
                for c in self.criteria_list]

    def configure(self):
        self.setupUi(self)
        self.btnAddCriteria.clicked.connect(self.add_criteria)
        self.btnDeleteCriteria.clicked.connect(self.delete_criteria)
        self.btnPushDown.clicked.connect(self.push_field_down)
        self.btnPushUp.clicked.connect(self.push_field_up)
        self.tableViewCriteria.setModel(CriteriaTableModel())

    def add_criteria(self):
        data = [self.lineEditGroup.text(),
                    self.comboBoxField.currentText(),
                    self.comboBoxCondition.currentText(),
                    self.lineEditValue.text(),
                    self.comboBoxAndOr.currentText()]
        self.criteria_table_model.add_criterion(data)

    def add_group(self, name=None):
        if name is None:
            name = self.lineEditGroup.text()
        match = self.listView.model().findItems(name)
        if not match:
            self.listView.model().appendRow(create_standard_item(name, editable=False, checkable=False))

    def delete_criteria(self, idx=None):
        if idx is None:
            idx = self.tableViewCriteria.selectedIndexes()[0]
        self.criteria_table_model.takeRow(idx.row())

    def delete_group(self, idx=None):
        if idx is None:
            idx = self.listView.selectedIndexes()[0]
        self.listView.model().takeRow(idx.row())

    def edit_criteria(self, idx):
        pass

    def set_fields(self, fields: list):
        for f in fields:
            match = self.comboBoxField.findText(f)
            if match <=0:
                self.comboBoxField.addItem(f)
        for i in range(self.comboBoxField.model().rowCount()):
            exists = self.comboBoxField.model().item(i).text() in fields
            if not exists:
                self.comboBoxField.model().takeRow(i)

    def push_field_down(self):
        idx = self.tableViewCriteria.selectedIndexes()[0]
        row = idx.row()
        if row < self.criteria_table_model.rowCount()-1:
            self.criteria_table_model.insertRow(row+2)
            for i in range(self.criteria_table_model.columnCount()):
               self.criteria_table_model.setItem(row+2,i,self.criteria_table_model.takeItem(row,i))
            self.criteria_table_model.takeRow(row)
            self.tableViewCriteria.setCurrentIndex(
                self.criteria_table_model.item(row + 1, 0).index())

    def push_field_up(self):
        idx = self.tableViewCriteria.selectedIndexes()[0]
        row = idx.row()
        if row > 0:
            self.criteria_table_model.insertRow(row-1)
            for i in range(self.criteria_table_model.columnCount()):
                self.criteria_table_model.setItem(row - 1, i, self.criteria_table_model.takeItem(row + 1, i))
            self.criteria_table_model.takeRow(row+1)
            self.tableViewCriteria.setCurrentIndex(self.criteria_table_model.item(row - 1, 0).index())

