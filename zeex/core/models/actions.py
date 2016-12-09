from core.compat import QtGui, QtCore


class FileViewModel(QtGui.QStandardItemModel):
    def __init__(self, models=None):
        QtGui.QStandardItemModel.__init__(self)
        self._df_models = {}
        if models is not None:
            [self.appendDataFrameModel(m) for m in models]
    def appendDataFrameModel(self, model):
        file_path = model.filePath
        f = QtGui.QStandardItem(file_path)
        c = QtGui.QStandardItem(str(model._dataFrame.index.size))
        row = self.rowCount()
        self.setItem(row, 0, f)
        self.setItem(row, 1, c)





