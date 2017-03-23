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
import ftputil
from zeex.core.utility.collection import SettingsINI, DictConfig
from zeex.ext.ftp.downloader import Downloader
from zeex.ext.ftp.networkaccessmanager import NetworkAccessManager
from zeex.ext.ftp.ftpreply import FtpReply
from zeex.core.compat import QtNetwork, QtGui, QtCore


class FtpConnection(object):
    """
    Holds ftputil FTP credentials.
    Uses either a QFtp connection or a
    FtpUtil connection depending on the request.
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.host = kwargs.pop('host')
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')
        self.port = kwargs.get('port', 21)

    def __call__(self, *args, **kwargs):
        """Call the FtpConnection class to get a ftputil.FTPHost object"""
        if args is None:
            user = self.username
            password = self.password
            host = self.host
        else:
            user, password, host = args

        return ftputil.FTPHost(host, user, password, **kwargs)

    def get_filesystem_model(self):
        model = QtGui.QStandardItemModel()
        directories, files = [], []
        dir_row = 0
        with self() as ftp:
            for dirname, subdirs, files in ftp.walk():
                dir_item = QtGui.QStandardItem(dirname)
                directories.append(dirname)
                file_row = 0
                for f in files:
                    fp = dirname + "/" + f
                    file_item = QtGui.QStandardItem(fp)
                    dir_item.addChild(file_row, file_item)
                    file_row += 1
                model.setItem(dir_row, dir_item)
                dir_row += 1
        return model





class FtpManager(object):
    def __init__(self, settings_ini=None):
        self._settings_ini = settings_ini
        self._connections = {}

    @property
    def settings_ini(self):
        if self._settings_ini is None:
            self._settings_ini = SettingsINI()
        return self._settings_ini

    @property
    def connections(self) -> dict:
        return self._connections

    def con(self, host) -> FtpConnection:
        return self.connections.get(host, None)

    def register_connection(self, *args, **kwargs) -> FtpConnection:
        if not kwargs.get('host', None):
            try:
                kwargs['host'] = args.pop(0)
            except IndexError:
                raise IndexError("Must provide the host as the first argument or a host keyword argument.")
        assert not args, "There should be no arguments aside from a host"
        con = self.connections(kwargs['host'])

        if con is None:
            con = FtpConnection(**kwargs)
            self._connections[con.host] = con
        return con





