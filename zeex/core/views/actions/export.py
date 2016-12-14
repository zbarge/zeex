import os
from core.compat import QtGui, QtCore
from core.ui.actions.export_ui import Ui_ExportFileDialog
from core.utility.widgets import configureComboBox, display_ok_msg
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
        display_ok_msg(self, "Exported {}!".format(file_path))





