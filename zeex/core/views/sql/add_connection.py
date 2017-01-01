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
from core.ctrls.sql import AlchemyConnectionManager, AlchemyConnection
from core.ui.sql.add_connection_ui import Ui_AlchemyConnectionDialog
from core.compat import QtGui, QtCore
from core.utility.widgets import get_ok_msg_box, configure_combo_box
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine

DBAPI_MAP = {'sqlite':['pysqlite'], 'mysql':['mysqldb','pymysql'],
             'postgresql':['psycopg2']}
DATABASE = {
    'drivername': 'postgres+pg8000',
    'host': '',
    'port': '',
    'username': '',
    'password': '',
    'database': ''
}


class AlchemyConnectionDialog(QtGui.QDialog, Ui_AlchemyConnectionDialog):
    """
    The general query/database maintenance MainWindow that is home
    to the following main objects:
        - A ToolBar with actions for simple database actions.
        - A TreeView of all databases registered.
        - A TextEdit for writing SQL queries
        - A TableView for viewing results.
    """
    signalConnectionAdded = QtCore.Signal(str)
    
    def __init__(self, connection_manager: AlchemyConnectionManager, **kwargs):
        QtGui.QDialog.__init__(self, **kwargs)
        self.con_manager = connection_manager
        self.configure()

    def configure(self):
        db_types = list(sorted(DBAPI_MAP.keys(), reverse=True))
        db_apis = DBAPI_MAP[db_types[0]]
        self.setupUi(self)
        self.btnTestConnection.clicked.connect(self.test_connection)
        self.buttonBox.clicked.connect(self.register_connection)
        self.comboBoxDatabaseType.currentIndexChanged.connect(self.sync_options)
        self.lineEditConnectionURL.textChanged.connect(self.sync_options)
        self.btnClear.clicked.connect(self.reset_line_edit_text)
        self.comboBoxDatabaseType.addItems(db_types)
        self.comboBoxDatabaseAPI.addItems(db_apis)
        self.sync_options()

    def test_connection(self, show_success=True):
        try:
            c = self.get_connection()
            if show_success is True:
                box = get_ok_msg_box(self, "Connected to database!", title="CONNECTION SUCCESS")
                box.show()
            return c
        except Exception as e:
            box = get_ok_msg_box(self, str(e), title="CONNECTION ERROR")
            box.show()
            raise

    def get_connection(self) -> AlchemyConnection:
        """
        Builds an AlchemyConnection as described by the user
        in the line edits/combo boxes.
        :return:
        """
        con_name = self.lineEditConnectionName.text()
        db_type = self.comboBoxDatabaseType.currentText()
        uri = self.lineEditConnectionURL.text()
        if db_type == 'sqlite' and uri == '':
            uri = self.lineEditHost.text()

        a = AlchemyConnection(name=con_name)

        if uri is '':
            port = self.lineEditPort.text()
            host = self.lineEditHost.text()
            username = self.lineEditUsername.text()
            password = self.lineEditPassword.text()
            database = self.lineEditDefaultDatabase.text()
            db_api = self.comboBoxDatabaseAPI.currentText()
            DATABASE = {
                        'drivername': "{}+{}".format(db_type, db_api),
                        'host': host or None,
                        'port': port or None,
                        'username': username or None,
                        'password': password or None,
                        'database': database or None}
            print(DATABASE)
            a._engine = create_engine(URL(**DATABASE))
        else:
            if db_type == 'sqlite' and not uri.startswith('sqlite'):
                uri = 'sqlite:///' + uri.replace("\\", "/").replace("//", "/").replace("/", "\\\\")
            print(uri)
            a._engine = create_engine(uri)

        a.configure(reset=False)
        return a

    def register_connection(self, connection=None):
        """

        :param connection: (AlchemyConnection, default None)
            A optional pre-compiled AlchemyConnection to register to the connection.
            Otherwise one will attempt to generate.
        :return: (None)
        """
        if not isinstance(connection, AlchemyConnection):
            connection = self.test_connection(show_success=False)
        self.con_manager.add_connection(connection=connection)
        self.signalConnectionAdded.emit(connection.name)

    def sync_options(self):
        """
        Keeps the available options in sync on the dialog.
        Makes sure users don't see irrelevant options.

        Example:
            - database type = sqlite
                - hide irrelevant options
            - database type = 'postgresql'
                - show hidden options (if any)
            - database type = 'mysql' & URL provided
                - only show URL
        :return: None
        """
        db_type = self.comboBoxDatabaseType.currentText()
        db_api = self.comboBoxDatabaseAPI.currentText()
        if db_type == 'sqlite' or (self.lineEditConnectionURL.text() != '' and
                                   db_type != 'sqlite'):
            if db_type != 'sqlite':
                self.labelHost.hide()
                self.lineEditHost.hide()
            else:
                self.lineEditConnectionURL.hide()
                self.labelConnectionURL.hide()
            self.lineEditPort.hide()
            self.labelPort.hide()
            self.lineEditDefaultDatabase.hide()
            self.lineEditPassword.hide()
            self.labelPassword.hide()
            self.lineEditUsername.hide()
            self.labelUsername.hide()
            self.labelDefaultDatabase.hide()
            self.labelDatabaseAPI.hide()
            self.comboBoxDatabaseAPI.hide()

        else:
            self.lineEditConnectionURL.show()
            self.labelConnectionURL.show()
            self.lineEditPort.show()
            self.labelPort.show()
            self.labelHost.show()
            self.lineEditHost.show()
            self.lineEditPassword.show()
            self.labelPassword.show()
            self.lineEditUsername.show()
            self.labelUsername.show()
            self.labelDefaultDatabase.show()
            self.lineEditDefaultDatabase.show()
        configure_combo_box(self.comboBoxDatabaseAPI, DBAPI_MAP[db_type], db_api)

    def reset_line_edit_text(self):
        for line in self.findChildren(QtGui.QLineEdit):
            line.setText('')



