# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 11:04:32 2016

@author: Zeke
"""
from core.models.filetree import FileTreeModel
from PySide import QtGui, QtCore

class FileTreeView(QtGui.QTreeView):
    def __init__(self, parent=None, root_dir=None):
        super(FileTreeView, self).__init__(parent)
        self._model = FileTreeModel(parent=parent, root_dir=root_dir)
        self.setModel(self._model)
        self.setRootIndex( self._model.index( QtCore.QDir.currentPath() ) )