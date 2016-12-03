# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 11:04:32 2016

@author: Zeke
"""

from PySide import QtGui

class FileTreeModel(QtGui.QFileSystemModel):
    def __init__(self, parent=None, root_dir=None):
        super(FileTreeModel, self).__init__(parent)
        self._root_dir = root_dir
        self.setRootPath(self._root_dir)