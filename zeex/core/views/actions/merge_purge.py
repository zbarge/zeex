import os
from functools import partial
from core.compat import QtGui, QtCore
import pandas as pd
from qtpandas.models.DataFrameModel import DataFrameModel
from core.ui.actions.merge_purge_ui import Ui_MergePurgeDialog
from core.views.actions.push_grid import PushGridHandler, PushGridWidget
from core.models.actions import FileViewModel
from core.views.file import FileTableWindow
from core.views.actions.map_grid import MapGridDialog
from core.ctrls.dataframe import DataFrameModelManager
from core.utility.widgets import create_standard_item_model


class MergePurgeDialog(QtGui.QDialog, Ui_MergePurgeDialog):
    signalMergeFileOpened = QtCore.Signal(str) # file path
    signalSFileOpened = QtCore.Signal(str) # file path
    signalExecuted = QtCore.Signal(str, str, str) # source_path, dest_path, report_path

    def __init__(self, df_manager: DataFrameModelManager, parent=None, source_model=None):
        self.df_manager = df_manager
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.source_model = source_model
        self._merge_view_model = FileViewModel()
        self._suppress_view_model = FileViewModel()
        self._suppress_files = {}
        self._merge_files = {}
        self._file_table_windows = {}
        self._field_map_grids = {}
        self._field_map_data = {}
        self.sortAscHandler = None
        self.sortOnHandler = None
        self.dedupeOnHandler = None

    def configure(self, source_path=None, dest_path=None) -> bool:

        if source_path is None:
            source_path = self.sourcePathLineEdit.text()
            assert os.path.exists(source_path), "source_path must exist: '{}'".format(source_path)
        self.set_line_edit_paths(source_path, dest_path=dest_path)
        if self.sortAscHandler is None:
            self.set_handler_sort_asc()

        self.signalMergeFileOpened.connect(self.add_merge_file)
        merge_file_func = partial(self.open_file, model_signal=self.signalMergeFileOpened)
        self.btnAddMergeFile.clicked.connect(merge_file_func)
        self.btnBrowseMergeFile.clicked.connect(merge_file_func)
        self.btnDeleteMergeFile.clicked.connect(partial(self.remove_file, self.mergeFileTable))
        self.btnEditMergeFile.clicked.connect(partial(self.open_edit_file_window, self.mergeFileTable, self._merge_files))
        self.mergeFileTable.setModel(self._merge_view_model)

        self.signalSFileOpened.connect(self.add_suppress_file)
        sfile_func = partial(self.open_file, model_signal=self.signalSFileOpened)
        self.btnEditSFile.clicked.connect(partial(self.open_edit_file_window, self.sFileTable, self._suppress_files))
        self.btnDeleteSFile.clicked.connect(partial(self.remove_file, self.sFileTable))
        self.btnAddSFile.clicked.connect(sfile_func)
        self.btnBrowseSFile.clicked.connect(sfile_func)
        self.sFileTable.setModel(self._suppress_view_model)
        self.btnMapSFields.clicked.connect(partial(self.open_field_map, self.sFileTable, self._suppress_files))
        self.btnMapMergeFields.clicked.connect(partial(self.open_field_map, self.mergeFileTable, self._merge_files))
        self.btnExecute.clicked.connect(self.execute)

    def set_source_model(self, model=None):
        if not isinstance(model, DataFrameModel):
            if model is None:
                model = self.sourcePathLineEdit.text()
            if isinstance(model, str) and os.path.exists(model):
                model = self.df_manager.read_file(model)
            else:
                raise Exception("model parameter must be a filepath or a qtpandas.models.DataFrameModel")
        self.source_model = model

    def set_line_edit_paths(self, source_path, dest_path=None):
        if dest_path is None:
            dirname = os.path.dirname(source_path)
            base, ext = os.path.splitext(os.path.basename(source_path))
            dest_path = os.path.join(dirname, base + "_merged" + ext)
        self.sourcePathLineEdit.setText(source_path)
        self.destPathLineEdit.setText(dest_path)

    def set_push_grid_handlers(self, column_model=None, sorton_model=None, sortasc_model=None,
                               dedupe_model=None):
        """
        Sets all default push grid handlers for the dialog.

        :param column_model: (QStandardItemModel, default None)
        :param sorton_model:  ((QStandardItemModel,list) default None)
        :param sortasc_model: ((QStandardItemModel,list) default None)
        :param dedupe_model: ((QStandardItemModel,list) default None)
        :return:
        """

        if column_model is None:
            column_model = self.get_source_columns_model()

        self.set_handler_sort_on(column_model, default_model=sorton_model)
        self.set_handler_sort_asc(default_model=sortasc_model)
        self.set_handler_dedupe_on(column_model, default_model=dedupe_model)

    def set_handler_sort_on(self, column_model=None, default_model=None):

        self.sortOnHandler = PushGridHandler(left_model=column_model, left_view=self.sortOnLeftView,
                                             left_button=self.sortOnLeftButton,
                                             left_delete=True, right_model=default_model,
                                             right_view=self.sortOnRightView,
                                             right_button=self.sortOnRightButton)

    def set_handler_sort_asc(self, default_model=None):
        if self.sortAscHandler is None:
            sort_asc = QtGui.QStandardItemModel()
            sort_asc.appendRow(QtGui.QStandardItem('True'))
            sort_asc.appendRow(QtGui.QStandardItem('False'))
            self.sortAscHandler = PushGridHandler(left_model=sort_asc, left_view=self.sortAscLeftView,
                                                  left_button=self.sortAscLeftButton,
                                                  left_delete=False, right_model=default_model,
                                                  right_view=self.sortAscRightView,
                                                  right_button=self.sortAscRightButton)

    def set_handler_dedupe_on(self, column_model=None, default_model=None):
        self.dedupeOnHandler = PushGridHandler(left_model=column_model, left_view=self.dedupeOnLeftView,
                                               left_button=self.dedupeOnLeftButton,
                                               left_delete=True, right_model=default_model,
                                               right_view=self.dedupeOnRightView,
                                               right_button=self.dedupeOnRightButton)

    def get_source_columns_model(self ,raise_on_error=True):
        if self.source_model is None:
            if raise_on_error:
                raise Exception("Cannot get source_columns as source_model is None!")
            else:
                columns = []
        else:
            columns = self.source_model.dataFrame().columns.tolist()

        return create_standard_item_model(columns)

    def open_file(self, file_names=None, model_signal=None):
        if file_names is None:
            file_names = QtGui.QFileDialog.getOpenFileNames()
        if file_names:
            file_names = file_names[0]
        for f in file_names:
            try:
                if os.path.exists(f):
                    model = self.df_manager.read_file(f)
                    if model_signal is not None:
                        model_signal.emit(f)
            except Exception as e:
                print(e)

    @QtCore.Slot(str)
    def add_merge_file(self, file_path):
        model = self.df_manager.get_model(file_path)
        model.enableEditing(True)
        self._merge_files.update({file_path:model})
        self._merge_view_model.appendDataFrameModel(model)
        self.mergeFileTable.setColumnWidth(0, 500)

    @QtCore.Slot(str)
    def add_suppress_file(self, file_path):
        model = self.df_manager.get_model(file_path)
        model.enableEditing(True)
        self._suppress_files.update({file_path:model})
        self._suppress_view_model.appendDataFrameModel(model)
        self.sFileTable.setColumnWidth(0, 500)

    def remove_file(self, view, indexes=None):
        if indexes is None:
            indexes = [x.row() for x in view.selectedIndexes()]
        model = view.model()
        for idx in indexes:
            model.takeRow(idx)

    def open_field_map(self, view, models):
        """
        Connects a MapGridDialog to help the  user map field names that
        are different between the source DataFrameModel and the
        selected merge or suppression DataFrameModel.

        :param view: (QtGui.QTableView)
            The view that has a selected filepath
        :param models: (dict)
            The dictionary of {file_path:DataFrameModel} where
            dataframe columns can be gathered from.
        :return: None

        """
        idx = view.selectedIndexes()[0]
        view_model = view.model()
        view_item = view_model.item(idx.row())
        view_item_text = view_item.text()

        try:
            self._field_map_grids[view_item_text].show()
        except KeyError:
            dfmodel = models[view_item_text]
            colmodel = dfmodel._dataFrame.columns.tolist()

            if self.source_model is None:
                self.set_source_model()

            source_colmodel = self.source_model._dataFrame.columns.tolist()

            fmap = MapGridDialog(parent=self)
            fmap.load_combo_box(source_colmodel, left=True)
            fmap.load_combo_box(colmodel, left=False)
            fmap.setWindowTitle("Map Fields")
            fmap.labelLeft.setText(os.path.basename(self.source_model.filePath))
            fmap.labelRight.setText(os.path.basename(dfmodel.filePath))
            fmap.signalNewMapping.connect(lambda x: self._field_map_data.update({dfmodel.filePath: x}))

            self._field_map_grids[view_item_text] = fmap
            self._field_map_grids[view_item_text].show()

    def open_edit_file_window(self, view, models):
        """
        Connects a DataFrameModel selected in the view
        to a FileTableWindow where the model can be edited.

        :param view: (QtGui.QTableView)
            The view that has a selected filepath
        :param models: (dict)
            The dictionary of {file_path:DataFrameModel}
            to supply the FileTableWindow
        :return: None
        """
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

    def execute(self):
        """
        Executes the merge_purge based upon the given settings.
        :return: None
        """
        if self.source_model is None:
            self.set_source_model()

        suppressed_results = {}
        merged_results = {}
        source_path = self.sourcePathLineEdit.text()
        dest_path = self.destPathLineEdit.text()
        source_df = self.source_model.dataFrame().copy()
        source_df.loc[:, 'ORIG_IDXER'] = source_df.index
        source_size = source_df.index.size

        sort_on = self.sortOnHandler.get_model_list(left=False)
        ascending = self.sortAscHandler.get_model_list(left=False)
        dedupe_on = self.dedupeOnHandler.get_model_list(left=False)

        # Make sure ascending/sort_on lists are equal.
        while len(sort_on) < len(ascending):
            ascending.append(False)

        while len(sort_on) > len(ascending):
            ascending.pop()

        # Get all merge models and merge.
        # Absorb all rows and columns
        for file_path, merge_model in self._merge_files.items():
            pre_size = source_df.index.size
            other_df = merge_model.dataFrame()
            source_df = pd.concat([source_df, other_df])
            merged_results.update({merge_model.filePath: source_df.index.size - pre_size})

        # Get all suppression models and suppress.
        for file_path, suppress_model in self._suppress_files.items():
            map_dict = self._field_map_data.get(file_path, {})
            sframe = suppress_model.dataFrame().copy()
            sframe.drop(['ORIG_IDXER'], axis=1, inplace=True, errors='ignore')

            if map_dict:
                # A mapping exists - rename the data and get the key_cols
                key_cols = list(map_dict.values())
                sframe.rename(columns=map_dict, inplace=True)
            else:
                # No mapping exists - Try to use the dedupe_on cols as key_cols
                key_cols = dedupe_on.copy()
                missing = [x for x in key_cols if x not in sframe.columns]
                if missing:
                    raise KeyError("Suppression file {} must have a field mapping or have the dedupe column labels, it has neither!.".format(
                                    suppress_model.filePath))

            sframe = sframe.loc[:, key_cols].drop_duplicates(key_cols)
            badframe = pd.merge(source_df, sframe, how='inner', left_on=key_cols, right_on=key_cols)
            source_df = source_df.loc[~source_df.index.isin(badframe.loc[:, 'ORIG_IDXER'].tolist()), :]
            suppressed_results.update({suppress_model.filePath: badframe.index.size})

        # Sort the data
        if sort_on and ascending:
            source_df.sort_values(sort_on, ascending=ascending, inplace=True)

        # Deduplicate the data.
        if dedupe_on:
            pre_size = source_df.index.size
            source_df.drop_duplicates(dedupe_on, inplace=True)
            dedupe_lost = pre_size - source_df.index.size
        else:
            dedupe_lost = 0

        # Export the data - done!
        source_df.drop(['ORIG_IDXER'], axis=1, inplace=True, errors='ignore')
        source_df.to_csv(dest_path, index=False)
        print("Exported: {}".format(dest_path))

        merge_string = "\n".join("Gained {} merging {}".format(v, k) for k, v in merged_results.items())
        suppress_string = "\n".join("Lost {} suppressing {}".format(v, k) for k,v in suppressed_results.items())
        report = """
        Merge Purge Report
        ==================
        Original Size: {}
        Final Size: {}
        Source Path: {}
        Output Path: {}


        Merge:
        ==================
        {}


        Purge:
        ==================
        {}


        Sort:
        ==================
            SORT BY: {}
            SORT ASCENDING: {}


        Dedupe:
        ==================
            DEDUPE ON: {}
            RECORDS LOST: {}



        """.format(source_size, source_df.index.size, source_path,
                   dest_path, merge_string, suppress_string,
                   sort_on, ascending, dedupe_on, dedupe_lost)

        report_path = os.path.splitext(dest_path)[0] + "_report.txt"
        with open(report_path, "w") as fh:
            fh.write(report)

        self.signalExecuted.emit(source_path, dest_path, report_path)




















