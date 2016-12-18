# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fields_edit.ui'
#
# Created: Sat Dec 17 17:31:45 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FieldsEditDialog(object):
    def setupUi(self, FieldsEditDialog):
        FieldsEditDialog.setObjectName("FieldsEditDialog")
        FieldsEditDialog.resize(764, 488)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FieldsEditDialog.sizePolicy().hasHeightForWidth())
        FieldsEditDialog.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(FieldsEditDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.tableView = QtGui.QTableView(FieldsEditDialog)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnExportTemplate = QtGui.QPushButton(FieldsEditDialog)
        self.btnExportTemplate.setObjectName("btnExportTemplate")
        self.gridLayout_2.addWidget(self.btnExportTemplate, 4, 0, 1, 1)
        self.btnLoadTemplate = QtGui.QPushButton(FieldsEditDialog)
        self.btnLoadTemplate.setObjectName("btnLoadTemplate")
        self.gridLayout_2.addWidget(self.btnLoadTemplate, 3, 0, 1, 1)
        self.btnSaveFile = QtGui.QPushButton(FieldsEditDialog)
        self.btnSaveFile.setObjectName("btnSaveFile")
        self.gridLayout_2.addWidget(self.btnSaveFile, 0, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.setCaseComboBox = QtGui.QComboBox(FieldsEditDialog)
        self.setCaseComboBox.setObjectName("setCaseComboBox")
        self.setCaseComboBox.addItem("")
        self.setCaseComboBox.addItem("")
        self.setCaseComboBox.addItem("")
        self.setCaseComboBox.addItem("")
        self.gridLayout_3.addWidget(self.setCaseComboBox, 0, 0, 1, 1)
        self.btnSetCase = QtGui.QPushButton(FieldsEditDialog)
        self.btnSetCase.setObjectName("btnSetCase")
        self.gridLayout_3.addWidget(self.btnSetCase, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 10, 0, 1, 1)
        self.radioBtnSyncDatabase = QtGui.QRadioButton(FieldsEditDialog)
        self.radioBtnSyncDatabase.setChecked(True)
        self.radioBtnSyncDatabase.setObjectName("radioBtnSyncDatabase")
        self.gridLayout_2.addWidget(self.radioBtnSyncDatabase, 2, 0, 1, 1)
        self.btnReset = QtGui.QPushButton(FieldsEditDialog)
        self.btnReset.setObjectName("btnReset")
        self.gridLayout_2.addWidget(self.btnReset, 1, 0, 1, 1)
        self.btnParseDates = QtGui.QPushButton(FieldsEditDialog)
        self.btnParseDates.setObjectName("btnParseDates")
        self.gridLayout_2.addWidget(self.btnParseDates, 7, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(150, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 6, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)

        self.retranslateUi(FieldsEditDialog)
        QtCore.QMetaObject.connectSlotsByName(FieldsEditDialog)

    def retranslateUi(self, FieldsEditDialog):
        FieldsEditDialog.setWindowTitle(QtGui.QApplication.translate("FieldsEditDialog", "Edit Fields", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExportTemplate.setText(QtGui.QApplication.translate("FieldsEditDialog", "Save Template", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLoadTemplate.setText(QtGui.QApplication.translate("FieldsEditDialog", "Load Template", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSaveFile.setText(QtGui.QApplication.translate("FieldsEditDialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(0, QtGui.QApplication.translate("FieldsEditDialog", "default", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(1, QtGui.QApplication.translate("FieldsEditDialog", "lower", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(2, QtGui.QApplication.translate("FieldsEditDialog", "Proper", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseComboBox.setItemText(3, QtGui.QApplication.translate("FieldsEditDialog", "UPPER", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSetCase.setText(QtGui.QApplication.translate("FieldsEditDialog", "Set Case", None, QtGui.QApplication.UnicodeUTF8))
        self.radioBtnSyncDatabase.setText(QtGui.QApplication.translate("FieldsEditDialog", "Sync Database", None, QtGui.QApplication.UnicodeUTF8))
        self.btnReset.setText(QtGui.QApplication.translate("FieldsEditDialog", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.btnParseDates.setText(QtGui.QApplication.translate("FieldsEditDialog", "Parse Dates", None, QtGui.QApplication.UnicodeUTF8))

