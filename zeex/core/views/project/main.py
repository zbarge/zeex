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
from functools import partial
from zeex.core.compat import QtGui, QtCore
from zeex.core.ctrls.dataframe import DataFrameModelManager, DataFrameModel
from zeex.core.models.filetree import FileTreeModel
from zeex.core.ui.project.main_ui import Ui_ProjectWindow
from zeex.core.utility.collection import SettingsINI
import zeex.core.utility.ostools as ostools
from zeex.core.views.settings import SettingsDialog
from zeex.core.views.actions.export import DataFrameModelExportDialog
from zeex.core.views.actions.merge_purge import MergePurgeDialog
from zeex.core.views.basic.directory import DropBoxViewDialog
from zeex.core.views.basic.line_edit import DirectoryPathCreateDialog
from zeex.core.views.basic.line_edit import FilePathRenameDialog
from zeex.core.views.actions.import_file import DataFrameModelImportDialog


class ProjectMainWindow(QtGui.QMainWindow, Ui_ProjectWindow):
    """
    The ProjectMainWindow displays a project that the user wants to work on.
    The project lives in a directory within the ZeexApp.ROOT_DIRECTORY.
    Each project gets a DataFrameModelManager object which controls the
    DataFrameModel of each file opened.
    The main window shows all files in this directory and provides
    very convenient features to work with files containing rows/columns.

    Project's settings are stored in a .ini file
    in the root project directory.
    """
    signalModelChanged = QtCore.Signal(str)
    signalModelOpened = QtCore.Signal(str)
    signalModelDestroyed = QtCore.Signal(str)

    def __init__(self, settings_ini: (str, SettingsINI), parent=None):
        """
        :param settings_ini: (str, SettingsINI)
            can be a settings_ini file path or configured SettingsINI object.
        """
        self.df_manager = DataFrameModelManager()
        QtGui.QMainWindow.__init__(self, parent=parent)
        self.setupUi(self)
        self.dialog_settings = SettingsDialog(settings=settings_ini)
        self.dialog_merge_purge = MergePurgeDialog(self.df_manager)
        self.dialog_export = DataFrameModelExportDialog(self.df_manager, parent=self)
        self.dialog_import = DataFrameModelImportDialog(self.df_manager, parent=self)
        self.dialog_new_folder = DirectoryPathCreateDialog(self.treeView,
                                                           parent=self)
        self.dialog_cloud = None
        self.key_delete = QtGui.QShortcut(self)
        self.key_enter = QtGui.QShortcut(self)
        self.key_zip = QtGui.QShortcut(self)
        self.key_rename = QtGui.QShortcut(self)
        self.connect_window_title()
        self.connect_actions()
        self.connect_treeview()
        self.connect_icons()
        self.connect_settings_dialog()
        self.connect_import_dialog()
        self.connect_export_dialog()
        self.connect_cloud_dialog()
        self.current_model = None

    @property
    def project_directory(self):
        """
        The project's root directory stores everything for the project.

        :return: (str)
            ProjectMainWindow.treeView.QFileSystemModel.rootPath
        """
        return self.treeView.model().rootPath()

    @property
    def log_directory(self):
        """
        The project's log directory stores output logs.
        :return: (str)
            ProjectMainWindow.project_directory/log
        """
        return os.path.join(self.project_directory, 'log')

    @QtCore.Slot(SettingsINI, str)
    def sync_settings(self, config:SettingsINI=None, file_path=None):
        """
        Anytime settings are saved this method gets triggered.
        Sets defaults for various views.
        :param config:
        :param file_path:
        :return:
        """
        self.connect_export_dialog()
        self.connect_import_dialog()

    def connect_window_title(self):
        """
        Sets the ProjectMainWindow.windowTitle to "Project - dirname - dirpath"
        :return: None
        """
        root_dir = self.dialog_settings.rootDirectoryLineEdit.text()
        base_name = os.path.basename(root_dir)
        self.dialog_settings.setWindowTitle("{} - Settings".format(base_name))
        self.setWindowTitle("Project: {} - {}".format(base_name, root_dir.replace(base_name, "")))

    def connect_actions(self):
        """
        Connects all project actions.
        :return: None
        """

        self.actionPreferences.triggered.connect(self.dialog_settings.show)
        self.actionAddFolder.triggered.connect(self.dialog_new_folder.show)
        self.actionNew.triggered.connect(self.dialog_import.show)
        self.actionOpen.triggered.connect(self.open_tableview_window)
        self.actionSave.triggered.connect(self.dialog_export.show)
        self.actionRemove.triggered.connect(self.remove_tree_selected_path)
        self.actionRename.triggered.connect(self.open_rename_path_dialog)
        self.actionMergePurge.triggered.connect(self.open_merge_purge_dialog)
        self.actionUnzip.triggered.connect(self.handle_compression)
        self.actionZip.triggered.connect(self.handle_compression)
        self.key_delete.setKey('del')
        self.key_enter.setKey('return')
        self.key_zip.setKey(QtGui.QKeySequence(self.tr('Ctrl+Z')))
        self.key_rename.setKey(QtGui.QKeySequence(self.tr('Ctrl+R')))
        self.key_delete.activated.connect(self.remove_tree_selected_path)
        self.key_enter.activated.connect(self.open_tableview_window)
        self.key_zip.activated.connect(self.handle_compression)
        self.key_rename.activated.connect(self.open_rename_path_dialog)

    def connect_icons(self):
        """
        Sets all the menu/window icons.
        :return: None
        """
        def i(n):
            return QtGui.QIcon(':/standard_icons/{}'.format(n))
        
        self.setWindowIcon(i('folder.png'))
        self.actionNew.setIcon(i('add.png'))
        self.actionAddFolder.setIcon(i('folder.png'))
        self.actionOpen.setIcon(i('spreadsheet.png'))
        self.actionPreferences.setIcon(i('settings.png'))
        self.actionRemove.setIcon(i('delete.png'))
        self.actionSave.setIcon(i('save.png'))
        self.dialog_settings.setWindowIcon(i('settings.png'))
        self.actionMergePurge.setIcon(i('merge.png'))
        self.actionRename.setIcon(i('rename.png'))
        self.dialog_merge_purge.setWindowIcon(i('merge.png'))
        self.actionZip.setIcon(i('archive.png'))
        self.dialog_new_folder.setWindowIcon(i('folder.png'))
        self.actionUnzip.setIcon(i('unzip.png'))

    def connect_treeview(self):
        """
        Uses the ProjectMainWindow.dialog_settings.rootDirectoryLineEdit
        to get the root directory name of the project. It then
        connects the filetree using a QFileSystemModel.
        :return: None
        """
        rootdir = self.dialog_settings.rootDirectoryLineEdit.text()
        model = FileTreeModel(root_dir=rootdir)
        self.treeView.setModel(model)
        self.treeView.setRootIndex(model.index(rootdir))
        self.treeView.setColumnWidth(0, 400)
        self.treeView.setSelectionMode(self.treeView.ExtendedSelection)

    def connect_settings_dialog(self):
        """
        Re-purposes the ProjectMainWindow.dialog_settings
        dialog to fit the scope of a project rather than
        the application as a whole.
        :return: None
        """
        #Adjust the box to remove irrelevant items.
        self.dialog_settings.cloudProviderComboBox.hide()
        self.dialog_settings.cloudProviderLabel.hide()
        self.dialog_settings.btnLogDirectory.hide()
        self.dialog_settings.btnRootDirectory.hide()
        self.dialog_settings.themeComboBox.hide()
        self.dialog_settings.themeLabel.hide()

        # Override the log/root directory options
        self.dialog_settings.logDirectoryLineEdit.setText(self.log_directory)
        self.dialog_settings.logDirectoryLineEdit.setReadOnly(True)
        self.dialog_settings.rootDirectoryLineEdit.setText(self.project_directory)
        self.dialog_settings.rootDirectoryLineEdit.setReadOnly(True)
        self.dialog_settings.btnSetDefault.setVisible(False)

        self.dialog_settings.signalSettingsSaved.connect(self.sync_settings)
        self.dialog_new_folder.base_dirname = self.dialog_settings.rootDirectoryLineEdit.text()

    def connect_cloud_dialog(self):
        try:
            self.dialog_cloud = DropBoxViewDialog(self.treeView, self)
            self.actionViewCloud.triggered.connect(self.dialog_cloud.show)
            self.actionViewCloud.setIcon(QtGui.QIcon(':/standard_icons/cloud.png'))
        except Exception as e:
            logging.error("Error connecting to cloud: {}".format(e))
            self.actionViewCloud.setVisible(False)

    def connect_export_dialog(self):
        """
        Sets defaults of the DataFrameModelExport Dialog.
        :return: None
        """
        self.dialog_export.signalExported.connect(self._flush_export)
        self.dialog_export.setWindowIcon(QtGui.QIcon(':/standard_icons/export_generic.png'))
        sep = self.dialog_settings.separatorComboBox.currentText()
        enc = self.dialog_settings.encodingComboBox.currentText()
        self.dialog_export.set_encoding(enc)
        self.dialog_export.set_separator(sep)

    def connect_import_dialog(self):
        """
        Sets defaults of the DataFrameModelImport Dialog.
        :return: None
        """
        self.dialog_import.signalImported.connect(self.import_file)

        self.dialog_import.setWindowIcon(QtGui.QIcon(':/standard_icons/add.png'))
        sep = self.dialog_settings.separatorComboBox.currentText()
        enc = self.dialog_settings.encodingComboBox.currentText()
        self.dialog_import.set_encoding(enc)
        self.dialog_import.set_separator(sep)

    def open_tableview_window(self, model: DataFrameModel = None):
        """
        Opens a FileTableWindow for the filename selected in the
        ProjectMainWindow.treeView.

        :param model: The qtpandas.models.DataFrameModel to edit.
        :return: None
        """
        if model is None:
            # Maybe it's selected on the tree?
            model = self.get_tree_selected_model()
            if model is None:
                # No, not sure why this was called..
                #box = get_ok_msg_box(self, "No model available to open.")
                #box.show()
                pass

        self.df_manager.get_fileview_window(model.filePath).show()
        self.add_recent_file_menu_entry(model.filePath, model)

    def open_merge_purge_dialog(self, model: DataFrameModel=None):
        if model is None:
            model = self.get_tree_selected_model()
        current_model = self.dialog_merge_purge.source_model
        if current_model is None or current_model.filePath is not model.filePath:
            self.dialog_merge_purge.set_source_model(model=model, configure=True)
        self.dialog_merge_purge.show()

    def get_tree_selected_model(self, raise_on_error=True) -> (DataFrameModel, None):
        """
        Returns a DataFrameModel based on the filepath selected
        in the ProjectMainWindow.treeView.
        :return: qtpandas.DataFrameModel
        """
        # Check if file is selected in tree view
        selected = self.treeView.selectedIndexes()
        if selected:
            idx = selected[0]
            file_path = self.treeView.model().filePath(idx)
            return self.df_manager.read_file(file_path)
        return None

    def get_tree_selected_path(self):
        selected = self.treeView.selectedIndexes()
        if selected:
            idx = selected[0]
            return self.treeView.model().filePath(idx)
        return None

    def remove_tree_selected_path(self):
        #TODO: need to emit a signal here.
        idxes = self.treeView.selectedIndexes()
        if idxes:
            file_model = self.treeView.model()
            for idx in idxes:
                if not file_model.isDir(idx):
                    file_model.remove(idx)
                else:
                    file_model.rmdir(idx)

    def open_tableview_current(self, model: DataFrameModel=None):
        """
        Opens a tableview window for the current_model or the model kwarg.

        :param model: DataFrameModel

        :return: None
        """
        if model is None:
            model = self.current_model
        else:
            self.set_current_df_model(model)

        assert isinstance(model, DataFrameModel), "No current DataFrame model."
        return self.open_tableview_window(model)

    def set_current_df_model(self, model: DataFrameModel):
        """
        Sets the current dataframe model. for the project.
        :param model: DataFrameModel
        :return: None
        """
        self.df_manager.set_model(model, model._filePath)
        self.current_model = self.df_manager.get_model(model._filePath)

    @QtCore.Slot('DataFrameModel', str)
    def import_file(self, filepath, open=True):
        if isinstance(filepath, DataFrameModel):
            model = filepath
            filepath = model.filePath
            self.df_manager.set_model(model, filepath)

        model = self.df_manager.get_model(filepath)
        name = os.path.basename(model.filePath)
        dirname = self.dialog_settings.rootDirectoryLineEdit.text()
        assert os.path.isdir(dirname), "Root Directory is not a directory: {}".format(dirname)

        if os.path.dirname(filepath) != dirname:
            newpath = os.path.join(dirname, name)
            self.df_manager.save_file(filepath, save_as=newpath, keep_orig=False)
            filepath = newpath

        if open is True:
            model = self.df_manager.get_model(filepath)
            self.open_tableview_window(model)

    def add_recent_file_menu_entry(self, name, model):
        action = QtGui.QAction(name, self.menuRecent_Files)
        action.triggered.connect(partial(self.open_tableview_window, model))
        actions = self.menuRecent_Files.actions()
        if actions:
            self.menuRecent_Files.insertAction(actions[0], action)
        else:
            self.menuRecent_Files.addAction(action)

    def maybe_save_copy(self, df, filepath, max_size=20000, **kwargs):
        """
        Saves a copy of the file to the project folder if
            its smaller than max_size
            its larger than 0 rows

        :param df: DataFrame: to save
        :param filepath: str: the filepath of the DataFrame
        :param max_size: int: max size of DataFrame
        :param kwargs: DataFrame.to_csv(**kwargs)
        :return: None
        """
        if df.index.size <= max_size and not df.empty:
            kwargs['index'] = kwargs.get('index', False)
            df.to_csv(filepath, **kwargs)

    def _flush_export(self, orig_path, new_path):
        if orig_path != new_path:
            self.add_recent_file_menu_entry(new_path, self.df_manager.get_model(new_path))

    def open_rename_path_dialog(self):
        current_path = self.get_tree_selected_path()
        dialog = FilePathRenameDialog(current_path, parent=self)
        dialog.show()

    def handle_compression(self, fpath=None, **kwargs):
        if fpath is None:
            fpath = self.get_tree_selected_path()
        assert fpath is not None, "No selected path!"
        if not fpath.lower().endswith('.zip'):
            return ostools.zipfile_compress(fpath, **kwargs)
        else:
            return ostools.zipfile_unzip(file_path=fpath,
                                 dir=self.dialog_settings.rootDirectoryLineEdit.text())


