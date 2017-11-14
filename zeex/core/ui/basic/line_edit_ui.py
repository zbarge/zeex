# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Zeke/Google Drive/dev/python/zeex/zeex/core/ui/basic/line_edit.ui'
#
# Created: Mon Nov 13 22:57:17 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_LineEditDialog(object):
    def setupUi(self, LineEditDialog):
        LineEditDialog.setObjectName("LineEditDialog")
        LineEditDialog.resize(294, 112)
        self.verticalLayoutWidget = QtGui.QWidget(LineEditDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 271, 91))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LineEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), LineEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), LineEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LineEditDialog)

    def retranslateUi(self, LineEditDialog):
        LineEditDialog.setWindowTitle(QtGui.QApplication.translate("LineEditDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LineEditDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

