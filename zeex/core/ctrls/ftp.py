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
from zeex.core.compat import QtNetwork


class QtFtpConnection(object):
    def __init__(self, *args, **kwargs):
        self.manager = NetworkAccessManager(QtNetwork.QNetworkAccessManager(), self)
        self.downloader = Downloader(self, self.manager)


class FtpConnection(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.qcon = QtFtpConnection()

    def con_ftputil(self):
        return ftputil.FTPHost(*self.args, **self.kwargs)

    def con_qt(self):



class FtpManager(object):
    def __init__(self, settings_ini=None):
        self._settings_ini = settings_ini
        self._connections = {}


    @property
    def settings_ini(self):
        if self._settings_ini is None:
            self._settings_ini = SettingsINI()
        return self._settings_ini

    def con(self, name):
        return