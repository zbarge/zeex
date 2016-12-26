"""
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

from core.compat import QtGui, QtCore
import pandas as pd
from collections import defaultdict
from core.utility.widgets import create_standard_item_model


def series_minmax(series:pd.Series):
    return [series.min(), series.max()]


def series_median(series:pd.Series):
    return series.mean()


def series_sum(series:pd.Series):
    return series.sum()


def series_count(series:pd.Series):
    return series.count()


class DataFrameAnalyzer(object):
    DATES = 'dates'
    NUMBERS = 'numbers'
    STRINGS = 'strings'
    __types__ = [DATES, NUMBERS, STRINGS]

    def __init__(self, df):
        self._df = df
        self._methods = defaultdict(list)
        self._columns = defaultdict(list)
        self._scan_dtypes()
        self.set_default_methods()
        self.results = dict()

    @property
    def columns(self):
        return self._columns

    @property
    def methods(self):
        return self._methods

    def process_all_methods(self, reprocess=True):
        if not self.results or reprocess:
            results = {dtype: self.get_results(dtype) for dtype in self.__types__}
            self.results = results

    def get_results(self, dtype):
        columns = self.columns[dtype]
        methods = self.methods[dtype]
        return {c:{m.__name__: m(self.df.loc[:, c].dropna()) for m in methods}
                for c in columns}

    def set_dataframe(self, df):
        assert isinstance(df, pd.DataFrame)
        self._df = df
        self._scan_dtypes()

    def set_method(self, dtype, method):
        self.methods[dtype].append(method)

    def set_default_methods(self):
        self.methods[self.STRINGS].extend([series_count])
        self.methods[self.DATES].extend([series_median, series_minmax])
        self.methods[self.NUMBERS].extend([series_count, series_median, series_minmax, series_sum])

    def get_column_view_model(self):
        dtype_model = QtGui.QStandardItemModel()
        dtype_row = 0
        for dtype, info in self.results.items():
            dtype = QtGui.QStandardItem(str(dtype))
            field_row = 0
            for field_name, totals in info.items():
                field_name = QtGui.QStandardItem(str(field_name))
                method_row = 0
                for method_name, method_result in totals.items():
                    method_name = QtGui.QStandardItem(str(method_name))
                    method_result = QtGui.QStandardItem(str(method_result))
                    method_name.setChild(0, 0, method_result)
                    field_name.setChild(method_row, 0, method_name)
                    method_row += 1
                field_row += 1
                dtype.setChild(field_row, 0, field_name)
            dtype_model.setItem(dtype_row, 0, dtype)
            dtype_row += 1
        return dtype_model

    def get_table_view_model(self):
        dtype_model = QtGui.QStandardItemModel()
        field_row = 0
        method_names = []
        [method_names.extend([x.__name__ for x in self.methods[n]]) for n in self.methods.keys()]
        method_names = list(set(method_names))
        method_positions = {n: i for i,n in enumerate(method_names, 2)}
        col_names = ['Data Type', 'Field'] + [n.title() for n in method_names]
        dtype_model.setHorizontalHeaderLabels(col_names)

        for dtype, info in sorted(self.results.items()):
            dtype = QtGui.QStandardItem(str(dtype))

            for field_name, totals in sorted(info.items()):
                field_name = QtGui.QStandardItem(str(field_name))
                dtype_model.setItem(field_row, 0, dtype.clone())
                dtype_model.setItem(field_row, 1, field_name)

                for method_name, method_result in totals.items():
                    col_num = method_positions[method_name]
                    method_result = QtGui.QStandardItem(str(method_result))
                    dtype_model.setItem(field_row, col_num, method_result)

                field_row += 1

        return dtype_model

    @property
    def df(self):
        return self._df

    def _scan_dtypes(self):
        for c in self._df.columns:
            d = str(self._df[c].dtype)
            if 'date' in d:
                self.columns['date'].append(c)
            elif 'int' in d or 'float' in d:
                self.columns['numbers'].append(c)
            elif 'object' in d or 'str' in d:
                self.columns['strings'].append(c)
            else:
                raise NotImplementedError("Update DataFrameAnalyzer._scan_dtypes for '{} - {}'".format(c, d))

