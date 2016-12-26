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
from core.compat import QtGui, QtCore
from core.models.filetree import FileTreeModel
from core.ui.main_ui import Ui_HomeWindow
from core.utility.collection import get_ini_file, SettingsINI
from core.utility.ostools import zipfile_compress
from core.views.basic.directory import DropBoxViewDialog
from core.views.project.main import ProjectMainWindow
from core.views.project.new import NewProjectDialog
from core.views.settings import SettingsDialog
from icons import Icons


class ZeexMainWindow(QtGui.QMainWindow, Ui_HomeWindow):
    signalProjectOpened = QtCore.Signal(list)          # [dirname, settings.ini]

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.setMaximumHeight(600)
        self.setMaximumWidth(800)
        self.icons = Icons()
        self.dialog_settings = SettingsDialog(parent=self)
        self.dialog_new_project = NewProjectDialog(parent=self)
        self.dialog_cloud = DropBoxViewDialog(self.treeView, parent=self)
        self.key_enter = QtGui.QShortcut(self)
        self.key_delete = QtGui.QShortcut(self)

        self.connect_actions()
        self.connect_filetree()
        self.connect_icons()
        self._project_cache = {}
        
    def connect_actions(self):
        self.key_delete.setKey('del')
        self.key_enter.setKey('return')
        self.dialog_new_project.signalProjectNew.connect(self.open_project)
        self.dialog_settings.signalSettingsSaved.connect(self.connect_filetree)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionOpen.triggered.connect(self.open_project)
        self.actionNew.triggered.connect(self.create_new_project)
        self.actionViewCloud.triggered.connect(self.dialog_cloud.show)
        self.actionZipFolder.triggered.connect(self.zip_path)
        self.actionEdit.setVisible(False)
        self.key_enter.activated.connect(self.open_project)
        self.key_delete.activated.connect(self.remove_tree_selected_path)
        # TODO: Show these actions when they do something.
        self.actionSave.setVisible(False)

    def connect_icons(self):
        self.setWindowIcon(self.icons['home'])
        self.dialog_new_project.setWindowIcon(self.icons['spreadsheet'])
        self.dialog_settings.setWindowIcon(self.icons['settings'])

        self.actionSettings.setIcon(self.icons['settings'])
        self.actionNew.setIcon(self.icons['add'])
        self.actionOpen.setIcon(self.icons['folder'])
        self.actionEdit.setIcon(self.icons['edit'])
        self.actionSave.setIcon(self.icons['save'])
        self.actionZipFolder.setIcon(self.icons['archive'])
        self.actionViewCloud.setIcon(self.icons['cloud'])

    @QtCore.Slot()
    def connect_filetree(self, rootdir=None):
        """
        Handles the FileSystemModel for the home view.
        Connects with dialog_settings.signalProjectSaved.
        Ignores the SettingsINI file emitted.

        :param rootdir: (str, default=None)
            a filepath to set as the root of the filetree.
            The dialog_settings.rootDirectoryLineEdit is used
            as a backup.
        :return: None
        
        """
        if rootdir is None or isinstance(rootdir, SettingsINI):
            rootdir = self.dialog_settings.rootDirectoryLineEdit.text()
            rootdir = os.path.realpath(rootdir)

        if not os.path.exists(rootdir):
            os.mkdir(rootdir)

        model = self.treeView.model()

        if model is None:
            model = FileTreeModel(root_dir=rootdir)
            self.treeView.setModel(model)

        if model.rootPath() is not rootdir:
            print("root directory: {}".format(rootdir))
            self.treeView.setRootIndex(model.index(rootdir))
            self.treeView.setColumnWidth(0, 175)
        
    def open_settings(self):
        self.dialog_settings.show()

    @QtCore.Slot(list)
    def open_project(self, contents: list = None):
        if contents:
            # New project came in off the slot.
            dirname, ini = contents
        else:
            # User must have selected off the tree.
            try:
                idx = self.treeView.selectedIndexes()[0]
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
            root_dir = p(self.dialog_settings.rootDirectoryLineEdit.text())
            assert not p(dirname) == root_dir, "Project directory cannot be the root!"

            # Update ROOT_DIRECTORY in settings.
            settings = SettingsINI(ini)
            settings.set_path('GENERAL', 'ROOT_DIRECTORY', dirname)
            ini_name = os.path.basename(ini)

            # Make sure the ini file goes
            # in the home folder of the project.
            ini = os.path.join(dirname, ini_name)
            settings.save_as(ini, set_self=True)

            # Build & cache window
            window = ProjectMainWindow(settings, parent=self)
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
        self.dialog_new_project.show()

    def _cache_project(self, dirname, window):
        self._project_cache.update({dirname: window})

    def zip_path(self, fpath=None, **kwargs):
        if fpath is None:
            fpath = self.get_tree_selected_path()
        assert fpath is not None, "No selected path!"
        return zipfile_compress(fpath, **kwargs)

    def get_tree_selected_path(self):
        selected = self.treeView.selectedIndexes()
        if selected:
            idx = selected[0]
            return self.treeView.model().filePath(idx)
        return None

    def remove_tree_selected_path(self):
        # TODO: need to emit a signal here.
        filename = self.get_tree_selected_path()
        if filename is not None:
            os.remove(filename)