# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'query_editor.ui'
#
# Created: Mon Jan  2 16:41:59 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_QueryEditorWindow(object):
    def setupUi(self, QueryEditorWindow):
        QueryEditorWindow.setObjectName("QueryEditorWindow")
        QueryEditorWindow.resize(746, 642)
        self.centralwidget = QtGui.QWidget(QueryEditorWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtGui.QTableView(self.centralwidget)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        QueryEditorWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(QueryEditorWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 746, 21))
        self.menubar.setObjectName("menubar")
        self.menuActions = QtGui.QMenu(self.menubar)
        self.menuActions.setObjectName("menuActions")
        QueryEditorWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(QueryEditorWindow)
        self.statusbar.setObjectName("statusbar")
        QueryEditorWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(QueryEditorWindow)
        self.toolBar.setObjectName("toolBar")
        QueryEditorWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionCommit = QtGui.QAction(QueryEditorWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/standard_icons/save.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.actionCommit.setIcon(icon)
        self.actionCommit.setObjectName("actionCommit")
        self.actionUndo = QtGui.QAction(QueryEditorWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/standard_icons/undo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUndo.setIcon(icon1)
        self.actionUndo.setObjectName("actionUndo")
        self.actionCriteria = QtGui.QAction(QueryEditorWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/standard_icons/filter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCriteria.setIcon(icon2)
        self.actionCriteria.setObjectName("actionCriteria")
        self.actionRefresh = QtGui.QAction(QueryEditorWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/standard_icons/refresh.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.actionRefresh.setIcon(icon3)
        self.actionRefresh.setObjectName("actionRefresh")
        self.menuActions.addAction(self.actionCommit)
        self.menuActions.addAction(self.actionUndo)
        self.menuActions.addAction(self.actionCriteria)
        self.menuActions.addAction(self.actionRefresh)
        self.menubar.addAction(self.menuActions.menuAction())
        self.toolBar.addAction(self.actionCommit)
        self.toolBar.addAction(self.actionUndo)
        self.toolBar.addAction(self.actionRefresh)
        self.toolBar.addAction(self.actionCriteria)

        self.retranslateUi(QueryEditorWindow)
        QtCore.QMetaObject.connectSlotsByName(QueryEditorWindow)

    def retranslateUi(self, QueryEditorWindow):
        QueryEditorWindow.setWindowTitle(QtGui.QApplication.translate("QueryEditorWindow", "Query Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.menuActions.setTitle(QtGui.QApplication.translate("QueryEditorWindow", "Actions", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("QueryEditorWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCommit.setText(QtGui.QApplication.translate("QueryEditorWindow", "Commit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCommit.setToolTip(QtGui.QApplication.translate("QueryEditorWindow", "Commit changes to the database", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUndo.setText(QtGui.QApplication.translate("QueryEditorWindow", "Undo", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUndo.setToolTip(QtGui.QApplication.translate("QueryEditorWindow", "Rollback changes made to data", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCriteria.setText(QtGui.QApplication.translate("QueryEditorWindow", "Criteria", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCriteria.setToolTip(QtGui.QApplication.translate("QueryEditorWindow", "View or change criteria", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefresh.setText(QtGui.QApplication.translate("QueryEditorWindow", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRefresh.setToolTip(QtGui.QApplication.translate("QueryEditorWindow", "Refresh data from the database/reset filters", None, QtGui.QApplication.UnicodeUTF8))

from zeex.icons import icons_rc
