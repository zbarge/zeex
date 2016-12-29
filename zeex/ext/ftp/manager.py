import ftputil
import datetime
import pandas as pd
import os

def now(): return pd.Timestamp(datetime.datetime.now())
#print(help(ftputil))




class FTPManager(object):
    """
    Basically a KeyChain that stores FTP credentials
    and generates ftputil.FTPHost objects.
    """
    def __init__(self):
        self._connections = {}

    def add_connection(self, *args, name=None, **kwargs):
        name = (args[0] if name is None else name)
        self._connections[name] = [args, kwargs]

    def remove_connection(self, name):
        self._connections.pop(name, None)

    def connection(self, name):
        args, kwargs = self._connections.get(name)
        return ftputil.FTPHost(*args, **kwargs)







