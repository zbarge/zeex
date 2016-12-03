# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:45:23 2016

@author: Zeke
"""

def configureComboBox(box, options, default):
    box.addItems(options)
    idx = box.findText(default)
    if idx >= 0:
        box.setCurrentIndex(idx)
    return box