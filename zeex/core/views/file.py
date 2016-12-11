import os
from icons import Icons
from core.compat import QtGui, QtCore
from qtpandas.models.DataFrameModel import DataFrameModel
from qtpandas.views.DataTableView import DataTableWidget
from core.ui.file_ui import Ui_FileWindow
from core.views.actions.rename import RenameDialog
from core.views.actions.fields_edit import FieldsEditDialog
from core.ctrls.dataframe import DataFrameModelManager


class FileTableWindow(QtGui.QMainWindow, Ui_FileWindow):
    def __init__(self, model: DataFrameModel, df_manager: DataFrameModelManager, **kwargs):
        QtGui.QMainWindow.__init__(self, parent=kwargs.pop('parent', None))
        self.df_manager = df_manager
        self._widget = DataTableWidget()
        self._widget.setModel(model)

        kwargs['parent'] = self
        self.icons = Icons()
        self.setupUi(self)
        self.dialog_rename = None
        self.dialog_fields_edit = None
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
        self.actionEditFields.triggered.connect(self.open_fields_edit_dialog)

    def connect_icons(self):
        self.setWindowTitle("{}".format(self.currentModel.filePath))
        self.setWindowIcon(self.icons['spreadsheet'])
        self.actionExecuteScript.setIcon(self.icons['edit'])
        self.actionDelete.setIcon(self.icons['delete'])
        self.actionMergePurge.setVisible(False)
        self.actionSave.setIcon(self.icons['save'])
        self.actionSuppress.setIcon(self.icons['suppress'])
        self.actionEditFields.setIcon(self.icons['add_column'])

    def open_rename_dialog(self):
        if self.dialog_rename is None:
            self.dialog_rename = RenameDialog(parent=self, model=self.currentModel)
        self.dialog_rename.show()

    def open_fields_edit_dialog(self):
        if self.dialog_fields_edit is None:
            self.dialog_fields_edit = FieldsEditDialog(self.currentModel, parent=self)
        self.dialog_fields_edit.show()






