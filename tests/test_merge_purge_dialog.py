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
import pytest
from tests.main import MainTestClass
from core.views.actions.merge_purge import MergePurgeDialog, DataFrameModelManager, DataFrameModel
from core.compat import QtCore, QtTest, QtGui



class TestMergePurgeDialog(MainTestClass):
    """
    Core tests for the MergePurgeDialog.
    """

    @pytest.fixture
    def dialog(self, qtbot, example_file_path) -> MergePurgeDialog:
        """
        Creates a MergePurgeDialog with a sample file loaded.

        :param qtbot:
        :param example_file_path:
        :return:
        """
        manager = DataFrameModelManager()
        manager.read_file(example_file_path)
        dialog = MergePurgeDialog(manager)
        dialog.set_source_model(manager.get_model(example_file_path), configure=True)
        qtbot.addWidget(dialog)
        check_path = dialog.destPathLineEdit.text()
        rpt_path = os.path.splitext(check_path)[0] + "_report.txt"
        for p in [check_path, rpt_path]:
            if os.path.exists(p):
                os.remove(p)
        return dialog

    def test_general_config(self, dialog: MergePurgeDialog, example_file_path):
        """
        Checks general configuration of the MergePurgeDialog
        to make sure that buttons/views/models are set up as expected.

        :param dialog:
        :param example_file_path:
        :return:
        """
        current_source = dialog.sourcePathLineEdit.text()
        current_dest = dialog.destPathLineEdit.text()
        caught_ascending = False
        caught_left = 0
        model = dialog.source_model
        columns = model.dataFrame().columns.tolist()

        assert isinstance(model, DataFrameModel)
        assert os.path.exists(current_source)
        source_base, source_ext = os.path.splitext(os.path.dirname(current_source))
        assert source_base in current_dest, "Default destination path should derive from the source."
        if os.path.exists(current_dest):
            os.remove(current_dest)

        for list_view in dialog.findChildren(QtGui.QListView):
            model = list_view.model()
            if model:
                items = [model.item(i).text() for i in range(model.rowCount())]
                object_name = list_view.objectName().lower()

                if object_name == 'sortascleftview':
                    assert 'True' in items
                    assert 'False' in items
                    caught_ascending = True

                if 'left' in object_name:

                    caught_left += 1
                    assert items

                    if len(items) > 5:
                        for i in items:
                            assert i in columns

        assert caught_ascending
        assert caught_left >= 3
        dialog.close()

    def test_sorting(self, dialog: MergePurgeDialog, example_file_path):
        """
        Runs a basic sorting scenario against the MergePurgeDialog and
        confirms that the exported data has been sorted according to the settings.

        :param dialog:
        :param example_file_path:
        :return:
        """
        model = dialog.df_manager.get_model(example_file_path)
        check_path = dialog.destPathLineEdit.text()
        df = model.dataFrame()
        columns = df.columns.tolist()
        check = 'policyid'
        check_not = 'fook_yoo'
        left_model = dialog.sortOnLeftView.model()
        right_model = dialog.sortOnRightView.model()

        # Make sure the item doesnt exist on the right model
        found_right = right_model.findItems(check)
        assert not found_right

        # Make sure the item DOES exist on the left model.
        items = left_model.findItems(check)
        assert items
        item = items[0]
        dialog.sortOnLeftView.setCurrentIndex(item.index())

        # Push column left->right and ensure the item popped over.
        dialog.sortOnRightButton.click()
        found_right = right_model.findItems(check)
        assert found_right
        found_wrong = right_model.findItems(check_not)
        assert not found_wrong

        #Get the sort order (True) for ascending and pop that over as well
        orders = dialog.sortAscLeftView.model().findItems("True")
        assert orders
        order = orders[0]
        dialog.sortAscLeftView.setCurrentIndex(order.index())
        dialog.sortAscRightButton.click()

        #Confirm the sort order popped over.
        orders = dialog.sortAscRightView.model().findItems("True")
        assert orders

        #Sort the opposite of how the dialog will sort.
        df.sort_values(check, ascending=False, inplace=True)

        #Make a copy to use for verification.
        verify_not_sort = df.copy()

        #Execute the simulation.
        dialog.btnExecute.click()

        assert os.path.exists(check_path)
        check_model = dialog.df_manager.read_file(check_path)
        check_df = check_model.dataFrame()
        assert check_df.index.size == df.index.size, "Sorting shouldnt/gain lose records."

        last = 0
        bads = []
        # Every item should be greater than the last.
        # Every item should also not be equal to the original.
        for i in check_df.index.tolist():
            check_entry = check_df.iloc[i]
            verify_not_entry = verify_not_sort.iloc[i]
            if check_entry[check] == verify_not_entry[check]:
                bads.append(check_entry[check])
            assert check_entry[check] >= last
            last = check_entry[check]
        assert len(bads) < 0.1 * check_df.index.size
        os.remove(check_path)
        dialog.close()

    def test_dedupe(self, dialog: MergePurgeDialog, example_file_path):
        """
        Runs a basic deduplication scenario against the MergePurgeDialog
        and confirms that the exported data has been deduplicated according
        to the settings.

        :param dialog:
        :param example_file_path:
        :return:
        """
        dfmodel = dialog.df_manager.get_model(example_file_path)
        column = 'construction'
        compare_df = dfmodel.dataFrame().copy()
        compare_df.drop_duplicates(column, inplace=True)
        compare_size = compare_df.index.size
        assert compare_size < dfmodel.dataFrame().index.size

        for view in dialog.findChildren(QtGui.QListView):
            if 'right' in view.objectName().lower():
                model = view.model()
                assert model is None or model.rowCount() == 0

        left_model = dialog.dedupeOnLeftView.model()
        col_match = left_model.findItems(column)
        assert col_match
        col_match = col_match[0]
        dialog.dedupeOnLeftView.setCurrentIndex(col_match.index())
        dialog.dedupeOnRightButton.click()
        pushed_match = dialog.dedupeOnRightView.model().findItems(column)
        assert pushed_match

        compare_path = dialog.destPathLineEdit.text()
        assert not os.path.exists(compare_path)
        dialog.btnExecute.click()
        assert os.path.exists(compare_path)

        dialog.df_manager.read_file(compare_path)
        df = dialog.df_manager.get_frame(compare_path)
        assert df.index.size == compare_size

        final_check_df = df.loc[df.loc[:,'policyid'].isin(compare_df.loc[:, 'policyid'].unique()), :]
        assert final_check_df.index.size == df.index.size
        dialog.close()

    def test_merge(self, dialog: MergePurgeDialog, example_file_path):
        """
        Runs a basic merge simulation against the MergePurgeDialog and
        confirms that the exported file has been properly merged.

        :param dialog:
        :param example_file_path:
        :return:
        """

        # Cut the example file in half for our merge simulation.
        orig_df = dialog.df_manager.get_frame(example_file_path)
        merge_path = os.path.splitext(example_file_path)[0] + "_merge_me.csv"
        check_path = dialog.destPathLineEdit.text()
        report_path = os.path.splitext(check_path)[0] + "_report.txt"

        # Split the data based on construction type.
        split_mask = orig_df.loc[:, 'construction'].isin(['Wood'])
        df1 = orig_df.loc[split_mask, :]
        df2 = orig_df.loc[~split_mask, :]

        assert df1.index.size != df2.index.size
        df2.to_csv(merge_path)

        # Register the source file with the first split
        dialog.df_manager.update_file(example_file_path, df1, notes="Took first half")
        dialog.open_file(file_names=[merge_path], model_signal=dialog.signalMergeFileOpened)
        assert merge_path in dialog.df_manager.file_paths

        # Make sure merge path made it into the MergeView's model
        table_model = dialog.mergeFileTable.model()
        items = table_model.findItems(merge_path)
        assert items

        dialog.btnExecute.click()

        try:
            assert os.path.exists(check_path)
            check_model = dialog.df_manager.read_file(check_path)
            check_df = check_model.dataFrame()
            assert check_df.index.size == orig_df.index.size, "Expected the merged dataframe \
                                                               to be the same size as the original."
            chmask = orig_df.loc[:, 'policyid'].isin(check_df.loc[:, 'policyid'].unique())
            check_df2 = orig_df.loc[chmask, :]
            assert check_df2.index.size == orig_df.index.size, "Expected every policyid in the original\
                                                                frame to exist in the merged one"
        finally:
            for p in [merge_path, check_path, report_path]:
                if os.path.exists(p):
                    os.remove(p)
        dialog.close()

    @pytest.mark.parametrize("overwrite", [True, False])
    def test_merge_gathered(self, dialog: MergePurgeDialog, example_file_path, overwrite):
        """
        Runs a gathered merge simulation against the MergePurgeDialog and
        confirms that the exported file has been properly merged along
        with fields gathered (or not if overwrite is False).

        :param dialog:
        :param example_file_path:
        :param overwrite (bool)
            Tests what should or shouldn't happen with an overwrite.
        :return:
        """

        # Cut the example file in half for our merge simulation.
        orig_df = dialog.df_manager.get_frame(example_file_path)
        merge_path = os.path.splitext(example_file_path)[0] + "_merge_me.csv"
        check_path = dialog.destPathLineEdit.text()
        report_path = os.path.splitext(check_path)[0] + "_report.txt"
        primary_key = 'policyid'
        check_column = 'construction'
        orig_value = 'Wood'
        check_value = 'Fook Yoo Hookayy'

        # Copy the wood segment and change the check_value.
        split_mask = orig_df.loc[:, check_column].isin([orig_value])
        update_df = orig_df.loc[split_mask, :]
        update_df.loc[:, check_column] = check_value

        # Export the updated segment to our merge_path
        update_df.to_csv(merge_path)

        dialog.open_file(file_names=[merge_path], model_signal=dialog.signalMergeFileOpened)
        assert merge_path in dialog.df_manager.file_paths

        # Make sure merge path made it into the MergeView's model
        table_model = dialog.mergeFileTable.model()
        items = table_model.findItems(merge_path)
        assert items

        # Tell the dialog we want to gather the check_column's data.
        items = dialog.gatherFieldsListViewLeft.model().findItems(check_column)
        assert items
        item = items[0]
        dialog.gatherFieldsListViewLeft.setCurrentIndex(item.index())
        dialog.gatherFieldsButtonRight.click()
        assert dialog.gatherFieldsListViewRight.model().findItems(check_column)

        # Set the primary key
        keys = dialog.primaryKeyComboBox.model().findItems(primary_key)
        assert keys
        key = keys[0]
        dialog.primaryKeyComboBox.setCurrentIndex(key.row())
        assert dialog.primaryKeyComboBox.currentText() == primary_key

        # Set the overwrite flag & run
        dialog.gatherFieldsOverWriteCheckBox.setChecked(overwrite)
        dialog.btnExecute.click()

        try:
            assert os.path.exists(check_path)
            check_model = dialog.df_manager.read_file(check_path)
            check_df = check_model.dataFrame()
            assert check_df.index.size == orig_df.index.size, "Expected the merged dataframe \
                                                               to be the same size as the original."

            for value in [orig_value, check_value]:
                mask = check_df.loc[:, check_column].isin([value])
                val_df = check_df.loc[mask, :]

                if value is orig_value:

                    if overwrite:
                        assert val_df.empty, "These records should have been overwritten.".format(val_df.index.size)
                    else:
                        assert val_df.index.size == update_df.index.size, "These records should not have been updated."

                elif value is check_value:

                    if overwrite:
                        assert val_df.index.size == update_df.index.size
                    else:
                        assert val_df.empty, "overwrite is false so this should be empty..."
        finally:
            for p in [merge_path, check_path, report_path]:
                if os.path.exists(p):
                    os.remove(p)
        dialog.close()

    def test_purge(self, dialog: MergePurgeDialog, example_file_path):
        """
        Runs a basic purge simulation against the MergePurgeDialog and confirms
        that the exported data has been purged according to the settings.

        :param dialog: (MergePurgeDialog)
        :param example_file_path: (str)
            the file path to the sample florida insurance policy data.
        :return:
        """

        # Cut the example file in half for our merge simulation.
        orig_df = dialog.df_manager.get_frame(example_file_path)
        kill_path = os.path.splitext(example_file_path)[0] + "_kill_me.csv"
        check_path = dialog.destPathLineEdit.text()
        report_path = os.path.splitext(check_path)[0] + "_report.txt"

        # Split/export the data based on construction type.
        df_kill = orig_df.loc[orig_df.loc[:, 'construction'].isin(['Wood']), :]
        df_kill.to_csv(kill_path)

        # Open the kill_path with the dialog's open file function.
        dialog.open_file(file_names=[kill_path], model_signal=dialog.signalSFileOpened)
        assert kill_path in dialog.df_manager.file_paths
        assert df_kill.index.size > 0

        # Make sure merge path made it into the MergeView's model
        table_model = dialog.sFileTable.model()
        items = table_model.findItems(kill_path)
        assert items

        # Push a dedupe-on field to use for suppression.
        items = dialog.dedupeOnLeftView.model().findItems("policyid")
        assert items
        item = items[0]
        dialog.dedupeOnLeftView.setCurrentIndex(item.index())
        dialog.dedupeOnRightButton.click()

        dialog.btnExecute.click()

        try:
            assert os.path.exists(check_path)
            check_model = dialog.df_manager.read_file(check_path)
            check_df = check_model.dataFrame()
            check_size = check_df.index.size == orig_df.index.size - df_kill.index.size
            assert check_size, "Expected the purged dataframe \
                                to have lost {} records.".format(df_kill.index.size)

            check_df2 = check_df.loc[check_df.loc[:, 'construction'].isin(['Wood']), :]
            assert check_df2.empty, "Expected no records with construction in Wood."
        finally:
            for p in [kill_path, check_path, report_path]:
                if os.path.exists(p):
                    os.remove(p)
        dialog.close()
