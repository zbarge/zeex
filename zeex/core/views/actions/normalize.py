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
from qtpandas import DataFrameModel
from core.utility.widgets import configureComboBox
from core.utility.collection import DictConfig, SettingsINI


class ColumnNormalizerDialog(QtGui.QDialog, Ui_ColumnNormalizerDialog):
    defaults = dict(sep=',', case='lower', merge_or_split='merge', merge_or_split_sep='',
                    merge_or_split_active=False)

    def __init__(self, df_model, **kwargs):
        QtGui.QDialog.__init__(self, **kwargs)
        self.setupUi(self)
        self.listViewColumns.model().set_df_model(df_model)

        self.settings = {}
        self.configure()

    @property
    def df_model(self) -> DataFrameModel:
        return self.listViewColumns.model().df_model

    def configure(self):
        cases = ['', 'lower', 'upper', 'proper']
        configureComboBox(self.comboBoxSetCase, cases, 'lower')
        if self.df_model is not None:
            title = "Normalize - {}".format(os.path.basename(self.df_model.filePath))
            self.setWindowTitle(title)
        self.buttonBox.accepted.connect(self.execute)
        self.btnUncheckAll.clicked.connect(self.uncheck_all)
        self.btnLoadSettings.clicked.connect(self.import_settings)
        self.btnSaveSettings.clicked.connect(self.export_settings)

    def uncheck_all(self):
        self.checkBoxDropFillNA.setChecked(False)
        self.checkBoxTrimSpaces.setChecked(False)
        self.checkBoxMergeOrSplit.setChecked(False)
        self.checkBoxRemoveSpecialChars.setChecked(False)
        self.checkBoxReplaceSpaces.setChecked(False)
        self.checkBoxSetCase.setChecked(False)

    def get_settings(self):
        settings = dict(case_active = self.checkBoxSetCase.isChecked(),
                        merge_or_split_active = self.checkBoxMergeOrSplit.isChecked(),
                        replace_spaces_active = self.checkBoxReplaceSpaces.isChecked(),
                        trim_spaces_active = self.checkBoxTrimSpaces.isChecked(),
                        drop_or_fill_active = self.checkBoxDropFillNA.isChecked(),

                        case = self.comboBoxSetCase.currentText(),
                        drop_or_fill = self.comboBoxDropFillNA.currentText().lower(),
                        drop_or_fill_how = self.comboBoxDropFillNAHow.currentText(),
                        drop_or_fill_with = self.lineEditDropFillNA.text(),
                        merge_or_split = self.comboBoxMergeOrSplit.currentText().lower(),
                        merge_or_split_sep = self.lineEditMergeOrSplitSep.text(),
                        replace_spaces = self.lineEditReplaceSpaces.text(),
                        trim_spaces = self.checkBoxTrimSpaces.isChecked())
        return settings

    def set_settings(self, settings: DictConfig):
        s = settings
        case = s.get_safe('NORMALIZE', 'case', fallback='')
        drop_or_fill = s.get_safe('NORMALIZE', 'drop_or_fill', fallback='Drop NA')
        drop_or_fill_how = s.get_safe('NORMALIZE', 'drop_or_fill_how', fallback='any')
        merge_or_split = s.get_safe('NORMALIZE', 'merge_or_split', fallback='split')
        self.checkBoxSetCase.setChecked(s.get_safe('NORMALIZE', 'case_active', fallback=False))
        self.checkBoxMergeOrSplit.setChecked(s.get_safe('NORMALIZE', 'merge_or_split_active', fallback=False))
        self.checkBoxReplaceSpaces.setChecked(s.get_safe('NORMALIZE', 'replace_spaces_active', fallback=False))
        self.checkBoxTrimSpaces.setChecked(s.get_safe('NORMALIZE', 'trim_spaces_active', fallback=False))
        self.checkBoxDropFillNA.setchecked(s.get_safe('NORMALIZE', 'drop_or_fill_active', fallback=False))
        self.comboBoxDropFillNA.setCurrentIndex(self.comboBoxDropFillNA.findText(drop_or_fill))
        self.comboBoxSetCase.setCurrentIndex(self.comboBoxSetCase.findText(case))
        self.comboBoxMergeOrSplit.setCurrentIndex(self.comboBoxMergeOrSplit.findText(merge_or_split))
        self.comboBoxDropFillNAHow.setCurrentIndex(self.comboBoxDropFillNAHow.findText(drop_or_fill_how))
        self.lineEditDropFillNA.setText(s.get_safe('NORMALIZE', 'drop_or_fill_with', fallback=''))
        self.lineEditMergeOrSplitSep.setText(s.get_safe('NORMALIZE', 'merge_or_split_sep', fallback=''))
        self.lineEditReplaceSpaces.setText(s.get_safe('NORMALIZE', 'replace_spaces', fallback=''))

    def export_settings(self, to=None):
        if to is None:
            to = QtGui.QFileDialog.getSaveFileName(self)
        settings = self.get_settings()
        ini = DictConfig(dictionary=dict(NORMALIZE=settings), filename=to)
        ini.save()

    def import_settings(self, filename=None, dictconfig:DictConfig=None):
        if filename is None:
            if dictconfig is None:
                raise TypeError("filename and dictconfig paramaters cannot be both be None.")
        else:
            dictconfig = SettingsINI(filename=filename)

        self.set_settings(dictconfig)

    def execute(self):
        df = self.df_model.dataFrame()
        df.columns = [str(x) for x in df.columns]
        columns = self.listViewColumns.model().get_items_checked()
        columns = [i.text() for i in columns]
        if not columns:
            columns = [c for c in df.columns.tolist() if str(df[c].dtype) is 'object']

        case_active = self.checkBoxSetCase.isChecked()
        mos_active = self.checkBoxMergeOrSplit.isChecked()
        replace_spaces_active = self.checkBoxReplaceSpaces.isChecked()
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

        if drop_fill_active:
            if 'drop' in drop_fill:
                df = df.dropna(axis=0, how=dof_how, subset=columns)
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
                df = pd.merge(df, frame, left_index=True, right_index=True)
                df.columns = pandatools.rename_dupe_cols(df.columns)

            elif merge_or_split == 'split':
                column = columns[0]
                add_df = pandatools.series_split(df.loc[:, column],sep=mos_sep)
                df = pd.merge(df, add_df, left_index=True, right_index=True)
                df.columns = pandatools.rename_dupe_cols(df.columns)
                print("Split column {} on {}".format(column, mos_sep))

        if any(activation_options):
            self.df_model.setDataFrame(df, filePath=self.df_model.filePath)





