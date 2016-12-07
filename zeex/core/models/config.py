# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:25:43 2016

@author: Zeke
"""
import os

data_dir = os.path.join(os.path.dirname(
                        os.path.dirname(
                        os.path.dirname(
                        os.path.dirname(__file__)))),
                        "data").replace("\\","/")

DEFAULT_SETTINGS = {'DATA_DIR': data_dir}


config = DEFAULT_SETTINGS