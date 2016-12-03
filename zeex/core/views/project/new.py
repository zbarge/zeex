# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:38:36 2016

@author: Zeke
"""

from PySide import QtGui
from core.views.project.uis.new_ui import Ui_NewProjectDialog


class NewProjectDialog(QtGui.QDialog, Ui_NewProjectDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)


 