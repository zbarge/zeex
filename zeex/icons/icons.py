import os
from core.compat import QtGui

ICONS_DIRECTORY = os.path.dirname(__file__)
ICON_NAMES = ['add', 'delete', 'download', 'export_csv',
              'export_generic', 'export_pdf','folder',
              'import','merge','redo','save','saveas', 'send','split',
              'suppress', 'undo', 'edit', 'settings', 'home','ok',
              'cancel','delete_database', 'lightning','add_column', 'add_row',
              'delete_column', 'delete_row', 'filter', 'rename', 'spreadsheet']


def path_for(name: str, directory: str = None,  verify=False):
    if directory is None:
        directory = ICONS_DIRECTORY

    filename = os.path.join(directory, name)

    if '.' not in name:
        filename += '.png'

    if verify and not os.path.exists(filename):
        raise OSError("Cannot find icon file {} ".format(filename))

    return QtGui.QIcon(filename)


class Icons(dict):
    """
    Initialize this after the application
    has started to avoid QtGui errors.
    Call like a dict or an object.
    """
    def __init__(self, directory=None):
        if directory is None:
            self._directory = directory

        self.update({x: self.path_for(x) for x in ICON_NAMES})

    def path_for(self, name, verify=True):
        return path_for(name, directory=self._directory, verify=verify)

    def __getattr__(self, item):
        return self[item]


