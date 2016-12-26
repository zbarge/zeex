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
from core.utility.pandatools import gather_frame_fields
from core.utility.collection import DictConfig, SettingsINI


class MergePurgeDialog(QtGui.QDialog, Ui_MergePurgeDialog):
    """
    This dialog allows a user to do large updates on a given source DataFrameModel.
        - Merging other file(s) with the source based on common keys/fields
        - Purging records from the source using other file(s) based on common keys/fields
        - Sorting the DataFrame by multiple columns/ascending/descending
        - Deduplicating the DataFrame based on common keys/fields
    Settings can exported to a config.ini file and re-imported at a later time.

    """
    signalMergeFileOpened = QtCore.Signal(str) # file path
    signalSFileOpened = QtCore.Signal(str) # file path
    signalSourcePathSet = QtCore.Signal(str) #file path
    signalExecuted = QtCore.Signal(str, str, str) # source_path, dest_path, report_path

    def __init__(self, df_manager: DataFrameModelManager, parent=None, source_model=None):
        """
        :param df_manager: (DataFrameModelManager)
            This will be used to handle reading/updating of DataFrameModels used
            in the operation.
        :param parent: (QMainWindow)

        :param source_model: (DataFrameModel)
            An optional source DataFrameModel
        """
        self.df_manager = df_manager
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.source_model = source_model
        self._merge_view_model = FileViewModel()
        self._suppress_view_model = FileViewModel()
        self._purge_files = {}
        self._merge_files = {}
        self._file_table_windows = {}
        self._field_map_grids = {}
        self._field_map_data = {}
        self.sortAscHandler = None
        self.sortOnHandler = None
        self.dedupeOnHandler = None
        self.uniqueFieldsHandler = None
        self.gatherFieldsHandler = None

    def configure(self, source_path=None, dest_path=None):
        """
        Connects main buttons and actions.
        :param source_path: (str, default None)
            If this is None there must be a valid path already in the sourcePathLineEdit or an AssertionError raises.

        :param dest_path: (str, default None)
            Optional custom destination path to be added to the destPathLineEdit.
        :return: None
        """
        if source_path is None:
            source_path = self.sourcePathLineEdit.text()
            assert os.path.exists(source_path), "source_path cannot be None, set ".format(source_path)
        self.set_line_edit_paths(source_path, dest_path=dest_path)
        if self.sortAscHandler is None:
            self.set_handler_sort_asc()
        source_func = partial(self.open_file, model_signal=self.signalSourcePathSet)

        self.signalSourcePathSet.connect(self.set_source_model_from_browse)
        self.btnBrowseSourcePath.clicked.connect(source_func)
        self.btnBrowseDestPath.clicked.connect(self.set_dest_path_from_browse)
        self.signalMergeFileOpened.connect(self.add_merge_file)
        merge_file_func = partial(self.open_file, model_signal=self.signalMergeFileOpened)
        self.btnAddMergeFile.clicked.connect(merge_file_func)
        self.btnBrowseMergeFile.clicked.connect(merge_file_func)
        self.btnDeleteMergeFile.clicked.connect(partial(self.remove_file, self.mergeFileTable))
        self.btnEditMergeFile.clicked.connect(partial(self.open_edit_file_window, self.mergeFileTable, self._merge_files))
        self.mergeFileTable.setModel(self._merge_view_model)

        self.signalSFileOpened.connect(self.add_purge_file)
        sfile_func = partial(self.open_file, model_signal=self.signalSFileOpened)
        self.btnEditSFile.clicked.connect(partial(self.open_edit_file_window, self.sFileTable, self._purge_files))
        self.btnDeleteSFile.clicked.connect(partial(self.remove_file, self.sFileTable))
        self.btnAddSFile.clicked.connect(sfile_func)
        self.btnBrowseSFile.clicked.connect(sfile_func)
        self.sFileTable.setModel(self._suppress_view_model)
        self.btnMapSFields.clicked.connect(partial(self.open_field_map, self.sFileTable, self._purge_files))
        self.btnMapMergeFields.clicked.connect(partial(self.open_field_map, self.mergeFileTable, self._merge_files))
        self.btnExecute.clicked.connect(self.execute)
        self.btnExportTemplate.clicked.connect(self.export_settings)
        self.btnImportTemplate.clicked.connect(self.import_settings)
        self.btnReset.clicked.connect(self.reset)

    def set_source_model_from_browse(self, filepath):
        self.set_line_edit_paths(filepath, dest_path=False)
        self.set_source_model(configure=True)

    def set_dest_path_from_browse(self, filepath=None):
        if filepath is None:
            filepath = QtGui.QFileDialog.getOpenFileName()[0]
        self.destPathLineEdit.setText(filepath)

    def set_source_model(self, model=None, configure=False):
        """
        Sets the source DataFrameModel for the Dialog.

        :param model: (DataFrameModel)
            The DataFrameModel to be set.
        :param configure:
            True re-configures file path line edits and the listviews.
        :return:
        """
        if not isinstance(model, DataFrameModel):
            if model is None:
                model = self.sourcePathLineEdit.text()
            if isinstance(model, str) and os.path.exists(model):
                model = self.df_manager.read_file(model)
            else:
                raise Exception("model parameter must be a filepath or a qtpandas.models.DataFrameModel")
        self.source_model = model
        if configure:
            self.configure(source_path=self.source_model.filePath)
            self.set_push_grid_handlers()
            self.set_primary_key_combo_box(default=self.primaryKeyComboBox.currentText())

    def set_line_edit_paths(self, source_path=None, dest_path=None):
        """
        Sets the source/destination line edits in the Dialog.
        :param source_path: (str, default None)
            An optional valid filepath for the source DataFrameModel.
            If None, :param dest_path cannot be None.
        :param dest_path: (str, default None)
            An optional destination path. One will be created automatically
            if None is given.
            False will prevent the destination path from being set at all.
        :return: None
        """
        assert any([dest_path, source_path]), "source_path or dest_path must be set."

        if dest_path is None:
            dirname = os.path.dirname(source_path)
            base, ext = os.path.splitext(os.path.basename(source_path))
            dest_path = os.path.join(dirname, base + "_merged" + ext)

        if source_path:
            self.sourcePathLineEdit.setText(source_path)

        if dest_path:
            self.destPathLineEdit.setText(dest_path)

    def set_push_grid_handlers(self, column_model=None, sorton_model=None, sortasc_model=None,
                               dedupe_model=None, gather_model=None, unique_model=None):
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

        self.set_handler_sort_on(column_model=None, default_model=sorton_model)
        self.set_handler_sort_asc(default_model=sortasc_model)
        self.set_handler_dedupe_on(column_model=None, default_model=dedupe_model)
        self.set_handler_gather_fields(column_model=None, default_model=gather_model)
        self.set_handler_unique_fields(column_model=None, default_model=unique_model)

    def set_handler_sort_on(self, column_model=None, default_model=None):
        if column_model is None:
            column_model = self.get_source_columns_model()
        self.sortOnHandler = PushGridHandler(left_model=column_model, left_view=self.sortOnLeftView,
                                             left_button=self.sortOnLeftButton,
                                             left_delete=True, right_model=default_model,
                                             right_view=self.sortOnRightView,
                                             right_button=self.sortOnRightButton)

    def set_handler_sort_asc(self, default_model=None, overwrite=False):
        if self.sortAscHandler is None or default_model is not None or overwrite:
            sort_asc = QtGui.QStandardItemModel()
            sort_asc.appendRow(QtGui.QStandardItem('True'))
            sort_asc.appendRow(QtGui.QStandardItem('False'))
            self.sortAscHandler = PushGridHandler(left_model=sort_asc, left_view=self.sortAscLeftView,
                                                  left_button=self.sortAscLeftButton,
                                                  left_delete=False, right_model=default_model,
                                                  right_view=self.sortAscRightView,
                                                  right_button=self.sortAscRightButton)

    def set_handler_dedupe_on(self, column_model=None, default_model=None):
        if column_model is None:
            column_model = self.get_source_columns_model()
        self.dedupeOnHandler = PushGridHandler(left_model=column_model, left_view=self.dedupeOnLeftView,
                                               left_button=self.dedupeOnLeftButton,
                                               left_delete=True, right_model=default_model,
                                               right_view=self.dedupeOnRightView,
                                               right_button=self.dedupeOnRightButton)

    def set_handler_gather_fields(self, column_model=None, default_model=None):
        if column_model is None:
            column_model = self.get_source_columns_model()
        self.gatherFieldsHandler = PushGridHandler(left_model=column_model,
                                                   left_view=self.gatherFieldsListViewLeft,
                                                   left_button=self.gatherFieldsButtonLeft,
                                                   left_delete=True, right_model=default_model,
                                                   right_view=self.gatherFieldsListViewRight,
                                                   right_button=self.gatherFieldsButtonRight)

    def set_handler_unique_fields(self, column_model=None, default_model=None):
        if column_model is None:
            column_model = self.get_source_columns_model()
        self.uniqueFieldsHandler = PushGridHandler(left_model=column_model,
                                                   left_view=self.uniqueFieldsListViewLeft,
                                                   left_button=self.uniqueFieldsPushButtonLeft,
                                                   left_delete=True, right_model=default_model,
                                                   right_view=self.uniqueFieldsListViewRight,
                                                   right_button=self.uniqueFieldsPushButtonRight)

    def get_source_columns_model(self, raise_on_error=True) -> QtGui.QStandardItemModel:
        """
        Quick way to get a QStandardItemModel form the DataFrameModel's columns.
        :param raise_on_error: (bool, default True)
            Raises an error if the source_model has not yet been set.
        :return: (QtGui.QStandardItemModel)
        """
        if self.source_model is None:
            if raise_on_error:
                raise Exception("Cannot get source_columns as source_model is None!")
            else:
                columns = []
        else:
            columns = self.source_model.dataFrame().columns.tolist()

        return create_standard_item_model(columns)

    def open_file(self, file_names: list=None, model_signal=None, allow_multi=True):
        """
        Opens a Merge or Purge file (or really any file) and calls the
        given model signal after registering the DataFrameModel with the DataFrameModelManager.
        :param file_names: (list, default None)
            An optional list of filenames to open.
            The user must select filenames otherwise.
        :param model_signal: (QtCore.Signal)
            A signal to be called after successfully reading the DataFrameModel.
        :param allow_multi: (bool, default True)
            True allows multiple files to be read (and the signal called each time).
            False allows only the first file to be read.
        :return: None
            You can call MergePurgeDialog.df_manager.get_frame(filename) to
            retrieve a DataFrameModel.
        """
        if file_names is None:
            file_names = QtGui.QFileDialog.getOpenFileNames(parent=self)

        if isinstance(file_names, str):
            file_names = list(file_names)

        assert not isinstance(file_names, str) and hasattr(file_names, "__iter__"), "file_names is not list-like!"

        if allow_multi is False:
            file_names = list(file_names[0])

        for f in file_names:
            try:
                if not isinstance(f, str) and hasattr(f, '__iter__'):
                    f = f[0]
                if os.path.exists(f):
                    self.df_manager.read_file(f)
                    if model_signal is not None:
                        model_signal.emit(f)
                        print("Emitted signal: {}".format(f))
            except Exception as e:
                print(e)

    @QtCore.Slot(str)
    def add_merge_file(self, file_path):
        """
        Adds a merge file to the merge view and
        also updates the internal dictionary storing the filepath/model.
        :param file_path: (str)
            The file path to add.
        :return: None
        """
        model = self.df_manager.get_model(file_path)
        model.enableEditing(True)
        self._merge_files.update({file_path:model})
        self._merge_view_model.append_df_model(model)
        self.mergeFileTable.setColumnWidth(0, 500)

    @QtCore.Slot(str)
    def add_purge_file(self, file_path):
        """
        Adds a purge file to the purge view and
        also updates the internal dictionary storing the filepath/model.
        :param file_path: (str)
            The file path to add.
        :return: None
        """
        model = self.df_manager.get_model(file_path)
        model.enableEditing(True)
        self._purge_files.update({file_path:model})
        self._suppress_view_model.append_df_model(model)
        self.sFileTable.setColumnWidth(0, 500)

    def remove_file(self, view, indexes=None):
        """
        Removes selected file(s) from the given view.
        :param view: (QListView)
            The view to drop the selected indexes on.
        :param indexes: (list, default None)
            A list of given indexes to drop.
            Otherwise relies on selected indexes in the view.
        :return: None
        """
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

    def get_map_grid(self, file_path):
        """
        Accessor to the MergePurgeDialog._field_map_grids dictionary.
        Contains map grid dialogs.
        :param file_path: (str)
            The filepath related to the desired MapGridDialog.
        :return: (MapGridDialog, None)
        """
        return self._field_map_grids.get(file_path, None)

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
        index_label = self.primaryKeyComboBox.currentText()

        sort_on = self.sortOnHandler.get_model_list(left=False)
        ascending = self.sortAscHandler.get_model_list(left=False)
        dedupe_on = self.dedupeOnHandler.get_model_list(left=False)
        gather_fields = self.gatherFieldsHandler.get_model_list(left=False)
        overwrite_existing = self.gatherFieldsOverWriteCheckBox.isChecked()

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
            if gather_fields:
                assert index_label in other_df.columns, "DataFrameModel for {} missing column {}".format(
                                                         merge_model.filePath, index_label)
                source_df = gather_frame_fields(source_df, other_df, index_label=index_label,
                                                fields=gather_fields, copy_frames=True,
                                                append_missing=True, overwrite=overwrite_existing)
            else:
                source_df = pd.concat([source_df, other_df])
            merged_results.update({merge_model.filePath: source_df.index.size - pre_size})
        # Get all suppression models and suppress.
        for file_path, suppress_model in self._purge_files.items():
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
                    raise KeyError("Suppression file {} must have a field mapping or \
                                    have the dedupe column labels, it has neither!.".format(
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

    def get_settings(self, dc:DictConfig = None, section="MERGE_PURGE") -> DictConfig:
        """
        Gathers the settings out of the Dialog and
        returns a DictConfig object with updated settings.

        :param dc (DictConfig, default None)
            An optional DictConfig object, one is created if none is given.
        :param section (str, default 'MERGE_PURGE')
            An optional section name to apply settings to.
            A pre-existing section with this name would be overwritten.
        :return: (DictConfig)
            An updated DictConfig object.
        """
        if dc is None:
            dc = DictConfig()
        if dc.has_section(section):
            dc.remove_section(section)
        dc.add_section(section)

        dc.set_safe(section, 'source_path',           self.sourcePathLineEdit.text())
        dc.set_safe(section, 'dest_path',             self.destPathLineEdit.text())
        dc.set_safe(section, 'primary_key',           self.primaryKeyComboBox.currentText())
        dc.set_safe(section, 'dedupe_on',             self.dedupeOnHandler.get_model_list(left=False))
        dc.set_safe(section, 'gather_fields',         self.gatherFieldsHandler.get_model_list(left=False))
        dc.set_safe(section, 'gather_fields_overwrite', self.gatherFieldsOverWriteCheckBox.isChecked())
        dc.set_safe(section, 'sort_on',               self.sortOnHandler.get_model_list(left=False))
        dc.set_safe(section, 'sort_ascending',        self.sortAscHandler.get_model_list(left=False))
        dc.set_safe(section, 'unique_fields',         self.uniqueFieldsHandler.get_model_list(left=False))
        dc.set_safe(section, 'field_map_data',        self._field_map_data)
        dc.set_safe(section, 'merge_files',           list(self._merge_files.keys()))
        dc.set_safe(section, 'purge_files',           list(self._purge_files.keys()))
        return dc

    def set_settings(self, dc:DictConfig, section="MERGE_PURGE"):
        """
        Applies settings from a DictConfig object to the Dialog.

        :param dc (DictConfig, default None)
            The DictConfig object that contains the settings to be applied.
        :param section (str, default 'MERGE_PURGE')
            The section name to read settings from.
        :return:
        """
        source_path = dc.get(section, 'source_path', fallback=self.sourcePathLineEdit.text())
        current_path = self.sourcePathLineEdit.text()
        if source_path != current_path:
            dfm = self.df_manager.read_file(source_path)
            dest = dc.get(section, 'dest_path', fallback=None)
            self.set_source_model(dfm, configure=False)
            self.set_line_edit_paths(source_path, dest_path=dest)
            self.primaryKeyComboBox.clear()
            self.set_primary_key_combo_box()

        key_id = self.primaryKeyComboBox.findText(dc.get(section, 'primary_key',
                                                         fallback=self.primaryKeyComboBox.currentText()))

        dedupe_on     = dc.get_safe(section, 'dedupe_on', fallback=None)
        sort_on       = dc.get_safe(section, 'sort_on', fallback=None)
        gather_fields = dc.get_safe(section, 'gather_fields', fallback=None)
        unique_fields = dc.get_safe(section, 'unique_fields', fallback=None)
        gather_fields_overwrite = dc.getboolean(section, 'gather_fields_overwrite', fallback=False)
        sort_ascending = dc.get_safe(section, 'sort_ascending', fallback=None)
        merge_files    = dc.get_safe(section, 'merge_files', fallback=[])
        purge_files    = dc.get_safe(section, 'purge_files', fallback=[])
        field_map_data = dc.get_safe(section, 'field_map_data', fallback={})

        self.primaryKeyComboBox.setCurrentIndex(key_id)
        self.set_push_grid_handlers(column_model=None, sorton_model=sort_on, sortasc_model=sort_ascending,
                               dedupe_model=dedupe_on, gather_model=gather_fields, unique_model=unique_fields)
        self.gatherFieldsOverWriteCheckBox.setChecked(gather_fields_overwrite)
        self._field_map_data.update(field_map_data)
        self.open_file(file_names=merge_files, model_signal=self.signalMergeFileOpened)
        self.open_file(file_names=purge_files, model_signal=self.signalSFileOpened)

    def reset(self):
        """
        Resets ListViews/CheckBoxes.
        The source/dest line edits are left alone
        The suppression/merge files are also left alone.
        :return: None
        """
        self.set_push_grid_handlers()
        self.set_handler_sort_asc(overwrite=True)
        self.set_primary_key_combo_box()
        self.gatherFieldsOverWriteCheckBox.setChecked(False)

    def set_primary_key_combo_box(self, default=None):
        """
        Sets the primary key combo box.
        :param default: (str, default None)
            An optional default field name to select.
        :return:
        """
        combo_model = create_standard_item_model([''] + self.source_model.dataFrame().columns.tolist(),
                                                 editable=False, checkable=True)
        self.primaryKeyComboBox.setModel(combo_model)
        if default is not None:
            self.primaryKeyComboBox.setCurrentIndex(self.primaryKeyComboBox.findText(default))

    def import_settings(self, from_path=None):
        """
        Imports settings to the Dialog from a file.
        :param from_path: (str, default None)
            None makes the user enter a file path.
        :return:
        """
        if from_path is None:
            from_path = QtGui.QFileDialog.getOpenFileName(self)[0]
        config = SettingsINI(filename=from_path)
        self.set_settings(config)

    def export_settings(self, to=None):
        """
        Exports settings from the Dialog to a file.
        :param to: (str, default None)
            None makes the user enter a file path.
        :return: None
        """
        if to is None:
            to = QtGui.QFileDialog.getSaveFileName(self)[0]
        config = self.get_settings()
        config.save_as(to, set_self=True)





























