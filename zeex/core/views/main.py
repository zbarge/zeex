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
from zeex.core.compat import QtGui, QtCore
from zeex.core.ui.main_ui import Ui_HomeWindow
from zeex.core.utility.ostools import zipfile_compress, zipfile_unzip
from zeex.core.views.basic.directory import DropBoxViewDialog
from zeex.core.views.sql.main import DatabasesMainWindow
from zeex.core.ctrls.main import MainController
from zeex.icons import icons_rc
import logging


class ZeexMainWindow(QtGui.QMainWindow, Ui_HomeWindow):

    def __init__(self, main_controller: MainController, configure=True):
        QtGui.QMainWindow.__init__(self)
        self.control = main_controller
        self.setupUi(self)
        self.dialog_cloud = None
        self.window_sql = DatabasesMainWindow(parent=self)
        self.key_enter = QtGui.QShortcut(self)
        self.key_delete = QtGui.QShortcut(self)
        if configure:
            self.configure()
        
    def configure(self):
        self.connect_cloud_dialog()

        self.control.main_window = self
        self.btnClearFilter.clicked.connect(lambda: self.lineEditFilter.setText(''))
        self.btnOpenProject.clicked.\
             connect(lambda: self.control.tree_set_project_from_file_path(self.comboBoxProject.currentText()))
        self.btnOpenFile.clicked.connect(self.open_combo_box_file)
        self.control.register_tree_views(projects=self.treeView, project=self.treeView_2, configure=True)
        self.lineEditFilter.textChanged.connect(self.filter)
        self.actionGeneralSettings.triggered.connect(self.control.dialog_settings_main.show)
        self.actionProjectSettings.triggered.connect(self.open_project_settings)
        self.actionOpenProject.triggered.connect(self.control.tree_set_project)
        self.actionNewProject.triggered.connect(self.create_new_project)
        self.actionZip.triggered.connect(self.handle_compression)
        self.actionUnzip.triggered.connect(self.handle_compression)
        self.actionEdit.setVisible(False)
        self.actionMergePurge.triggered.connect(lambda: self.control.current_project.get_dialog_merge_purge().show())
        self.actionSQL.triggered.connect(self.window_sql.show)
        self.actionOpenSheet.triggered.connect(self.open_sheet)
        self.actionRename.triggered.connect(lambda: self.control.current_project.get_dialog_rename_path().show())
        self.actionImportSheet.triggered.connect(lambda: self.control.current_project.dialog_import_df_model.show())
        self.key_enter.setKey('return')
        self.key_enter.activated.connect(self.control.tree_set_project)
        self.key_enter.activated.connect(self.open_sheet)
        self.key_delete.setKey('del')
        self.key_delete.activated.connect(self.remove_tree_selected_path)
        # TODO: Show these actions when they do something.
        self.actionSaveFile.setVisible(False)
        self.actionPurgeFile.setVisible(False)
        self.setWindowIcon(QtGui.QIcon(':/standard_icons/home.png'))

    def connect_cloud_dialog(self):
        try:
            self.dialog_cloud = DropBoxViewDialog(self.treeView_2, self)
            self.actionViewCloud.triggered.connect(self.dialog_cloud.show)
            self.actionViewCloud.setIcon(QtGui.QIcon(':/standard_icons/dropbox.png'))
        except Exception as e:
            logging.warning("Error connecting to cloud: {}".format(e))
            self.actionViewCloud.setVisible(False)

    def open_combo_box_file(self):
        file_path = self.comboBoxFile.currentText()
        orig_path = file_path
        project = None
        while project is None:
            file_path = os.path.dirname(file_path)
            project = self.control.project(file_path)
            if os.path.dirname(file_path) == file_path:
                break
        self.control.tree_set_project_from_file_path(file_path)
        self.control.current_project.df_manager.get_fileview_window(orig_path).show()

    def create_new_project(self):
        # Creates new project dialog and
        # Routes the user back to self.open_existing_project
        self.control.dialog_new_project.show()

    def handle_compression(self, fpath=None, **kwargs):
        if fpath is None:
            fpath = self.get_tree_selected_path()
        assert fpath is not None, "No selected path!"
        if not fpath.lower().endswith('.zip'):
            return zipfile_compress(fpath, **kwargs)
        else:
            return zipfile_unzip(file_path=fpath)

    def get_tree_selected_path(self):
        selected = self.treeView_2.selectedIndexes()
        if selected:
            idx = selected[0]
            return self.treeView_2.model().filePath(idx)

    def remove_tree_selected_path(self):
        #TODO: need to emit a signal here.
        idxes = self.treeView_2.selectedIndexes()
        if idxes:
            file_model = self.treeView.model()
            for idx in idxes:
                if not file_model.isDir(idx):
                    file_model.remove(idx)
                else:
                    file_model.rmdir(idx)

    def open_sheet(self):
        w = self.control.get_fileview_window()
        if w is not None:
            w.show()

    def open_project_settings(self):
        w = self.control.get_project_settings_dialog()
        w.show()

    def filter(self):
        info = self.lineEditFilter.text()
        model = self.treeView_2.model()
        if info != '':
            if not info.startswith("*"):
                info = "*" + info
            if not info.endswith("*"):
                info += "*"
            model.setNameFilters([info])
        else:
            model.setNameFilters(['*'])