
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


