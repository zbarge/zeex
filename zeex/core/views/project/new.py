# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:38:36 2016
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
from core.compat import QtGui, QtCore
from core.ui.project.new_ui import Ui_NewProjectDialog


class NewProjectDialog(QtGui.QDialog, Ui_NewProjectDialog):
    signalProjectNew = QtCore.Signal(list) #[dirname, settings.ini]

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.namePushButton.clicked.connect(self.set_dirname)
        self.settingsFilePushButton.clicked.connect(self.set_config_ini)
        self.buttonBox.accepted.connect(self.create_project)
        self.buttonBox.rejected.connect(self.close)

    def set_dirname(self):
        dirname = QtGui.QFileDialog.getExistingDirectory(self)
        self.nameLineEdit.setText(dirname)

    def set_config_ini(self):
        ini_file = QtGui.QFileDialog.getOpenFileName()
        self.settingsFileLineEdit.setText(ini_file[0])

    def create_project(self):
        proj_dirname = self.nameLineEdit.text()
        proj_ini = self.settingsFileLineEdit.text()

        if not os.path.exists(proj_dirname):
            os.mkdir(proj_dirname)
        self.signalProjectNew.emit([proj_dirname, proj_ini])
        self.close()











 