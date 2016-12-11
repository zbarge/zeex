from core.compat import QtGui, QtCore
from core.ui.actions.map_grid_ui import Ui_MapGrid


class MapGridDialog(QtGui.QDialog, Ui_MapGrid):
    """
    Small dialog that contains two combo
    boxes, 4 buttons, and a table view.

    The two combo boxes should be filled with
    different lists of values that the user can
    map together and add to the table view.

    When the user select's the OK button, a
    signalNewMapping signal is emitted with the dictionary
    containing the left combo box values as dict values, and the right
    combo box values as dict keys.
    """
    signalNewMapping = QtCore.Signal(dict)

    def __init__(self, *args, **kwargs):
        self._data_source = kwargs.pop('data_source', None)
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.map_model = QtGui.QStandardItemModel(0, 2)
        self.configure()

    def configure(self):
        self.btnAdd.clicked.connect(self.push_combo_boxes)
        self.btnDelete.clicked.connect(self.delete_selection)
        self.btnBox.accepted.connect(self.emit_selection)
        self.btnBox.rejected.connect(self.hide)
        self.tableView.setModel(self.map_model)
        self.map_model.setHorizontalHeaderLabels(['Left On', 'Right On'])
        self.comboBoxLeft.currentIndexChanged.connect(self.sync_right_box)

    def load_combo_box(self, model, default=None, left=True):
        if not isinstance(model, (QtCore.QAbstractItemModel, QtGui.QStandardItemModel)):
            model = self.list_to_model(model)

        if left:
            box = self.comboBoxLeft
        else:
            box = self.comboBoxRight

        box.setModel(model)
        if default is not None:
            idx = box.findText(default)
            box.setCurrentIndex(idx)

    def push_combo_boxes(self):
        left_item = self.comboBoxLeft.currentText()
        right_item = self.comboBoxRight.currentText()
        row = self.map_model.rowCount()
        for col, val in enumerate([left_item, right_item]):
            item = QtGui.QStandardItem(val)
            item.setEditable(False)
            self.map_model.setItem(row, col, item)

    def sync_right_box(self, index):
        """
        Tries to set the right-hand combo box
        by searching for what's currently selected on the left-hand
        combo box. Case-insensitive but the string must match otherwise.
        :param index: Useless, part of the signal that comes out of the combo box.
        :return: None
        """
        try:
            text = self.comboBoxLeft.currentText()
            idx = self.comboBoxRight.findText(text, flags=QtCore.Qt.MatchFixedString)
            self.comboBoxRight.setCurrentIndex(idx)
        except:
            pass

    def delete_selection(self):
        for item in self.tableView.selectedIndexes():
            self.map_model.takeRow(item.row())

    def emit_selection(self):
        """
        Emits a signalNewMapping signal containing a
        dictionary with keys from the right-hand combo box selections,
        and values from the left-hand combo box selections.
        :return: None
        """
        data = dict()
        for row in range(self.map_model.rowCount()):
            left_item = self.map_model.item(row, 0)
            right_item = self.map_model.item(row, 1)
            data.update({right_item.text(): left_item.text()})
        self.signalNewMapping.emit(data)

    def clear_boxes(self):
        """
        Resets the models of both ComboBoxes.
        :return:
        """
        for b in self.findChildren(QtGui.QComboBox):
            b.setModel(False)

    @staticmethod
    def list_to_model(items):
        """
        Creates a QtGui.StandardItemModel filled
        with QtGui.QStandardItems from the list of
        items.
        :param items: (list)
            of string-like items to store.
        :return: (QtGui.QStandardItemModel)
            With all items from the list.
        """
        model = QtGui.QStandardItemModel()
        for i in items:
            model.appendRow(QtGui.QStandardItem(i))
        return model








