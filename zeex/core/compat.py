# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 12:51:47 2016

@author: Zeke
"""
try:
    from PySide import QtGui, QtCore
except ImportError:
    try:
        from PyQt4 import QtGui, QtCore
    except ImportError:
        try:
            from PyQt5 import QtGui, QtCore, Qt
        except ImportError:
            raise ImportError("Cannot import PySide, PyQt4, or PyQt5, please install PySide (preferred) or one of the others.")










TRUES = ['TRUE','YES','Y']
UNQUOTE_OPTIONS = {'"':'',
                   "'":'', 
                   "{":'',
                   "}":'',
                   "]":'',
                   '[':'',
                   '(':'',
                   ')':''}  

def string_to_bool(x):
    if isinstance(x, bool):
        return x
    else:
        x = str(x).upper()
        if x in TRUES:
            return True
        else:
            return False
            
         
def string_unquote(x):
    """
    Tries to unquote a string 
    """
    try:
        UNQUOTE_OPTIONS[x[0]]
        UNQUOTE_OPTIONS[x[-1]]
        return x[1:-1]
    except KeyError:
        return x
    
    
def string_to_list(x):
    if isinstance(x, list):
        return x
    else:
        x = str(x)
        if not x:
            x = "None"
        #convert stringified lists/sequences
        x = string_unquote(x)
                
        #Split strings by comma        
        if "," in x:
            x = [string_unquote(v.lstrip().rstrip()) for v in x.split(",")]
        else:
            #Make list of 1 item.
            x = [x]
            
    return x


        