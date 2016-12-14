# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 20:57:39 2016

@author: Zeke
"""
import os
import pandas as pd
import qtpandas
from collections import defaultdict
import datetime
from core.compat import QtCore


class DataFrameModelManager(QtCore.QObject):
    """
    A central storage unit for managing
    DataFrameModels.
    """
    signalNewModelRead = QtCore.Signal(str)
    signalModelDestroyed = QtCore.Signal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self._models = {}
        self._updates = defaultdict(list)
        self._paths_read = []
        self._paths_updated = []

    @property
    def file_paths(self):
        return list(self._models.keys())

    @property
    def models(self):
        return list(self._models.values())

    @property
    def last_path_read(self):
        if self._paths_read:
            return self._paths_read[-1]
        else:
            return None

    @property
    def last_path_updated(self):
        if self._paths_updated:
            return self._paths_updated[-1]
        else:
            return None

    def save_file(self, filepath, save_as=None, keep_orig=False, **kwargs):
        df = self._models[filepath].dataFrame()
        kwargs['index'] = kwargs.get('index', False)

        if save_as is not None:
            to_path = save_as
        else:
            to_path = filepath

        ext = os.path.splitext(to_path)[1].lower()

        if ext == ".xlsx":
            kwargs.pop('sep', None)
            df.to_excel(to_path, **kwargs)
            
        elif ext in ['.csv','.txt']:
            df.to_csv(to_path, **kwargs)
            
        else:
            raise NotImplementedError("Cannot save file of type {}".format(ext))
        
        if save_as is not None:
            if  keep_orig is False:
                # Re-purpose the original model
                model = self._models.pop(filepath)
                model._filePath = to_path
            else:
                # Create a new model.
                model = qtpandas.DataFrameModel()
                model.setDataFrame(df, copyDataFrame=True, filePath=to_path)

            self._models[to_path] = model

    def set_model(self, df_model: qtpandas.DataFrameModel, file_path):
        assert isinstance(df_model, qtpandas.DataFrameModel), "df_model argument must be a DataFrameModel!"
        df_model._filePath = file_path

        try:
            self._models[file_path]
        except KeyError:
            self.signalNewModelRead.emit(file_path)

        self._models[file_path] = df_model

    def get_model(self, filepath):
        return self._models[filepath]

    def get_frame(self, filepath):
        return self._models[filepath].dataFrame()
            
    def update_file(self, filepath, df, notes=None):
        assert isinstance(df, pd.DataFrame), "Cannot update file with type '{}'".format(type(df))
        
        self._models[filepath].setDataFrame(df, copyDataFrame=False)
        
        if notes:
            update = dict(date=pd.Timestamp(datetime.datetime.now()),
                                                     notes=notes)
            
            self._updates[filepath].append(update)
        self._paths_updated.append(filepath)
        
    def remove_file(self, filepath):
        self._models.pop(filepath)
        self.signalModelDestroyed.emit(filepath)

    def read_file(self, filepath, **kwargs):
        try:
            model = self._models[filepath]
        except KeyError:
            model = qtpandas.read_file(filepath, **kwargs)
            self._models[filepath] = model
            self.signalNewModelRead.emit(filepath)
        finally:
            self._paths_read.append(filepath)
            
        return model
    