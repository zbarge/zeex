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
from ...ui.sql.main_ui import Ui_DatabasesMainWindow
from ...compat import QtGui
from ...models.fieldnames import connection_info as fieldnames_connection_info
DEFAULT_CONNECTIONS = {'field_names': fieldnames_connection_info}
from ...ctrls.sql import AlchemyConnectionManager


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
        self.setupUi(self)
        if connection_manager is None:
            self.con_manager = AlchemyConnectionManager()
        else:
            self.con_manager = connection_manager
        self.connect_database_treeview()
        self.connect_default_databases()

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
        pass

    def delete(self, idx):
        item = self.tree_model.itemFromIndex(idx)
        if item:
            if not item.parent():
                # Top level item...delete an entire database??
                pass
            elif not item.parent().parent():
                # It's a table
                pass
            elif not item.hasChildren():
                # It's a column
                pass


















