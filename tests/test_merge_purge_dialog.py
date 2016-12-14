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
        model = dialog.df_manager.get_model(example_file_path)
        df = model.dataFrame()
        columns = df.columns.tolist()
        check = columns[:2]

        left_model = dialog.sortOnLeftView.model()
        for col in check:
            idx = left_model.findText(col)
            assert idx >= 0
            left_model.select


    def test_dedupe(self, dialog: MergePurgeDialog, example_file_path):
        pass

    def test_merge(self, dialog: MergePurgeDialog, example_file_path):
        pass

    def test_purge(self, dialog: MergePurgeDialog, example_file_path):
        pass