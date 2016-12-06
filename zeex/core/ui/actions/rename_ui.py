# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rename.ui'
#
# Created: Mon Dec  5 15:45:36 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_renameDialog(object):
    def setupUi(self, renameDialog):
        renameDialog.setObjectName("renameDialog")
        renameDialog.resize(311, 488)
        self.gridLayoutWidget = QtGui.QWidget(renameDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 30, 251, 421))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.cancelPushButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.gridLayout_2.addWidget(self.cancelPushButton, 0, 1, 1, 1)
        self.renamePushButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.renamePushButton.setObjectName("renamePushButton")
        self.gridLayout_2.addWidget(self.renamePushButton, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.tableView = QtGui.QTableView(self.gridLayoutWidget)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)

        self.retranslateUi(renameDialog)
        QtCore.QMetaObject.connectSlotsByName(renameDialog)

    def retranslateUi(self, renameDialog):
        renameDialog.setWindowTitle(QtGui.QApplication.translate("renameDialog", "Rename Fields", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setText(QtGui.QApplication.translate("renameDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.renamePushButton.setText(QtGui.QApplication.translate("renameDialog", "Rename", None, QtGui.QApplication.UnicodeUTF8))

