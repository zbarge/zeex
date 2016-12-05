
import os
from PySide import QtGui, QtCore
from pandasqt.utils import superReadFileToFrameModel
from pandasqt.models.DataFrameModel import DataFrameModel
from pandasqt.views.DataTableView import DataTableWidget
from core.views.file_ui import Ui_FileWindow
from core.views.actions.action import MergePurgeDialog

class FileTableWidget(DataTableWidget):
    signalDataMerged = QtCore.Signal(DataFrameModel)

    def read_file(*args, **kwargs):
        return FileTableWidget(superReadFileToFrameModel(*args, **kwargs))

    def __init__(self, model, **kwargs):
        DataTableWidget.__init__(self, **kwargs)
        self.setModel(model)


class FileTableWindow(QtGui.QMainWindow, Ui_FileWindow):
    def __init__(self, model, **kwargs):
        QtGui.QMainWindow.__init__(self, parent=kwargs.pop('parent', None))
        kwargs['parent'] = self
        self._widget = FileTableWidget(model, **kwargs)
        self.setupUi(self)
        self.connect_actions()

    @property
    def widget(self):
        # Overrides the Ui_FileWindow.widget
        return self._widget

    @widget.setter
    def widget(self, x):
        # Prevent the Ui_FileWindow from overriding our widget.
        pass

    def connect_actions(self):
        self.actionMergePurge.triggered.connect(self.open_merge_purge_dialog)

    def open_merge_purge_dialog(self):
        model = self.widget.model()
        df = model._dataFrame
        file_base, ext = os.path.splitext(model.filePath)
        dialog = MergePurgeDialog()

        settings = dict()
        settings['sort_model'] = dialog.create_sort_model(df.columns)
        settings['dedupe_model'] = dialog.create_dedupe_model(df.columns)
        settings['source_path'] = model.filePath
        settings['dest_path'] =  file_base + "_merged" + ext
        dialog.configure(settings)
        
        self.dialogMergePurge = dialog
        self.dialogMergePurge.show()



