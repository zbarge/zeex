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
from qtpandas.models.DataFrameModelManager import DataFrameModelManager as DFM

class DataFrameModelManager(DFM):
    """
    A central storage unit for managing
    DataFrameModels.
    """
    def __init__(self):
        DFM.__init__(self)
