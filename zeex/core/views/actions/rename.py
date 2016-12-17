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






