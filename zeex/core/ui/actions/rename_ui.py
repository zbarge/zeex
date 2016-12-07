# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rename.ui'
#
# Created: Tue Dec  6 02:00:51 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_renameDialog(object):
    def setupUi(self, renameDialog):
        renameDialog.setObjectName("renameDialog")
        renameDialog.resize(470, 488)
        self.gridLayoutWidget = QtGui.QWidget(renameDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 30, 251, 421))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tableView = QtGui.QTableView(self.gridLayoutWidget)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.gridLayoutWidget_2 = QtGui.QWidget(renameDialog)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(300, 30, 154, 167))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnSaveRenames = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.btnSaveRenames.setObjectName("btnSaveRenames")
        self.gridLayout_2.addWidget(self.btnSaveRenames, 1, 0, 1, 1)
        self.btnLoadTemplate = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.btnLoadTemplate.setObjectName("btnLoadTemplate")
        self.gridLayout_2.addWidget(self.btnLoadTemplate, 3, 0, 1, 1)
        self.btnSaveFile = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.btnSaveFile.setObjectName("btnSaveFile")
        self.gridLayout_2.addWidget(self.btnSaveFile, 0, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.setCaseBtn = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.setCaseBtn.setObjectName("setCaseBtn")
        self.gridLayout_3.addWidget(self.setCaseBtn, 0, 1, 1, 1)
        self.setCaseComboBox = QtGui.QComboBox(self.gridLayoutWidget_2)
        self.setCaseComboBox.setObjectName("setCaseComboBox")
        self.setCaseComboBox.addItem("")
        self.setCaseComboBox.addItem("")
        self.setCaseComboBox.addItem("")
        self.setCaseComboBox.addItem("")
        self.gridLayout_3.addWidget(self.setCaseComboBox, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 4, 0, 1, 1)
        self.syncDatabaseRadioButton = QtGui.QRadioButton(self.gridLayoutWidget_2)
        self.syncDatabaseRadioButton.setChecked(True)
        self.syncDatabaseRadioButton.setObjectName("syncDatabaseRadioButton")
        self.gridLayout_2.addWidget(self.syncDatabaseRadioButton, 2, 0, 1, 1)

        self.retranslateUi(renameDialog)
        QtCore.QMetaObject.connectSlotsByName(renameDialog)

    def retranslateUi(self, renameDialog):
        renameDialog.setWindowTitle(QtGui.QApplication.translate("renameDialog", "Rename Fields", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSaveRenames.setText(QtGui.QApplication.translate("renameDialog", "Save Renames", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLoadTemplate.setText(QtGui.QApplication.translate("renameDialog", "Load Template", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSaveFile.setText(QtGui.QApplication.translate("renameDialog", "Save File", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseBtn.setText(QtGui.QApplication.translate("renameDialog", "Set Case", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(0, QtGui.QApplication.translate("renameDialog", "default", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(1, QtGui.QApplication.translate("renameDialog", "lower", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(2, QtGui.QApplication.translate("renameDialog", "Proper", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(3, QtGui.QApplication.translate("renameDialog", "UPPER", None, QtGui.QApplication.UnicodeUTF8))
        self.syncDatabaseRadioButton.setText(QtGui.QApplication.translate("renameDialog", "Sync Renames Database", None, QtGui.QApplication.UnicodeUTF8))

