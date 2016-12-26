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
from core.views.actions.analyze import FileAnalyzerDialog
from core.views.actions.normalize import ColumnNormalizerDialog
from core.views.actions.export import DataFrameModelExportDialog
from core.utility.widgets import create_standard_item_model


class FileTableWindow(QtGui.QMainWindow, Ui_FileWindow):
    """
    A spreadsheet-like window that displays rows and columns
    of the source DataFrame. Menu actions in this window allow the user to make
    updates to the DataFrame and see the changes update in the view.
    """
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
        self.dialog_export = DataFrameModelExportDialog(df_manager, filename=model.filePath,
                                                        allow_multi_source=False, parent=self)
        self.dialog_split = SplitFileDialog(model, parent=self)
        self.dialog_analyze = FileAnalyzerDialog(model, parent=self)
        self.dialog_normalize = ColumnNormalizerDialog(model, parent=self)
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
    def df_model(self):
        return self.widget.model()

    @property
    def df(self):
        return self.df_model.dataFrame()

    def connect_actions(self):
        self.actionEditFields.triggered.connect(self.open_fields_edit_dialog)
        self.actionSplit.triggered.connect(self.dialog_split.show)
        self.actionAnalyze.triggered.connect(self.dialog_analyze.show)
        self.actionNormalize.triggered.connect(self.dialog_normalize.show)
        self.actionSave.triggered.connect(self.save)
        self.actionSaveAs.triggered.connect(self.dialog_export.show)
        self.dialog_export.comboBoxSource.setModel(create_standard_item_model([self.df_model.filePath]))
        self.dialog_export.btnBrowseSource.setVisible(False)
        # TODO: Make these actions do something then activate.
        self.actionExecuteScript.setVisible(False)
        self.actionSuppress.setVisible(False)
        self.actionDelete.setVisible(False)

    def connect_icons(self):
        self.setWindowTitle("{}".format(self.df_model.filePath))
        self.setWindowIcon(self.icons['spreadsheet'])
        self.actionExecuteScript.setIcon(self.icons['edit'])
        self.actionDelete.setIcon(self.icons['delete'])
        self.actionMergePurge.setVisible(False)
        self.actionSave.setIcon(self.icons['save'])
        self.actionSaveAs.setIcon(self.icons['saveas'])
        self.actionSplit.setIcon(self.icons['split'])
        self.actionSuppress.setIcon(self.icons['suppress'])
        self.actionEditFields.setIcon(self.icons['add_column'])
        self.actionAnalyze.setIcon(self.icons['count'])
        self.actionNormalize.setIcon(self.icons['normalize'])
        self.dialog_normalize.setWindowIcon(self.icons['normalize'])
        self.dialog_analyze.setWindowIcon(self.icons['count'])
        self.dialog_export.setWindowIcon(self.icons['export_generic'])

    def open_rename_dialog(self):
        if self.dialog_rename is None:
            self.dialog_rename = RenameDialog(parent=self, model=self.df_model)
        self.dialog_rename.show()

    def open_fields_edit_dialog(self):
        if self.dialog_fields_edit is None:
            self.dialog_fields_edit = FieldsEditDialog(self.df_model, parent=self)
        self.dialog_fields_edit.show()

    def open_analyze_dialog(self):
        self.dialog_analyze.setWindowTitle("Analyze {}".format(os.path.basename(self.df_model.filePath)))
        self.dialog_analyze.show()

    def save(self):
        self.dialog_export.set_destination_path_from_source()
        self.dialog_export.export()


