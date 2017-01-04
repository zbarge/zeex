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
from zeex.core.compat import QtGui, QtCore
from zeex.core.ui.sql.query_editor_ui import Ui_QueryEditorWindow
from zeex.core.views.basic.criteria import CriteriaDialog, CriteriaTableModel
from zeex.core.models.sql import AlchemyTableModel


class AlchemyQueryEditorWindow(QtGui.QMainWindow,Ui_QueryEditorWindow):
    def __init__(self, alchemy_query_model: AlchemyTableModel, **kwargs):
        QtGui.QMainWindow.__init__(self, **kwargs)
        self._query_model = alchemy_query_model
        self._dialog_criteria = CriteriaDialog(parent=self)
        self.configure()

    def configure(self):
        self.setupUi(self)

        self.actionCommit.triggered.connect(self._query_model.commit)
        self.actionUndo.triggered.connect(self._query_model.rollback)
        self.actionRefresh.triggered.connect(self._query_model.refresh)
        self.tableView.setModel(self._query_model)
        self.actionCriteria.triggered.connect(self._dialog_criteria.show)
        self.dialog_criteria.set_fields(self._query_model.fields)

    @property
    def query_model(self) -> AlchemyTableModel:
        return self._query_model

    @property
    def dialog_criteria(self) ->CriteriaDialog:
        return self._dialog_criteria

