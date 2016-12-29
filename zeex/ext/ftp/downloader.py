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


from core.compat import QtCore, QtGui, QtNetwork, QtWebKit


class Downloader(QtCore.QObject):

    def __init__(self, parentWidget, manager):
        super(Downloader, self).__init__(parentWidget)

        self.manager = manager
        self.reply = None
        self.downloads = {}
        self.path = ""
        self.parentWidget = parentWidget

    def chooseSaveFile(self, url):
        fileName = url.path().split("/")[-1]
        if len(self.path) != 0:
            fileName = QtCore.QDir(self.path).filePath(fileName)

        return QtGui.QFileDialog.getSaveFileName(self.parentWidget, u"Save File", fileName);

    def startDownload(self, request):
        self.downloads[request.url().toString()] = self.chooseSaveFile(request.url())

        reply = self.manager.get(request)
        reply.finished.connect(self.finishDownload)

    def saveFile(self, reply):
        newPath = self.downloads.get(reply.url().toString())

        if not newPath:
            newPath = self.chooseSaveFile(reply.url())[0]
        if isinstance(newPath, tuple):
            newPath = newPath[0]
        if len(newPath) != 0:
            file = QtCore.QFile(newPath)
            if file.open(QtCore.QIODevice.WriteOnly):
                file.write(reply.readAll())
                file.close()
                path = QtCore.QDir(newPath).dirName()
                QtGui.QMessageBox.information(self.parentWidget, u"Download Completed", u"Saved '%s'." % newPath)
            else:
                QtGui.QMessageBox.warning(self.parentWidget, u"Download Failed", u"Failed to save the file.")

    def finishDownload(self):
        reply = self.sender()
        self.saveFile(reply)
        self.downloads.pop(reply.url().toString(), None)
        reply.deleteLater()
