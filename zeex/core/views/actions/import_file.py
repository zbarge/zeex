# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:09:50 2016
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
from core.ui.actions.import_ui import Ui_ImportFileDialog
from core.compat import QtGui, QtCore
import core.utility.pandatools as pandatools
from core.ctrls.dataframe import DataFrameModelManager, DataFrameModel,SEPARATORS, ENCODINGS
from core.utility.widgets import configureComboBox


class DataFrameModelImportDialog(QtGui.QDialog, Ui_ImportFileDialog):
    signalImported = QtCore.Signal(str) # file path

    def __init__(self, df_manager: DataFrameModelManager, file_path=None, **kwargs):
        QtGui.QDialog.__init__(self, **kwargs)
        self.df_manager = df_manager
        self.file_path = file_path
        self.setupUi(self)
        self.configure()

    def configure(self):
        self.checkBoxHasHeaders.setChecked(True)
        if self.file_path is not None:
            self.set_file_path(self.file_path)
        self.btnBrowseFilePath.clicked.connect(self.set_file_path)
        self.buttonBox.accepted.connect(self.execute)
        configureComboBox(self.comboBoxSeparator, list(SEPARATORS.keys()), 'Comma')
        configureComboBox(self.comboBoxEncoding, list(ENCODINGS.keys()), 'ISO-8859-1')

    def set_file_path(self, file_path=None):
        if file_path is None:
            if self.file_path is None:
                file_path = self.lineEditFilePath.text()
            else:
                file_path = self.file_path
        if not os.path.isfile(file_path):
            last = self.df_manager.last_path_updated
            if last is not None:
                kwargs = dict(dir=os.path.dirname(last))
            else:
                kwargs = dict()
            file_path = QtGui.QFileDialog.getOpenFileName(**kwargs)[0]
        self.lineEditFilePath.setText(str(file_path))

    def process_dataframe(self, df, trim_spaces=False, remove_linebreaks=False, parse_dates=False):
        if trim_spaces and not remove_linebreaks:
            for c in df.columns:
                if str(df[c].dtype) == 'object':
                    df.loc[:, c] = pandatools.series_strip(df.loc[:, c])
        elif remove_linebreaks:
            df = pandatools.dataframe_remove_linebreaks(df, copy=False)

        if parse_dates:
            df = pandatools.dataframe_to_datetime(df)
        return df

    def set_separator(self, sep):
        try:
            SEPARATORS[sep]
        except KeyError:
            mapper = {v: k for k, v in SEPARATORS.items()}
            try:
                sep = mapper[sep]
            except KeyError:
                self.radioBtnOtherSeparator.setChecked(True)
                return self.lineEditOtherSeparator.setText(sep)

        self.comboBoxSeparator.setCurrentIndex(self.comboBoxSeparator.findText(sep))

    def set_encoding(self, en):
        try:
            ENCODINGS[en]
        except KeyError as e:
            mapper = {v: k for k, v in ENCODINGS.items()}
            try:
                en = mapper[en]
            except KeyError as e:
                raise KeyError("Invalid Encoding {}".format(e))
        self.comboBoxEncoding.setCurrentIndex(self.comboBoxEncoding.findText(en))

    def execute(self):
        file_path = self.lineEditFilePath.text()
        file_megabytes = os.path.getsize(file_path) / 1000 / 1000
        remove_linebreaks = self.checkBoxScrubLinebreaks.isChecked()
        trim_spaces = self.checkBoxTrimSpaces.isChecked()
        has_headers = self.checkBoxHasHeaders.isChecked()
        parse_dates = self.checkBoxParseDates.isChecked()
        encoding = self.comboBoxEncoding.currentText()

        kwargs = dict()
        if self.radioBtnOtherSeparator.isChecked():
            sep = self.lineEditOtherSeparator.text()
            kwargs['sep'] = sep
        else:
            sep = self.comboBoxSeparator.currentText()
            kwargs['sep'] = SEPARATORS.get(sep, ',')

        if not has_headers:
            kwargs['header'] = 0
        kwargs['first_codec'] = ENCODINGS.get(encoding, 'utf8')

        if file_megabytes > 1000:
            kwargs['chunksize'] = 50 * 1000 * 1000
        df_reader = pandatools.superReadFile(file_path, **kwargs)

        if kwargs.get('chunksize', 0) > 0:
            # Process the dataframe in chunks
            df = pd.DataFrame()
            for chunk in df_reader:

                chunk = self.process_dataframe(chunk, trim_spaces=trim_spaces,
                                               remove_linebreaks=remove_linebreaks,
                                               parse_dates=parse_dates)
                df = df.append(chunk)
        else:

            df = self.process_dataframe(df_reader, trim_spaces=trim_spaces,
                                        remove_linebreaks=remove_linebreaks,
                                        parse_dates=parse_dates)

        dfm = DataFrameModel(dataFrame=df,filePath=file_path)
        self.df_manager.set_model(df_model=dfm, file_path=file_path)
        self.signalImported.emit(file_path)










