from functools import partial
from core.compat import QtGui, QtCore
from qtpandas.models.DataFrameModel import DataFrameModel

from core.models.fieldnames import FieldRenameModel
from core.ui.actions.merge_purge_ui import Ui_MergePurgeDialog
from core.views.actions.push_grid import PushGridHandler



class MergePurgeDialog(QtGui.QDialog, Ui_MergePurgeDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._suppress_files = {}
        self._merge_files = {}

    def configure(self, settings: dict = None) -> bool:
        sort_model   = settings.get('sort_model', [])
        dedupe_model = settings.get('dedupe_model', [])
        source_path  = settings.get('source_path', None)
        dest_path    = settings.get('dest_path', None)

        sort_asc = QtGui.QStandardItemModel()
        sort_asc.appendRow(QtGui.QStandardItem('True'))
        sort_asc.appendRow(QtGui.QStandardItem('False'))

        self.sortAscHandler = PushGridHandler(left_model=sort_asc, left_view=self.sortAscLeftView,
                                              left_button=self.sortAscLeftButton,
                                              left_delete=False, right_model=None,
                                              right_view=self.sortAscRightView,
                                              right_button=self.sortAscRightButton)

        self.sortOnHandler = PushGridHandler(left_model=sort_model, left_view=self.sortOnLeftView,
                                             left_button=self.sortOnLeftButton,
                                             left_delete=True, right_model=None,
                                             right_view=self.sortOnRightView,
                                             right_button=self.sortOnRightButton)

        self.dedupeOnHandler = PushGridHandler(left_model=dedupe_model, left_view=self.dedupeOnLeftView,
                                               left_button=self.dedupeOnLeftButton,
                                               left_delete=True, right_model=None,
                                               right_view=self.dedupeOnRightView,
                                               right_button=self.dedupeOnRightButton)

        if source_path is not None:
            self.sourcePathLineEdit.setText(source_path)

        if dest_path is not None:
            self.destPathLineEdit.setText(dest_path)

        merge_file_func = partial(self.open_file, self.mergeFileLineEdit, self._add_merge_file)
        sfile_func = partial(self.open_file, self.sFileLineEdit, self._add_suppress_file)
        self.btnAddMergeFile.clicked.connect(merge_file_func)
        self.btnAddSFile.clicked.connect(sfile_func)


    def create_dedupe_model(self, columns: list):
        columns = list(columns)
        model = QtGui.QStandardItemModel()

        for idx, col in enumerate(columns):
            item = QtGui.QStandardItem(col)
            for order in ['asc', 'desc']:
                oitem = QtGui.QStandardItem(order)
                item.appendRow(oitem)
            model.appendRow(item)
        return model

    def create_sort_model(self, columns: list):
        columns = list(columns)
        model = QtGui.QStandardItemModel()
        for idx, col in enumerate(columns):
            item = QtGui.QStandardItem(col)
            model.appendRow(item)
        return model

    def open_file(self, line_edit, callback=None):
        file_names = QtGui.QFileDialog.getOpenFileNames()

        for f in file_names:
            line_edit.setText(f[0])
            if callback is not None:
                callback()

    def get_file_preview_model(self, *args, **kwargs):
        file_path = kwargs['file_path']
        file_type = kwargs['file_type']
        df_columns = kwargs['columns']
        header = ['filepath', 'columns', 'edit']
        model = QtGui.QStandardItemModel()
        colbox = QtGui.QComboBox(list(df_columns))
        checkbox = QtGui.QCheckBox()
        model.setItem(0, 0, file_path)
        model.setItem(0, 1, colbox)
        model.setItem(0, 2, checkbox)
        model.setHorizontalHeaderLabels(header)
        return model

    def _add_merge_file(self):
        file_path = self.mergeFileLineEdit.text()
        model = DataFrameModel()
        model.setDataFrameFromFile(file_path)
        model.enableEditing(True)
        self._suppress_files.update({file_path:model})


    def _add_suppress_file(self):
        file_path = self.sFileLineEdit.text()
        model = DataFrameModel()
        model.setDataFrameFromFile(file_path)
        model.enableEditing(True)
        df = model._dataFrame
        self._merge_files.update({file_path:model})
        dtype_model = model.columnDtypeModel()
        self.sFileTable.setModel(dtype_model)

        rename_model = FieldRenameModel()
        for row_idx, col in enumerate(sorted(df.columns)):
            item = QtGui.QStandardItem(col)
            rename = item.clone()

            item.setCheckable(True)
            rename_model.setItem(row_idx, 0, item)
            rename_model.setItem(row_idx, 1, rename)

        self.sRenameTable.setModel(rename_model)


