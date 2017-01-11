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
import logging
from zeex.core.ctrls.dataframe import DataFrameModel, DataFrameModelManager
from zeex.core.ui.sql.table_import_ui import Ui_AlchemyTableImportDialog
from zeex.core.ctrls.sql import AlchemyConnection, AlchemyConnectionManager
from zeex.core.compat import QtGui
import zeex.core.utility.widgets as widgets


class AlchemyTableImportDialog(QtGui.QDialog, Ui_AlchemyTableImportDialog):
    def __init__(self, con:AlchemyConnection, con_manager: AlchemyConnectionManager,
                 df_manager=None, **kwargs):
        QtGui.QDialog.__init__(self, **kwargs)
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
        return self._con_manager

    @property
    def df_manager(self) -> DataFrameModelManager:
        if self._df_manager is None:
            self._df_manager = DataFrameModelManager()
        return self._df_manager

    @property
    def source_model(self) -> DataFrameModel:
        file_path = self.lineEditSourcePath.text()
        if self._source_model is None or file_path == '':
            if not os.path.isfile(file_path):
                file_path = QtGui.QFileDialog.getOpenFileName(dir='')[0]
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
        if isinstance(model, str) and os.path.isfile(model):
            model = self.df_manager.read_file(model)
        elif model is None:
            model = self.source_model
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
        orig_size = df.index.size
        key_name = self.comboBoxPrimaryKey.currentText()
        key_priority = self.comboBoxPrimaryKeyPriority.currentText()
        if_exists = self.comboBoxExistingTableOption.currentText()

        try:
            Table = self.con.meta.tables[table_name]
        except (KeyError, AttributeError):
            Table = None

        if key_name in df.columns and key_name != df.index.name:
            df.set_index(key_name, drop=True, inplace=True)

        if Table is not None:
            if if_exists == 'fail':
                raise Exception("Table name {} already exists!".format(table_name))
            elif if_exists == 'append' and key_name != '':
                session = self.con.Session()
                query = session.query(Table)
                if key_priority == 'delete from table':
                    # Delete the data from the table that has the same primary_key
                    try:
                        keys = list(df.index)
                        query.filter(getattr(Table, key_name).in_(keys)).delete()
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        logging.error("Got an error trying to delete matching keys: {}".format(e))

                elif key_priority == 'delete from import data':
                    # Delete the data from the df that has a matching key.
                    ids = [getattr(o, key_name) for o in query.all()]
                    df = df.loc[~df.index.isin(ids), :]
                    logging.info("Removed {} records from the import data with matching keys".format(orig_size - df.index.size))
                session.close()

        if key_name == '':
            key_name = None
            index = False
        else:
            index = True

        if not df.empty:
            df.to_sql(table_name, self.con.engine, if_exists=if_exists, index_label=key_name, index=index)

    def edit_source_model(self):
        source_path = self.lineEditSourcePath.text()
        window = self.df_manager.get_fileview_window(source_path)
        window.show()



