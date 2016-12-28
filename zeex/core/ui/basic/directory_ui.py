# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'directory.ui'
#
# Created: Wed Dec 28 14:31:35 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_DirectoryViewDialog(object):
    def setupUi(self, DirectoryViewDialog):
        DirectoryViewDialog.setObjectName("DirectoryViewDialog")
        DirectoryViewDialog.resize(408, 337)
        self.gridLayoutWidget = QtGui.QWidget(DirectoryViewDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 20, 371, 301))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnRefresh = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnRefresh.setObjectName("btnRefresh")
        self.gridLayout_2.addWidget(self.btnRefresh, 4, 0, 1, 1)
        self.btnUpload = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnUpload.setObjectName("btnUpload")
        self.gridLayout_2.addWidget(self.btnUpload, 0, 0, 1, 1)
        self.btnDelete = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnDelete.setObjectName("btnDelete")
        self.gridLayout_2.addWidget(self.btnDelete, 3, 0, 1, 1)
        self.btnDownload = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnDownload.setObjectName("btnDownload")
        self.gridLayout_2.addWidget(self.btnDownload, 1, 0, 1, 1)
        self.btnAddFolder = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnAddFolder.setObjectName("btnAddFolder")
        self.gridLayout_2.addWidget(self.btnAddFolder, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.treeView = QtGui.QTreeView(self.gridLayoutWidget)
        self.treeView.setObjectName("treeView")
        self.gridLayout.addWidget(self.treeView, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi(DirectoryViewDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DirectoryViewDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DirectoryViewDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DirectoryViewDialog)

    def retranslateUi(self, DirectoryViewDialog):
        DirectoryViewDialog.setWindowTitle(QtGui.QApplication.translate("DirectoryViewDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRefresh.setText(QtGui.QApplication.translate("DirectoryViewDialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.btnUpload.setText(QtGui.QApplication.translate("DirectoryViewDialog", "Upload", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("DirectoryViewDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDownload.setText(QtGui.QApplication.translate("DirectoryViewDialog", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAddFolder.setText(QtGui.QApplication.translate("DirectoryViewDialog", "Add Folder", None, QtGui.QApplication.UnicodeUTF8))

