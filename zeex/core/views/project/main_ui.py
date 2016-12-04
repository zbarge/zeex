# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Sun Dec  4 09:46:04 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ProjectWindow(object):
    def setupUi(self, ProjectWindow):
        ProjectWindow.setObjectName("ProjectWindow")
        ProjectWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(ProjectWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ProjectsTreeView = QtGui.QTreeView(self.centralwidget)
        self.ProjectsTreeView.setGeometry(QtCore.QRect(40, 110, 721, 441))
        self.ProjectsTreeView.setObjectName("ProjectsTreeView")
        ProjectWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ProjectWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuRecent_Files = QtGui.QMenu(self.menubar)
        self.menuRecent_Files.setObjectName("menuRecent_Files")
        ProjectWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(ProjectWindow)
        self.statusbar.setObjectName("statusbar")
        ProjectWindow.setStatusBar(self.statusbar)
        self.actionNew = QtGui.QAction(ProjectWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtGui.QAction(ProjectWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtGui.QAction(ProjectWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionRemove = QtGui.QAction(ProjectWindow)
        self.actionRemove.setObjectName("actionRemove")
        self.actionPreferences = QtGui.QAction(ProjectWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionRemove)
        self.menuSettings.addAction(self.actionPreferences)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuRecent_Files.menuAction())

        self.retranslateUi(ProjectWindow)
        QtCore.QMetaObject.connectSlotsByName(ProjectWindow)

    def retranslateUi(self, ProjectWindow):
        ProjectWindow.setWindowTitle(QtGui.QApplication.translate("ProjectWindow", "MyProject", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("ProjectWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setTitle(QtGui.QApplication.translate("ProjectWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRecent_Files.setTitle(QtGui.QApplication.translate("ProjectWindow", "Recent Files", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("ProjectWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("ProjectWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("ProjectWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemove.setText(QtGui.QApplication.translate("ProjectWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("ProjectWindow", "Preferences", None, QtGui.QApplication.UnicodeUTF8))

