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
        print("Pushed {} and {} to view.".format(left_item, right_item))

    def delete_selection(self):
        for item in self.tableView.selectedIndexes():
            self.map_model.takeRow(item.row())

    def emit_selection(self):
        data = dict()
        for row in range(self.map_model.rowCount()):
            left_item = self.map_model.item(row, 0)
            right_item = self.map_model.item(row, 1)
            data.update({right_item.text(): left_item.text()})
        self.signalNewMapping.emit(data)
        print("new mapping signal activated: {}".format(data))

    def clear_boxes(self):
        for b in self.findChildren(QtGui.QComboBox):
            b.setModel(False)

    @staticmethod
    def list_to_model(items):
        model = QtGui.QStandardItemModel()
        for i in items:
            model.appendRow(QtGui.QStandardItem(i))
        return model








