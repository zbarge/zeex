# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:02:26 2016

@author: Zeke
"""
import os
from core.utility.collection import get_ini_file, SettingsINI
from core.views.settings import SettingsDialog
from core.views.project.new import NewProjectDialog
from core.views.main_ui import Ui_HomeWindow
from core.models.filetree import FileTreeModel
from core.views.project.main import ProjectMainWindow
from PySide import QtGui, QtCore


class ZeexMainWindow(QtGui.QMainWindow, Ui_HomeWindow):
    signalProjectOpened = QtCore.Signal(list) # [dirname, settings.ini]

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.SettingsDialog = SettingsDialog()
        self.NewProjectDialog = NewProjectDialog()
        self.NewProjectDialog.signalProjectNew.connect(self.open_existing_project)
        self.connect_actions()
        self.connect_filetree()
        self._project_cache = {}
        
    def connect_actions(self):
        self.actionSettings.triggered.connect(   self.open_settings)
        self.actionOpen.triggered.connect(       self.open_existing_project)
        self.actionNew.triggered.connect(        self.create_new_project)
        self.actionEdit.setVisible(False)

    def connect_filetree(self):
        rootdir = self.SettingsDialog.rootDirectoryLineEdit.text()
        if not os.path.exists(rootdir):
            os.mkdir(rootdir)
        model = FileTreeModel(root_dir=rootdir)    
        self.ProjectsTreeView.setModel(model)
        self.ProjectsTreeView.setRootIndex(model.index(rootdir))
        
    def open_settings(self):
        self.SettingsDialog.exec_()

    @QtCore.Slot(list)
    def open_existing_project(self, contents: list = None):
        if contents:
            # New project came in off the slot.
            dirname, ini = contents
        else:
            # User must have selected off the tree.
            try:
                idx = self.ProjectsTreeView.selectedIndexes()[0]
            except IndexError:
                # User failed to select anything..
                return self.display_ok_msg("No project folder selected")

            dirname = idx.model().filePath(idx)
            ini = get_ini_file(dirname)

        # See if project is cached.
        try:

            self._project_cache[dirname].show()

        except KeyError:
            # Oh well, not cached...
            # Make sure the project is valid
            assert ini and os.path.exists(ini), "Need a settings.ini file for project '{}'".format(dirname)
            assert dirname and os.path.exists(dirname), "Directory '{}' needs to exist!".format(dirname)
            p = os.path.normpath
            assert not p(dirname) == p(self.SettingsDialog.rootDirectoryLineEdit.text()), "Project directory cannot be the root!"

            # Update ROOT_DIRECTORY in settings.
            Settings = SettingsINI(ini)
            Settings.set('GENERAL', 'ROOT_DIRECTORY', dirname)
            ini_name = os.path.basename(ini)

            # Make sure the ini file goes
            # in the home folder of the project.
            ini = os.path.join(dirname, ini_name)
            with open(ini, "w") as ns:
                Settings.write(ns)

            #Build & cache window
            window = ProjectMainWindow(dirname, ini)
            self._cache_project(dirname, window)
            self.signalProjectOpened.emit([dirname, ini])
            window.show()

    def display_ok_msg(self, msg):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setText(msg)
        msgBox.exec_()

    def create_new_project(self):
        # Creates new project dialog and
        # Routes the user back to self.open_existing_project
        self.NewProjectDialog.exec_()

    def _cache_project(self, dirname, window):
        self._project_cache.update({dirname: window})
