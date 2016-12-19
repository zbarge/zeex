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
from core.compat import QtGui, QtCore
import pandas as pd
from functools import partial
from qtpandas.models.DataFrameModel import DataFrameModel
from core.ui.actions.split_ui import Ui_FileSplitDialog
from core.views.actions.push_grid import PushGridHandler
from core.ctrls.dataframe import DataFrameModelManager
from core.utility.widgets import create_standard_item_model
from core.utility.pandatools import dataframe_split_to_files


class SplitFileDialog(QtGui.QDialog, Ui_FileSplitDialog):
    signalFileSplit = QtCore.Signal(list) # [source_path, [p1, p2, p3, p4]]

    def __init__(self, source_model, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        source_model.dataChanged.connect(partial(self.configure_model, reset=True))
        self.df_model = source_model
        self.setupUi(self)
        self.configure_model()
        self.buttonBox.accepted.connect(self.execute)
        self.buttonBox.rejected.connect(self.close)
        cols = source_model.dataFrame().columns.tolist()
        self.handler_split_on = PushGridHandler(left_button=self.btnSplitOnPushLeft,
                                                left_view=self.listViewSplitOnLeft,
                                                right_button=self.btnSplitOnPushRight,
                                                right_view=self.listViewSplitOnRight,
                                                left_model=cols)
        self.handler_use_cols = PushGridHandler(left_button=self.btnUseColsPushLeft,
                                                left_view=self.listViewUseColsLeft,
                                                right_button=self.btnUseColsPushRight,
                                                right_view=self.listViewUseColsRight,
                                                left_model=cols)

    def configure_model(self, reset=False):
        p = self.df_model.filePath
        self.lineEditSourcePath.setText(p)

        base, ext = os.path.splitext(p)
        filename = os.path.basename(base).lower()
        dirname = os.path.basename(os.path.dirname(base))
        self.lineEditExportPath.setText(os.path.join(os.path.dirname(p), "{}_split".format(filename)))
        self.setWindowTitle("Split: {} - Project - {}".format(filename, dirname))
        if reset is True:
            cols = self.df_model.dataFrame().columns.tolist()
            self.handler_split_on.set_model_from_list(cols)
            self.handler_use_cols.set_model_from_list(cols)

    def execute(self):
        split_on = self.handler_split_on.get_model_list(left=False)
        fields = self.handler_use_cols.get_model_list(left=False)
        dropna = self.checkBoxDropNulls.isChecked()
        dirname = self.lineEditExportPath.text()
        source_path = self.lineEditSourcePath.text()
        max_rows = self.lineEditMaxRows.text()

        try:
            max_rows = int(max_rows)
        except ValueError:
            max_rows = None

        df = self.df_model.dataFrame()

        exported_paths = dataframe_split_to_files(df,
                                                  source_path,
                                                  split_on,
                                                  fields=fields,
                                                  dropna=dropna,
                                                  dest_dirname=dirname,
                                                  chunksize=max_rows,
                                                  index=False)
        emission = [source_path, exported_paths]
        self.signalFileSplit.emit(emission)
        [print(e) for e in emission[1]]














