# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 00:03:14 2016
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
import os

def path_incremented(p, overwrite=False):
    """
    Increments a file path so you don't overwrite
    an existing file (unless you choose to).
    :param p: (str)
        The file path to possibly increment
    :param overwrite: (str)
        True will just increment once and return the path.
        False will keep incrementing until the path is available
    :return:
        The original file path if it doesn't exist.
        The file path incremented by 1 until it doesn't exist.
    """
    dirname = os.path.dirname(p)
    while os.path.exists(p):
        name = os.path.basename(p)
        name, ext = os.path.splitext(name)

        try:
            val = ''.join(e for e in name if e.isdigit())
            count = int(val) + 1
            name = name.replace(val, str(count))
        except ValueError:
            name = "{}{}".format(name, 2)
        p = os.path.join(dirname, name + ext)
        if overwrite is True:
            break
    return p

