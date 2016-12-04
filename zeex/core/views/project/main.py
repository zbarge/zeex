
import os
from PySide import QtGui, QtCore
from core.views.project.main_ui import Ui_ProjectWindow
from core.utility.collection import SettingsINI
from core.models.filetree import FileTreeModel
from core.views.settings import SettingsDialog
from pandasqt.views.CSVDialogs import CSVImportDialog


class ProjectMainWindow(QtGui.QMainWindow, Ui_ProjectWindow):
    def __init__(self, dirname: str, settings_ini: str):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.SettingsDialog = SettingsDialog(filename=settings_ini)
        self.setWindowTitle(self.SettingsDialog.rootDirectoryLineEdit.text())
        self.connect_actions()
        self.connect_filetree()
        self.df_models = {}

    def connect_actions(self):
        self.actionPreferences.triggered.connect(self.open_settings_dialog)
        self.actionNew.triggered.connect(self.open_csv)

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

    def open_csv(self):
        Dialog = CSVImportDialog(self)
        Dialog.load.connect(self.import_file)
        Dialog.exec_()

    @QtCore.Slot('DataFrameModel', str)
    def import_file(self, model, filepath):
        name = os.path.basename(filepath)

        self.df_models[name] = model
        dirname = self.SettingsDialog.rootDirectoryLineEdit.text()
        if os.path.dirname(filepath) != dirname:
            self.maybe_save_copy(model.dataFrame(),
                                 os.path.join(dirname, name),
                                 index=False
                                 )

    def maybe_save_copy(self, df, filepath, max_size=20000, **kwargs):
        if df.index.size <= max_size and not df.empty:
            kwargs['index'] = kwargs.get('index', False)
            df.to_csv(filepath, **kwargs)

    def open_settings_dialog(self):
        self.SettingsDialog.exec_()

