# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:02:26 2016

@author: Zeke
"""
import os
from core.utility.uiloader import loadUiWidget   
from core.views.settings import MainSettings
from core.models.filetree import FileTreeModel

here = os.path.dirname(__file__)

class ZeexMainWindow(object):
    ui_path = os.path.join(here, "main.ui").replace("\\","/")
    def __init__(self, parent=None):
        super(ZeexMainWindow, self).__init__()
        
        self.ui = loadUiWidget(self.ui_path, parent)
        self.Settings = MainSettings()
        self.connect_actions()
        self.connect_filetree()
        
    def connect_actions(self):
        self.ui.actionSettings.triggered.connect(   self.open_settings)
        self.ui.actionOpen.triggered.connect(       self.open_existing_project)
        self.ui.actionNew.triggered.connect(        self.open_new_project)
        self.ui.actionEdit.triggered.connect(       self.open_edit_project)
        
    def connect_filetree(self):
        rootdir = self.Settings.ui.rootDirectoryLineEdit.text()
        if not os.path.exists(rootdir):
            os.mkdir(rootdir)
        model = FileTreeModel(root_dir=rootdir)    
        self.ui.ProjectsTreeView.setModel(model)

    def show(self):
        self.ui.show()
        
    def open_settings(self):
        self.Settings.ui.exec_()
        
    def open_existing_project(self):
        pass
    
    def open_new_project(self):
        pass
    
    def open_edit_project(self):
        pass