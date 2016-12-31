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
from core.utility.widgets import create_standard_item, get_ok_msg_box
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
        self.actionConnectToDatabase.triggered.connect(self.connect_database)
        self.actionDisconnectFromDatabase.triggered.connect(self.disconnect_database)
        self.actionExportFile.triggered.connect(self.export_table)
        self.actionImportFile.triggered.connect(self.import_table)
        self.actionAddDatabase.triggered.connect(self.add_database)
        self.actionExecuteQuery.triggered.connect(self.execute_query)
        self.actionExecuteSelectedQuery.triggered.connect(self.execute_query_selected)
        self.treeView.expanded.connect(self.sync_current_database)

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
            self.comboBoxCurrentFile.insertItem(0, file_path)
            idx = self.comboBoxCurrentFile.findText(file_path)
        self.comboBoxCurrentFile.setCurrentIndex(idx)

    def set_current_database(self, db_name):
        idx = self.comboBoxCurrentDatabase.findText(db_name)
        if idx < 0:
            self.comboBoxCurrentDatabase.insertItem(0, db_name)
            idx = self.comboBoxCurrentDatabase.currentIndex()
        self.comboBoxCurrentDatabase.setCurrentIndex(idx)

    def sync_current_database(self, idx):
        item = self.tree_model.itemFromIndex(idx)
        if not item.parent():
            # It's a database
            self.set_current_database(item.text())
        elif not item.parent().parent():
            # It's a table
            self.set_current_database(item.parent().text())
        elif not item.hasChildren():
            # It's a column
            self.set_current_database(item.parent().parent().text())

    def connect_database(self, db_name):
        """
        Sets the currently active database.
        This one is a 'tough' design call because the con_manager
        automatically generates connections for databases
        in order to read out their MetaData and such...
        :param db_name: (str)
            The name of the database to activate
        :return: None
        """
        if db_name is None:
            db_name = self.tree_model.findItems(db_name)[0].text()
        self.set_current_database(db_name)

    def disconnect_database(self):
        """
        Sets the comboBoxCurrentDatabase to blank.
        :param db_name: (str)
            The name of the database to deactivate.
        :return: None
        """
        self.set_current_database('')

    def import_table(self, db_name, table_name, **kwargs):
        """
        Opens a DatabaseTableImportDialog for the current (or given)
        database name allowing the user to import a DataFrameModel.
        :param db_name: (str)
            The name of a registered AlchemyConnection/database
        :param table_name: (str)
            The name of the table to add
        :param kwargs:
        :return:
        """
        pass

    def export_table(self, db_name, table_name, **kwargs):
        """
        Opens export dialog for current database displaying
        a DatabaseTableExportDialog. The user can export a table
        to a file from there.
        :param db_name:
        :param table_name:
        :param kwargs:
        :return: (None)
        """
        pass

    def add_database(self, *args, **kwargs):
        """
        Registers a new database connection.
        and sync's the databases treeview.

        This is also a slot that gets activated
        when the DatabaseImportDialog is accepted.

        See zeex.core.ctrls.sql.AlchemyConnectionManager.add_connection(*args, **kwargs)
        for more details.

        :param args: (AlchemyConnectionManager.add_connection(*args, **kwargs))
        :param kwargs: (AlchemyConnectionManager.add_connection(*args, **kwargs))
        :return: (None)
        """
        name = kwargs.get('name', None)
        con = kwargs.get('connection', None)
        check_name = (name if name is not None else con.name)
        kwargs['allow_duplicate'] = False
        self.con_manager.add_connection(*args, **kwargs)
        self.refresh_schemas()

    def execute_query(self, db_name=None, selected_text_only=False):
        """
        Executes the given SQL query against the given database.
        Displays a message box with the error (if any), otherwise:
        Stores the DataFrameModel to the TableView.

        :param db_name: (str)
            The name of the database to execute the query on.
        :param selected_text_only: (bool, default False)
            True executes only the selected text in the textEdit
            False executes the entire text no matter what.
        :return: None
        """
        if db_name is None:
            db_name = self.comboBoxCurrentDatabase.currentText()
        con = self.con_manager.connection(db_name)
        statement = self.textEdit.textCursor().selectedText().lstrip().rstrip()
        if selected_text_only is False or statement is '':
            statement = self.textEdit.document().toPlainText().lstrip().rstrip()
        try:
            self._last_df_model = dfm = con.execute_sql(statement)
        except Exception as e:
            box = get_ok_msg_box(self, str(e), title="ERROR EXECUTING QUERY")
            box.show()
            raise
        self.tableView.setModel(dfm)


    def execute_query_selected(self, db_name=None):
        """
        Executes the selected text against the given database.
        DatabasesMainWindow.execute_query(db_name, selected_text_only=True)
        :param db_name: (str)
            The database to execute the query on.
        :return: None
        """
        return self.execute_query(db_name=db_name, selected_text_only=True)























