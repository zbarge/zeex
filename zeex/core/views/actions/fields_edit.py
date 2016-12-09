import os
from core.ui.actions.fields_edit_ui import Ui_FieldsEditDialog
from core.compat import QtGui, QtCore
from core.models.fieldnames import FieldModel

CASE_MAP = {'lower': str.lower,
            'upper': str.upper,
            'proper': str.title,
            'default': lambda x: x}

class FieldsEditDialog(QtGui.QDialog, Ui_FieldsEditDialog):
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
        self.setCaseBtn.clicked.connect(self.apply_case)
        self.setWindowTitle("Edit Fields - {}".format(os.path.basename(self.dfmodel.filePath)))

    def apply_case(self):
        value = self.setCaseComboBox.currentText()
        self.fmodel.apply_new_name(CASE_MAP[value.lower()])

    def apply_renames(self):
        pass

    def apply_changes(self, rename=True, dtype=True):
        renames = {}
        dtypes = {}
        df = self.dfmodel._dataFrame
        df_dtypes = self.dfmodel._columnDtypeModel
        for i in range(self.fmodel.rowCount()):
            orig_name = self.fmodel.item(i, 0).text()
            new_name = self.fmodel.item(i, 1).text()
            dtype = self.fmodel.item(i, 2).text()
            dtypes.update({orig_name:new_name})
            renames.update({orig_name:new_name})

        if dtype is True:
            for i in range(dtype.rowCount()):
                item = dtype.item(i)
                name = item.text()
                dt = dtypes[name]

                if str(dt) != str(df[name].dtype):
                    print("Changing dtype {}".format(name))
                    df_dtypes.setData(item.index(), dt)




