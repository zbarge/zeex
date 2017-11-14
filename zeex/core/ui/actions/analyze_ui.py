# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Zeke/Google Drive/dev/python/zeex/zeex/core/ui/actions/analyze.ui'
#
# Created: Mon Nov 13 22:57:15 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FileAnalyzerDialog(object):
    def setupUi(self, FileAnalyzerDialog):
        FileAnalyzerDialog.setObjectName("FileAnalyzerDialog")
        FileAnalyzerDialog.resize(904, 505)
        self.gridLayoutWidget = QtGui.QWidget(FileAnalyzerDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 881, 471))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnRefresh = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnRefresh.setObjectName("btnRefresh")
        self.gridLayout_2.addWidget(self.btnRefresh, 1, 0, 1, 1)
        self.btnExport = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnExport.setObjectName("btnExport")
        self.gridLayout_2.addWidget(self.btnExport, 0, 0, 1, 1)
        self.btnPivot = QtGui.QPushButton(self.gridLayoutWidget)
        self.btnPivot.setObjectName("btnPivot")
        self.gridLayout_2.addWidget(self.btnPivot, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.tableView = QtGui.QTableView(self.gridLayoutWidget)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 0, 1, 1, 1)

        self.retranslateUi(FileAnalyzerDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), FileAnalyzerDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), FileAnalyzerDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FileAnalyzerDialog)

    def retranslateUi(self, FileAnalyzerDialog):
        FileAnalyzerDialog.setWindowTitle(QtGui.QApplication.translate("FileAnalyzerDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRefresh.setText(QtGui.QApplication.translate("FileAnalyzerDialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("FileAnalyzerDialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPivot.setText(QtGui.QApplication.translate("FileAnalyzerDialog", "Pivot", None, QtGui.QApplication.UnicodeUTF8))

