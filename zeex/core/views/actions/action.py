from functools import partial
from core.compat import QtGui, QtCore
from core.views.file import DataFrameModel


class AbstractAction(object):
    signalActionBegin = QtCore.Signal(str)
    signalActionError = QtCore.Signal(str)
    signalActionEnd = QtCore.Signal(DataFrameModel)

    def __init__(self, model=None):
        pass

