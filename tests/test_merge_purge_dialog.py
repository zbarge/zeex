import os
import pytest
from tests.main import MainTestClass
from core.views.actions.merge_purge import MergePurgeDialog, DataFrameModelManager, DataFrameModel
from core.compat import QtCore, QtTest, QtGui


class TestMergePurgeDialog(MainTestClass):

    @pytest.fixture
    def dialog(self, qtbot, example_file_path) -> MergePurgeDialog:
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

    def test_sorting(self, dialog: MergePurgeDialog, example_file_path):
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

    def test_dedupe(self, dialog: MergePurgeDialog, example_file_path):
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

    def test_merge(self, dialog: MergePurgeDialog, example_file_path):

        # Cut the example file in half for our merge simulation.
        orig_df = dialog.df_manager.get_frame(example_file_path)
        merge_path = os.path.splitext(example_file_path)[0] + "_merge_me.csv"
        check_path = dialog.destPathLineEdit.text()

        # Split the data based on construction type.
        df1 = orig_df.loc[orig_df.loc[:, 'construction'].isin(['Wood']), :]
        df2 = orig_df.loc[~orig_df.loc[:, 'construction'].isin(['Wood']), :]

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
            for p in [merge_path, check_path]:
                if os.path.exists(p):
                    os.remove(p)

    def test_purge(self, dialog: MergePurgeDialog, example_file_path):

        # Cut the example file in half for our merge simulation.
        orig_df = dialog.df_manager.get_frame(example_file_path)
        kill_path = os.path.splitext(example_file_path)[0] + "_kill_me.csv"
        check_path = dialog.destPathLineEdit.text()

        # Split/export the data based on construction type.
        df_kill = orig_df.loc[orig_df.loc[:, 'construction'].isin(['Wood']), :]
        df_kill.to_csv(kill_path)

        # Open the kill_path with the dialog's open file function.
        dialog.open_file(file_names=[kill_path], model_signal=dialog.signalSFileOpened)
        assert kill_path in dialog.df_manager.file_paths

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
            for p in [kill_path, check_path]:
                if os.path.exists(p):
                    os.remove(p)
