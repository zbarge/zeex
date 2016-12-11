# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 19:41:37 2016

@author: Zeke
"""


import sys
from core.main import ZeexApp

if __name__ == '__main__':

    #The main application
    app = ZeexApp(sys.argv)

    sys.exit(app.exec_())        
        

        



