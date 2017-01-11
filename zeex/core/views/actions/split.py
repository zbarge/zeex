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
from zeex.core.compat import QtGui, QtCore
from zeex.core.ui.actions.split_ui import Ui_FileSplitDialog
from zeex.core.utility.collection import DictConfig, import_settings, export_settings
from zeex.core.utility.pandatools import dataframe_split_to_files
from zeex.core.views.basic.push_grid import PushGridHandler


class SplitFileDialog(QtGui.QDialog, Ui_FileSplitDialog):
    signalFileSplit = QtCore.Signal(list) # [source_path, [p1, p2, p3, p4]]

    def __init__(self, source_model, parent=None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.df_model = source_model
        self.setupUi(self)
        self.configure_model()
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
        self.configure()

    def configure(self):
        self.btnExportTemplate.clicked.connect(self.export_settings)
        self.btnImportTemplate.clicked.connect(self.import_settings)
        self.df_model.dataChanged.connect(partial(self.configure_model, reset=True))
        self.buttonBox.accepted.connect(self.execute)
        self.buttonBox.rejected.connect(self.close)

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

    def get_settings(self, dc:DictConfig=None, section:str="SPLIT"):
        if dc is None:
            dc = DictConfig()
        if dc.has_section(section):
            dc.remove_section(section)
        dictionary = dict(dropna = self.checkBoxDropNulls.isChecked(),
                          dirname = self.lineEditExportPath.text(),
                          source_path = self.lineEditSourcePath.text(),
                          max_rows = self.lineEditMaxRows.text())
        dc.update({section: dictionary})
        dc.set_safe(section, 'split_on', self.handler_split_on.get_model_list(left=False))
        dc.set_safe(section, 'fields', self.handler_use_cols.get_model_list(left=False))
        return dc

    def set_settings(self, dc:DictConfig, section='SPLIT'):
        self.lineEditTemplate.setText(dc.filename)
        self.handler_split_on.set_model_from_list(dc.get_safe(section, 'split_on',
                                                              fallback=self.handler_split_on.get_model_list(left=False)),
                                                  left=False)
        self.handler_split_on.drop_duplicates(left_priority=False)
        self.handler_use_cols.set_model_from_list(dc.get_safe(section, 'fields',
                                                              fallback=self.handler_use_cols.get_model_list(left=False)),
                                                  left=False)
        self.handler_use_cols.drop_duplicates(left_priority=False)
        self.checkBoxDropNulls.setChecked(dc.getboolean(section, 'dropna', fallback=self.checkBoxDropNulls.isChecked()))
        self.lineEditSourcePath.setText(dc.get(section, 'source_path', fallback=self.lineEditSourcePath.text()))
        self.lineEditExportPath.setText(dc.get(section, 'dirname', fallback=self.lineEditExportPath.text()))
        self.lineEditMaxRows.setText(dc.get(section, 'max_rows', fallback=self.lineEditMaxRows.text()))

    def import_settings(self):
        import_settings(self.set_settings, parent=self)

    def export_settings(self):
        export_settings(self.get_settings(),parent=self)

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














