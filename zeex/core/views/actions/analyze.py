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

from core.compat import QtGui
from core.models.dataframe import DataFrameDescriptionModel
from core.ui.actions.analyze_ui import Ui_FileAnalyzerDialog
from models import DataFrameModel


class FileAnalyzerDialog(QtGui.QDialog, Ui_FileAnalyzerDialog):

    def __init__(self, source_model: DataFrameModel, parent=None):
        self.df_model = source_model
        self.analyze_model = DataFrameDescriptionModel(source_model=source_model)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.configure()

    @property
    def df(self):
        return self.df_model.dataFrame()

    def configure(self):
        self.tableView.setModel(self.analyze_model)
        self.btnRefresh.clicked.connect(self.sync)
        # TODO: Make these buttons work and show them.
        self.btnExport.setVisible(False)
        self.btnPivot.setVisible(False)
        self.df_model.dataChanged.connect(self.sync)
        self.sync()

    def sync(self):
        self.setWindowTitle("Analyze {}".format(os.path.basename(self.df_model.filePath)))


