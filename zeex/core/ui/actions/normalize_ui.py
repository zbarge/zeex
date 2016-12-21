# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'normalize.ui'
#
# Created: Wed Dec 21 04:32:54 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ColumnNormalizerDialog(object):
    def setupUi(self, ColumnNormalizerDialog):
        ColumnNormalizerDialog.setObjectName("ColumnNormalizerDialog")
        ColumnNormalizerDialog.resize(357, 376)
        self.formLayoutWidget_2 = QtGui.QWidget(ColumnNormalizerDialog)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(30, 20, 295, 331))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtGui.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.removeSpecialCharactersLabel = QtGui.QLabel(self.formLayoutWidget_2)
        self.removeSpecialCharactersLabel.setObjectName("removeSpecialCharactersLabel")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.removeSpecialCharactersLabel)
        self.removeSpecialCharactersCheckBox = QtGui.QCheckBox(self.formLayoutWidget_2)
        self.removeSpecialCharactersCheckBox.setObjectName("removeSpecialCharactersCheckBox")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.removeSpecialCharactersCheckBox)
        self.trimSpacesLabel = QtGui.QLabel(self.formLayoutWidget_2)
        self.trimSpacesLabel.setObjectName("trimSpacesLabel")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.trimSpacesLabel)
        self.trimSpacesCheckBox = QtGui.QCheckBox(self.formLayoutWidget_2)
        self.trimSpacesCheckBox.setObjectName("trimSpacesCheckBox")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.trimSpacesCheckBox)
        self.comboBox_2 = QtGui.QComboBox(self.formLayoutWidget_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.comboBox_2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox = QtGui.QComboBox(self.formLayoutWidget_2)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.formLayoutWidget_2)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.mergeCheckBox = QtGui.QCheckBox(self.formLayoutWidget_2)
        self.mergeCheckBox.setObjectName("mergeCheckBox")
        self.gridLayout.addWidget(self.mergeCheckBox, 0, 0, 1, 1)
        self.formLayout_2.setLayout(3, QtGui.QFormLayout.FieldRole, self.gridLayout)
        self.replaceSpacesLabel = QtGui.QLabel(self.formLayoutWidget_2)
        self.replaceSpacesLabel.setObjectName("replaceSpacesLabel")
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.LabelRole, self.replaceSpacesLabel)
        self.replaceSpacesLineEdit = QtGui.QLineEdit(self.formLayoutWidget_2)
        self.replaceSpacesLineEdit.setObjectName("replaceSpacesLineEdit")
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.FieldRole, self.replaceSpacesLineEdit)
        self.setCaseLabel = QtGui.QLabel(self.formLayoutWidget_2)
        self.setCaseLabel.setObjectName("setCaseLabel")
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.LabelRole, self.setCaseLabel)
        self.setCaseComboBox = QtGui.QComboBox(self.formLayoutWidget_2)
        self.setCaseComboBox.setObjectName("setCaseComboBox")
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.FieldRole, self.setCaseComboBox)
        self.columnsLabel = QtGui.QLabel(self.formLayoutWidget_2)
        self.columnsLabel.setObjectName("columnsLabel")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.columnsLabel)
        self.listViewColumns = ColumnsListView(self.formLayoutWidget_2)
        self.listViewColumns.setObjectName("listViewColumns")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.listViewColumns)
        self.buttonBox = QtGui.QDialogButtonBox(self.formLayoutWidget_2)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(ColumnNormalizerDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ColumnNormalizerDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ColumnNormalizerDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ColumnNormalizerDialog)

    def retranslateUi(self, ColumnNormalizerDialog):
        ColumnNormalizerDialog.setWindowTitle(QtGui.QApplication.translate("ColumnNormalizerDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.removeSpecialCharactersLabel.setText(QtGui.QApplication.translate("ColumnNormalizerDialog", "Remove Special Characters", None, QtGui.QApplication.UnicodeUTF8))
        self.trimSpacesLabel.setText(QtGui.QApplication.translate("ColumnNormalizerDialog", "Trim Spaces", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_2.setItemText(0, QtGui.QApplication.translate("ColumnNormalizerDialog", "Merge", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_2.setItemText(1, QtGui.QApplication.translate("ColumnNormalizerDialog", "Split", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ColumnNormalizerDialog", "Separator", None, QtGui.QApplication.UnicodeUTF8))
        self.replaceSpacesLabel.setText(QtGui.QApplication.translate("ColumnNormalizerDialog", "Replace Spaces", None, QtGui.QApplication.UnicodeUTF8))
        self.setCaseLabel.setText(QtGui.QApplication.translate("ColumnNormalizerDialog", "Set Case", None, QtGui.QApplication.UnicodeUTF8))
        self.columnsLabel.setText(QtGui.QApplication.translate("ColumnNormalizerDialog", "Columns", None, QtGui.QApplication.UnicodeUTF8))

from core.views.dataframe import ColumnsListView
