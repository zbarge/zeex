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
import pandas as pd
from zeex.core.compat import QtGui
import zeex.core.utility.pandatools as pandatools
from zeex.core.ctrls.dataframe import DataFrameModel
from zeex.core.models.fieldnames import FieldModel
from zeex.core.ui.actions.fields_edit_ui import Ui_FieldsEditDialog
from zeex.core.utility.pandatools import dataframe_to_datetime, rename_dupe_cols
from zeex.core.utility.pandatools import superReadFile
import zeex.core.utility.widgets as widgets
CASE_MAP = {'lower': str.lower,
            'upper': str.upper,
            'proper': str.title,
            'default': lambda x: x}

ORIG_NAME = 'orig_name'
NEW_NAME = 'new_name'
DTYPE = 'dtype'


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
        self.key_delete = QtGui.QShortcut(self)
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
        self.btnUp.clicked.connect(self.push_field_up)
        self.btnDown.clicked.connect(self.push_field_down)
        self.btnTop.clicked.connect(self.push_field_top)
        self.btnBottom.clicked.connect(self.push_field_bottom)
        self.btnDelete.clicked.connect(self.delete_selected_fields)
        self.btnSort.clicked.connect(self.sort_fields)
        self.setWindowTitle("Edit Fields - {}".format(os.path.basename(self.dfmodel.filePath)))
        self.key_delete.setKey('del')
        self.key_delete.activated.connect(self.delete_selected_fields)
        # TODO: Make this work.
        self.radioBtnSyncDatabase.setVisible(False)
        self.tableView.setSelectionMode(self.tableView.ExtendedSelection)

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
        df.columns = [str(x) for x in df.columns]
        orig_cols = df.columns.tolist()

        if len(list(set(orig_cols))) < len(orig_cols):
            df.columns = rename_dupe_cols(df.columns)
            self.dfmodel.dataChanged.emit()

        if cur_ct > 0:
            for i in range(self.fmodel.rowCount()):
                item = self.fmodel.item(i, 0)
                if item and item.text() not in df.columns:
                    self.fmodel.takeRow(i)
        for col in df.columns:
            self.fmodel.set_field(col, dtype=df[col].dtype)

    def push_field_down(self):
        widgets.table_push_item_down(self.tableView)

    def push_field_up(self):
        widgets.table_push_item_up(self.tableView)

    def push_field_top(self):
        model = self.fmodel
        view = self.tableView
        rows = reversed([v.row() for v in view.selectedIndexes()])
        for ct, row in enumerate(rows, start=1):
            model.insertRow(0)
            [model.setItem(0, i, v) for i, v in enumerate(model.takeRow(row + ct))]
            view.setCurrentIndex(model.item(row, 0).index())

    def push_field_bottom(self):
        model = self.fmodel
        view = self.tableView
        rows = reversed([v.row() for v in view.selectedIndexes()])
        for ct, row in enumerate(rows, start=1):
            bottom = model.rowCount()
            model.insertRow(bottom)
            [model.setItem(bottom, i, v) for i, v in enumerate(model.takeRow(row))]
            model.takeRow(model.rowCount() - 2)
            view.setCurrentIndex(model.item(row, 0).index())

    def sort_fields(self):
        asc = self.checkBoxSortAscending.isChecked()
        df = self.export_template(to_frame=True)
        df.sort_values(NEW_NAME, ascending=asc, inplace=True)
        self.import_template(df=df)

    def apply_template(self, df, columns=None):
        if columns is None:
            columns = [ORIG_NAME, NEW_NAME, DTYPE]
        current_frame_cols = self.dfmodel.dataFrame().columns.tolist()
        df.columns = columns  # Make or break this frame.

        for i in range(df.index.size):
            entry = df.iloc[i]
            matches = self.fmodel.findItems(entry[columns[0]])
            if matches:
                [self.fmodel.takeRow(r.row()) for r in matches]

            self.fmodel.set_field(*[entry[c] for c in columns])

        # Clear entries that dont exist in the dataframe columns.
        for i in range(self.fmodel.rowCount()):
            name = self.fmodel.item(i, 0)
            if name and name.text() not in current_frame_cols:
                self.fmodel.takeRow(i)

    def delete_selected_fields(self):
        model = self.fmodel
        view = self.tableView
        for idx in view.selectedIndexes():
            row_num = idx.row()
            row = model.takeRow(row_num)
            if row:
                self.dfmodel.dataFrame().drop(row[0].text(), axis=1, inplace=True)
            if row_num > model.rowCount():
                row_num = model.rowCount() - 1

        self.dfmodel.dataChanged.emit()
        self.dfmodel.layoutChanged.emit()
        view.setCurrentIndex(model.item(row_num, 0).index())

    def import_template(self, filename=None,df=None, columns=None):
        def_cols = [ORIG_NAME, NEW_NAME, DTYPE]
        if df is None:
            if filename is None:
                try:
                    dirname = os.path.dirname(self.dfmodel.filePath)
                except:
                    dirname = ''
                filename = QtGui.QFileDialog.getOpenFileName(dir=dirname)[0]
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

    def export_template(self, filename=None, to_frame=False, **kwargs):
        fm = self.fmodel
        columns = [fm.horizontalHeaderItem(i).text() for i in range(fm.columnCount())]
        data = [[fm.item(i, x).text() for x in range(fm.columnCount())]
                for i in range(fm.rowCount())]

        df = pd.DataFrame(data, columns=columns, index=list(range(len(data))))
        if filename is None and not to_frame:
            try:
                dirname = os.path.dirname(self.dfmodel.filePath)
            except:
                dirname = ''
            filename = QtGui.QFileDialog.getSaveFileName(dir=dirname)[0]
            filebase, ext = os.path.splitext(filename)
            if not ext.lower() in ['.txt','.csv']:
                ext = '.csv'
            filename = filebase + ext
            kwargs['index'] = kwargs.get('index', False)
            df.to_csv(filename, **kwargs)
            return filename
        elif to_frame:
            return df
        else:
            raise Exception("filename and to to_frame cannot be a False value!")

    def apply_changes(self, rename=True, dtype=True):
        renames = {}
        dtypes = {}
        df = self.dfmodel.dataFrame()
        df_dtypes = self.dfmodel._columnDtypeModel
        orig_cols = [str(x) for x in df.columns]
        new_cols = [self.fmodel.item(i, 0).text() for i in range(self.fmodel.rowCount())]
        extra_cols = [x for x in new_cols if x not in orig_cols]
        new_cols = [x for x in new_cols if x in orig_cols]
        order_match = [x for i, x in enumerate(new_cols) if orig_cols[i] == x]
        change_order = len(order_match) != len(new_cols)

        if change_order:
            df = df.loc[:, new_cols]

        if extra_cols:
            for e in extra_cols:
                idx = self.fmodel.findItems(e)
                if idx:
                    self.fmodel.takeRow(idx[0].row())

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
                dt = str(dtypes[name])

                if dt != str(df[name].dtype):
                    if 'int' in dt:
                        df.loc[:, name] = pandatools.series_to_numeric(df.loc[:, name],astype=int)
                    elif 'float' in dt:
                        df.loc[:, name] = pandatools.series_to_numeric(df.loc[:, name], astype=float)
                    elif 'date' in dt:
                        df.loc[:, name] = pd.to_datetime(df.loc[:, name], errors='coerce')
                    elif 'str' in dt or 'obj' in dt:
                        df.loc[:, name] = df.loc[:, name].astype(str)

        # Use the DataFrameModel's rename method.
        if rename is True:
            df.rename(columns=renames, inplace=True)

        if any([change_order, rename, dtype]):
            self.dfmodel.setDataFrame(df, copyDataFrame=False, filePath=self.dfmodel.filePath)





