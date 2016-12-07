# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:38:36 2016

@author: Zeke
"""
import os
from core.compat import QtGui, QtCore
from core.ui.project.new_ui import Ui_NewProjectDialog


class NewProjectDialog(QtGui.QDialog, Ui_NewProjectDialog):
    signalProjectNew = QtCore.Signal(list) #[dirname, settings.ini]
    def __init__(self):
        QtGui.QDialog.__init__(self)
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











 