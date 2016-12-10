from core.compat import QtGui, QtCore
from core.ui.actions.rename_ui import Ui_renameDialog
from core.models.fieldnames import FieldRenameModel

CASE_MAP = {'lower': str.lower,
            'upper': str.upper,
            'proper': str.title,
            'default': lambda x: x}

class RenameDialog(QtGui.QDialog, Ui_renameDialog):
    def __init__(self, *args, **kwargs):
        self.dfmodel = kwargs.pop('model')
        self.rnmodel = FieldRenameModel()
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.configure_settings()

    def configure_settings(self):
        df = self.dfmodel._dataFrame
        self.rnmodel.set_renames(df.columns, fill_missing=True, clear_current=True)
        self.tableView.setModel(self.rnmodel)
        self.btnSaveRenames.clicked.connect(self.apply_renames)
        self.btnLoadTemplate.clicked.connect(self.load_template)
        self.btnSaveFile.clicked.connect(self.save_file)
        self.setCaseBtn.clicked.connect(self.set_case)

    def apply_renames(self):
        rename_cols = self.rnmodel.get_renames_dict()
        self.dfmodel.rename(columns=rename_cols)

    def load_template(self):
        pass

    def save_file(self):
        pass

    def set_case(self):
        value = self.setCaseComboBox.currentText().lower()
        if value:
            self.rnmodel.set_case(CASE_MAP[value])






