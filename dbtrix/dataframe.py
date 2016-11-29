# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 20:57:39 2016

@author: Zeke
"""
import os
import pandas as pd
from collections import defaultdict
import datetime



class DataFrameManager:
    
    def __init__(self):
        self._file_paths = {}
        self._file_updates = defaultdict(list)
    
    def save_file(self, filepath, **kwargs):
        df = self._file_paths[filepath]
        ext = os.path.splitext(filepath)[1].lower()
        
        kwargs['index'] = kwargs.get('index', False)
        
        if ext == ".xlsx":
            df.to_excel(filepath, **kwargs)
            
        elif ext in ['.csv','.txt']:
            df.to_csv(filepath, **kwargs)
            
        else:
            raise NotImplementedError("Cannot save file of type {}".format(ext))

            
    def update_file(self, filepath, df, notes=None):
        assert isinstance(df, pd.DataFrame), "Cannot update file with type '{}'".format(type(df))
        
        self._file_paths[filepath] = df
        
        if notes:
            update = dict(date=pd.Timestamp(datetime.datetime.now()),
                                                     notes=notes)
            
            self._file_updates[filepath].append(update)
        
    def remove_file(self, filepath):
        self._file_paths.pop(filepath)
    
    def read_file(self, filepath, **kwargs):
        
        try:
            df = self._file_paths[filepath]
        except KeyError:
            df = self._read_file(filepath, **kwargs)
            self._file_paths[filepath] = df
            
        return df
          
    def _read_file(self, filepath, **kwargs):
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.csv':
            
            df = pd.read_csv(filepath, **kwargs)
            
        elif ext == '.xlsx':
            
            df = pd.read_excel(filepath, **kwargs)
            
        elif ext == '.tsv':
            
            kwargs.update({"sep":"\t"})
            df = pd.read_csv(filepath, **kwargs)
            
        elif ext == '.txt':
            #TODO: Figure out separator.
            df = pd.read_csv(filepath, **kwargs)
            
        else:
            raise NotImplementedError("Cannot read filepath: {}".format(filepath))
        
        return df
    