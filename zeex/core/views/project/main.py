import os
from functools import partial
from icons import Icons
from core.compat import QtGui, QtCore
from qtpandas.views.CSVDialogs import _encodings, DelimiterSelectionWidget
from qtpandas.views.MultiFileDialogs import DataFrameExportDialog, CSVImportDialog, DataFrameModel
from qtpandas.models.DataFrameModel import DataFrameModel
from core.models.filetree import FileTreeModel
from core.ui.project.main_ui import Ui_ProjectWindow
from core.utility.widgets import display_ok_msg
from core.views.file import FileTableWindow
from core.views.settings import SettingsDialog


class ProjectMainWindow(QtGui.QMainWindow, Ui_ProjectWindow):
    signalModelChanged = QtCore.Signal(str)
    signalModelOpened = QtCore.Signal(DataFrameModel)
    signalModelDestroyed = QtCore.Signal(DataFrameModel)

    def __init__(self, settings_ini: str):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.icons = Icons()
        self.SettingsDialog = SettingsDialog(settings=settings_ini)
        self.connect_window_title()
        self.connect_actions()
        self.connect_filetree()
        self.connect_icons()
        self.connect_settings_dialog()
        self.current_model = None

        # Temp caches
        self.df_models = {}
        self.df_windows = {}

    @property
    def project_directory(self):
        return self.ProjectsTreeView.model().rootPath()

    @property
    def log_directory(self):
        return os.path.join(self.project_directory, 'log')

    def connect_window_title(self):
        root_dir = self.SettingsDialog.rootDirectoryLineEdit.text()
        base_name = os.path.basename(root_dir)
        self.SettingsDialog.setWindowTitle("{} - Settings".format(base_name))
        self.setWindowTitle("Project: {} - {}".format(base_name, root_dir.replace(base_name, "")))

    def connect_actions(self):
        self.actionPreferences.triggered.connect(self.open_settings_dialog)
        self.actionNew.triggered.connect(self.open_import_dialog)
        self.actionOpen.triggered.connect(self.open_tableview_window)
        self.actionSave.triggered.connect(self.open_export_dialog)
        self.actionRemove.triggered.connect(self.remove_tree_selected_model)

    def connect_icons(self):
        self.setWindowIcon(self.icons['folder'])
        self.actionNew.setIcon(self.icons['add'])
        self.actionOpen.setIcon(self.icons['spreadsheet'])
        self.actionPreferences.setIcon(self.icons['settings'])
        self.actionRemove.setIcon(self.icons['delete'])
        self.actionSave.setIcon(self.icons['save'])
        self.SettingsDialog.setWindowIcon(self.icons['settings'])


    def connect_filetree(self):
        rootdir = self.SettingsDialog.rootDirectoryLineEdit.text()
        model = FileTreeModel(root_dir=rootdir)
        self.ProjectsTreeView.setModel(model)
        self.ProjectsTreeView.setRootIndex(model.index(rootdir))
        self.ProjectsTreeView.setColumnWidth(0, 400)

    def connect_settings_dialog(self):
        #Adjust the box to remove irrelevant items.
        self.SettingsDialog.cloudProviderComboBox.hide()
        self.SettingsDialog.cloudProviderLabel.hide()
        #self.SettingsDialog.rootDirectoryLabel.hide()
        #self.SettingsDialog.rootDirectoryLineEdit.hide()
        self.SettingsDialog.btnLogDirectory.hide()
        self.SettingsDialog.btnRootDirectory.hide()
        self.SettingsDialog.themeComboBox.hide()
        self.SettingsDialog.themeLabel.hide()

        # Override the log/root directory options
        self.SettingsDialog.logDirectoryLineEdit.setText(self.log_directory)
        self.SettingsDialog.rootDirectoryLineEdit.setText(self.project_directory)

        self.SettingsDialog.logDirectoryLineEdit.setReadOnly(True)
        self.SettingsDialog.rootDirectoryLineEdit.setReadOnly(True)

    def open_export_dialog(self):
        dialog = ProjectDataFrameExportDialog(parent=self,
                                              models=self.df_models)

        dialog.exported.connect(self._flush_export)
        dialog.setWindowIcon(self.icons['export_generic'])
        dialog.exec_()

    def open_import_dialog(self):
        dialog = CSVImportDialog(self)
        dialog.load.connect(self.import_file)
        dialog.setWindowIcon(self.icons['add'])
        dialog.exec_()

    def open_tableview_window(self, model: DataFrameModel = None):
        if model is None:
            # Maybe it's selected on the tree?
            model = self.get_tree_selected_model()
            if model is None:
                # No, not sure why this was called..
                return display_ok_msg(self, "No model available to open.")

        name = os.path.basename(model.filePath)

        try:
            return self.df_windows[name].show()
        except KeyError:
            self.df_windows[name] = FileTableWindow(model)
            self.add_recent_file_menu_entry(name, model)
            return self.df_windows[name].show()

    def get_tree_selected_model(self) -> (DataFrameModel, None):
        # Check if file is selected in tree view
        selected = self.ProjectsTreeView.selectedIndexes()
        if selected:
            idx = selected[0]
            file_path = self.ProjectsTreeView.model().filePath(idx)
            filename = os.path.basename(file_path)
            # Try to return a cached model
            try:
                return self.df_models[filename]
            except KeyError:
                # Ensure its a path we even want to open
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.txt', '.xlsx', '.csv']:
                    # Good to open, lets make/cache the model
                    model = DataFrameModel()
                    model.setDataFrameFromFile(file_path)
                    self.df_models[filename] = model
                    return self.df_models[filename]
        return None

    def remove_tree_selected_model(self):
        #TODO: need to emit a signal here.
        model = self.get_tree_selected_model()
        if model is not None:
            os.remove(model.filePath)
        else:
            display_ok_msg(self, "Unable to remove file.")

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
        self.SettingsDialog.exec_()

    def _flush_export(self, filepath):
        name = os.path.basename(filepath)
        self.df_models.pop(name, None)
        self.menuRecent_Files.removeAction(os.path.basename(filepath))


