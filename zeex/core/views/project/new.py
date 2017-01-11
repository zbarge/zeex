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
import shutil
from zeex.core.compat import QtGui, QtCore
from zeex.core.ui.project.new_ui import Ui_NewProjectDialog


class NewProjectDialog(QtGui.QDialog, Ui_NewProjectDialog):
    signalProjectNew = QtCore.Signal(list) #[dirname, settings.ini]

    def __init__(self, base_dirname=None, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self._base_dirname = base_dirname
        self.setupUi(self)
        self.namePushButton.clicked.connect(self.set_dirname)
        self.settingsFilePushButton.clicked.connect(self.set_config_ini)
        self.buttonBox.accepted.connect(self.create_project)
        self.buttonBox.rejected.connect(self.close)
        self.namePushButton.hide()
        self.nameLineEdit.setText("Folder Name:")

    def set_dirname(self):
        dirname = QtGui.QFileDialog.get(self)
        self.nameLineEdit.setText(dirname)

    def set_base_dirname(self, dirname):
        assert not os.path.isfile(dirname)
        self._base_dirname = dirname

    def set_config_ini(self):
        ini_file = QtGui.QFileDialog.getOpenFileName()
        self.settingsFileLineEdit.setText(ini_file[0])

    def create_project(self):
        proj_dirname = self.nameLineEdit.text()

        if os.path.isdir(proj_dirname):
            proj_dirname = os.path.basename(proj_dirname)

        if self._base_dirname is not None:
            proj_dirname = os.path.join(self._base_dirname, proj_dirname)
        else:
            raise AttributeError("NewProjectDialog.set_base_dirname and try again. Invalid directory: '{}'".format(
                                  self._base_dirname))

        proj_ini = self.settingsFileLineEdit.text()
        ini_correct = os.path.join(proj_dirname, os.path.basename(proj_ini))

        if not os.path.exists(proj_dirname):
            os.mkdir(proj_dirname)

        if not os.path.exists(ini_correct):
            shutil.copy2(proj_ini, ini_correct)

        self.signalProjectNew.emit([proj_dirname, ini_correct])
        self.close()











 