# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:45:23 2016

@author: Zeke
"""
from PySide import QtGui


def configureComboBox(box, options, default):
    box.addItems(options)
    idx = box.findText(default)
    if idx >= 0:
        box.setCurrentIndex(idx)
    return box


def create_standard_item_model(columns: list = None):
        if columns is None:
            columns = []
        elif not isinstance(columns, list):
            columns = list(columns)
        model = QtGui.QStandardItemModel()
        for idx, col in enumerate(columns):
            item = QtGui.QStandardItem(col)
            for order in ['asc', 'desc']:
                oitem = QtGui.QStandardItem(order)
                item.appendRow(oitem)
            model.appendRow(item)
        return model


def ensure_modeled(item: (str, list, QtGui.QStandardItemModel)):
    if isinstance(item, str):
        item = [item]
    if hasattr(item, "__iter__"):
        item = create_standard_item_model(item)
    elif not hasattr(item, "rowCount"):
        raise NotImplementedError("unable to convert item of type {} to QStandardItemModel".format(type(item)))
    return item


def display_ok_msg(parent, msg):
    msgBox = QtGui.QMessageBox(parent)
    msgBox.setText(msg)
    msgBox.show()


def shift_grid_layout_down(layout):
    # TODO: Make this legit?
    col_range = range(layout.columnCount())
    row_range = range(layout.rowCount())
    print(layout.columnCount())
    print(layout.rowCount())
    temp = []

    for row_idx in row_range:
        items = [layout.itemAtPosition(row_idx, col_idx)
                 for col_idx in col_range]
        temp.append(items)
    temp.insert(0, [i for i in temp[0]])
    print("got temp")
    for row_idx, items in enumerate(temp):
        print("working row {}".format(row_idx))
        for col_idx, item in enumerate(items):
            print("working column {}".format(col_idx))
            if item is not None:
                layout.addWidget(item)
    print("redid layout")
    print(layout.columnCount())
    print(layout.rowCount())
    return layout


