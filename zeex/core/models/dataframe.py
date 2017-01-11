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
import logging
from zeex.core.ctrls.dataframe import DataFrameModel


class DataFrameDescriptionModel(DataFrameModel):
    """
    A DataFrameModel that partners up with a source DataFrameModel
    providing a consistent description of data in the DataFrame.
    The purpose of this is to make analysis more simple and interface
    pandas.DataFrame.describe information.
    """
    def __init__(self, source_model: DataFrameModel = None, **kwargs):
        self.source_model = source_model
        self.source_model.dataChanged.connect(self.sync)
        DataFrameModel.__init__(self, dataFrame=self.get_describe_frame(self.df_source),
                                copyDataFrame=kwargs.get('copyDataFrame', False),
                                filePath=kwargs.get('filePath', self._get_describe_path()))

    def set_source_model(self, model):
        self.source_model = model
        self.source_model.dataChanged.connect(self.sync)
        self.sync()

    @property
    def df_source(self):
        return self.source_model.dataFrame()

    def sync(self):
        self.setDataFrame(self.get_describe_frame(self.df_source),
                          copyDataFrame=False,
                          filePath=self._get_describe_path())

    def _get_describe_path(self):
        return self.get_describe_path(self.source_model.filePath)

    @staticmethod
    def get_describe_path(file_path):
        try:
            base, ext = os.path.splitext(file_path)
        except:
            return None
        return "{}_desc{}".format(base, ext)

    @staticmethod
    def get_describe_frame(df, index_label='category', include='all', **kwargs):
        try:
            df = df.describe(include=include, **kwargs)
            orig_cols = df.columns.tolist()
            df.index.name = index_label
            df.reset_index(drop=False, inplace=True)

            if df.index.size < len(orig_cols):
                df = df.transpose().reset_index()
                df.columns = [df.iloc[0][c] for c in df.columns]
                df = df[1:]
        except TypeError as e:
            df = pd.DataFrame()
            # TODO: Figure out how to overcome this?
            logging.warning('DataFrameDescriptionDialog.get_describe_frame: Error getting describe frame: {}'.format(e))

        return df