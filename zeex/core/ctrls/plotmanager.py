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

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import pyqtgraph as pg


class FramePlotter(object):
    def __init__(self, name, df, data):
        self.name = name
        self.df = df
        self.data = data
        self.plot_type = None
        self.plot_df = None

    def set_plot_type(self, x):
        self.plot_type = x

    def set_plot_df(self, df, plot_type=None):
        if plot_type:
            self.plot_type = plot_type
        self.plot_df = df

    def set_data(self, data):
        self.data = data

    def to_file(self, file_path):
        raise NotImplemented("Child classes must implement this method")

    def from_file(self, file_path):
        raise NotImplemented("Child classes must implement this method")

    def from_dataframe(self, df):
        raise NotImplemented("Child classes must implement this method")

    def to_div(self, data):
        return py.offline.plot(data, include_plotlyjs=False, output_type='div')

    def to_html(self, data):
        pass





class PlotManager(object):
    FILE_FORMATS = ['.png', '.html']
    def __init__(self, directory=None, file_formats:list=None, plots=None):
        self._directory = directory
        self._file_formats = (file_formats if file_formats is not None else self.FILE_FORMATS)
        self._plotters = plots or {}

    @property
    def directory(self):
        return self._directory

    @property
    def file_formats(self):
        return self._file_formats

    @property
    def plots(self):
        return self._plots

    def register_plotter(self, plotter):
        self._plotters[plotter.name] = plotter

    def plotter(self, name) -> FramePlotter:
        return self._plotters.get(name, None)



