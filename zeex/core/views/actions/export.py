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
from core.ui.actions.export_ui import Ui_ExportFileDialog
from core.utility.widgets import configureComboBox, get_ok_msg_box
from core.ctrls.dataframe import DataFrameModelManager

SEPARATORS = {'Comma':',',
              'Semi Colon': ';',
              'Tab':r'\t',
              'Pipe':'|'}

ENCODINGS = {'UTF-8':'UTF_8',
             'ASCII':'ASCII',
             'UTF-16':'UTF_16',
             'UTF-32':'UTF_32',
             'ISO-8859-1':'ISO-8859-1'}


class DataFrameModelExportDialog(QtGui.QDialog, Ui_ExportFileDialog):
    signalExported = QtCore.Signal(str, str) # original_path, new_path

    def __init__(self, df_manager: DataFrameModelManager, filename: str=None, **kwargs):
        self._parent = kwargs.pop('parent', None)
        self.df_manager = df_manager
        self.df_manager.signalNewModelRead.connect(self.append_source_filename)

        if filename is None:

            if df_manager.last_path_updated is not None:
                self._default_path = df_manager.last_path_updated
            else:
                self._default_path = df_manager.last_path_read

        else:
            self._default_path = filename
            assert filename in df_manager.file_paths, "Invalid filename {} not in DataFrameModelManager paths: {}".format(
                                                       filename, df_manager.file_paths)

        QtGui.QDialog.__init__(self, **kwargs)
        self.setupUi(self)
        self.configure()
    @property
    def parent(self):
        if self._parent is not None:
            return self._parent
        return self

    def configure(self):
        self.btnBrowseDestination.clicked.connect(self.browse_destination)
        self.btnBrowseSource.clicked.connect(self.browse_source)
        configureComboBox(self.comboBoxSource, self.df_manager.file_paths, self._default_path)
        configureComboBox(self.comboBoxSeparator, list(SEPARATORS.keys()), 'Comma')
        configureComboBox(self.comboBoxEncoding, list(ENCODINGS.keys()), 'ISO-8859-1')
        self.buttonBox.accepted.connect(self.export)

        if self._default_path is not None:
            base, ext = os.path.splitext(self._default_path)
            destination_path = "{}_updated{}".format(base, ext)
            self.lineEditDestination.setText(destination_path)

    def browse_destination(self):
        filename = QtGui.QFileDialog.getSaveFileName(self)[0]
        self.lineEditDestination.setText(filename)

    def browse_source(self):
        filename = QtGui.QFileDialog.getOpenFileName(self)[0]
        if filename not in self.df_manager.file_paths:
            self.df_manager.read_file(filename)
        idx = self.comboBoxSource.findText(filename)
        self.comboBoxSource.setCurrentIndex(idx)

    @QtCore.Slot(str)
    def append_source_filename(self, filename: str):
        self.comboBoxSource.addItem(filename)

    def export(self):
        source_path = self.comboBoxSource.currentText()
        file_path = self.lineEditDestination.text()
        encoding = self.comboBoxEncoding.currentText()

        if self.radioBtnOtherSeparator.isChecked():
            sep = self.lineEditOtherSeparator.text()
        else:
            sep = self.comboBoxSeparator.currentText()

        kwargs = dict(index=False)
        kwargs['encoding'] = ENCODINGS[encoding]
        kwargs['sep'] = SEPARATORS[sep]

        self.df_manager.save_file(source_path, save_as=file_path, keep_orig=True, **kwargs)
        self.signalExported.emit(source_path, file_path)
        self.hide()
        #box = get_ok_msg_box(self.parent, "Exported {}!".format(file_path))
        #box.show()





