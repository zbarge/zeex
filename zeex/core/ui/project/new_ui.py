# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Zeke/Google Drive/dev/python/zeex/zeex/core/ui/project/new.ui'
#
# Created: Mon Nov 13 22:57:18 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_NewProjectDialog(object):
    def setupUi(self, NewProjectDialog):
        NewProjectDialog.setObjectName("NewProjectDialog")
        NewProjectDialog.resize(514, 243)
        self.buttonBox = QtGui.QDialogButtonBox(NewProjectDialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtGui.QWidget(NewProjectDialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 40, 481, 111))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtGui.QLabel(self.formLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.nameLabel)
        self.settingsFileLabel = QtGui.QLabel(self.formLayoutWidget)
        self.settingsFileLabel.setObjectName("settingsFileLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.settingsFileLabel)
        self.nameGridLayout = QtGui.QGridLayout()
        self.nameGridLayout.setObjectName("nameGridLayout")
        self.namePushButton = QtGui.QPushButton(self.formLayoutWidget)
        self.namePushButton.setObjectName("namePushButton")
        self.nameGridLayout.addWidget(self.namePushButton, 0, 1, 1, 1)
        self.nameLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameGridLayout.addWidget(self.nameLineEdit, 0, 0, 1, 1)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.nameGridLayout)
        self.settingsFileGridLayout = QtGui.QGridLayout()
        self.settingsFileGridLayout.setObjectName("settingsFileGridLayout")
        self.settingsFilePushButton = QtGui.QPushButton(self.formLayoutWidget)
        self.settingsFilePushButton.setObjectName("settingsFilePushButton")
        self.settingsFileGridLayout.addWidget(self.settingsFilePushButton, 0, 1, 1, 1)
        self.settingsFileLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.settingsFileLineEdit.setObjectName("settingsFileLineEdit")
        self.settingsFileGridLayout.addWidget(self.settingsFileLineEdit, 0, 0, 1, 1)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.settingsFileGridLayout)

        self.retranslateUi(NewProjectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewProjectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewProjectDialog)

    def retranslateUi(self, NewProjectDialog):
        NewProjectDialog.setWindowTitle(QtGui.QApplication.translate("NewProjectDialog", "New Project", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLabel.setText(QtGui.QApplication.translate("NewProjectDialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.settingsFileLabel.setText(QtGui.QApplication.translate("NewProjectDialog", "Settings File", None, QtGui.QApplication.UnicodeUTF8))
        self.namePushButton.setText(QtGui.QApplication.translate("NewProjectDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.settingsFilePushButton.setText(QtGui.QApplication.translate("NewProjectDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))

