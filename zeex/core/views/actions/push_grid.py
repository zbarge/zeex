from core.views.actions.push_grid_ui import Ui_PushGridWidget
from PySide import QtGui


class PushGridWidget(QtGui.QWidget, Ui_PushGridWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self._left_delete = True
        self._right_delete = True
        self._left_model = None
        self._right_model = QtGui.QStandardItemModel()

    def connect_buttons(self):
        self.btnPushLeft.clicked.connect(self.push_left)
        self.btnPushRight.clicked.connect(self.push_right)

    def set_model(self, model):
        self.listViewLeft.setModel(model)

    def push_right(self):
        selected = self.listViewLeft.selectedIndexes()
        for idx in selected:
            item = self.listViewLeft.findChild(idx)
            self._right_model.appendRow(item)
            self._left_model.removeRow(idx)

    def push_left(self):
        selected = self.listViewRight.selectedIndexes()
        for idx in selected:
            item = self.listViewRight.findChild(idx)
            self._left_model.appendRow(item)
            self._right_model.removeRow(idx)

    def set_model_from_list(self, items: list):
        pass

    def set_deletes(self, left: bool = True, right: bool = True):
        self._left_delete = left
        self._right_delete = right

