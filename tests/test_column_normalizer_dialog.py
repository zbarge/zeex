import pytest
from tests.main import MainTestClass
from core.views.actions.normalize import ColumnNormalizerDialog, DataFrameModel
import core.utility.pandatools as pandatools
from core.compat import QtGui, QtCore
import os


class TestColumnNormalizerDialog(MainTestClass):

    @pytest.fixture
    def dialog(self, qtbot, example_file_path) -> ColumnNormalizerDialog:

        dm = DataFrameModel()
        dm.setDataFrameFromFile(example_file_path)
        dialog = ColumnNormalizerDialog(dm)
        dialog.show()
        qtbot.add_widget(dialog)
        return dialog

    def test_set_case(self, dialog: ColumnNormalizerDialog):
        check_box = dialog.checkBoxSetCase
        combo_box = dialog.comboBoxSetCase
        df = dialog.df_model.dataFrame()

        lower, upper, proper = [c for c in df.columns if str(df[c].dtype) == 'object'][:3]
        options = {'lower': lower, 'upper': upper, 'proper': proper}
        col_model = dialog.listViewColumns.model()

        # Make sure cases are set to something different.
        df.loc[:, lower] = df.loc[:, lower].str.upper()
        df.loc[:, upper] = df.loc[:, upper].str.title()
        df.loc[:, proper] = df.loc[:, proper].str.lower()
        assert check_box.isVisible()
        assert check_box.isCheckable()
        assert combo_box.isVisible()

        for case, col in options.items():

            dialog.uncheck_all()
            [c.setCheckState(QtCore.Qt.Checked) for c in col_model.get_items() if c.text() == col]
            case_id = combo_box.findText(case)
            assert col_model.get_items_checked()
            assert not df.loc[:, col].dropna().empty
            assert case_id >= 0

            combo_box.setCurrentIndex(case_id)
            check_box.setChecked(True)
            dialog.execute()
            df_check = dialog.df_model.dataFrame()

            for i in df_check.loc[:, col].unique():
                assert pandatools.case_map[case](i) == i

    def test_trim_spaces(self, dialog:ColumnNormalizerDialog):
        col = 'SAMPLE_COLUMN'
        bad_text = '    BETTER BE TRIMMED         '
        good_text = bad_text.strip()
        check_box = dialog.checkBoxTrimSpaces
        col_model = dialog.listViewColumns.model()
        df = dialog.df_model.dataFrame()
        df.loc[:, col] = bad_text
        dialog.df_model.dataChanged.emit()

        dialog.uncheck_all()
        check_box.setChecked(True)
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() == col]

        assert check_box.isVisible()
        assert check_box.isCheckable()
        assert col_model.get_items_checked()

        dialog.execute()
        df_check = dialog.df_model.dataFrame()

        for i in df_check.loc[:, col].unique():
            assert i == good_text

    def test_split_columns(self, dialog:ColumnNormalizerDialog):
        col_model = dialog.listViewColumns.model()
        df = dialog.df_model.dataFrame()
        col = 'SAMPLE_COLUMN_SPLIT'
        df.loc[:, col] = 'Oceanside, CA 92058'
        orig_cols = df.columns.tolist()
        dialog.df_model.dataChanged.emit()

        dialog.uncheck_all()
        dialog.checkBoxMergeOrSplit.setChecked(True)
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() == col]
        dialog.comboBoxMergeOrSplit.setCurrentIndex(dialog.comboBoxMergeOrSplit.findText('Split'))
        dialog.lineEditMergeOrSplitSep.setText(', ')
        assert dialog.comboBoxMergeOrSplit.currentText() == 'Split'
        assert dialog.comboBoxMergeOrSplit.isVisible()
        assert dialog.lineEditMergeOrSplitSep.isVisible()
        assert dialog.checkBoxMergeOrSplit.isVisible()
        assert dialog.checkBoxMergeOrSplit.isCheckable()

        dialog.execute()
        df_check = dialog.df_model.dataFrame()
        new_cols = [c for c in df_check.columns if not c in orig_cols]

        for i in df_check.index:
            info = [df_check.iloc[i][c] for c in new_cols]
            assert 'Oceanside' in info
            assert 'CA' in info
            assert '92058' in info

    def test_remove_special_characters(self, dialog:ColumnNormalizerDialog):
        col_model = dialog.listViewColumns.model()
        df = dialog.df_model.dataFrame()
        col = 'SAMPLE_COL_REMOVE_SPEC_CHARS'
        keeps = [' ']
        bad_text = 'What$s U$p B55R)**o'
        good_text = ''.join(e for e in bad_text if e.isalnum() or e in keeps)
        df.loc[:, col] = bad_text
        dialog.df_model.dataChanged.emit()

        dialog.uncheck_all()
        dialog.checkBoxRemoveSpecialChars.setChecked(True)
        dialog.lineEditRemoveSpecialCharsKeeps.setText(' ')
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() == col]

        assert dialog.checkBoxRemoveSpecialChars.isVisible()
        assert dialog.checkBoxMergeOrSplit.isCheckable()
        assert dialog.lineEditRemoveSpecialCharsKeeps.isVisible()

        dialog.execute()
        df_check = dialog.df_model.dataFrame()

        for i in df_check.index:
            assert df_check.iloc[i][col] == good_text

    def test_scrub_linebreaks(self, dialog:ColumnNormalizerDialog):
        col_model = dialog.listViewColumns.model()
        df = dialog.df_model.dataFrame()
        col = 'SAMPLE_COL_REMOVE_SPEC_CHARS'
        keeps = [' ']
        bad_text = "Dear John,\n How's life?"
        good_text = pandatools.remove_line_breaks(bad_text)
        df.loc[:, col] = bad_text
        dialog.df_model.dataChanged.emit()

        dialog.uncheck_all()
        dialog.checkBoxScrubLineBreaks.setChecked(True)
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() == col]

        assert dialog.checkBoxScrubLineBreaks.isVisible()

        dialog.execute()
        df_check = dialog.df_model.dataFrame()
        assert '\n' in bad_text
        assert '\n' not in good_text
        for i in df_check.index:
            assert df_check.iloc[i][col] == good_text


    def test_replace_spaces(self, dialog:ColumnNormalizerDialog):
        col_model = dialog.listViewColumns.model()
        df = dialog.df_model.dataFrame()
        col = 'SAMPLE_COL_REPLACE_SPACES'
        replace_with = '_'
        df.loc[:, col] = 'I shouldnt have any more spaces after this is done'
        dialog.df_model.dataChanged.emit()

        dialog.uncheck_all()
        dialog.checkBoxReplaceSpaces.setChecked(True)
        dialog.lineEditReplaceSpaces.setText(replace_with)
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() == col]

        assert dialog.checkBoxReplaceSpaces.isVisible()
        assert dialog.checkBoxReplaceSpaces.isCheckable()

        dialog.execute()
        df2 = dialog.df_model.dataFrame()
        for i in df2.index:
            return_value = df2.iloc[i][col]
            assert ' ' not in return_value
            assert replace_with in return_value

    @pytest.mark.parametrize('how', ['any','all'])
    def test_drop_na(self, dialog:ColumnNormalizerDialog, how:str):
        col_model = dialog.listViewColumns.model()
        df = dialog.df_model.dataFrame()
        col = 'SAMPLE_COL_DROP_NA'
        df.loc[:, col] = ''
        dialog.df_model.dataChanged.emit()

        dialog.uncheck_all()
        dialog.checkBoxDropFillNA.setChecked(True)
        dialog.comboBoxDropFillNA.setCurrentIndex(dialog.comboBoxDropFillNA.findText('Drop NA'))
        dialog.comboBoxDropFillNAHow.setCurrentIndex(dialog.comboBoxDropFillNAHow.findText(how))
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() == col]

        assert dialog.checkBoxDropFillNA.isVisible()
        assert dialog.checkBoxDropFillNA.isCheckable()
        assert dialog.comboBoxDropFillNA.currentText() == 'Drop NA'
        assert dialog.comboBoxDropFillNA.isVisible()
        assert dialog.comboBoxDropFillNAHow.currentText() == how
        assert dialog.comboBoxDropFillNAHow.isVisible()
        assert col_model.get_items_checked()

        dialog.execute()
        df2 = dialog.df_model.dataFrame()
        if how == 'any':
            assert df2.empty, "Should've dropped all records since the column was set to an empty string."
        else:
            assert df2.index.size == df.index.size, "Should've lost no records with how = 'all'"

    def test_merge_columns(self, dialog:ColumnNormalizerDialog):
        pass

    def test_fill_na(self, dialog:ColumnNormalizerDialog):
        pass

    def test_settings_io(self, dialog:ColumnNormalizerDialog):
        df = dialog.df_model.dataFrame()
        cols = df.columns.tolist()
        col_model = dialog.listViewColumns.model()
        file_path = os.path.splitext(dialog.df_model.filePath)[0] + "_normalize_config.ini"
        if os.path.exists(file_path):
            os.remove(file_path)
        for cbox in dialog.findChildren(QtGui.QCheckBox):
            cbox.setChecked(True)
        [c.setCheckState(QtCore.Qt.Checked)
         for c in col_model.get_items()
         if c.text() in cols]
        orig_check_size = len(col_model.get_items_checked())
        assert col_model.get_items_checked()
        assert dialog.checkBoxDropFillNA.isChecked()

        dialog.export_settings(to=file_path)
        dialog.uncheck_all()

        assert os.path.exists(file_path)

        try:
            assert not dialog.checkBoxDropFillNA.isChecked()
            assert not col_model.get_items_checked()

            dialog.import_settings(filename=file_path)

            for cbox in dialog.findChildren(QtGui.QCheckBox):
                assert cbox.isChecked()
            assert len(col_model.get_items_checked()) == orig_check_size
        finally:
            os.remove(file_path)
















