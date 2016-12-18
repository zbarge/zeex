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
import shutil
import pytest
from core.views.project.main import ProjectMainWindow
from core.views.main import ZeexMainWindow
from core.views.settings import SettingsDialog, SettingsINI
from tests.main import MainTestClass
from core.compat import QtCore, QtTest, QtGui


class TestProjectMainWindow(MainTestClass):

    @pytest.fixture
    def window(self, qtbot, project_settings_ini) -> ProjectMainWindow:
        window = ProjectMainWindow(project_settings_ini)
        window.show()
        qtbot.addWidget(window)
        return window

    def test_project_settings(self, qtbot, window: ProjectMainWindow):
        dialog = window.dialog_settings
        window.actionPreferences.trigger()
        assert dialog.isVisible()
        dialog.close()
        window.close()


    def test_merge_purge_dialog(self, qtbot, window: ProjectMainWindow, example_file_path):
        file_base, ext = os.path.splitext(os.path.basename(example_file_path))
        dialog = window.dialog_merge_purge
        model = window.df_manager.read_file(example_file_path)
        df = model.dataFrame()
        columns = df.columns.tolist()
        caught_ascending = False
        caught_left = 0

        window.open_merge_purge_dialog(model=model)
        assert dialog.isVisible()
        assert dialog.sourcePathLineEdit.text() == example_file_path
        assert file_base in dialog.destPathLineEdit.text()

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
        window.close()

    def test_export_dialog(self, qtbot, window: ProjectMainWindow, example_file_path):
        """
        Runs a test against the ProjectMainWindow's export dialog to make sure
        all the buttons are connected properly and that the

        :param qtbot:
        :param window:
        :param example_file_path:
        :return:
        """

        #Read the example file so the df_manager has it.
        window.df_manager.read_file(example_file_path)

        # Make & check the expected export path
        # to make sure it doesnt exist before we execute.
        example_export_path = os.path.splitext(example_file_path)[0] + "_export_test.csv"
        if os.path.exists(example_export_path):
            os.remove(example_export_path)
        # Confirm we have no exported file.
        assert not os.path.exists(example_export_path)

        window.open_export_dialog()
        dialog = window.dialog_export
        #qtbot.addWidget(dialog)
        current_idx = dialog.comboBoxSource.findText(example_file_path)
        comma_idx = dialog.comboBoxSeparator.findText("Comma")
        encode_idx = dialog.comboBoxEncoding.findText("UTF-8")

        assert dialog is not None
        assert dialog.isVisible()
        assert dialog.df_manager.file_paths
        assert dialog.df_manager.file_paths == window.df_manager.file_paths
        assert current_idx >= 0
        assert comma_idx >= 0
        assert encode_idx >= 0

        dialog.comboBoxSource.setCurrentIndex(current_idx)
        dialog.comboBoxSeparator.setCurrentIndex(comma_idx)
        dialog.comboBoxEncoding.setCurrentIndex(encode_idx)
        dialog.lineEditDestination.setText(example_export_path)

        assert dialog.comboBoxSource.currentText() == example_file_path
        dialog.buttonBox.accepted.emit()
        assert os.path.exists(example_export_path)
        dialog.close()

    def test_import_dialog(self, qtbot, window: ProjectMainWindow, example_file_path):
        """
        Semi irrelevant feature as it would be used in rare cases. When there's an error reading
        a file. Adding super basic tests - I should probably recreate the code for the object
        and everything, though.
        :param qtbot:
        :param window:
        :param example_file_path:
        :return: None
        """
        assert os.path.exists(example_file_path)
        assert example_file_path not in window.df_manager.file_paths
        window.open_import_dialog()
        assert window.dialog_import.isVisible()
        window.dialog_import.close()






































