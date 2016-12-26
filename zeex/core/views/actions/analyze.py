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
from functools import partial
from core.compat import QtGui, QtCore
import pandas as pd
from qtpandas.models.DataFrameModel import DataFrameModel
from core.ui.actions.analyze_ui import Ui_FileAnalyzerDialog
from core.ctrls.analyze import DataFrameAnalyzer


class FileAnalyzerDialog(QtGui.QDialog, Ui_FileAnalyzerDialog):

    def __init__(self, source_model, parent=None):
        self.df_model = source_model
        self.analyzer = DataFrameAnalyzer(self.df)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.configure()

    @property
    def df(self):
        return self.df_model.dataFrame()

    def configure(self):
        self.analyzer.process_all_methods()
        self.tableView.setModel(self.analyzer.get_table_view_model())
        self.btnRefresh.clicked.connect(self.refresh)

        # TODO: Make these buttons work and show them.
        self.btnExport.setVisible(False)
        self.btnPivot.setVisible(False)

    def refresh(self):
        self.analyzer.process_all_methods(reprocess=True)


