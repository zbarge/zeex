# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:09:50 2016
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
from zeex.core.ctrls.dataframe import DataFrameModel, DataFrameModelManager
from zeex.core.ui.sql.table_import_ui import Ui_AlchemyTableImportDialog
from zeex.core.ctrls.sql import AlchemyConnection, AlchemyConnectionManager
from zeex.core.compat import QtGui
import zeex.core.utility.widgets as widgets


class AlchemyTableImportDialog(QtGui.QDialog, Ui_AlchemyTableImportDialog):
    def __init__(self, con:AlchemyConnection, con_manager: AlchemyConnectionManager,
                 df_manager=None, **kwargs):
        QtGui.QMainWindow.__init__(self, **kwargs)
        self._con = con
        self._con_manager = con_manager
        self._df_manager = df_manager
        self._source_model = None
        self.configure()

    @property
    def con(self) -> AlchemyConnection:
        return self._con

    @property
    def con_manager(self) -> AlchemyConnectionManager:
        return self._manager

    @property
    def df_manager(self) -> DataFrameModelManager:
        if self._df_manager is None:
            self._df_manager = DataFrameModelManager()
        return self._df_manager

    @property
    def source_model(self) -> DataFrameModel:
        if self._source_model is None:
            file_path = self.lineEditSourcePath.text()
            assert os.path.isfile(file_path), "file_path must be a valid file, not {}".format(
                                               file_path)
            self._source_model = self.df_manager.read_file(file_path)

        return self._source_model

    def configure(self):
        self.setupUi(self)
        widgets.configure_combo_box(self.comboBoxConnectionName, self.con_manager.connections, self.con.name)
        self.buttonBox.accepted.connect(self.import_table)
        self.lineEditSourcePath.textChanged.connect(self.set_source_model)
        self.btnEditSourcePath.clicked.connect(self.edit_source_model)
        self.btnBrowseSourcePath.clicked.connect(self.set_source_model)

    def set_source_model(self, model:DataFrameModel = None):
        """
        Configures a source DataFrameModel to be imported.
        connects dialog signal(s) and combo box(es)
        :param model: (DataFrameModel, default None)
        :return: None
        """
        if model is None:
            model = self.source_model
        else:
            if self._source_model is not None:
                widgets.signal_adjust(self._source_model.dataChanged,
                                      oldhandler=self.set_source_model)
            self._source_model = model
            if model.filePath is not None and model.filePath not in self.df_manager.file_paths:
                self.df_manager.set_model(model, model.filePath)
        widgets.signal_adjust(model.dataChanged, self.set_source_model, self.set_source_model)

        if model.filePath is not None:
            self.lineEditSourcePath.setText(model.filePath)

        df = model.dataFrame()
        options = [df.index.name] + df.columns.tolist()
        widgets.configure_combo_box(self.comboBoxPrimaryKey, options,
                                    self.comboBoxPrimaryKey.currentText())

    def import_table(self):
        table_name = self.lineEditTableName.text()
        source_model = self.source_model
        df = source_model.dataFrame().copy()
        key_name = self.comboBoxPrimaryKey.currentText()
        key_priority = self.comboBoxPrimaryKeyPriority.currentText()
        if_exists = self.comboBoxExistingTableOption.currentText()
        try:
            Table = self.con.meta.tables[table_name]
        except (KeyError, AttributeError):
            Table = None

    def edit_source_model(self):
        source_path = self.lineEditSourcePath.text()
        window = self.df_manager.get_fileview_window(source_path)
        window.show()



