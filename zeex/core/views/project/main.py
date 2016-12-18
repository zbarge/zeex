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
from icons import Icons
from functools import partial
from core.compat import QtGui, QtCore
from core.ui.project.main_ui import Ui_ProjectWindow
from qtpandas.views.MultiFileDialogs import CSVImportDialog
from qtpandas.models.DataFrameModel import DataFrameModel
from core.models.filetree import FileTreeModel
from core.ctrls.dataframe import DataFrameModelManager
from core.views.actions.export import DataFrameModelExportDialog
from core.views.actions.merge_purge import MergePurgeDialog
from core.views.file import FileTableWindow
from core.views.settings import SettingsDialog
from core.utility.widgets import get_ok_msg_box, create_standard_item_model
from core.utility.collection import SettingsINI



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
        self.icons = Icons()
        self.dialog_settings = SettingsDialog(settings=settings_ini)
        self.dialog_merge_purge = MergePurgeDialog(self.df_manager)
        self.dialog_export = DataFrameModelExportDialog(self.df_manager, parent=self)
        self.dialog_import = CSVImportDialog(self)
        self.connect_window_title()
        self.connect_actions()
        self.connect_filetree()
        self.connect_icons()
        self.connect_settings_dialog()
        self.current_model = None

        # Temp cache
        self.df_windows = {}

    @property
    def project_directory(self):
        """
        The project's root directory stores everything for the project.

        :return: (str)
            ProjectMainWindow.ProjectsTreeView.QFileSystemModel.rootPath
        """
        return self.ProjectsTreeView.model().rootPath()

    @property
    def log_directory(self):
        """
        The project's log directory stores output logs.
        :return: (str)
            ProjectMainWindow.project_directory/log
        """
        return os.path.join(self.project_directory, 'log')

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
        self.actionPreferences.triggered.connect(self.open_settings_dialog)
        self.actionNew.triggered.connect(self.open_import_dialog)
        self.actionOpen.triggered.connect(self.open_tableview_window)
        self.actionSave.triggered.connect(self.open_export_dialog)
        self.actionRemove.triggered.connect(self.remove_tree_selected_path)
        self.actionMerge_Purge.triggered.connect(self.open_merge_purge_dialog)

    def connect_icons(self):
        """
        Sets all the menu/window icons.
        :return: None
        """
        self.setWindowIcon(self.icons['folder'])
        self.actionNew.setIcon(self.icons['add'])
        self.actionOpen.setIcon(self.icons['spreadsheet'])
        self.actionPreferences.setIcon(self.icons['settings'])
        self.actionRemove.setIcon(self.icons['delete'])
        self.actionSave.setIcon(self.icons['save'])
        self.dialog_settings.setWindowIcon(self.icons['settings'])
        self.actionMerge_Purge.setIcon(self.icons['merge'])
        self.actionRename.setIcon(self.icons['rename'])
        self.dialog_merge_purge.setWindowIcon(self.icons['merge'])

    def connect_filetree(self):
        """
        Uses the ProjectMainWindow.dialog_settings.rootDirectoryLineEdit
        to get the root directory name of the project. It then
        connects the filetree using a QFileSystemModel.
        :return: None
        """
        rootdir = self.dialog_settings.rootDirectoryLineEdit.text()
        model = FileTreeModel(root_dir=rootdir)
        self.ProjectsTreeView.setModel(model)
        self.ProjectsTreeView.setRootIndex(model.index(rootdir))
        self.ProjectsTreeView.setColumnWidth(0, 400)

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
        #self.dialog_settings.rootDirectoryLabel.hide()
        #self.dialog_settings.rootDirectoryLineEdit.hide()
        self.dialog_settings.btnLogDirectory.hide()
        self.dialog_settings.btnRootDirectory.hide()
        self.dialog_settings.themeComboBox.hide()
        self.dialog_settings.themeLabel.hide()

        # Override the log/root directory options
        self.dialog_settings.logDirectoryLineEdit.setText(self.log_directory)
        self.dialog_settings.logDirectoryLineEdit.setReadOnly(True)
        self.dialog_settings.rootDirectoryLineEdit.setText(self.project_directory)
        self.dialog_settings.rootDirectoryLineEdit.setReadOnly(True)

    def open_export_dialog(self):
        """
        Opens a ProjectDataFrameExportDialog object
        and supplies the current df_models making them
        available in the dropdown for the user to export
        to a file.
        :return: None
        """
        dialog = self.dialog_export
        dialog.signalExported.connect(self._flush_export)
        dialog.setWindowIcon(self.icons['export_generic'])
        dialog.show()

    def open_import_dialog(self):
        """
        Opens a CSVImportDialog object
        allowing the user to select a model to
        import (kind of pointless? - use open_tableview_window).
        :return: None
        """
        dialog = self.dialog_import
        dialog.load.connect(self.import_file)
        dialog.setWindowIcon(self.icons['add'])
        dialog.show()

    def open_tableview_window(self, model: DataFrameModel = None):
        """
        Opens a FileTableWindow for the filename selected in the
        ProjectMainWindow.ProjectsTreeView.

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

        name = os.path.basename(model.filePath)

        try:
            return self.df_windows[name].show()
        except KeyError:
            self.df_windows[name] = FileTableWindow(model, self.df_manager)
            self.add_recent_file_menu_entry(name, model)
            return self.df_windows[name].show()

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
        in the ProjectMainWindow.ProjectsTreeView.
        :return: qtpandas.DataFrameModel
        """
        # Check if file is selected in tree view
        selected = self.ProjectsTreeView.selectedIndexes()
        if selected:
            idx = selected[0]
            file_path = self.ProjectsTreeView.model().filePath(idx)
            return self.df_manager.read_file(file_path)
        return None

    def get_tree_selected_path(self):
        selected = self.ProjectsTreeView.selectedIndexes()
        if selected:
            idx = selected[0]
            return self.ProjectsTreeView.model().filePath(idx)
        return None

    def remove_tree_selected_path(self):
        #TODO: need to emit a signal here.
        filename = self.get_tree_selected_path()
        if filename is not None:
            os.remove(filename)
        else:
            #box = get_ok_msg_box(self, "No file selected.")
            #box.show()
            pass

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
    def import_file(self, filepath):
        name = os.path.basename(filepath)

        model = self.df_manager.get_model(filepath)
        self.add_recent_file_menu_entry(name, model)
        dirname = self.SettingsDialog.rootDirectoryLineEdit.text()
        if os.path.dirname(filepath) != dirname:
            newpath = os.path.join(dirname, name)
            model._filePath = newpath
            self.maybe_save_copy(model.dataFrame(),
                                 newpath,
                                 index=False
                                 )

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

    def open_settings_dialog(self):
        self.dialog_settings.show()

    def _flush_export(self, orig_path, new_path):
        if orig_path != new_path:
            self.add_recent_file_menu_entry(new_path, self.df_manager.get_model(new_path))