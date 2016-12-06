# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'push_grid.ui'
#
# Created: Sun Dec  4 17:51:06 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PushGridWidget(object):
    def setupUi(self, PushGridWidget):
        PushGridWidget.setObjectName("PushGridWidget")
        PushGridWidget.resize(302, 203)
        self.gridLayoutWidget_2 = QtGui.QWidget(PushGridWidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 301, 201))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.pushGrid = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.pushGrid.setContentsMargins(0, 0, 0, 0)
        self.pushGrid.setObjectName("pushGrid")
        self.listViewLeft = QtGui.QListView(self.gridLayoutWidget_2)
        self.listViewLeft.setObjectName("listViewLeft")
        self.pushGrid.addWidget(self.listViewLeft, 0, 0, 1, 1)
        self.listViewRight = QtGui.QListView(self.gridLayoutWidget_2)
        self.listViewRight.setObjectName("listViewRight")
        self.pushGrid.addWidget(self.listViewRight, 0, 2, 1, 1)
        self.btnGrid = QtGui.QGridLayout()
        self.btnGrid.setObjectName("btnGrid")
        self.btnPushRight = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.btnPushRight.setObjectName("btnPushRight")
        self.btnGrid.addWidget(self.btnPushRight, 0, 0, 1, 1)
        self.btnPushLeft = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.btnPushLeft.setObjectName("btnPushLeft")
        self.btnGrid.addWidget(self.btnPushLeft, 1, 0, 1, 1)
        self.pushGrid.addLayout(self.btnGrid, 0, 1, 1, 1)

        self.retranslateUi(PushGridWidget)
        QtCore.QMetaObject.connectSlotsByName(PushGridWidget)

    def retranslateUi(self, PushGridWidget):
        PushGridWidget.setWindowTitle(QtGui.QApplication.translate("PushGridWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPushRight.setText(QtGui.QApplication.translate("PushGridWidget", ">>", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPushLeft.setText(QtGui.QApplication.translate("PushGridWidget", "<<", None, QtGui.QApplication.UnicodeUTF8))