class ProjectDataFrameExportDialog(DataFrameExportDialog):
    def __init__(self, *args, **kwargs):
        """

        :param args:

        :param kwargs:
            models = {filename: df_model}
            parent = parent widget object
        """
        self._models = kwargs.pop('models', {})
        DataFrameExportDialog.__init__(self, *args, **kwargs)

    def _saveModel(self):
        sourcename = self._sourceNameComboBox.currentText()
        self._model = self._models[sourcename]
        super(ProjectDataFrameExportDialog, self)._saveModel()

    def _initUI(self):
        """Initiates the user interface with a grid layout and several widgets.
        """
        self.setModal(self._modal)
        self.setWindowTitle(self._windowTitle)

        layout = QtGui.QGridLayout()
        self._sourceNameLabel = QtGui.QLabel(u'Output Source', self)
        self._sourceNameComboBox = QtGui.QComboBox(self)
        self._sourceNameComboBox.addItems(list(self._models.keys()))
        self._filenameLabel = QtGui.QLabel(u'Output File', self)
        self._filenameLineEdit = QtGui.QLineEdit(self)
        self._chooseFileButtonIcon = QtGui.QIcon(QtGui.QPixmap(':/icons/document-save-as.png'))
        self._chooseFileAction = QtGui.QAction(self)
        self._chooseFileAction.setIcon(self._chooseFileButtonIcon)
        self._chooseFileAction.triggered.connect(self._createFile)
        self._chooseFileButton = QtGui.QToolButton(self)
        self._chooseFileButton.setDefaultAction(self._chooseFileAction)

        layout.addWidget(self._sourceNameLabel, 0, 0)
        layout.addWidget(self._sourceNameComboBox, 0, 1, 1, 2)
        layout.addWidget(self._filenameLabel, 1, 0)
        layout.addWidget(self._filenameLineEdit, 1, 1, 1, 2)
        layout.addWidget(self._chooseFileButton, 1, 3)

        self._encodingLabel = QtGui.QLabel(u'File Encoding', self)

        encoding_names = list(map(lambda x: x.upper(), sorted(list(set(_encodings.values())))))
        self._encodingComboBox = QtGui.QComboBox(self)
        self._encodingComboBox.addItems(encoding_names)
        self._idx = encoding_names.index('UTF_8')
        self._encodingComboBox.setCurrentIndex(self._idx)
        #self._encodingComboBox.activated.connect(self._updateEncoding)

        layout.addWidget(self._encodingLabel, 2, 0)
        layout.addWidget(self._encodingComboBox, 2, 1, 1, 1)

        self._hasHeaderLabel = QtGui.QLabel(u'Header Available?', self)
        self._headerCheckBox = QtGui.QCheckBox(self)
        #self._headerCheckBox.toggled.connect(self._updateHeader)
        self._headerCheckBox.setChecked(True)

        layout.addWidget(self._hasHeaderLabel, 3, 0)
        layout.addWidget(self._headerCheckBox, 3, 1)

        self._delimiterLabel = QtGui.QLabel(u'Column Delimiter', self)
        self._delimiterBox = DelimiterSelectionWidget(self)

        layout.addWidget(self._delimiterLabel, 4, 0)
        layout.addWidget(self._delimiterBox, 4, 1, 1, 3)

        self._exportButton = QtGui.QPushButton(u'Export Data', self)
        self._cancelButton = QtGui.QPushButton(u'Cancel', self)

        self._buttonBox = QtGui.QDialogButtonBox(self)
        self._buttonBox.addButton(self._exportButton, QtGui.QDialogButtonBox.AcceptRole)
        self._buttonBox.addButton(self._cancelButton, QtGui.QDialogButtonBox.RejectRole)

        self._buttonBox.accepted.connect(self.accepted)
        self._buttonBox.rejected.connect(self.rejected)

        layout.addWidget(self._buttonBox, 6, 2, 1, 2)
        self._exportButton.setDefault(False)
        self._filenameLineEdit.setFocus()

        self._statusBar = QtGui.QStatusBar(self)
        self._statusBar.setSizeGripEnabled(False)
        layout.addWidget(self._statusBar, 5, 0, 1, 4)
        self.setLayout(layout)
