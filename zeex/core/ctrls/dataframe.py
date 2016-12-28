# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 20:57:39 2016

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
import pandas as pd
import qtpandas
from collections import defaultdict
import datetime
from core.compat import QtCore
from qtpandas.models.DataFrameModelManager import DataFrameModelManager as DFM, DataFrameModel
from core.models.dataframe import DataFrameDescriptionModel

SEPARATORS = {'Comma': ',',
              'Semicolon': ';',
              'Tab': "\t",
              'Pipe': '|'}

ENCODINGS = {'UTF-8':'UTF_8',
             'ASCII':'ASCII',
             'UTF-16':'UTF_16',
             'UTF-32':'UTF_32',
             'ISO-8859-1':'ISO-8859-1'}


class DataFrameModelManager(DFM):
    """
    A central storage unit for managing
    DataFrameModels.
    """
    def __init__(self):
        DFM.__init__(self)

    def get_df_describe_model(self, filepath):
        describe_path = DataFrameDescriptionModel.get_describe_path(filepath)
        try:
            return self.models[describe_path]
        except KeyError:
            dfm = self.read_file(filepath)
            dfm2 = DataFrameDescriptionModel(source_model=dfm, filePath=describe_path)
            self.set_model(dfm2, describe_path)
            return self.get_model(describe_path)