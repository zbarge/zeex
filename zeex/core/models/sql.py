"""
The below code was borrowed & modified from the following website:
https://gist.github.com/harvimt/4699169
#-*- coding=utf-8 -*-
# © 2013 Mark Harviston, BSD License
"""
import logging
from zeex.core.compat import QtGui, QtCore
QAbstractTableModel, QVariant, Qt = QtCore.QAbstractTableModel, str, QtCore.Qt

class CustomQVariant(object):
    def __init__(self, value=''):
        self.value = str(value)

    def get(self, *args, **kwargs):
        return self.value

QVariant = CustomQVariant

class AlchemyTableModel(QAbstractTableModel):
    """
    A Qt Table Model that binds to a SQL Alchemy query
    Example:
    >>> model = AlchemyTableModel(Session, [('Name', Entity.name)])
    >>> table = QTableView(parent)
    >>> table.setModel(model)
    """

    def __init__(self, session, query, columns):
        super(AlchemyTableModel, self).__init__()
        # TODO self.sort_data = None
        self.session = session
        self.fields = columns
        self.query = query

        self.results = None
        self.count = None
        self.sort = None
        self.filter = None
        self.refresh()
        self.changes = []

    def headerData(self, col, orientation, role):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.fields[col]
        elif orientation == Qt.Vertical:
            return col

        return QVariant()

    def setFilter(self, filter):
        """Sets or clears the filter, clear the filter by setting to None"""
        self.filter = filter
        self.refresh()

    def refresh(self):
        """Recalculates, self.results and self.count"""

        self.layoutAboutToBeChanged.emit()
        if not isinstance(self.fields, list):
            logging.info("Fields wasn't list: {}".format(self.fields))
            self.fields = [f for f in self.fields]
        q = self.query
        if self.sort is not None:
            order, col = self.sort
            col = self.fields[col][1]
            if order == Qt.DescendingOrder:
                col = col.desc()
        else:
            col = None

        if self.filter is not None:
            q = q.filter(self.filter)

        q = q.order_by(col)

        self.results = q.all()
        self.count = q.count()
        self.layoutChanged.emit()

    def flags(self, index):
        _flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if self.sort is not None:
            order, col = self.sort

            if index.column() == col:
                _flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        _flags |= Qt.ItemIsEditable

        return _flags

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(self, data, action, row, col, parent):
        if action != Qt.MoveAction:
            return

        return False

    def rowCount(self, parent):
        return self.count or 0

    def columnCount(self, parent):
        return len(self.fields)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        elif role not in (Qt.DisplayRole, Qt.EditRole):
            return QVariant()

        row = self.results[index.row()]
        name = self.fields[index.column()]

        return str(getattr(row, name))

    def setData(self, index, value, role=None):
        row = self.results[index.row()]
        name = self.fields[index.column()]
        if not isinstance(value, str):
            value = value.toString()
        try:
            orig = getattr(row, name, value)
            setattr(row, name, value)
            new = getattr(row, name, value)
            logging.info("Commited - {} - {}".format(orig, new))
        except Exception as ex:
            logging.error(str(ex))
            QtGui.QMessageBox.critical(None, 'SQL Error', str(ex))
            return False
        else:
            self.changes.append(index)
            return True

    def sort(self, col, order):
        """Sort table by given column number."""
        pass

    def commit(self):
        if self.changes:
            self.session.commit()
            for i in range(len(self.changes)):
                idx = self.changes[i]
                self.dataChanged.emit(idx, idx)
            self.changes = []
            self.refresh()

    def rollback(self):
        if self.changes:
            self.session.rollback()
            self.changes = []
            self.refresh()

