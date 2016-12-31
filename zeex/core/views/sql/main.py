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
import os
from ...ui.sql.main_ui import Ui_DatabasesMainWindow
from ...compat import QtGui
from ...models.fieldnames import connection_info as fieldnames_connection_info
from ...ctrls.sql import AlchemyConnectionManager
from core.utility.widgets import create_standard_item
DEFAULT_CONNECTIONS = {'field_names': fieldnames_connection_info}


class DatabasesMainWindow(QtGui.QMainWindow, Ui_DatabasesMainWindow):
    """
    The general query/database maintenance MainWindow that is home
    to the following main objects:
        - A ToolBar with actions for simple database actions.
        - A TreeView of all databases registered.
        - A TextEdit for writing SQL queries
        - A TableView for viewing results.
    """
    def __init__(self, *args, connection_manager: AlchemyConnectionManager = None, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        self._last_text_dir = ''
        self._last_text_path = ''
        self.setupUi(self)
        if connection_manager is None:
            self.con_manager = AlchemyConnectionManager()
        else:
            self.con_manager = connection_manager
        self.connect_database_treeview()
        self.connect_default_databases()
        self.connect_actions()

    @property
    def tree_model(self) -> QtGui.QStandardItemModel:
        return self.treeView.model()

    def connect_database_treeview(self):
        model = self.treeView.model()
        model = self.con_manager.get_standard_item_model(model=model)
        self.treeView.setModel(model)

    def connect_default_databases(self):
        new = False
        for name, ci in DEFAULT_CONNECTIONS.items():
            try:
                self.con_manager.connection(name)
            except KeyError:
                self.con_manager.add_connection(name=name, **ci)
                new = True
        if new:
            self.connect_database_treeview()

    def connect_actions(self):
        self.actionRemove.triggered.connect(self.delete)
        self.actionRefreshSchemas.triggered.connect(self.refresh_schemas)
        self.actionSaveText.triggered.connect(self.save_last_sql_text)
        self.actionSaveTextAs.triggered.connect(self.save_sql_text)
        self.actionOpenFile.triggered.connect(self.open_sql_text)

    def refresh_schemas(self):
        self.treeView.setModel(self.con_manager.get_standard_item_model())

    def delete(self, idx=None):
        if idx is None:
            idx = self.treeView.selectedIndexes()
            if not idx:
                raise Exception("Nothing selected to delete!")
            idx = idx[0]
        item = self.tree_model.itemFromIndex(idx)
        if item:
            if not item.parent():
                # It's a database - just remove it off the list
                self.con_manager.remove_connection(item.text())
                self.tree_model.takeRow(item.row())
            elif not item.parent().parent():
                # It's a table
                db_item = item.parent()
                table_name = item.text()
                db_name = db_item.text()
                con = self.con_manager.connection(db_name)
                table = con.meta.tables[table_name]
                table.drop(checkfirst=True)
                db_item.removeRow(item.row())
            elif not item.hasChildren():
                # It's a column
                table_item = self.tree_model.itemFromIndex(item.parent().index())
                db_name = self.tree_model.itemFromIndex(table_item.parent().index()).text()
                con = self.con_manager.connection(db_name)
                table_name = table_item.text()
                try:
                    sql = "ALTER TABLE '{}' DROP COLUMN '{}'".format(table_name, item.text())
                    con.engine.execute(sql)
                    table_item.removeRow(item.row())
                except Exception:
                    raise NotImplementedError("Unable to drop columns for SQL version: {}".format(
                        con.engine.name))

    def save_sql_text(self, file_path=''):
        if file_path is '':
            file_path = QtGui.QFileDialog.getSaveFileName(dir=self._last_text_dir)[0]

        self._last_text_dir = os.path.dirname(file_path)
        with open(file_path, "w") as fp:
            fp.write(self.textEdit.document().toPlainText())
        self.set_current_file(file_path)

    def save_last_sql_text(self):
        self.save_sql_text(file_path=self._last_text_path)

    def open_sql_text(self, file_path=''):
        if file_path is '':
            file_path = QtGui.QFileDialog.getOpenFileName(dir=self._last_text_dir)[0]
        self._last_text_dir = os.path.dirname(file_path)
        self._last_text_path = file_path
        with open(file_path, "r") as fp:
            self.textEdit.setPlainText(fp.read())
        self.set_current_file(file_path)

    def set_current_file(self, file_path):
        idx = self.comboBoxCurrentFile.findText(file_path)
        if idx < 0:
            self.comboBoxCurrentFile.addItem(file_path)
            idx = self.comboBoxCurrentFile.findText(file_path)
        self.comboBoxCurrentFile.setCurrentIndex(idx)





















