# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Thu Dec  8 23:41:34 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ProjectWindow(object):
    def setupUi(self, ProjectWindow):
        ProjectWindow.setObjectName("ProjectWindow")
        ProjectWindow.resize(644, 422)
        self.centralwidget = QtGui.QWidget(ProjectWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ProjectsTreeView = QtGui.QTreeView(self.centralwidget)
        self.ProjectsTreeView.setObjectName("ProjectsTreeView")
        self.horizontalLayout.addWidget(self.ProjectsTreeView)
        ProjectWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ProjectWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 644, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuRecent_Files = QtGui.QMenu(self.menubar)
        self.menuRecent_Files.setObjectName("menuRecent_Files")
        self.menuActions = QtGui.QMenu(self.menubar)
        self.menuActions.setObjectName("menuActions")
        ProjectWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(ProjectWindow)
        self.statusbar.setObjectName("statusbar")
        ProjectWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(ProjectWindow)
        self.toolBar.setObjectName("toolBar")
        ProjectWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
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
        self.actionMerge_Purge = QtGui.QAction(ProjectWindow)
        self.actionMerge_Purge.setObjectName("actionMerge_Purge")
        self.actionRename = QtGui.QAction(ProjectWindow)
        self.actionRename.setObjectName("actionRename")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionRemove)
        self.menuSettings.addAction(self.actionPreferences)
        self.menuActions.addAction(self.actionMerge_Purge)
        self.menuActions.addAction(self.actionRename)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuRecent_Files.menuAction())
        self.menubar.addAction(self.menuActions.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.toolBar.addSeparator()

        self.retranslateUi(ProjectWindow)
        QtCore.QMetaObject.connectSlotsByName(ProjectWindow)

    def retranslateUi(self, ProjectWindow):
        ProjectWindow.setWindowTitle(QtGui.QApplication.translate("ProjectWindow", "MyProject", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("ProjectWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setTitle(QtGui.QApplication.translate("ProjectWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRecent_Files.setTitle(QtGui.QApplication.translate("ProjectWindow", "Recent", None, QtGui.QApplication.UnicodeUTF8))
        self.menuActions.setTitle(QtGui.QApplication.translate("ProjectWindow", "Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("ProjectWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("ProjectWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("ProjectWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("ProjectWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemove.setText(QtGui.QApplication.translate("ProjectWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("ProjectWindow", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMerge_Purge.setText(QtGui.QApplication.translate("ProjectWindow", "Merge/Purge", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRename.setText(QtGui.QApplication.translate("ProjectWindow", "Rename", None, QtGui.QApplication.UnicodeUTF8))

