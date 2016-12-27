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
import pandas as pd
from core.ui.actions.normalize_ui import Ui_ColumnNormalizerDialog
from core.compat import QtGui, QtCore
import core.utility.pandatools as pandatools
from core.ctrls.dataframe import DataFrameModel
from core.utility.widgets import configureComboBox
from core.utility.collection import DictConfig, SettingsINI


class ColumnNormalizerDialog(QtGui.QDialog, Ui_ColumnNormalizerDialog):
    """
    A dialog for normalizing DataFrame columns.
    Allows the user to select columns in the active DataFrameModel
    and make updates. The following updates are supported:
        - Fill or drop NA values
        - Trim trailing spaces (left or right)
        - Merge or split columns
        - Remove special characters
        - Replace spaces
        - Set case (lower, UPPER, Proper)
    """
    defaults = dict(sep=',', case='lower', merge_or_split='merge', merge_or_split_sep='',
                    merge_or_split_active=False)

    def __init__(self, df_model, **kwargs):
        """
        :param df_model: (qtpandas.DataFrameModel)
            A DataFrameModel containing the DataFrame to be updated.
            The DataFrame's columns will be displayed in the listViewColumns.

        :param kwargs: (QtGui.QDialog.__init__(**kwargs))
            :param parent (QtGui.QMainWindow/QDialog)
                It's recommended to set this to the parent window object
        """
        QtGui.QDialog.__init__(self, **kwargs)
        self.setupUi(self)
        self.listViewColumns.model().set_df_model(df_model)

        self.settings = {}
        self.configure()

    @property
    def df_model(self) -> DataFrameModel:
        return self.listViewColumns.model().df_model

    def configure(self):
        """
        Configures basic views/boxes - called automatically on init.
        :return: None
        """
        cases = ['', 'lower', 'upper', 'proper']
        configureComboBox(self.comboBoxSetCase, cases, 'lower')
        if self.df_model is not None:
            title = "Normalize - {}".format(os.path.basename(self.df_model.filePath))
            self.setWindowTitle(title)
        self.buttonBox.accepted.connect(self.execute)
        self.btnUncheckAll.clicked.connect(self.uncheck_all)
        self.btnLoadSettings.clicked.connect(self.import_settings)
        self.btnSaveSettings.clicked.connect(self.export_settings)

    def uncheck_all(self, checkboxes=True, columns=True):
        """
        Unchecks all checkboxes and columns.
        :return: None
        """
        if checkboxes:
            self.checkBoxDropFillNA.setChecked(False)
            self.checkBoxTrimSpaces.setChecked(False)
            self.checkBoxMergeOrSplit.setChecked(False)
            self.checkBoxRemoveSpecialChars.setChecked(False)
            self.checkBoxReplaceSpaces.setChecked(False)
            self.checkBoxSetCase.setChecked(False)
        if columns:
            [c.setCheckState(QtCore.Qt.Unchecked) for c in self.listViewColumns.model().get_items_checked()]

    def get_settings(self):
        """
        Returns a dictionary with current settings & checked columns in the dialog.
        :return:
        """
        settings = dict(case_active = self.checkBoxSetCase.isChecked(),
                        merge_or_split_active = self.checkBoxMergeOrSplit.isChecked(),
                        replace_spaces_active = self.checkBoxReplaceSpaces.isChecked(),
                        trim_spaces_active = self.checkBoxTrimSpaces.isChecked(),
                        drop_or_fill_active = self.checkBoxDropFillNA.isChecked(),
                        remove_special_chars_active=self.checkBoxRemoveSpecialChars.isChecked(),

                        case = self.comboBoxSetCase.currentText(),
                        drop_or_fill = self.comboBoxDropFillNA.currentText(),
                        drop_or_fill_how = self.comboBoxDropFillNAHow.currentText(),
                        drop_or_fill_with = self.lineEditDropFillNA.text(),
                        remove_special_chars_keeps=self.lineEditRemoveSpecialCharsKeeps.text(),
                        merge_or_split = self.comboBoxMergeOrSplit.currentText(),
                        merge_or_split_sep = self.lineEditMergeOrSplitSep.text(),
                        replace_spaces = self.lineEditReplaceSpaces.text(),
                        trim_spaces = self.checkBoxTrimSpaces.isChecked(),
                        columns=[c.text() for c in self.listViewColumns.model().get_items_checked()])
        return settings

    def set_settings(self, settings: (DictConfig, SettingsINI), section='NORMALIZE'):
        """
        Applies settings from a configuration object to the dialog.
        :param settings: (DictConfig, SettingsINI)
            The configuration object that contains the settings to be
            applied to the Dialog.
        :param section: (str, default NORMALIZE)
            The section to gather settings from in the configuration object.
        :return: None
        """
        s = settings
        case = s.get_safe(section, 'case', fallback='')
        drop_or_fill = s.get_safe(section, 'drop_or_fill', fallback='Drop NA')
        drop_or_fill_how = s.get_safe(section, 'drop_or_fill_how', fallback='any')
        merge_or_split = s.get_safe(section, 'merge_or_split', fallback='split')
        columns = [c.lower() for c in s.get_safe(section, 'columns', fallback=[])]

        self.checkBoxRemoveSpecialChars.setChecked(s.getboolean(section, 'remove_special_chars_active', fallback=False))
        self.checkBoxSetCase.setChecked(s.getboolean(section, 'case_active', fallback=False))
        self.checkBoxMergeOrSplit.setChecked(s.getboolean(section, 'merge_or_split_active', fallback=False))
        self.checkBoxReplaceSpaces.setChecked(s.getboolean(section, 'replace_spaces_active', fallback=False))
        self.checkBoxTrimSpaces.setChecked(s.getboolean(section, 'trim_spaces_active', fallback=False))
        self.checkBoxDropFillNA.setChecked(s.getboolean(section, 'drop_or_fill_active', fallback=False))
        self.comboBoxDropFillNA.setCurrentIndex(self.comboBoxDropFillNA.findText(drop_or_fill))
        self.comboBoxSetCase.setCurrentIndex(self.comboBoxSetCase.findText(case))
        self.comboBoxMergeOrSplit.setCurrentIndex(self.comboBoxMergeOrSplit.findText(merge_or_split))
        self.comboBoxDropFillNAHow.setCurrentIndex(self.comboBoxDropFillNAHow.findText(drop_or_fill_how))
        self.lineEditDropFillNA.setText(s.get_safe(section, 'drop_or_fill_with', fallback=''))
        self.lineEditMergeOrSplitSep.setText(s.get_safe(section, 'merge_or_split_sep', fallback=''))
        self.lineEditReplaceSpaces.setText(s.get_safe(section, 'replace_spaces', fallback=''))
        self.lineEditRemoveSpecialCharsKeeps.setText(s.get_safe(section, 'remove_special_chars_keeps', fallback=''))
        current_items = self.listViewColumns.model().get_items()
        [c.setCheckState(QtCore.Qt.Checked) for c in current_items if c.text().lower() in columns]

    def export_settings(self, to=None):
        """
        Outputs Dialog's settings to a text-like file object.
        These settings can be re-imported later.

        :param to: (str, default None)
            The filepath to output the settings to.
            None opens a QFileDialog requiring the user to select a filename to
            save to.
        :return: None
        """
        if to is None:
            to = QtGui.QFileDialog.getSaveFileName(self)[0]
        settings = self.get_settings()
        ini = DictConfig(dictionary=dict(NORMALIZE=settings), filename=to)
        ini.save()

    def import_settings(self, filename=None, dictconfig:DictConfig=None, **kwargs):
        """
        Imports a filepath or a DictConfig/SettingsINI object and
        applies settings to the dialog.

        :param filename: (str, default None)
            The file path to the configuration settings.
        :param diciguration object that holds the settings.
        :param **kwargs: (ColumnNormalizerDialog.set_settings(**kwargs))

        :return: None
        """
        if filename is None:
            if dictconfig is None:
                filename = QtGui.QFileDialog.getOpenFileName(self)[0]
                dictconfig = SettingsINI(filename=filename)

        else:
            dictconfig = SettingsINI(filename=filename)

        self.set_settings(dictconfig, **kwargs)


    def execute(self):
        """
        Applies settings the user has chosen in the dialog to the DataFrameModel.dataFrame().
        :return: None
        """
        df = self.df_model.dataFrame()
        df.columns = [str(x) for x in df.columns]
        columns = self.listViewColumns.model().get_items_checked()
        columns = [i.text() for i in columns]
        if not columns:
            columns = [c for c in df.columns.tolist() if str(df[c].dtype) is 'object']

        case_active = self.checkBoxSetCase.isChecked()
        mos_active = self.checkBoxMergeOrSplit.isChecked()
        replace_spaces_active = self.checkBoxReplaceSpaces.isChecked()
        remove_special_chars_active = self.checkBoxRemoveSpecialChars.isChecked()
        trim_spaces_active = self.checkBoxTrimSpaces.isChecked()
        drop_fill_active = self.checkBoxDropFillNA.isChecked()
        activation_options = [replace_spaces_active, trim_spaces_active,
                              mos_active, case_active, drop_fill_active]
        case = self.comboBoxSetCase.currentText()
        drop_fill = self.comboBoxDropFillNA.currentText().lower()
        dof_how = self.comboBoxDropFillNAHow.currentText()
        dof_with = self.lineEditDropFillNA.text()
        merge_or_split = self.comboBoxMergeOrSplit.currentText().lower()
        mos_sep = self.lineEditMergeOrSplitSep.text()
        replace_spaces = self.lineEditReplaceSpaces.text()
        trim_spaces = self.checkBoxTrimSpaces.isChecked()
        remove_special_chars_keeps = [e for e in self.lineEditRemoveSpecialCharsKeeps.text()
                                      if not e.isalnum() and e is not '']

        if drop_fill_active:
            if 'drop' in drop_fill:
                df = df.dropna(axis=0, how=dof_how, subset=columns)
                if dof_how == 'any':
                    for c in columns:
                        df = df.loc[~df[c].isin(['']), :]
            else:
                try:
                    dof_with = int(dof_with)
                except ValueError:
                    try:
                        dof_with = float(dof_with)
                    except ValueError:
                        pass
                [df.loc[:, c].fillna(value=dof_with) for c in columns]

        if trim_spaces and trim_spaces_active:
            for c in columns:
                df.loc[:, c] = pandatools.series_strip(df.loc[:, c])

        if remove_special_chars_active:
            if not drop_fill_active:
                for c in columns:
                    df.loc[:, c] = df.loc[:, c].fillna(value='')
            for c in columns:

                df.loc[:, c] = df.loc[:, c].apply(lambda x: ''.join(e for e in str(x)
                                                                    if e.isalnum()
                                                                    or e in remove_special_chars_keeps))

        if replace_spaces_active:
            for c in columns:
                df.loc[:, c] = df.loc[:, c].apply(lambda x: str(x).replace(' ', replace_spaces))

        if case not in ['default', ''] and case_active:
            for c in columns:
                df.loc[:, c] = pandatools.series_set_case(df.loc[:, c], how=case)

        if mos_active:
            if merge_or_split == 'merge':
                series = pandatools.dataframe_merge_to_series(df, columns, sep=mos_sep)
                frame = series.to_frame()

            elif merge_or_split == 'split':
                column = columns[0]
                frame = pandatools.series_split(df.loc[:, column],sep=mos_sep)

            df = pd.merge(df, frame, left_index=True, right_index=True)
            df.columns = pandatools.rename_dupe_cols(df.columns)

        if any(activation_options):
            print("Executed normalization on {}".format(self.df_model.filePath))
            self.df_model.setDataFrame(df, filePath=self.df_model.filePath)





