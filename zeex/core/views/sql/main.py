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
from zeex.core.ui.sql.main_ui import Ui_DatabasesMainWindow
from zeex.core.compat import QtGui
from zeex.core.models.fieldnames import connection_info as fieldnames_connection_info
from zeex.core.ctrls.sql import AlchemyConnectionManager, AlchemyConnection
from zeex.core.utility.widgets import get_ok_msg_box
from zeex.core.ctrls.dataframe import DataFrameModelManager
from zeex.core.views.sql.add_connection import AlchemyConnectionDialog
from zeex.core.views.sql.table_description import AlchemyTableDescriptionDialog
from zeex.core.ctrls.bookmark import BookmarkManager
from zeex.core.views.sql.table_import import AlchemyTableImportDialog

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
    def __init__(self, *args,
                 df_manager:DataFrameModelManager = None,
                 connection_manager: AlchemyConnectionManager = None, **kwargs):
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        self.bookmarks = BookmarkManager('sql_bookmark_manager')
        self._last_df_model = None
        self._last_text_dir = ''
        self._last_text_path = ''
        self.con_manager = connection_manager
        self.df_manager = df_manager
        self._dialog_add_con = None
        self._dialog_import = None
        self._key_enter = QtGui.QShortcut(self)
        self._key_ctrl_t = QtGui.QShortcut(self)
        self.configure()

    @property
    def tree_model(self) -> QtGui.QStandardItemModel:
        """
        Returns the QStandardItemModel containing
        the databases, tables, and columns.
        :return: (QtGui.QStandardItemModel)
        """
        return self.treeView.model()

    @property
    def dialog_add_con(self) -> AlchemyConnectionDialog:
        if self._dialog_add_con is None:
            self._dialog_add_con = AlchemyConnectionDialog(self.con_manager, parent=self)
            self._dialog_add_con.signalConnectionAdded.connect(self.refresh_schemas)
        return self._dialog_add_con

    @property
    def dialog_import(self) -> AlchemyTableImportDialog:
        if self._dialog_import is None:
            self._dialog_import = AlchemyTableImportDialog(self.connection, self.con_manager,
                                                           df_manager=self.df_manager,
                                                           parent=self)
        return self._dialog_import

    @property
    def connection(self) -> AlchemyConnection:
        return self.con_manager.connection(self.comboBoxCurrentDatabase.currentText())

    def connect_default_databases(self):
        """
        Connects to system databases by default.
        TODO: maybe repurpose this into adding a dictionary of
        database configurations?
        :return: (None)
        """
        new = False
        for name, ci in DEFAULT_CONNECTIONS.items():
            try:
                self.con_manager.connection(name)
            except KeyError:
                try:
                    self.con_manager.add_connection(name=name, **ci)
                    new = True
                except Exception as e:
                    pass

        others = self.con_manager.add_connections_from_settings()
        if new or others:
            self.treeView.setModel(self.con_manager.get_standard_item_model())

    def configure(self):
        """
        called once on __init__
        - Sets AlchemyConnectionManager and/or DataFrameModelManager if they
          were not set in the __init__(**kwargs)
        - Connects default actions
        - sets treeView model.
        :return: (None)
        """
        self.setupUi(self)
        if self.con_manager is None:
            self.con_manager = AlchemyConnectionManager()
        if self.df_manager is None:
            self.df_manager = DataFrameModelManager()
        self._key_enter.setKey('return')
        self._key_ctrl_t.setKey('ctrl+T')
        self._key_enter.activated.connect(self.open_query_alchemyview)
        self._key_ctrl_t.activated.connect(self.open_table_description_dialog)
        self.treeView.setModel(self.con_manager.get_standard_item_model())
        self.actionRemove.triggered.connect(self.delete)
        self.actionRefreshSchemas.triggered.connect(self.refresh_schemas)
        self.actionSaveText.triggered.connect(self.save_last_sql_text)
        self.actionSaveTextAs.triggered.connect(self.save_sql_text)
        self.actionOpenFile.triggered.connect(self.open_sql_text)
        self.actionOpenQueryData.triggered.connect(self.open_query_fileview)
        self.actionConnectToDatabase.triggered.connect(self.connect_database)
        self.actionDisconnectFromDatabase.triggered.connect(self.disconnect_database)
        self.actionExportFile.triggered.connect(self.export_table)
        self.actionImportFile.triggered.connect(self.open_import_dialog)
        self.actionAddDatabase.triggered.connect(self.open_add_connection_dialog)
        self.actionExecuteQuery.triggered.connect(self.execute_query)
        self.actionExecuteSelectedQuery.triggered.connect(self.execute_query_selected)
        self.treeView.expanded.connect(self.sync_current_database)
        self.connect_default_databases()

    def refresh_schemas(self):
        """
        Refreshes the database schemas for each connection.
        Then resets the treeView with the new info.
        :return: (None)
        """
        for c in self.con_manager.connections.keys():
            con = self.con_manager.connection(c)
            con.refresh_schemas()
        self.treeView.setModel(self.con_manager.get_standard_item_model())

    def delete(self, idx=None):
        """
        Deletes a database, table, or column on a database.
        If a database can't support dropping a column (like SQLite), an error
        is raised. Otherwise, the item is removed from the database if it's a table/column,
        the item is always removed from the treeView list if removed.
        :param idx:
        :return:
        """
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
        """
        Saves the current text in the textEdit to file_path.
        :param file_path: (str, default None)
            None will open a QFileDialog to ask for a save name.
        :return: (str)
            Of the saved file_path.
        """
        if file_path == '':
            file_path = self.comboBoxCurrentFile.currentText()
            if file_path == '':
                file_path = QtGui.QFileDialog.getSaveFileName(dir=self._last_text_dir)[0]

        self._last_text_dir = os.path.dirname(file_path)
        new_text = self.textEdit.document().toPlainText()
        with open(file_path, "w") as fp:
            fp.write(new_text)
        if file_path in self.bookmarks.names:
            self.bookmarks.bookmark(file_path).set_text(new_text, save_changes=False)

        self.set_current_file(file_path)

        return file_path

    def save_last_sql_text(self):
        """
        Convenience function to save the last opened text file back
        to disk.
        :return: (str)
            The saved file path
        """
        return self.save_sql_text(file_path=self._last_text_path)

    def open_sql_text(self, file_path=''):
        """
        Reads all text from file_path into the text edit widget
        :param file_path: (str, default '')
            The file_path to open.
            Defaults to a getOpenFileName
        :return: None
        """
        if file_path is '':
            file_path = QtGui.QFileDialog.getOpenFileName(dir=self._last_text_dir)[0]
        self._last_text_dir = os.path.dirname(file_path)
        self._last_text_path = file_path
        self.bookmarks.add_bookmark(file_path, file_path=file_path)
        text = self.bookmarks.bookmark(file_path).get_text()
        self.textEdit.setPlainText(text)
        self.set_current_file(file_path)

    def open_add_connection_dialog(self):
        self.dialog_add_con.show()

    def open_import_dialog(self):
        self.dialog_import.show()

    def open_table_description_dialog(self, idx=None):
        if idx is None:
            idx = self.treeView.selectedIndexes()[0]
        table_name = self.tree_model.itemFromIndex(idx).text()
        con_name = self.tree_model.itemFromIndex(idx.parent()).text()
        con = self.con_manager.connection(con_name)
        self._table_desc_dialog = AlchemyTableDescriptionDialog(con)
        self._table_desc_dialog.set_table(table_name)
        self._table_desc_dialog.show()

    def set_current_file(self, file_path):
        """
        Sets the current file combo box based on the given
        :param file_path. new items are inserted at the top.
        :param file_path: (str)
        :return: None
        """
        idx = self.comboBoxCurrentFile.findText(file_path)
        if idx < 0:
            self.comboBoxCurrentFile.insertItem(0, file_path)
            idx = self.comboBoxCurrentFile.findText(file_path)
        self.comboBoxCurrentFile.setCurrentIndex(idx)

    def set_current_database(self, db_name):
        """
        Sets the current database combo box based on the
        :param db_name. new items are inserted at the top.
        :param db_name: (str)
        :return: None
        """
        idx = self.comboBoxCurrentDatabase.findText(db_name)
        if idx < 0:
            self.comboBoxCurrentDatabase.insertItem(0, db_name)
            idx = self.comboBoxCurrentDatabase.currentIndex()
        self.comboBoxCurrentDatabase.setCurrentIndex(idx)

    def sync_current_database(self, idx):
        """
        Keeps the database combo box item up-to-date based on the
        user's current treeview selection.
        :param idx: (QModelIndex)
            Accepted from TreeView (or anyone, really)
        :return: None
        """
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

    def connect_database(self, db_name=None):
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
            db_name = self.tree_model.itemFromIndex(self.treeView.selectedIndexes()[0]).text()
        self.set_current_database(db_name)

    def disconnect_database(self):
        """
        Sets the comboBoxCurrentDatabase to blank.
        :param db_name: (str)
            The name of the database to deactivate.
        :return: None
        """
        self.set_current_database('')

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

        try:
            con = self.con_manager.connection(db_name)
            statement = self.textEdit.textCursor().selectedText().lstrip().rstrip()
            if selected_text_only is False or statement is '':
                statement = self.textEdit.document().toPlainText().lstrip().rstrip()
            self._last_df_model = dfm = con.execute_sql(statement)
        except Exception as e:
            if isinstance(e, KeyError):
                e = "Invalid database selection: {}".format(e)
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

    def open_query_fileview(self, save_path=None):
        dfm = self.tableView.model()
        assert dfm is not None, "No dataframe model available!"
        if save_path is None:
            if self._last_text_path is not '':
                save_path = os.path.splitext(self._last_text_path)[0] + ".csv"
            else:
                save_path = QtGui.QFileDialog.getSaveFileName(dir=self._last_text_dir)[0]
        base, ext = os.path.splitext(save_path)
        if ext.lower() not in ['.txt','.xlsx', '.csv']:
            save_path = base + ".csv"
        self.df_manager.set_model(dfm, save_path)
        self.df_manager.get_fileview_window(save_path).show()

    def open_query_alchemyview(self):
        con = self.connection
        table_name = self.tree_model.itemFromIndex(self.treeView.selectedIndexes()[0]).text()
        window = con.get_alchemy_query_editor_window(table_name, parent=self)
        window.show()

























