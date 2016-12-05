# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'merge_purge.ui'
#
# Created: Sun Dec  4 16:43:10 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MergePurgeDialog(object):
    def setupUi(self, MergePurgeDialog):
        MergePurgeDialog.setObjectName("MergePurgeDialog")
        MergePurgeDialog.resize(421, 413)
        self.formLayoutWidget = QtGui.QWidget(MergePurgeDialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 20, 341, 361))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.sourcePathLabel = QtGui.QLabel(self.formLayoutWidget)
        self.sourcePathLabel.setObjectName("sourcePathLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.sourcePathLabel)
        self.sourcePathLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.sourcePathLineEdit.setObjectName("sourcePathLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.sourcePathLineEdit)
        self.destPathLabel = QtGui.QLabel(self.formLayoutWidget)
        self.destPathLabel.setObjectName("destPathLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.destPathLabel)
        self.destPathLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.destPathLineEdit.setObjectName("destPathLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.destPathLineEdit)
        self.sortOnLabel = QtGui.QLabel(self.formLayoutWidget)
        self.sortOnLabel.setObjectName("sortOnLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.sortOnLabel)
        self.sortOnColumnView = QtGui.QColumnView(self.formLayoutWidget)
        self.sortOnColumnView.setObjectName("sortOnColumnView")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.sortOnColumnView)
        self.dedupeOnLabel = QtGui.QLabel(self.formLayoutWidget)
        self.dedupeOnLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.dedupeOnLabel.setOpenExternalLinks(False)
        self.dedupeOnLabel.setObjectName("dedupeOnLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.dedupeOnLabel)
        self.dedupeOnListView = QtGui.QListView(self.formLayoutWidget)
        self.dedupeOnListView.setObjectName("dedupeOnListView")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.dedupeOnListView)
        self.btnGridLayout = QtGui.QGridLayout()
        self.btnGridLayout.setObjectName("btnGridLayout")
        self.btnCancel = QtGui.QPushButton(self.formLayoutWidget)
        self.btnCancel.setObjectName("btnCancel")
        self.btnGridLayout.addWidget(self.btnCancel, 0, 1, 1, 1)
        self.btnExecute = QtGui.QPushButton(self.formLayoutWidget)
        self.btnExecute.setObjectName("btnExecute")
        self.btnGridLayout.addWidget(self.btnExecute, 0, 0, 1, 1)
        self.formLayout.setLayout(4, QtGui.QFormLayout.FieldRole, self.btnGridLayout)

        self.retranslateUi(MergePurgeDialog)
        QtCore.QMetaObject.connectSlotsByName(MergePurgeDialog)

    def retranslateUi(self, MergePurgeDialog):
        MergePurgeDialog.setWindowTitle(QtGui.QApplication.translate("MergePurgeDialog", "Merge/Purge", None, QtGui.QApplication.UnicodeUTF8))
        self.sourcePathLabel.setText(QtGui.QApplication.translate("MergePurgeDialog", "Source Path", None, QtGui.QApplication.UnicodeUTF8))
        self.destPathLabel.setText(QtGui.QApplication.translate("MergePurgeDialog", "Destination Path", None, QtGui.QApplication.UnicodeUTF8))
        self.sortOnLabel.setText(QtGui.QApplication.translate("MergePurgeDialog", "Sort On", None, QtGui.QApplication.UnicodeUTF8))
        self.dedupeOnLabel.setText(QtGui.QApplication.translate("MergePurgeDialog", "Dedupe On", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("MergePurgeDialog", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExecute.setText(QtGui.QApplication.translate("MergePurgeDialog", "PushButton", None, QtGui.QApplication.UnicodeUTF8))

