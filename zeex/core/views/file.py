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
from core.compat import QtGui, QtCore
from qtpandas.models.DataFrameModel import DataFrameModel
from qtpandas.views.DataTableView import DataTableWidget
from core.ui.file_ui import Ui_FileWindow
from core.views.actions.rename import RenameDialog
from core.views.actions.fields_edit import FieldsEditDialog
from core.ctrls.dataframe import DataFrameModelManager
from core.views.actions.split import SplitFileDialog

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
        self.dialog_split = SplitFileDialog(model, parent=self)
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
        self.actionSplit.triggered.connect(self.dialog_split.show)

    def connect_icons(self):
        self.setWindowTitle("{}".format(self.currentModel.filePath))
        self.setWindowIcon(self.icons['spreadsheet'])
        self.actionExecuteScript.setIcon(self.icons['edit'])
        self.actionDelete.setIcon(self.icons['delete'])
        self.actionMergePurge.setVisible(False)
        self.actionSave.setIcon(self.icons['save'])
        self.actionSplit.setIcon(self.icons['split'])
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







