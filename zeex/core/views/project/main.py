
import os
from PySide import QtGui, QtCore
from core.views.project.main_ui import Ui_ProjectWindow
from functools import partial
from core.utility.collection import SettingsINI
from core.models.filetree import FileTreeModel
from core.views.settings import SettingsDialog
from pandasqt.views.MultiFileDialogs import DataFrameExportDialog, CSVImportDialog, DataFrameModel
from core.views.file import FileTableWidget
from core.utility.widgets import display_ok_msg

class ProjectMainWindow(QtGui.QMainWindow, Ui_ProjectWindow):
    signalModelChanged = QtCore.Signal(str)

    def __init__(self, dirname: str, settings_ini: str):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.SettingsDialog = SettingsDialog(filename=settings_ini)
        self.setWindowTitle(self.SettingsDialog.rootDirectoryLineEdit.text())
        self.connect_actions()
        self.connect_filetree()
        self.current_model = None
        self.df_models = {}
        self.df_windows = {}

    def connect_actions(self):
        self.actionPreferences.triggered.connect(self.open_settings_dialog)
        self.actionNew.triggered.connect(self.open_import_dialog)
        self.actionOpen.triggered.connect(self.open_tableview_window)
        self.actionSave.triggered.connect(self.open_export_dialog)

    def connect_filetree(self):
        rootdir = self.SettingsDialog.rootDirectoryLineEdit.text()
        model = FileTreeModel(root_dir=rootdir)
        self.ProjectsTreeView.setModel(model)
        self.ProjectsTreeView.setRootIndex(model.index(rootdir))

    def connect_settings_dialog(self):
        self.SettingsDialog.cloudProviderComboBox.setVisible(False)
        self.SettingsDialog.cloudProviderLabel.setVisible(False)
        self.SettingsDialog.rootDirectoryLabel.setVisible(False)
        self.SettingsDialog.rootDirectoryLineEdit.setVisible(False)

    def open_export_dialog(self):

        Dialog = DataFrameExportDialog(self)
        Dialog.exported.connect(self._flush_export)
        Dialog.exec_()

    def open_import_dialog(self):
        Dialog = CSVImportDialog(self)
        Dialog.load.connect(self.import_file)
        Dialog.exec_()

    def open_tableview_window(self, model: DataFrameModel = None):
        if model is None:
            model = self.get_tree_selected_model()
            if model is None:
                return display_ok_msg(self, "No model available to open.")
        name = os.path.basename(model.filePath)

        try:
            return self.df_windows[name].show()
        except KeyError:
            self.df_windows[name] = FileTableWidget(model)
            return self.df_windows[name].show()

    def get_tree_selected_model(self):
        # Check if file is selected in treeview
        selected = self.ProjectsTreeView.selectedIndexes()
        if selected:
            idx = selected[0]
            filepath = self.ProjectsTreeView.model().filePath(idx)
            filename = os.path.basename(filepath)
            # Try to return a cached model
            try:
                return self.df_models[filename]
            except KeyError:
                # Ensure its a path we even want to open
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ['.txt', '.xlsx', '.csv']:
                    # Good to open, lets build the window and cache both
                    window = FileTableWidget.read_file(filepath)
                    self.df_windows[filename] = window

                    model = window.model()
                    self.df_models[filename] = model
                    self.add_recent_file_menu_entry(filename, model)
                    return self.df_models[filename]
        return None

    def open_tableview_current(self):
        model = self.current_model
        assert isinstance(model, DataFrameModel), "No current DataFrame model."
        return self.open_tableview_window(model)

    @QtCore.Slot('DataFrameModel', str)
    def import_file(self, model, filepath):
        name = os.path.basename(filepath)

        self.df_models[name] = model
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
        self.SettingsDialog.exec_()

    def _flush_export(self, filepath):
        name = os.path.basename(filepath)
        self.df_models.pop(name, None)
        self.menuRecent_Files.removeAction(os.path.basename(filepath))



