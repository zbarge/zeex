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

from zeex.core.ui.ftp.main_ui import Ui_FtpMainWindow
from zeex.core.compat import QtGui, QtCore
from zeex.core.ctrls.main import MainController

class FtpMainWindow(QtGui.QMainWindow, Ui_FtpMainWindow):
    def __init__(self, main_controller: MainController, *args, **kwargs):
        QtGui.QMainWindow.__init__(self, **kwargs)
        self.setupUi(self)
        self.main_control = main_controller
        self._current_connection = None

    @property
    def ftp_manager(self):
        return self.main_control.ftp_manager

    @property
    def current_connection(self):
        return self._current_connection

    def get_credential_line_edits(self):
        return dict(
                    host = self.lineEditHost.text(),
                    username = self.lineEditUsername.text(),
                    password = self.lineEditPassword.text(),
                    port = self.lineEditPort.text())

    def set_credential_line_edits(self, host='', username='', password='', port=''):
        self.lineEditHost.setText(host)
        self.lineEditUsername.setText(username)
        self.lineEditPassword.setText(password)
        self.lineEditPort.setText(port)

    def connect(self, **kwargs):
        if kwargs:
            self.set_credential_line_edits(**kwargs)
        kwargs = self.get_credential_line_edits()
        assert '.' in str(kwargs['host']), "Invalid host: {}".format(kwargs['host'])
        self.ftp_manager.register_connection(**kwargs)
        con = self.ftp_manager.con(kwargs['host'])
        self.treeViewRemote.setModel(con.get_filesystem_model())
        self._current_connection = con



