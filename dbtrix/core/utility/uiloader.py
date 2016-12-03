# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 11:24:29 2016

@author: Zeke
"""

from PySide import QtCore, QtUiTools


def loadUiWidget(uifilename, parent=None):
    loader = QtUiTools.QUiLoader()
    uifile = QtCore.QFile(uifilename)
    uifile.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uifile, parent)
    uifile.close()
    return ui
