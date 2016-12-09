import os
from functools import partial
from core.compat import QtGui, QtCore
from qtpandas.models.DataFrameModel import DataFrameModel
from core.ui.actions.merge_purge_ui import Ui_MergePurgeDialog
from core.views.actions.push_grid import PushGridHandler
from core.models.actions import FileViewModel
from core.views.file import FileTableWindow


class MergePurgeDialog(QtGui.QDialog, Ui_MergePurgeDialog):
    signalMergeFileOpened = QtCore.Signal(DataFrameModel)
    signalSFileOpened = QtCore.Signal(DataFrameModel)

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._suppress_files = {}
        self._merge_files = {}
        self._merge_view_model = FileViewModel()
        self._suppress_view_model = FileViewModel()
        self._file_table_windows = {}

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

        self.signalMergeFileOpened.connect(self._add_merge_file)
        merge_file_func = partial(self.open_file, model_signal=self.signalMergeFileOpened)
        self.btnAddMergeFile.clicked.connect(merge_file_func)
        self.btnBrowseMergeFile.clicked.connect(merge_file_func)
        self.btnDeleteMergeFile.clicked.connect(partial(self._remove_file, self.mergeFileTable))
        self.btnEditMergeFile.clicked.connect(partial(self._open_edit_file_window, self.mergeFileTable, self._merge_files))
        self.mergeFileTable.setModel(self._merge_view_model)

        self.signalSFileOpened.connect(self._add_suppress_file)
        sfile_func = partial(self.open_file, model_signal=self.signalSFileOpened)
        self.btnEditSFile.clicked.connect(partial(self._open_edit_file_window, self.sFileTable, self._suppress_files))
        self.btnDeleteSFile.clicked.connect(partial(self._remove_file, self.sFileTable))
        self.btnAddSFile.clicked.connect(sfile_func)
        self.btnBrowseSFile.clicked.connect(sfile_func)
        self.sFileTable.setModel(self._suppress_view_model)

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

    def open_file(self, file_names=None, model_signal=None):
        if file_names is None:
            file_names = QtGui.QFileDialog.getOpenFileNames()
        if file_names:
            file_names = file_names[0]
        for f in file_names:
            try:
                if os.path.exists(f):
                    model = DataFrameModel()
                    model.setDataFrameFromFile(f)
                    if model_signal is not None:
                        model_signal.emit(model)
            except Exception as e:
                print(e)

    @QtCore.Slot(DataFrameModel)
    def _add_merge_file(self, model: DataFrameModel):
        file_path = model.filePath
        model.enableEditing(True)
        self._merge_files.update({file_path:model})
        self._merge_view_model.appendDataFrameModel(model)
        self.mergeFileTable.setColumnWidth(0, 500)

    @QtCore.Slot(DataFrameModel)
    def _add_suppress_file(self, model: DataFrameModel):
        file_path = model.filePath
        model.enableEditing(True)
        self._suppress_files.update({file_path:model})
        self._suppress_view_model.appendDataFrameModel(model)
        self.sFileTable.setColumnWidth(0, 500)

    def _remove_file(self, view, indexes=None):
        if indexes is None:
            indexes = [x.row() for x in view.selectedIndexes()]
        model = view.model()
        for idx in indexes:
            model.takeRow(idx)

    def _open_edit_file_window(self, view, models):
        idx = view.selectedIndexes()[0]
        vmodel = view.model()
        vitem = vmodel.item(idx.row())
        model = models.get(vitem.text())

        fp = model.filePath
        try:
            self._file_table_windows[fp].show()
        except KeyError:
            self._file_table_windows[fp] = FileTableWindow(model)
            self._file_table_windows[fp].show()








