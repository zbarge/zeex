# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 19:41:37 2016

@author: Zeke
"""

from core.compat import QtGui
from core.models.main import Model
from core.ctrls.main import MainController
from core.views.main import ZeexMainWindow


def pprint_dict(dictionary):
    for key, val in dictionary.items():
        print("{}: {}".format(key, val))
      

class ZeexApp(QtGui.QApplication):
    def __init__(self, sys_argv):
        super(ZeexApp, self).__init__(sys_argv)
        self.model = Model()
        self.main_ctrl = MainController(self.model)
        self.main_view = ZeexMainWindow()
        self.main_view.show()

