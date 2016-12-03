# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:02:26 2016

@author: Zeke
"""
import os
from core.views.settings import SettingsDialog
from core.views.project.new import NewProjectDialog
from core.views.uis.main_ui import Ui_HomeWindow
from core.models.filetree import FileTreeModel
from PySide import QtGui


class ZeexMainWindow(QtGui.QMainWindow, Ui_HomeWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.SettingsDialog = SettingsDialog()
        self.connect_actions()
        self.connect_filetree()
        
    def connect_actions(self):
        self.actionSettings.triggered.connect(   self.open_settings)
        self.actionOpen.triggered.connect(       self.open_existing_project)
        self.actionNew.triggered.connect(        self.open_new_project)
        self.actionEdit.triggered.connect(       self.open_edit_project)
        
    def connect_filetree(self):
        rootdir = self.SettingsDialog.rootDirectoryLineEdit.text()
        if not os.path.exists(rootdir):
            os.mkdir(rootdir)
        model = FileTreeModel(root_dir=rootdir)    
        self.ProjectsTreeView.setModel(model)
        
    def open_settings(self):
        self.SettingsDialog.exec_()
        
    def open_existing_project(self):
        pass
    
    def open_new_project(self):
        pass
    
    def open_edit_project(self):
        pass