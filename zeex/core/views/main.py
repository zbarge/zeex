# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:02:26 2016

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
from icons import Icons
from core.compat import QtGui, QtCore
from core.models.filetree import FileTreeModel
from core.ui.main_ui import Ui_HomeWindow
from core.utility.collection import get_ini_file, SettingsINI
from core.views.project.main import ProjectMainWindow
from core.views.project.new import NewProjectDialog
from core.views.settings import SettingsDialog


class ZeexMainWindow(QtGui.QMainWindow, Ui_HomeWindow):
    signalProjectOpened = QtCore.Signal(list)          # [dirname, settings.ini]

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.setMaximumHeight(600)
        self.setMaximumWidth(800)
        self.icons = Icons()
        self.SettingsDialog = SettingsDialog(parent=self)
        self.NewProjectDialog = NewProjectDialog(parent=self)

        self.connect_actions()
        self.connect_filetree()
        self.connect_icons()
        self._project_cache = {}
        
    def connect_actions(self):
        self.NewProjectDialog.signalProjectNew.connect(self.open_project)
        self.SettingsDialog.signalSettingsSaved.connect(self.connect_filetree)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionOpen.triggered.connect(self.open_project)
        self.actionNew.triggered.connect(self.create_new_project)
        self.actionEdit.setVisible(False)

    def connect_icons(self):
        self.setWindowIcon(self.icons['home'])
        self.NewProjectDialog.setWindowIcon(self.icons['spreadsheet'])
        self.SettingsDialog.setWindowIcon(self.icons['settings'])

        self.actionSettings.setIcon(self.icons['settings'])
        self.actionNew.setIcon(self.icons['add'])
        self.actionOpen.setIcon(self.icons['folder'])
        self.actionEdit.setIcon(self.icons['edit'])
        self.actionSave.setIcon(self.icons['save'])

    @QtCore.Slot()
    def connect_filetree(self, rootdir=None):
        """
        Handles the FileSystemModel for the home view.
        Connects with SettingsDialog.signalProjectSaved.
        Ignores the SettingsINI file emitted.

        :param rootdir: (str, default=None)
            a filepath to set as the root of the filetree.
            The SettingsDialog.rootDirectoryLineEdit is used
            as a backup.
        :return: None
        
        """
        if rootdir is None or isinstance(rootdir, SettingsINI):
            rootdir = self.SettingsDialog.rootDirectoryLineEdit.text()

        if not os.path.exists(rootdir):
            os.mkdir(rootdir)

        model = self.ProjectsTreeView.model()

        if model is None:
            model = FileTreeModel(root_dir=rootdir)
            self.ProjectsTreeView.setModel(model)

        if model.rootPath() is not rootdir:
            self.ProjectsTreeView.setRootIndex(model.index(rootdir))
            self.ProjectsTreeView.setColumnWidth(0, 175)
        
    def open_settings(self):
        self.SettingsDialog.show()

    @QtCore.Slot(list)
    def open_project(self, contents: list = None):
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
            assert ini and os.path.exists(ini), "Need a settings.ini file for project '{}'- got: '{}'".format(dirname, ini)
            assert dirname and os.path.exists(dirname), "Directory '{}' needs to exist!".format(dirname)
            p = os.path.normpath
            root_dir = p(self.SettingsDialog.rootDirectoryLineEdit.text())
            assert not p(dirname) == root_dir, "Project directory cannot be the root!"

            # Update ROOT_DIRECTORY in settings.
            settings = SettingsINI(ini)
            settings.set('GENERAL', 'ROOT_DIRECTORY', dirname)
            ini_name = os.path.basename(ini)

            # Make sure the ini file goes
            # in the home folder of the project.
            ini = os.path.join(dirname, ini_name)
            settings.save_as(ini, set_self=True)

            # Build & cache window
            window = ProjectMainWindow(ini, parent=self)
            self._cache_project(dirname, window)
            self.signalProjectOpened.emit([dirname, ini])
            window.show()

    def display_ok_msg(self, msg):
        box = QtGui.QMessageBox(self)
        box.setText(msg)
        box.show()

    def create_new_project(self):
        # Creates new project dialog and
        # Routes the user back to self.open_existing_project
        self.NewProjectDialog.show()

    def _cache_project(self, dirname, window):
        self._project_cache.update({dirname: window})
