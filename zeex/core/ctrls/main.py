"""
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
from zeex.core.compat import QtGui
from zeex.core.ctrls.sql import AlchemyConnectionManager
from zeex.core.ctrls.project import ProjectController
from zeex.core.views.settings import SettingsDialog, SettingsINI
import zeex.core.utility.widgets as widgets
from zeex.core.views.project.new import NewProjectDialog
from zeex.core.models.filetree import FileTreeModel


class MainController(object):
    def __init__(self, window=None, settings_ini=None):
        self.main_window = window
        self._settings_ini = settings_ini
        self._project_controllers = dict()
        self._con_manager = AlchemyConnectionManager()
        self._tree_view_projects = None
        self._tree_view_project = None
        self._dialog_settings_main = None
        self._dialog_new_project = None
        self._current_project = None

    @property
    def projects(self) -> dict:
        return self._project_controllers

    @property
    def directory(self):
        return self.dialog_settings_main.rootDirectoryLineEdit.text()

    @property
    def con_manager(self) -> AlchemyConnectionManager:
        return self._con_manager

    @property
    def current_project(self) -> ProjectController:
        return self._current_project

    @property
    def dialog_settings_main(self) -> SettingsDialog:
        if self._dialog_settings_main is None:
            self._dialog_settings_main = SettingsDialog(settings=self._settings_ini, parent=self.main_window)
        return self._dialog_settings_main

    @property
    def dialog_new_project(self) -> NewProjectDialog:
        if self._dialog_new_project is None:
            self._dialog_new_project = NewProjectDialog(parent=self.main_window)
            self._dialog_new_project.signalProjectNew.connect(self.tree_set_project_from_dialog)
        return self._dialog_new_project

    @property
    def tree_view(self) -> QtGui.QTreeView:
        return self._tree_view_projects

    @property
    def tree_view_project(self) -> QtGui.QTreeView:
        return self._tree_view_project

    @property
    def settings_ini(self) -> SettingsINI:
        return self.dialog_settings_main.settings_ini

    def project(self, directory) -> ProjectController:
        return self.projects.get(directory, None)

    def register_project(self, obj: ProjectController):
        self.projects[obj.directory] = obj

    def remove_project(self, obj: ProjectController):
        self.projects.pop(obj.directory, None)

    def register_tree_views(self, projects=None, project=None, configure=True):
        if projects is not None:
            self._tree_view_projects = projects
            projects.setColumnWidth(0, 175)
            projects.hideColumn(1)
            projects.hideColumn(2)
            projects.setExpandsOnDoubleClick(False)
            projects.setItemsExpandable(False)

        if project is not None:
            self._tree_view_project = project

        if configure is True:
            self.set_projects_file_tree()

    def build_project_controller(self, dirname, settings_ini=None, tree_view=None, register=True) -> ProjectController:
        if settings_ini is None:
            if os.path.exists(dirname):
                for dirname, subdirs, files in os.walk(dirname):
                    for f in files:
                        if f.endswith('.ini'):
                            try:
                                settings_ini = SettingsINI(filename=os.path.join(dirname, f))
                                if 'GENERAL' in settings_ini.sections():
                                    break
                            except Exception:
                                pass
            if settings_ini is None:
                settings_ini = self.settings_ini.copy()
                settings_ini._default_path = os.path.join(dirname, "config.ini")
                settings_ini._default_backup_path = os.path.join(dirname, "config.ini")
                settings_ini.save()
        controller = ProjectController(dirname, settings_ini, tree_view=tree_view, parent=self.main_window)
        if register is True:
            self.register_project(controller)
        return controller

    def get_fileview_window(self, idx=None):
        model = self.tree_view_project.model()
        project = self.current_project
        if idx is None:
            idx = self.tree_view_project.selectedIndexes()
            if idx:
                idx = idx[0]
            else:
                idx = None

        if idx is not None:
            file_path = model.filePath(idx)
            project.df_manager.read_file(file_path)
            window = project.df_manager.get_fileview_window(file_path, parent=self.main_window)
            if hasattr(self.main_window, 'comboBoxFile'):
                widgets.combo_box_append(self.main_window.comboBoxFile, file_path, select=True)
            return window

    def get_project_settings_dialog(self):
        return self.current_project.dialog_settings

    def tree_set_project(self, idx=None):
        if idx is None:
            idx = self.tree_view.selectedIndexes()[0]

        model = self.tree_view.model()
        file_path = model.filePath(idx)
        project = self.project(file_path)
        if project is None:
            project = self.build_project_controller(file_path, register=True)
        self._current_project = project
        project.tree_view = self._tree_view_project
        if hasattr(self.main_window, 'comboBoxProject'):
            widgets.combo_box_append(self.main_window.comboBoxProject, file_path, select=True)

    def tree_set_project_from_file_path(self, filename):
        idx = self.tree_view.model().index(filename)
        self.tree_set_project(idx=idx)

    def tree_set_project_from_dialog(self, info: list):
        dirname, settings_ini = info
        self.tree_set_project_from_file_path(dirname)

    def project_selected_file_path(self):
        try:
            return self.tree_view_project.model().filePath(self.tree_view_project.selectedIndexes()[0])
        except IndexError:
            pass

    def project_selected_file_paths(self):
        return self.tree_view_project.selected_paths()

    def set_projects_file_tree(self, rootdir=None):
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
        if rootdir is None or hasattr(rootdir, 'set_safe'):
            rootdir = self.dialog_settings_main.rootDirectoryLineEdit.text()
            rootdir = os.path.realpath(rootdir)

        if not os.path.exists(rootdir):
            os.mkdir(rootdir)

        model = self.tree_view.model()

        if model is None:
            model = FileTreeModel(root_dir=rootdir)
            self.tree_view.setModel(model)

        if model.rootPath() is not rootdir:
            self.tree_view.setRootIndex(model.index(rootdir))
















