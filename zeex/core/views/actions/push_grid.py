from core.ui.actions.push_grid_ui import Ui_PushGridWidget
from core.compat import QtGui, QtCore


class PushGridHandler(object):
    """
    A handler for a two-list-view, two-button setup
    The left_model, view, button control the source data
    The right model, view, button control the select data.
    Supply the awfully long initialization parameters and the
    rest of the work will be handled for you to make the two
    list views push items back and forth via their buttons.
    """
    def __init__(self, left_model=None, left_view=None, left_button=None, left_delete=True,
                 right_model=None, right_view=None, right_button=None, right_delete=True):

        self._left_model = left_model
        self.listViewLeft = left_view
        self.listViewRight = right_view
        self.btnPushLeft = left_button
        self.btnPushRight = right_button
        self._left_delete = left_delete
        self._right_delete = right_delete

        if right_model is None:
            self._right_model = QtGui.QStandardItemModel()
        else:
            self._right_model = right_model

        self.listViewRight.setModel(self._right_model)
        self.connect_buttons()

        if self._left_model is not None:
            if isinstance(self._left_model, list):
                self.set_model_from_list(self._left_model)
            else:
                self.set_model(self._left_model)

    def connect_buttons(self):
        self.btnPushLeft.clicked.connect(self.push_left)
        self.btnPushRight.clicked.connect(self.push_right)

    def set_model(self, model):
        self.listViewLeft.setModel(model)

    def push_right(self):
        selected = self.listViewLeft.selectedIndexes()
        for idx in selected:
            item = self._left_model.itemFromIndex(idx)
            itemc = item.clone()
            self._right_model.appendRow(itemc)
            if self._left_delete:
                self._left_model.removeRow(item.row())

    def push_left(self):
        selected = self.listViewRight.selectedIndexes()
        for idx in selected:
            item = self._right_model.itemFromIndex(idx)
            itemc = item.clone()
            if self._left_delete:
                # Give the item back to the left
                # Because it was deleted
                self._left_model.appendRow(itemc)

            if self._right_delete:
                self._right_model.removeRow(item.row())

    def set_model_from_list(self, items: list):
        if self._left_model is None:
            self._left_model = QtGui.QStandardItemModel()

        for i in items:
            it = QtGui.QStandardItem(i)
            self._left_model.appendRow(it)
        self.set_model(self._left_model)

    def set_deletes(self, left: bool = True, right: bool = True):
        self._left_delete = left
        self._right_delete = right

    def get_model_list(self, left=True):
        if left is True:
            model = self._left_model
        else:
            model = self._right_model
        return [model.item(i).text() for i in range(model.rowCount())]


class PushGridWidget(QtGui.QWidget, Ui_PushGridWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.handle = None

    def set_handle(self, left_model, left_delete=True, right_delete=True):
        self.handle = PushGridHandler(left_model=left_model,
                                      left_button=self.btnPushLeft,
                                      left_delete=left_delete,
                                      right_model=None,
                                      right_button=self.btnPushRight,
                                      right_delete=right_delete)

    def get_left_data(self):
        return self.handle.get_model_list(left=True)

    def get_right_data(self):
        return self.handle.get_model_list(left=False)