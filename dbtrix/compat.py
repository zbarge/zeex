# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 12:51:47 2016

@author: Zeke
"""
TRUES = ['TRUE','YES','Y']


def string_to_bool(x):
    if isinstance(x, bool):
        return x
    else:
        x = str(x).upper()
        if x in TRUES:
            return True
        else:
            return False

def string_to_list(x):
    if isinstance(x, list):
        return x
    else:
        x = str(x)
        if "," in x:
            x = [v.lstrip().rstrip() for v in x.split(",")]
        else:
            x = [x]
    return x


        