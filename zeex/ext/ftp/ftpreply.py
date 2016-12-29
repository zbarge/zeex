############################################################################
##
## Copyright (C) 2014 Moritz Warning <moritzwarning@web.de>.
## Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
## Contact: Nokia Corporation (qt-info@nokia.com)
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
############################################################################


from core.compat import QtCore, QtNetwork


class FtpReply(QtNetwork.QNetworkReply):

    def __init__(self, url, parent):
        super(FtpReply, self).__init__(parent)

        self.items = []
        self.content = ""

        self.ftp = QtNetwork.QFtp(self)
        self.ftp.listInfo.connect(self.processListInfo)
        self.ftp.readyRead.connect(self.processData)
        self.ftp.commandFinished.connect(self.processCommand)

        self.offset = 0
        self.units = ["bytes", "K", "M", "G", "Ti", "Pi", "Ei", "Zi", "Yi"]

        self.setUrl(url)
        self.ftp.connectToHost(url.host())

    def processCommand(self, _, err):

        if err:
            self.setError(QtNetwork.QNetworkReply.ContentNotFoundError, "Unknown command")
            self.error.emit(QtNetwork.QNetworkReply.ContentNotFoundError)

        cmd = self.ftp.currentCommand()
        if cmd == QtNetwork.QFtp.ConnectToHost:
            self.ftp.login()
        elif cmd == QtNetwork.QFtp.Login:
            self.ftp.list(self.url().path())
        elif cmd == QtNetwork.QFtp.List:
            if len(self.items) == 1:
                self.ftp.get(self.url().path())
            else:
                self.setListContent()
        elif cmd == QtNetwork.QFtp.Get:
            self.setContent()

    def processListInfo(self, urlInfo):
        self.items.append(QtNetwork.QUrlInfo(urlInfo))

    def processData(self):
        self.content += str(self.ftp.readAll())

    def setContent(self):
        self.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Unbuffered)
        self.setHeader(QtNetwork.QNetworkRequest.ContentLengthHeader, QtCore.QVariant(len(self.content)))
        self.readyRead.emit()
        self.finished.emit()
        self.ftp.close()

    def setListContent(self):
        u = self.url()
        if not u.path().endswith("/"):
            u.setPath(u.path() + "/")

        base_url = self.url().toString()
        base_path = u.path()

        self.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Unbuffered)
        content = (
            u'<html>\n'
            '<head>\n'
            '  <title>%s</title>\n'
            '  <style type="text/css">\n'
            '  th { background-color: #aaaaaa; color: black }\n'
            '  table { border: solid 1px #aaaaaa }\n'
            '  tr.odd { background-color: #dddddd; color: black\n }\n'
            '  tr.even { background-color: white; color: black\n }\n'
            '  </style>\n'
            '</head>\n\n'
            '<body>\n'
            '<h1>Listing for %s</h1>\n\n'
            '<table align="center" cellspacing="0" width="90%%">\n'
            '<tr><th>Name</th><th>Size</th></tr>\n' % (QtCore.Qt.escape(base_url), base_path))

        parent = u.resolved(QtCore.QUrl(".."))

        if parent.isParentOf(u):
            content += (u'<tr><td><strong><a href="%s">' % parent.toString()
            + u'Parent directory</a></strong></td><td></td></tr>\n')

        i = 0
        for item in self.items:
            child = u.resolved(QtCore.QUrl(item.name()))

            if i == 0:
                content += u'<tr class="odd">'
            else:
                content += u'<tr class="even">'

            content += u'<td><a href="%s">%s</a></td>' % (child.toString(), QtCore.Qt.escape(item.name()))

            size = item.size()
            unit = 0
            while size:
                new_size = size/1024
                if new_size and unit < len(self.units):
                    size = new_size
                    unit += 1
                else:
                    break

            if item.isFile():
                try:
                    bit = self.units[unit]
                except IndexError:
                    bit = 'UNK'
                content += u'<td>%s %s</td></tr>\n' % (str(size), bit)
            else:
                content += u'<td></td></tr>\n'

            i = 1 - i

        content += u'</table>\n</body>\n</html>\n'

        self.content = content.encode('utf-8')

        self.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, QtCore.QVariant("text/html; charset=UTF-8"))
        self.setHeader(QtNetwork.QNetworkRequest.ContentLengthHeader, QtCore.QVariant(len(self.content)))
        self.readyRead.emit()
        self.finished.emit()
        self.ftp.close()

    def abort(self):
        pass

    def bytesAvailable(self):
        return len(self.content) - self.offset + QtNetwork.QNetworkReply.bytesAvailable(self)

    def isSequential(self):
        return True

    def readData(self, maxSize):
        if self.offset < len(self.content):
            number = min(maxSize, len(self.content) - self.offset)
            data = self.content[self.offset:self.offset+number]
            self.offset += number
            return data
        return None
