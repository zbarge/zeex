
import os
from PySide import QtGui, QtCore
from pandasqt.utils import superReadFileToFrameModel
from pandasqt.models.DataFrameModel import DataFrameModel
from pandasqt.views.DataTableView import DataTableWidget


class FileTableWidget(DataTableWidget):
    signalDataMerged = QtCore.Signal(DataFrameModel)

    def read_file(*args, **kwargs):
        return FileTableWidget(superReadFileToFrameModel(*args, **kwargs))

    def __init__(self, model, **kwargs):
        DataTableWidget.__init__(self, **kwargs)
        self.setModel(model)


