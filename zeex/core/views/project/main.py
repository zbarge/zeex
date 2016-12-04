
import os
from PySide import QtGui
from core.views.project.main_ui import Ui_ProjectWindow
from core.utility.collection import SettingsINI
from core.models.filetree import FileTreeModel
from core.views.settings import SettingsDialog
class ProjectMainWindow(QtGui.QMainWindow, Ui_ProjectWindow):
    def __init__(self, dirname: str, settings_ini: str):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.SettingsDialog = SettingsDialog(filename=settings_ini)
        self.setWindowTitle(self.SettingsDialog.rootDirectoryLineEdit.text())
        self.connect_actions()
        self.connect_filetree()

    def connect_actions(self):
        self.actionPreferences.triggered.connect(self.open_settings_dialog)

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



    def open_settings_dialog(self):
        self.SettingsDialog.exec_()

