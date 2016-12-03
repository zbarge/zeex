# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 19:41:37 2016

@author: Zeke
PyQT
PACKAGE CONTENTS
    QtCore
    QtDeclarative
    QtGui
    QtHelp
    QtMultimedia
    QtNetwork
    QtOpenGL
    QtScript
    QtScriptTools
    QtSql
    QtSvg
    QtTest
    QtUiTools
    QtWebKit
    QtXml
    QtXmlPatterns
    _utils
    phonon
    scripts (package)
    shiboken
"""


import sys
from core.main import ZeexApp
        

if __name__ == '__main__':

    app = ZeexApp(sys.argv)

    sys.exit(app.exec_())        
        

        



