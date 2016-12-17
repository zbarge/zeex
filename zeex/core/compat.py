# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 12:51:47 2016
MIT License

Copyright (c) 2016 Zeke Barge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from PySide import QtGui, QtCore, QtTest


def if_we_need_multi_version_support():
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


        