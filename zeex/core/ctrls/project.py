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
import logging
from zeex.core.compat import QtGui, QtCore
from zeex.core.ctrls.dataframe import DataFrameModelManager
from zeex.core.models.filetree import FileTreeModel
from zeex.core.views.actions.export import DataFrameModelExportDialog
from zeex.core.views.actions.merge_purge import MergePurgeDialog
from zeex.core.views.basic.directory import DropBoxViewDialog
from zeex.core.views.basic.line_edit import DirectoryPathCreateDialog
from zeex.core.views.basic.line_edit import FilePathRenameDialog
from zeex.core.views.actions.import_file import DataFrameModelImportDialog
from zeex.core.views.project.settings import ProjectSettingsDialog


class ProjectController(object):
    def __init__(self, directory, settings_ini, default_dirs=True, tree_view=None, main_control=None,**kwargs):
        self.parent = kwargs.get('parent', None)
        self.main_control = main_control
        if default_dirs is True:
            settings_ini.set_safe('GENERAL', 'ROOT_DIRECTORY', directory)
            settings_ini.set_safe('GENERAL', 'LOG_DIRECTORY', os.path.join(directory, 'logs'))
        self._directory = directory
        self._df_manager = DataFrameModelManager()
        self._file_tree_model = FileTreeModel(root_dir=directory, parent=self.parent)
        self._dialog_export_df_model = DataFrameModelExportDialog(self.df_manager)
        self._dialog_merge_purge = MergePurgeDialog(self.df_manager, parent=self.parent)
        self._dialog_add_directory = DirectoryPathCreateDialog(base_dirname=directory, parent=self.parent)
        self._dialog_import_df_model = DataFrameModelImportDialog(self.df_manager, parent=self.parent)
        self._dialog_import_df_model.signalImported.connect(self._handle_imported_df_model)
        self._dialog_settings = ProjectSettingsDialog(settings_ini)
        self._tree_view = None
        self.tree_view = tree_view

    @property
    def directory(self):
        return self._dialog_settings.rootDirectoryLineEdit.text()

    @property
    def df_manager(self) -> DataFrameModelManager:
        return self._df_manager

    @property
    def file_tree_model(self) -> FileTreeModel:
        return self._file_tree_model

    @property
    def dialog_export_df_model(self) -> DataFrameModelExportDialog:
        return self._dialog_export_df_model

    @property
    def dialog_import_df_model(self) -> DataFrameModelImportDialog:
        d = self._dialog_import_df_model
        fp = d.lineEditFilePath.text()
        if fp == '' and d.dir == '':
            d.dir = self.directory
        return d

    @property
    def dialog_merge_purge(self) -> MergePurgeDialog:
        return self._dialog_merge_purge

    @property
    def dialog_add_directory(self) -> DirectoryPathCreateDialog:
        return self._dialog_add_directory

    @property
    def dialog_settings(self) -> ProjectSettingsDialog:
        return self._dialog_settings

    @property
    def tree_view(self) -> QtGui.QTreeView:
        return self._tree_view

    @tree_view.setter
    def tree_view(self, x):
        self._tree_view = self.configure_tree_view(x)

    def get_dialog_rename_path(self, orig_path=None) -> FilePathRenameDialog:
        if orig_path is None:
            orig_path = self.tree_view.model().filePath(self.tree_view.selectedIndexes()[0])
        return FilePathRenameDialog(orig_path, parent=self.parent)

    def get_dialog_merge_purge(self, filename=None):
        dialog = self.dialog_merge_purge
        if filename is None:
            try:
                filename = self.tree_view.model().filePath(self.tree_view.selectedIndexes()[0])
            except IndexError:
                pass
        if filename is not None and os.path.isfile(filename) and filename != dialog.sourcePathLineEdit.text():
            dialog.set_source_model(self.df_manager.read_file(filename), configure=True)
        return dialog

    def configure_tree_view(self, view):
        if view is not None:
            model = view.model()

            if model is None or model.rootPath() != self.file_tree_model.rootPath():
                model = self.file_tree_model
                view.setModel(model)
                logging.info("Project tree view configured for {}".format(model.rootPath()))

            view.setRootIndex(model.index(self.directory))
            view.setColumnWidth(0, 300)
            view.setSelectionMode(view.ExtendedSelection)

            model.setReadOnly(False)
            model.setNameFilterDisables(False)
        return view

    def _handle_imported_df_model(self, file_path):
        dfm = self.df_manager.get_model(file_path)
        dirname = os.path.dirname(dfm.filePath)
        if dirname.replace("\\","/") != self.directory.replace("\\", "/"):
            to_path = os.path.join(self.directory, os.path.basename(dfm.filePath))
            self.df_manager.save_file(file_path, save_as=to_path,
                                      keep_orig=False, index=False)
            file_path = to_path
        if hasattr(self.main_control, 'get_fileview_window'):
            self.main_control.get_fileview_window(self.tree_view.model().index(file_path)).show()
        else:
            self.df_manager.get_fileview_window(file_path).show()








