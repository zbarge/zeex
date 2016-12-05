import pandas as pd
from PySide import QtGui, QtCore
from core.views.file import DataFrameModel
from core.views.actions.merge_purge_ui import Ui_MergePurgeDialog

class AbstractAction(object):
    signalActionBegin = QtCore.Signal(str)
    signalActionError = QtCore.Signal(str)
    signalActionEnd = QtCore.Signal(DataFrameModel)

    def __init__(self, model=None):
        pass


class MergePurgeDialog(QtGui.QDialog, Ui_MergePurgeDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def configure(self, settings: dict = None) -> bool:
        sort_model   = settings.get('sort_model', [])
        dedupe_model = settings.get('dedupe_model', [])
        source_path  = settings.get('source_path', None)
        dest_path    = settings.get('dest_path', None)

        if sort_model:
            self.sortOnColumnView.setModel(sort_model)

        if dedupe_model:
            self.dedupeOnListView.setModel(dedupe_model)

        if source_path is not None:
            self.sourcePathLineEdit.setText(source_path)

        if dest_path is not None:
            self.destPathLineEdit.setText(dest_path)

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





