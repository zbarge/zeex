# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'map_grid.ui'
#
# Created: Sat Dec 10 00:21:31 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MapGrid(object):
    def setupUi(self, MapGrid):
        MapGrid.setObjectName("MapGrid")
        MapGrid.resize(400, 300)
        self.gridLayout_3 = QtGui.QGridLayout(MapGrid)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.comboBoxLeft = QtGui.QComboBox(MapGrid)
        self.comboBoxLeft.setObjectName("comboBoxLeft")
        self.gridLayout.addWidget(self.comboBoxLeft, 1, 0, 1, 1)
        self.comboBoxRight = QtGui.QComboBox(MapGrid)
        self.comboBoxRight.setObjectName("comboBoxRight")
        self.gridLayout.addWidget(self.comboBoxRight, 1, 1, 1, 1)
        self.labelLeft = QtGui.QLabel(MapGrid)
        self.labelLeft.setAlignment(QtCore.Qt.AlignCenter)
        self.labelLeft.setObjectName("labelLeft")
        self.gridLayout.addWidget(self.labelLeft, 0, 0, 1, 1)
        self.labelRight = QtGui.QLabel(MapGrid)
        self.labelRight.setAlignment(QtCore.Qt.AlignCenter)
        self.labelRight.setMargin(0)
        self.labelRight.setObjectName("labelRight")
        self.gridLayout.addWidget(self.labelRight, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.btnDelete = QtGui.QPushButton(MapGrid)
        self.btnDelete.setObjectName("btnDelete")
        self.gridLayout_2.addWidget(self.btnDelete, 2, 0, 1, 1)
        self.btnAdd = QtGui.QPushButton(MapGrid)
        self.btnAdd.setObjectName("btnAdd")
        self.gridLayout_2.addWidget(self.btnAdd, 1, 0, 1, 1)
        self.tableView = QtGui.QTableView(MapGrid)
        self.tableView.setObjectName("tableView")
        self.gridLayout_2.addWidget(self.tableView, 4, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.btnBox = QtGui.QDialogButtonBox(MapGrid)
        self.btnBox.setOrientation(QtCore.Qt.Horizontal)
        self.btnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnBox.setObjectName("btnBox")
        self.gridLayout_3.addWidget(self.btnBox, 1, 0, 1, 1)

        self.retranslateUi(MapGrid)
        QtCore.QObject.connect(self.btnBox, QtCore.SIGNAL("accepted()"), MapGrid.accept)
        QtCore.QObject.connect(self.btnBox, QtCore.SIGNAL("rejected()"), MapGrid.reject)
        QtCore.QMetaObject.connectSlotsByName(MapGrid)

    def retranslateUi(self, MapGrid):
        MapGrid.setWindowTitle(QtGui.QApplication.translate("MapGrid", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLeft.setText(QtGui.QApplication.translate("MapGrid", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.labelRight.setText(QtGui.QApplication.translate("MapGrid", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("MapGrid", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("MapGrid", "Add", None, QtGui.QApplication.UnicodeUTF8))

