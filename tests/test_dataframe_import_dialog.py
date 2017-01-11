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
import pytest
from tests.main import MainTestClass
from zeex.core.views.actions.import_file import DataFrameModelImportDialog, pandatools
from zeex.core.ctrls.dataframe import DataFrameModel, DataFrameModelManager, SEPARATORS, ENCODINGS


class TestDataFrameModelImportDialog(MainTestClass):

    @pytest.fixture
    def dialog(self, qtbot, example_file_path) -> DataFrameModelImportDialog:

        dfm = DataFrameModelManager()
        dialog = DataFrameModelImportDialog(dfm, file_path=example_file_path)
        dialog.show()
        qtbot.add_widget(dialog)
        return dialog

    def test_general(self, dialog: DataFrameModelImportDialog, example_file_path):
        assert example_file_path not in dialog.df_manager.file_paths
        dialog.execute()
        assert example_file_path in dialog.df_manager.file_paths

    def test_parse_dates(self, dialog:DataFrameModelImportDialog):
        dialog.checkBoxParseDates.setChecked(True)

    @pytest.mark.parametrize('sep', list(SEPARATORS.keys()))
    def test_separators(self, dialog: DataFrameModelImportDialog, example_file_path, sep):
        out_path = os.path.splitext(example_file_path)[0] + "_sep_test.csv"
        if os.path.exists(out_path):
            os.remove(out_path)
        df = pandatools.superReadFile(example_file_path)
        df.to_csv(out_path, sep=SEPARATORS[sep], index=False)
        try:
            assert out_path not in dialog.df_manager.file_paths
            idx = dialog.comboBoxSeparator.findText(sep)
            assert idx >= 0
            dialog.comboBoxSeparator.setCurrentIndex(idx)
            dialog.set_file_path(out_path)
            dialog.checkBoxParseDates.setChecked(False)
            dialog.checkBoxTrimSpaces.setChecked(False)
            dialog.checkBoxScrubLinebreaks.setChecked(False)
            dialog.checkBoxHasHeaders.setChecked(True)
            dialog.execute()
            assert out_path in dialog.df_manager.file_paths
        finally:
            os.remove(out_path)

    def test_extensions(self):
        pass

    def test_encoding(self):
        pass
