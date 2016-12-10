import os
from qtpandas.utils import superReadFile
import pandas as pd
from core.ui.actions.fields_edit_ui import Ui_FieldsEditDialog
from core.compat import QtGui, QtCore
from core.models.fieldnames import FieldModel


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
    def __init__(self, model, *args, **kwargs):

        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.dfmodel = model
        self.fmodel = FieldModel()
        self.configure()

    def configure(self):
        df = self.dfmodel._dataFrame
        for field in df.columns:
            self.fmodel.set_field(field, field, dtype=df[field].dtype)
        self.tableView.setModel(self.fmodel)
        self.btnReset.clicked.connect(self.fmodel.reset_to_original)
        self.btnSaveFile.clicked.connect(self.apply_changes)
        self.btnSetCase.clicked.connect(self.apply_case)
        self.btnLoadTemplate.clicked.connect(self.import_template)
        self.btnExportTemplate.clicked.connect(self.export_template)
        self.setWindowTitle("Edit Fields - {}".format(os.path.basename(self.dfmodel.filePath)))

    def apply_case(self):
        value = self.setCaseComboBox.currentText()
        self.fmodel.apply_new_name(CASE_MAP[value.lower()])

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





