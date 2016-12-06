# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Sun Dec  4 09:43:09 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_HomeWindow(object):
    def setupUi(self, HomeWindow):
        HomeWindow.setObjectName("HomeWindow")
        HomeWindow.resize(800, 600)
        self.HomeWidget = QtGui.QWidget(HomeWindow)
        self.HomeWidget.setObjectName("HomeWidget")
        self.ProjectsTreeView = QtGui.QTreeView(self.HomeWidget)
        self.ProjectsTreeView.setGeometry(QtCore.QRect(35, 81, 721, 441))
        self.ProjectsTreeView.setObjectName("ProjectsTreeView")
        HomeWindow.setCentralWidget(self.HomeWidget)
        self.homemenu = QtGui.QMenuBar(HomeWindow)
        self.homemenu.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.homemenu.setObjectName("homemenu")
        self.menuProjects = QtGui.QMenu(self.homemenu)
        self.menuProjects.setObjectName("menuProjects")
        HomeWindow.setMenuBar(self.homemenu)
        self.statusbar = QtGui.QStatusBar(HomeWindow)
        self.statusbar.setObjectName("statusbar")
        HomeWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(HomeWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionNew = QtGui.QAction(HomeWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionSave = QtGui.QAction(HomeWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionEdit = QtGui.QAction(HomeWindow)
        self.actionEdit.setObjectName("actionEdit")
        self.actionSettings = QtGui.QAction(HomeWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.menuProjects.addAction(self.actionOpen)
        self.menuProjects.addAction(self.actionNew)
        self.menuProjects.addAction(self.actionSave)
        self.menuProjects.addAction(self.actionEdit)
        self.menuProjects.addAction(self.actionSettings)
        self.homemenu.addAction(self.menuProjects.menuAction())

        self.retranslateUi(HomeWindow)
        QtCore.QMetaObject.connectSlotsByName(HomeWindow)

    def retranslateUi(self, HomeWindow):
        HomeWindow.setWindowTitle(QtGui.QApplication.translate("HomeWindow", "Zeex Home", None, QtGui.QApplication.UnicodeUTF8))
        self.menuProjects.setTitle(QtGui.QApplication.translate("HomeWindow", "Projects", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("HomeWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("HomeWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("HomeWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEdit.setText(QtGui.QApplication.translate("HomeWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("HomeWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))

