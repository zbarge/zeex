import os
from icons import Icons
from core.compat import QtGui, QtCore
from qtpandas.models.DataFrameModel import DataFrameModel
from qtpandas.views.DataTableView import DataTableWidget
from core.ui.file_ui import Ui_FileWindow
from core.views.actions.merge_purge import MergePurgeDialog
from core.views.actions.rename import RenameDialog


class FileTableWidget(DataTableWidget):
    signalDataMerged = QtCore.Signal(DataFrameModel)

    def read_file(*args, **kwargs):
        model = DataFrameModel()
        model.setDataFrameFromFile(args[0], **kwargs)
        return FileTableWidget(model)

    def __init__(self, model, **kwargs):
        DataTableWidget.__init__(self, **kwargs)
        self.setModel(model)


class FileTableWindow(QtGui.QMainWindow, Ui_FileWindow):
    def __init__(self, model, **kwargs):
        QtGui.QMainWindow.__init__(self, parent=kwargs.pop('parent', None))
        kwargs['parent'] = self
        self.icons = Icons()
        self._widget = FileTableWidget(model, **kwargs)
        self.setupUi(self)
        self.dialogRename = None
        self.dialogMergePurge = None
        self.connect_actions()
        self.connect_icons()

    @property
    def widget(self):
        # Overrides the Ui_FileWindow.widget
        return self._widget

    @widget.setter
    def widget(self, x):
        # Prevent the Ui_FileWindow from overriding our widget.
        pass

    @property
    def currentModel(self):
        return self.widget.model()

    @property
    def currentDataFrame(self):
        return self.currentModel._dataFrame

    def connect_actions(self):
        self.actionMergePurge.triggered.connect(self.open_merge_purge_dialog)
        self.actionRename.triggered.connect(self.open_rename_dialog)

    def connect_icons(self):
        self.setWindowTitle("{}".format(self.currentModel.filePath))
        self.setWindowIcon(self.icons['spreadsheet'])
        self.actionExecuteScript.setIcon(self.icons['edit'])
        self.actionDelete.setIcon(self.icons['delete'])
        self.actionMergePurge.setIcon(self.icons['merge'])
        self.actionRename.setIcon(self.icons['lightning'])
        self.actionSave.setIcon(self.icons['save'])
        self.actionSuppress.setIcon(self.icons['suppress'])

    def open_rename_dialog(self):
        if self.dialogRename is None:
            self.dialogRename = RenameDialog(parent=self, model=self.currentModel)
        self.dialogRename.show()

    def open_merge_purge_dialog(self):
        if self.dialogMergePurge is None:
            model = self.widget.model()
            df = model._dataFrame
            file_base, ext = os.path.splitext(model.filePath)
            dialog = MergePurgeDialog()

            settings = dict()
            settings['sort_model'] = dialog.create_sort_model(df.columns)
            settings['dedupe_model'] = dialog.create_dedupe_model(df.columns)
            settings['source_path'] = model.filePath
            settings['dest_path'] =  file_base + "_merged" + ext
            dialog.configure(settings)

            self.dialogMergePurge = dialog
        self.dialogMergePurge.show()



