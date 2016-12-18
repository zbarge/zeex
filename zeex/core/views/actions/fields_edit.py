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
from qtpandas.utils import superReadFile
import pandas as pd
from core.ui.actions.fields_edit_ui import Ui_FieldsEditDialog
from core.compat import QtGui, QtCore
from core.models.fieldnames import FieldModel
from core.utility.pandatools import dataframe_to_datetime
from qtpandas import DataFrameModel

CASE_MAP = {'lower': str.lower,
            'upper': str.upper,
            'proper': str.title,
            'default': lambda x: x}


class FieldsEditDialog(QtGui.QDialog, Ui_FieldsEditDialog):
    """
    The FieldsEditDialog shows the data types and field names
    of the fields in a qtpandas.models.DataFrameModel.

    Users can edit the new_name and dtype columns in this dialog's view.
    Changes can be saved to a .csv/txt template file as well as to a template
    that can be stored for future use.

    To use:
        dialog = FieldsEditDialog(DataFrameModel)
        dialog.show()
    """
    def __init__(self, model: DataFrameModel, *args, **kwargs):

        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.dfmodel = model
        self.fmodel = FieldModel()
        self.configure()

    def configure(self):
        self.update_fields_model()
        self.tableView.setModel(self.fmodel)
        self.dfmodel.dataChanged.connect(self.update_fields_model)
        self.btnReset.clicked.connect(self.fmodel.reset_to_original)
        self.btnSaveFile.clicked.connect(self.apply_changes)
        self.btnSetCase.clicked.connect(self.apply_case)
        self.btnLoadTemplate.clicked.connect(self.import_template)
        self.btnExportTemplate.clicked.connect(self.export_template)
        self.btnParseDates.clicked.connect(self.parse_dates)
        self.setWindowTitle("Edit Fields - {}".format(os.path.basename(self.dfmodel.filePath)))

    def apply_case(self):
        value = self.setCaseComboBox.currentText()
        self.fmodel.apply_new_name(CASE_MAP[value.lower()])

    def update_fields_model(self, *args, **kwargs):
        """
        Updates the fields model - designed to connect
        to propogate changes off the dataFrameModel
        :param args:
        :param kwargs:
        :return:
        """
        cur_ct = self.fmodel.rowCount()
        df = self.dfmodel.dataFrame()
        if cur_ct > 0:
            for i in range(self.fmodel.rowCount()):
                item = self.fmodel.item(i, 0)
                if item and item.text() not in df.columns:
                    self.fmodel.takeRow(i)
        for col in df.columns:
            self.fmodel.set_field(col, dtype=df[col].dtype)

    def apply_template(self, df, columns=['old', 'new', 'dtype']):
        df.columns = columns #Make or break this frame.
        for i in range(df.index.size):
            entry = df.iloc[i]
            matches = self.fmodel.findItems(entry['old'])
            if matches:
                [self.fmodel.takeRow(r.row()) for r in matches]
                self.fmodel.set_field(entry['old'], entry['new'], entry['dtype'])

    def import_template(self, filename=None, columns=None):
        def_cols = ['old', 'new', 'dtype']
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName()[0]
        df = superReadFile(filename)
        if columns is None:
            df = df.loc[:, def_cols]
            columns = def_cols
        self.apply_template(df, columns=columns)

    def parse_dates(self):
        df = self.dfmodel.dataFrame()
        dt_model = self.dfmodel.columnDtypeModel()
        dt_model.setEditable(True)
        all_cols = df.columns.tolist()
        new_df = df.copy()
        new_df = dataframe_to_datetime(new_df)
        new_cols = [c for c in all_cols
                    if new_df[c].dtype != df[c].dtype
                    and 'date' in str(new_df[c].dtype)]
        if new_cols:
            self.dfmodel.setDataFrame(new_df, filePath=self.dfmodel.filePath)
            for n in new_cols:
                self.fmodel.set_field(n, dtype=new_df[n].dtype)

    def export_template(self, filename=None, **kwargs):
        if filename is None:
            filename = QtGui.QFileDialog.getSaveFileName()[0]
        filebase, ext = os.path.splitext(filename)
        if not ext.lower() in ['.txt','.csv']:
            ext = '.csv'
        filename = filebase + ext
        columns = ['old', 'new', 'dtype']
        fm = self.fmodel
        data = [[fm.item(i, x).text() for x in range(3)]
                for i in range(fm.rowCount())]

        df = pd.DataFrame(data, columns=columns, index=list(range(len(data))))
        kwargs['index'] = kwargs.get('index', False)
        df.to_csv(filename, **kwargs)

    def apply_changes(self, rename=True, dtype=True):
        renames = {}
        dtypes = {}
        df = self.dfmodel._dataFrame
        df_dtypes = self.dfmodel._columnDtypeModel

        # Gather rename/dtype info from FieldsModel
        for i in range(self.fmodel.rowCount()):
            orig_name = self.fmodel.item(i, 0).text()
            new_name = self.fmodel.item(i, 1).text()
            dt = self.fmodel.item(i, 2).text()
            dtypes.update({orig_name: dt})
            renames.update({orig_name: new_name})

        # Update the ColumnDtypeModel for the data
        if dtype is True:
            for i in range(df_dtypes.rowCount()):
                idx = df_dtypes.index(i, 0)
                name = idx.data()
                dt = dtypes[name]

                if str(dt) != str(df[name].dtype):

                    print("Changing dtype {}".format(name))
                    df_dtypes.setData(idx, dt)

        # Use the DataFrameModel's rename method.
        if rename is True:
            print("Applying renames {}".format(renames))
            self.dfmodel.rename(columns=renames)





