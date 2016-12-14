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
        dialog.set_line_edit_paths(example_file_path)
        dialog.configure()
        dialog.set_source_model(manager.get_model(example_file_path))
        dialog.set_push_grid_handlers()
        qtbot.addWidget(dialog)
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
        check_path = dialog.destPathLineEdit.text()
        if os.path.exists(check_path):
            os.remove(check_path)
        model = dialog.df_manager.get_model(example_file_path)
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
        pytest.skip("TODO: make test_dedupe")

    def test_merge(self, dialog: MergePurgeDialog, example_file_path):
        pytest.skip("TODO: make test_merge")

    def test_purge(self, dialog: MergePurgeDialog, example_file_path):
        pytest.skip("TODO: make test_purge")