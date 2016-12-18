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
import pytest
from tests.main import MainTestClass
from core.views.actions.fields_edit import FieldsEditDialog, DataFrameModel


class TestFieldsEditDialog(MainTestClass):

    @pytest.fixture
    def dialog(self, qtbot, example_file_path) -> FieldsEditDialog:

        dm = DataFrameModel()
        dm.setDataFrameFromFile(example_file_path)
        dialog = FieldsEditDialog(dm)
        dialog.show()
        qtbot.add_widget(dialog)
        return dialog

    def test_parse_dates(self, dialog: FieldsEditDialog):
        """
        Makes sure the Parse Dates action is connected and
        propagates changes to the view correctly.
        :param dialog:
        :return: None
        """
        model = dialog.dfmodel
        df = model.dataFrame()
        col = 'sample_date_column_name'
        df.loc[:, col] = '2016-10-01'
        assert df[col].dtype == 'object'
        model.dataChanged.emit()

        items = dialog.fmodel.findItems(col)
        assert items
        item = items[0]
        dtype = dialog.fmodel.item(item.row(), 2)
        assert dtype.text() == 'object'

        dialog.btnParseDates.click()

        items = dialog.fmodel.findItems(col)
        assert items
        item = items[0]
        dtype = dialog.fmodel.item(item.row(), 2)
        assert 'datetime' in dtype.text()








